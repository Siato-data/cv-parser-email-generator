#cv parsing 2/app_parsing/services/resume_processor.py

import json
import os
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import List
from dotenv import load_dotenv
from openai import OpenAI

from app_parsing.models.candidate import Candidate
from app_parsing.services.document_loader import DocumentLoader
from app_parsing.services.api_tracker import APIUsageTracker
from app_parsing.utils.prompts import PROMPT_TEMPLATE






def format_processing_time(seconds: float) -> str:
    """Converts seconds to minutes and seconds format.
    
    Args:
        seconds: Number of seconds to convert
        
    Returns:
        str: Formatted time (e.g., "5m 30s")
    """
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes}m {remaining_seconds}s"






def parse_single_resume(args: dict, max_retries=3) -> dict:
    """Parse a single resume with retry handling.
    
    Args:
        args: Dictionary containing file_path, client and api_tracker
        max_retries: Maximum number of parsing attempts
        
    Returns:
        dict: Structured resume data or error data
    """
    file_path, client, api_tracker = args["file_path"], args["client"], args["api_tracker"]
    
    for attempt in range(max_retries):
        try:
            resume_text = DocumentLoader.load_document(file_path)
            
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": PROMPT_TEMPLATE.format(resume_text=resume_text)}],
                max_tokens=4000,
                temperature=0
            )
            
            api_tracker.update(response.usage.total_tokens)
            
            parsed_data = json.loads(response.choices[0].message.content.strip())
            parsed_data["_metadata"] = {
                "filename": file_path.name,
                "file_type": file_path.suffix.lower(),
                "tokens_used": response.usage.total_tokens,
                "success": True
            }
            
            logging.info(f"Successfully parsed {file_path.name}")
            return parsed_data
            
        except Exception as e:
            logging.error(f"Attempt {attempt + 1} failed for {file_path.name}. Error: {str(e)}")
            if attempt == max_retries - 1:
                return {
                    "_metadata": {
                        "filename": file_path.name,
                        "file_type": file_path.suffix.lower(),
                        "success": False,
                        "error": str(e)
                    }
                }
            time.sleep(2 ** attempt)






def process_resumes(cv_file_paths: List[str], output_json_path: str = "parsed_resumes.json", max_workers: int = 3):
    """Process a list of resumes and extract structured information.

    This function coordinates the resume parsing process, including:
    - Document loading
    - Information extraction via GPT
    - Error handling and retries
    - Statistics generation
    - Results export

    Args:
        cv_file_paths (List[str]): List of paths to resume files
        output_json_path (str): Path for the output JSON file
        max_workers (int): Maximum number of parallel workers

    Returns:
        Path: Path of the generated JSON file

    Raises:
        FileNotFoundError: If no resume files are found
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    api_tracker = APIUsageTracker()
    
    cv_paths = [Path(path) for path in cv_file_paths]
    all_data = []
    batch_size = 10
    
    # Log format statistics at start
    format_counts = {}
    for path in cv_paths:
        fmt = path.suffix.lower()
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
    logging.info(f"Found files by format: {format_counts}")
    
    logging.info(f"Starting to process {len(cv_paths)} resumes")
    start_time = time.time()
    
    for i in range(0, len(cv_paths), batch_size):
        batch = cv_paths[i:i + batch_size]
        logging.info(f"Processing batch {i//batch_size + 1}")
        
        args_list = [{"file_path": path, "client": client, "api_tracker": api_tracker} for path in batch]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = list(executor.map(parse_single_resume, args_list))
            all_data.extend(results)
        
        if i + batch_size < len(cv_paths):
            time.sleep(5)
    
    processing_time = time.time() - start_time
    
    # Calculate format-specific statistics
    format_stats = {}
    for data in all_data:
        file_type = data.get("_metadata", {}).get("file_type")
        if file_type:
            if file_type not in format_stats:
                format_stats[file_type] = {"total": 0, "successful": 0}
            format_stats[file_type]["total"] += 1
            if data.get("_metadata", {}).get("success", False):
                format_stats[file_type]["successful"] += 1
    
    successful = sum(1 for data in all_data if data.get("_metadata", {}).get("success", False))
    
    output_path = Path(output_json_path)
    with output_path.open("w") as f:
        json.dump({
            "resumes": all_data,
            "statistics": {
                "total_processed": len(cv_paths),
                "successful": successful,
                "failed": len(cv_paths) - successful,
                "processing_time": format_processing_time(processing_time),
                "processing_time_seconds": round(processing_time, 2),
                "format_statistics": format_stats,
                "api_usage": api_tracker.get_stats()
            }
        }, f, indent=2)
    
    return output_path