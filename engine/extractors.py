import csv
import json
import re

def parse_csv(filepath):
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for row in csv.DictReader(f):
                records.append({
                    "source": filepath,
                    "method": "csv_dict_reader",
                    "confidence": 0.8,
                    "full_name": row.get("name"),
                    "emails": [row.get("email")] if row.get("email") else [],
                    "phones": [row.get("phone")] if row.get("phone") else [],
                    "experience": [{
                        "company": row.get("current_company"),
                        "title": row.get("title")
                    }] if row.get("current_company") else []
                })
    except Exception as e:
        print(f"Warning: Failed to read CSV {filepath}: {e}")
    return records

def parse_ats_json(filepath):
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                records.append({
                    "source": filepath,
                    "method": "json_parser",
                    "confidence": 0.9,
                    "full_name": f"{item.get('firstName', '')} {item.get('lastName', '')}".strip(),
                    "emails": [item.get("contactEmail")] if item.get("contactEmail") else [],
                    "phones": [item.get("contactPhone")] if item.get("contactPhone") else [],
                    "skills": [{"name": s} for s in item.get("tags", [])]
                })
    except Exception as e:
        print(f"Warning: Failed to read JSON {filepath}: {e}")
    return records

def parse_txt(filepath):
    records = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            
        emails = re.findall(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+', text)
        phones = re.findall(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
        name_match = re.search(r'Candidate:\s*([A-Za-z\s]+)', text)
        skills_match = re.search(r'Skills:\s*(.+?)(?:\n|$)', text)
        
        skills = []
        if skills_match:
            skills = [{"name": s.strip()} for s in skills_match.group(1).split(',')]

        records.append({
            "source": filepath,
            "method": "regex_heuristics",
            "confidence": 0.6,
            "full_name": name_match.group(1).strip() if name_match else None,
            "emails": emails,
            "phones": phones,
            "skills": skills
        })
    except Exception as e:
        print(f"Warning: Failed to read TXT {filepath}: {e}")
    return records