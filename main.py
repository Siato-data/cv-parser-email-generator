#cv parsing 2/main.py

from typing import List
import json
import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Local imports
from app_parsing.services.resume_processor import process_resumes
from app_parsing.services.document_loader import DocumentLoader

# Modifiez le logging pour afficher aussi dans la console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("resume_parser.log"),
        logging.StreamHandler()
    ]
)

# Chemin mis à jour pour le fichier .env
ENV_PATH = Path(__file__).parent / '.env'

# Load environment variables
load_dotenv(dotenv_path=ENV_PATH)

if __name__ == "__main__":
    print("Starting resume processing...")
    
    base_path = Path(__file__).parent
    resume_path = base_path / "app_parsing" / "data" / "resumes"
    print(f"Looking for resumes in: {resume_path}")
    
    cv_file_paths = []
    for file_path in resume_path.glob("*"):
        if file_path.suffix.lower() in DocumentLoader.SUPPORTED_FORMATS:
            cv_file_paths.append(str(file_path))
            
    print(f"Found {len(cv_file_paths)} supported files")
    
    if not cv_file_paths:
        print(f"No supported files found in {resume_path}")
        exit(1)

    # Ensure the output directory exists
    output_dir = base_path / "app_parsing" / "data" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist

    output_path = process_resumes(
        cv_file_paths,
        output_json_path=output_dir / "parsed_resumes.json",  # Use the created directory
        max_workers=3
    )