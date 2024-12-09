# cv parsing 2/app_parsing/services/email_personalizer.py

import os
import json
import logging
from typing import Dict, Any, List, Set, Optional
from openai import OpenAI
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from app_parsing.services.api_tracker import APIUsageTracker
from app_parsing.scripts.email_analysis import analyze_email_results

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Load the .env file located outside the app_parsing folder
load_dotenv(dotenv_path=Path(__file__).parent.parent.parent / '.env')

class EmailPersonalizer:
    """Service for generating personalized emails based on CV data and job requirements."""
    
    def __init__(self, api_key: str = None):
        """Initialize with OpenAI client."""
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

        self.EMAIL_TEMPLATES = {
            'standard': """
You are an expert recruiter writing highly personalized emails to candidates.
Use the provided candidate information and role requirements to craft a compelling email.
The candidate has a match rate of {match_score}% for this role.

Key Requirements:
1. Use a warm, conversational tone that reflects the company culture.
2. Structure the email in three parts:
   - Greeting: "Hey [Name] 👋"
   - Body: Two short paragraphs (2-3 sentences each)
   - Closing: "Best regards,\\n[Recruiter Name]"
3. Add phrases like "I noticed" or "I think" to make it personal.
4. Keep the email concise (around 20-30 words in body).
5. Use "\\n" for line breaks between paragraphs.
6. Write in a friendly, approachable style.
7. Focus on their key skills and potential fit.

Candidate Information:
{candidate_info}

Role Information:
{role_info}

IMPORTANT: Return your response in the exact JSON format shown below. Do not include any additional text or formatting:
{{
    "subject_line": "Exciting [Position] opportunity at [Company Name]😊",
    "email_body": "Hey [Name] 👋\\n\\nI noticed your strong [Key Skill] work at [Company]. Your [Specific Achievement] background caught my eye.\\n\\nLet's discuss our [Position] opportunity.\\n\\nBest regards,\\n[Recruiter Name]",
    "personalization_points": [
        "Point about candidate's specific experience",
        "Point about candidate's relevant achievements",
        "Point about matching skills and qualifications"
    ],
    "highlight_skills": [
        "Relevant Skill 1",
        "Relevant Skill 2",
        "Relevant Skill 3"
    ]
}}

Note: Replace placeholders with actual content. Ensure all keys and structure remain exactly as shown above.
"""
        }

    def _validate_role_data(self, role_data: Dict[str, Any]) -> bool:
        """Validate role_data to ensure required keys exist."""
        required_keys = ['title', 'company', 'requirements']
        for key in required_keys:
            if key not in role_data:
                logging.error(f"Missing required key in role_data: {key}")
                return False
        return True

    def _validate_candidate_data(self, candidate_data: Dict[str, Any]) -> bool:
        """Validate candidate data has essential information."""
        required_keys = [
            'Full Name',
            'Professional Title',
            'Work Experience',
            'Skills'
        ]
        return all(candidate_data.get(key) for key in required_keys)

    def _format_candidate_info(self, candidate_data: Dict[str, Any]) -> str:
        """Format candidate data dynamically based on available information."""
        formatted_info = [
            f"Name: {candidate_data['Full Name']}",
            f"Current Role: {candidate_data['Professional Title']}"
        ]

        # Work Experience
        if work_experience := candidate_data.get('Work Experience'):
            current_role = work_experience[0]
            formatted_info.append(f"- Current: {current_role['Company']} ({current_role['Title']})")
            if achievements := current_role.get('Achievements', []):
                formatted_info.append(f"- Notable Achievement: {achievements[0]}")

        # Total experience
        years_exp = candidate_data.get('Professional Summary', {}).get('Years of Experience')
        if years_exp:
            formatted_info.append(f"- Total Experience: {years_exp} years")

        # Education
        if candidate_data.get('Education'):
            latest_edu = candidate_data['Education'][0]
            edu_parts = []
            if degree := latest_edu.get('Degree'):
                edu_parts.append(degree)
            if field := latest_edu.get('Field of Study'):
                edu_parts.append(f"in {field}")
            if institution := latest_edu.get('Institution'):
                edu_parts.append(f"from {institution}")
            if edu_parts:
                formatted_info.append("Education: " + " ".join(edu_parts))

        # Skills
        if skills := candidate_data.get('Skills', {}):
            if tech_skills := skills.get('Technical Skills', []):
                formatted_info.append(f"Technical Skills: {', '.join(tech_skills[:4])}")
            if soft_skills := skills.get('Soft Skills', []):
                formatted_info.append(f"Soft Skills: {', '.join(soft_skills[:3])}")

        return "\n".join(formatted_info)

    def _format_role_info(self, role_data: Dict[str, Any]) -> str:
        """Format role information for the prompt."""
        must_have = ", ".join(role_data.get('requirements', {}).get('must_have', []))
        nice_to_have = ", ".join(role_data.get('requirements', {}).get('nice_to_have', []))
        
        return f"""
        Title: {role_data.get('title', 'N/A')}
        Company: {role_data.get('company', 'N/A')}
        Required Skills: {must_have if must_have else 'None specified'}
        Nice-to-have Skills: {nice_to_have if nice_to_have else 'None specified'}
        Experience Level: {role_data.get('requirements', {}).get('experience_level', 'Not specified')}
        Work Style: {role_data.get('remote_policy', 'Not specified')}
        Team Size: {role_data.get('team_size', 'Not specified')}
        Industry: {role_data.get('industry', 'Not specified')}
        Company Culture: {role_data.get('culture', 'Not specified')}
        """

    def calculate_match_score(self, candidate_data: Dict[str, Any], role_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate a detailed match score."""
        try:
            required_skills = set(s.lower() for s in role_data.get('requirements', {}).get('must_have', []))
            nice_to_have = set(s.lower() for s in role_data.get('requirements', {}).get('nice_to_have', []))
            
            candidate_skills = set(s.lower() for s in (
                candidate_data.get('Skills', {}).get('Technical Skills', []) +
                candidate_data.get('Skills', {}).get('Soft Skills', [])
            ))

            # Calculate scores
            required_match = self._calculate_skills_match(required_skills, candidate_skills)
            nice_to_have_match = self._calculate_skills_match(nice_to_have, candidate_skills)
            experience_score = self._calculate_experience_relevance(candidate_data, role_data)
            background_score = self._calculate_background_relevance(candidate_data, role_data)

            # Weight the scores
            total_score = (
                required_match * 0.4 +     # 40% for required skills
                nice_to_have_match * 0.1 + # 10% for nice-to-have skills
                experience_score * 0.3 +   # 30% for experience
                background_score * 0.2     # 20% for background relevance
            )

            # Final adjustments
            total_score = self._apply_scoring_adjustments(total_score, candidate_data, role_data)

            return {
                'total_score': round(total_score, 1),
                'breakdown': {
                    'required_skills': round(required_match, 1),
                    'nice_to_have': round(nice_to_have_match, 1),
                    'experience': round(experience_score, 1),
                    'background': round(background_score, 1)
                },
                'matching_skills': list(required_skills.intersection(candidate_skills)),
                'bonus_skills': list(nice_to_have.intersection(candidate_skills))
            }

        except Exception as e:
            logging.error(f"Error calculating match score: {str(e)}")
            return {'total_score': 0, 'breakdown': {}, 'matching_skills': [], 'bonus_skills': []}

    def generate_email(self, candidate_data: Dict[str, Any], role_data: Dict[str, Any], api_tracker: APIUsageTracker) -> Optional[Dict[str, Any]]:
        """Generate personalized email based on candidate-role match."""
        try:
            # Basic validation
            if not self._validate_role_data(role_data) or not self._validate_candidate_data(candidate_data):
                return None

            # Calculate match score
            match_results = self.calculate_match_score(candidate_data, role_data)
            total_score = match_results['total_score']

            # Do not generate email if the score is too low
            if total_score < 50:  # Changed to 50% for standard
                logging.info(f"Score too low ({total_score}%) for candidate: {candidate_data['Full Name']}")
                return None

            # Use the standard template for all candidates with a score of 50% or higher
            template = self.EMAIL_TEMPLATES['standard']

            # Prepare context
            context = {
                'candidate_info': self._format_candidate_info(candidate_data),
                'role_info': self._format_role_info(role_data),
                'match_score': total_score,
                'matching_skills': ', '.join(match_results['matching_skills'])
            }

            # Generate the email
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{
                    "role": "user", 
                    "content": template.format(**context)
                }],
                temperature=0.7
            )

            api_tracker.update(response.usage.total_tokens)

            email_data = json.loads(response.choices[0].message.content)
            email_data.update({
                'match_score': f"{total_score}%",
                'match_details': match_results
            })

            return email_data

        except Exception as e:
            logging.error(f"Error generating email: {str(e)}")
            return None

    def process_batch(self, cv_file: str, role_data: Dict[str, Any], output_dir: str = "app_parsing/data/output/emails") -> None:
        """Process a batch of CVs and generate personalized emails."""
        try:
            api_tracker = APIUsageTracker()
            start_time = datetime.now()

            # Load parsed CVs
            with open(cv_file, "r") as f:
                parsed_data = json.load(f)
                cvs = parsed_data["resumes"]

            logging.info(f"Starting to process {len(cvs)} CVs")

            # Create output directory
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # Process each CV
            results = []
            successful = 0
            failed = 0

            for cv in cvs:
                if cv.get("_metadata", {}).get("success", False):
                    if email_data := self.generate_email(cv, role_data, api_tracker):
                        successful += 1
                        results.append({
                            "candidate_name": cv["Full Name"],
                            "email_data": email_data,
                            "timestamp": datetime.now().isoformat()
                        })
                    else:
                        failed += 1

            # Calculate statistics
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            
            output_data = {
                "emails": results,
                "statistics": {
                    "total_processed": len(cvs),
                    "successful": successful,
                    "failed": failed,
                    "success_rate": (successful / len(cvs) * 100) if len(cvs) > 0 else 0,
                    "processing_time": str(end_time - start_time),
                    "processing_time_seconds": processing_time,
                    "api_usage": api_tracker.get_stats()
                },
                "role_data": role_data,
                "timestamp": datetime.now().isoformat()
            }

            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = output_path / f"generated_emails_{timestamp}.json"
            with open(output_file, "w") as f:
                json.dump(output_data, f, indent=2)

            logging.info(f"Successfully generated {successful} emails out of {len(cvs)} CVs")
            logging.info(f"Results saved to {output_file}")
            
            # Run analysis
            analyze_email_results(str(output_file))
            
        except Exception as e:
            logging.error(f"Error processing batch: {str(e)}")
            raise

    def _calculate_skills_match(self, required: Set[str], candidate: Set[str]) -> float:
        """Calcule la correspondance des compétences."""
        if not required:
            return 100.0
            
        matches = 0
        for skill in required:
            if skill.lower() in (s.lower() for s in candidate):
                matches += 1
                
        return (matches / len(required)) * 100.0

    def _calculate_experience_relevance(self, candidate_data: Dict[str, Any], role_data: Dict[str, Any]) -> float:
        """Évalue la pertinence de l'expérience."""
        required_years = self._parse_experience_requirement(role_data.get('requirements', {}).get('experience_level', '0'))
        candidate_years = float(candidate_data.get('Professional Summary', {}).get('Years of Experience', 0))
        
        # Compare l'expérience et donne un score
        if required_years > 0:
            if candidate_years >= required_years:
                return min(100.0, 80.0 + (candidate_years - required_years) * 5)  # Bonus pour plus d'expérience
            else:
                return (candidate_years / required_years) * 80.0  # Score proportionnel jusqu'à 80%
        
        return 100.0  # Si pas d'exigence d'expérience

    def _calculate_background_relevance(self, candidate_data: Dict[str, Any], role_data: Dict[str, Any]) -> float:
        """Évalue la pertinence du background."""
        current_title = candidate_data.get('Professional Title', '').lower()
        target_title = role_data.get('title', '').lower()
        industry = role_data.get('industry', '').lower()

        score = 0.0
        
        # Pertinence du titre
        if any(word in current_title for word in target_title.split()):
            score += 60.0
            
        # Pertinence de l'industrie
        work_exp = candidate_data.get('Work Experience', [])
        if work_exp and any(industry in exp.get('Company Industry', '').lower() for exp in work_exp):
            score += 40.0
            
        return min(100.0, score)

    def _apply_scoring_adjustments(self, score: float, candidate_data: Dict[str, Any], role_data: Dict[str, Any]) -> float:
        """Applique des ajustements au score final."""
        return min(100.0, max(0.0, score))

    def _parse_experience_requirement(self, exp_requirement: str) -> float:
        """Parse les exigences d'expérience en années."""
        try:
            if '-' in exp_requirement:
                return float(exp_requirement.split('-')[0])
            elif 'year' in exp_requirement.lower():
                return float(''.join(filter(str.isdigit, exp_requirement)))
            return 0.0
        except:
            return 0.0

    def preview_email(self, candidate_data: Dict[str, Any], role_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Preview the email generated for a candidate based on their data and role data."""
        api_tracker = APIUsageTracker()
        return self.generate_email(candidate_data, role_data, api_tracker)


def main():
    """Example usage of EmailPersonalizer."""
    role_data = {
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "requirements": {
            "must_have": ["Python", "AWS"],
            "nice_to_have": ["Microservices", "Docker"],
            "experience_level": "3-5 years",
        },
        "culture": "Fast-paced, innovative startup environment",
        "team_size": "10-15 people",
        "remote_policy": "Hybrid",
        "industry": "FinTech"
    }

    personalizer = EmailPersonalizer()
    personalizer.process_batch(
        cv_file="app_parsing/data/output/parsed_resumes.json",
        role_data=role_data
    )


if __name__ == "__main__":
    main()