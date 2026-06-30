import re
from datetime import datetime

def clean_string(val):
    if not val or not isinstance(val, str): return None
    return val.strip() or None

def norm_phone(phone):
    if not phone: return None
    nums = re.sub(r'\D', '', str(phone))
    if len(nums) == 10:
        return f"+1{nums}"
    if len(nums) > 10 and not str(phone).startswith('+'):
        return f"+{nums}"
    return phone if str(phone).startswith('+') else f"+{nums}"

def norm_date(date_str):
    if not date_str: return None
    for fmt in ('%Y-%m-%d', '%m/%d/%Y', '%b %Y', '%B %Y', '%Y-%m'):
        try:
            return datetime.strptime(date_str, fmt).strftime('%Y-%m')
        except ValueError:
            continue
    return clean_string(date_str) # Fallback

def norm_skill(skill):
    if not skill: return None
    return str(skill).lower().strip('.,;!"\' ')