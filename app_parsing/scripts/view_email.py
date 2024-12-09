import json
from pathlib import Path
from datetime import datetime

def view_formatted_emails(json_path: str):
    """View formatted emails from the generated JSON file."""
    try:
        # Read the JSON file
        with open(json_path, 'r') as f:
            data = json.load(f)

        output_dir = Path("app_parsing/data/output/emails")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = output_dir / f"formatted_emails_{timestamp}.txt"    
     
        # For each email in the file
        with open(output_file, 'w') as file:
            for email in data['emails']:
                file.write("=" * 50 + "\n")
                file.write(f"Candidate: {email['candidate_name']}\n")
                file.write(f"Match Score: {email['email_data'].get('match_score', 'N/A')}\n")
                if 'match_details' in email['email_data']:
                    matched_skills = ', '.join(email['email_data']['match_details'].get('matched_skills', []))
                    file.write(f"Matched Skills: {matched_skills}\n")
                file.write("-" * 20 + "\n")
                file.write(f"Subject: {email['email_data']['subject_line']}\n")
                file.write("-" * 20 + "\n")
                file.write(email['email_data']['email_body'] + "\n")
                file.write("\n")

        print(f"Formatted emails have been written to {output_file}")

    except Exception as e:
        print(f"Error reading file: {str(e)}")

def list_json_files(directory: str):
    """List all JSON files in the specified directory."""
    path = Path(directory)
    return list(path.glob("*.json"))

if __name__ == "__main__":
    email_directory = "app_parsing/data/output/emails"
    json_files = list_json_files(email_directory)
    
    if not json_files:
        print("No JSON files found in the specified directory.")
    else:
        print("Available JSON files:")
        for i, file in enumerate(json_files):
            print(f"{i + 1}: {file.name}")
        
        choice = int(input("Select a file number to view: ")) - 1
        if 0 <= choice < len(json_files):
            view_formatted_emails(json_files[choice])
        else:
            print("Invalid choice.")