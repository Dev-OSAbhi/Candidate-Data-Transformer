import argparse
import json
import sys
from engine.extractors import parse_csv, parse_txt, parse_ats_json
from engine.merger import merge_records
from engine.projector import apply_config

def main():
    parser = argparse.ArgumentParser(description="Multi-Source Candidate Data Transformer")
    parser.add_argument("--csv", help="Path to recruiter CSV")
    parser.add_argument("--ats", help="Path to ATS JSON blob")
    parser.add_argument("--txt", help="Path to recruiter notes TXT")
    parser.add_argument("--config", help="Path to twist config JSON")
    args = parser.parse_args()

    raw_data = []
    
    if args.csv: raw_data.extend(parse_csv(args.csv))
    if args.ats: raw_data.extend(parse_ats_json(args.ats))
    if args.txt: raw_data.extend(parse_txt(args.txt))
    
    if not raw_data:
        print("Error: Provide at least one source file (--csv, --ats, or --txt)")
        sys.exit(1)

    # 1. Merge into canonical schema
    canonical_profiles = merge_records(raw_data)

    # 2. Apply projection if config is provided
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            
            final_output = []
            for profile in canonical_profiles:
                try:
                    final_output.append(apply_config(profile, config))
                except ValueError as e:
                    print(f"Skipping profile {profile.get('candidate_id')} due to config error: {e}")
            
            print(json.dumps(final_output, indent=2))
            
        except Exception as e:
            print(f"Config error ({e}). Falling back to base canonical schema.")
            print(json.dumps(canonical_profiles, indent=2))
    else:
        # Default Output
        print(json.dumps(canonical_profiles, indent=2))

if __name__ == "__main__":
    main()