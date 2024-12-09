import pandas as pd
import json
from pathlib import Path
import time
from typing import Dict

def analyze_email_results(json_path: str = "app_parsing/data/output/emails/generated_emails_20241130_223043.json") -> Dict:
    """Analyze email generation results and provide detailed statistics."""
    # Read JSON file
    with open(json_path, "r") as f:
        data = json.load(f)

    # Create DataFrame from emails
    emails_df = pd.DataFrame(data["emails"])
    
    # Calculate match score statistics
    match_scores = []
    for email in data['emails']:
        match_score = email['email_data'].get('match_score', '0%')
        score = float(match_score.strip('%'))
        match_scores.append(score)

    print("\n=== EMAIL GENERATION ANALYSIS REPORT ===")
    print("-" * 50)
    
    print("\nMATCH SCORE STATISTICS:")
    print("-" * 50)
    if match_scores:
        print(f"Average Match Score : {sum(match_scores)/len(match_scores):.2f}%")
        print(f"Qualified Matches (≥50%) : {len([s for s in match_scores if s >= 50])}")
        print(f"Unqualified Matches (<50%) : {len([s for s in match_scores if s < 50])}")
    else:
        print("No match scores available.")

    print("\nGLOBAL STATISTICS:")
    print("-" * 50)
    
    # Check if there are any emails processed
    total_emails = len(data['emails'])
    print(f"Total CVs Processed : {total_emails}")
    print(f"Emails Generated   : {len(emails_df)}")
    
    # Check to avoid division by zero
    if total_emails > 0:
        print(f"Generation Rate    : {(len(emails_df) / total_emails * 100):.2f}%")
    else:
        print("No emails generated. Cannot calculate generation rate.")

    # Group by matched skills
    skills_mentioned = []
    for email in data['emails']:
        if 'match_details' in email['email_data']:
            skills_mentioned.extend(email['email_data']['match_details'].get('matched_skills', []))
    
    print("\nMOST COMMON MATCHED SKILLS:")
    print("-" * 50)
    skill_counts = pd.Series(skills_mentioned).value_counts()
    for skill, count in skill_counts.head().items():
        print(f"{skill:20}: {count} times")

    # API Usage Statistics
    if 'statistics' in data and 'api_usage' in data['statistics']:
        print("\nAPI COSTS AND USAGE:")
        print("-" * 50)
        api_stats = data['statistics']['api_usage']
        print(f"Tokens used     : {api_stats['total_tokens']:,}")
        print(f"Total cost      : ${api_stats['total_cost_usd']:.2f}")
        
        # Check if emails_df is empty before calculating average cost per email
        if len(emails_df) > 0:
            print(f"Average cost/email : ${api_stats['total_cost_usd'] / len(emails_df):.4f}")
        else:
            print("No emails generated, cannot calculate average cost per email.")

    # Time Analysis
    if 'timestamp' in emails_df.columns:
        emails_df['timestamp'] = pd.to_datetime(emails_df['timestamp'])
        total_time = (emails_df['timestamp'].max() - emails_df['timestamp'].min()).total_seconds()
        print("\nPERFORMANCE:")
        print("-" * 50)
        print(f"Total time        : {total_time/60:.2f} minutes")
        print(f"Average time/email: {total_time/len(emails_df):.2f} seconds" if len(emails_df) > 0 else "No emails generated, cannot calculate average time per email.")

    # Generate candidates summary
    print("\nCANDIDATES SUMMARY:")
    print("-" * 50)
    for email in data['emails'][:5]:
        score = email['email_data'].get('match_score', 'N/A')
        name = email['candidate_name']
        matched = []
        if 'match_details' in email['email_data']:
            matched = email['email_data']['match_details'].get('matched_skills', [])
        matched_str = ', '.join(matched[:3])
        print(f"{name:30} | Match: {score} | Matched Skills: {matched_str}")
    if len(data['emails']) > 5:
        print(f"... and {len(data['emails'])-5} more candidates")

    return {
        "total_processed": len(data['emails']),
        "emails_generated": len(emails_df),
        "match_scores": match_scores,
        "skill_statistics": skill_counts.to_dict(),
        "api_usage": data.get('api_usage', {})
    }

if __name__ == "__main__":
    analyze_email_results()