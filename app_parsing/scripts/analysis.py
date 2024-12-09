# cv parsing 2/app_parsing/scripts/analysis.py

import pandas as pd
import json
from pathlib import Path
import time
from typing import Dict

def analyze_parsing_results(json_path: str = "app_parsing/data/output/parsed_resumes.json") -> Dict:
    """Analyze CV parsing results and provide detailed statistics.
    
    Args:
        json_path: Path to the parsing results JSON file
        
    Returns:
        Dict containing analysis results
    """
    # Read JSON file
    with open(json_path, "r") as f:
        data = json.load(f)

    # Create DataFrame from CVs
    resumes_df = pd.DataFrame(data["resumes"])

    print(resumes_df.columns)# Find CVs with success = False
    failed_resumes = resumes_df[resumes_df["_metadata"].apply(lambda x: not x["success"])]

    # Print results
    print("\n=== PARSING ANALYSIS REPORT ===")
    print("\nFAILED CVs:")
    print("-" * 50)
    if len(failed_resumes) > 0:
        for _, row in failed_resumes.iterrows():
            print(f"File: {row['_metadata']['filename']}")
            print(f"Error: {row['_metadata'].get('error', 'Not specified')}")
            print("-" * 30)
    else:
        print("No failures! 🎉")

    print("\nGLOBAL STATISTICS:")
    print("-" * 50)
    print(f"Total processed  : {data['statistics']['total_processed']}")
    print(f"Successful      : {data['statistics']['successful']}")
    print(f"Failed          : {data['statistics']['failed']}")
    print(f"Success rate    : {(data['statistics']['successful']/data['statistics']['total_processed']*100):.2f}%")
    
    print("\nPERFORMANCE:")
    print("-" * 50)
    print(f"Total time      : {data['statistics']['processing_time']}")
    print(f"Average time/CV : {data['statistics']['processing_time_seconds']/data['statistics']['total_processed']:.2f} seconds")
    
    print("\nAPI COSTS AND USAGE:")
    print("-" * 50)
    api_stats = data['statistics']['api_usage']
    print(f"Tokens used     : {api_stats['total_tokens']:,}")
    print(f"Total cost      : ${api_stats['total_cost_usd']:.2f}")
    print(f"Average cost/CV : ${api_stats['total_cost_usd']/data['statistics']['total_processed']:.4f}")

    print("\nSTATISTICS BY FORMAT:")
    print("-" * 50)
    for fmt, stats in data['statistics']['format_statistics'].items():
        success_rate = (stats['successful'] / stats['total'] * 100)
        print(f"{fmt:5} : {stats['successful']}/{stats['total']} ({success_rate:.1f}% success)")

    return {
        "failed_resumes": failed_resumes.to_dict('records'),
        "statistics": data['statistics']
    }



if __name__ == "__main__":
    analyze_parsing_results()

