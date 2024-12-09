#cv parsing 2/app_parsing/models/candidate

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid

@dataclass
class Candidate:
    """Explicit structure to represent a candidate parsed from a resume.

    This class defines the standard data structure for storing
    information extracted from a resume.

    Attributes:
        id (str): Unique identifier for the candidate
        full_name (str): Full name of the candidate
        professional_title (str): Current or target professional title
        contact_info (dict): Contact information (email, phone, etc.)
        professional_summary (dict): Professional summary and experience
        work_experience (List[dict]): List of professional experiences
        education (List[dict]): List of educational background
        skills (dict): Technical and soft skills
        certifications (List[dict]): List of certifications
        hr_evaluation (dict): HR evaluation and notes
        metadata (dict): Technical parsing metadata
    """
    id: str
    full_name: str
    professional_title: str
    contact_info: dict
    professional_summary: dict
    work_experience: List[dict]
    education: List[dict]
    skills: dict
    certifications: List[dict]
    hr_evaluation: dict
    metadata: dict

    @classmethod
    def from_parsed_data(cls, parsed_data: dict) -> 'Candidate':
        """Creates a Candidate instance from parsed data.

        Args:
            parsed_data (dict): Raw parsed data from resume

        Returns:
            Candidate: New instance with structured data
        """
        return cls(
            id=str(uuid.uuid4()),
            full_name=parsed_data.get('full_name', ''),
            professional_title=parsed_data.get('professional_title', ''),
            contact_info=parsed_data.get('contact_info', {}),
            professional_summary=parsed_data.get('professional_summary', {}),
            work_experience=parsed_data.get('work_experience', []),
            education=parsed_data.get('education', []),
            skills=parsed_data.get('skills', {}),
            certifications=parsed_data.get('certifications', []),
            hr_evaluation=parsed_data.get('hr_evaluation', {}),
            metadata=parsed_data.get('_metadata', {})
        )