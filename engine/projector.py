from .normalizers import norm_phone, norm_skill

def get_nested_value(obj, path):
    """Safely extracts nested dictionary/list values using dot and bracket notation."""
    try:
        keys = path.replace('[', '.').replace(']', '').split('.')
        val = obj
        for k in keys:
            if not k: continue
            if isinstance(val, dict):
                val = val.get(k)
            elif isinstance(val, list) and k.isdigit():
                val = val[int(k)] if int(k) < len(val) else None
            else:
                return None
        return val
    except Exception:
        return None

def apply_config(canonical_record, config):
    out = {}
    missing_rule = config.get("on_missing", "null")
    
    for field in config.get("fields", []):
        target_key = field["path"]
        src_path = field.get("from", target_key)
        
        val = get_nested_value(canonical_record, src_path)
        
        if val is None or val == []:
            if missing_rule == "omit": continue
            elif missing_rule == "error": raise ValueError(f"Strict rule: Missing field '{target_key}'")
            out[target_key] = None
            continue
            
        # Apply projection normalizations
        if field.get("normalize") == "E164": val = norm_phone(val)
        if field.get("normalize") == "canonical" and isinstance(val, str): val = norm_skill(val)
            
        out[target_key] = val
        
    if config.get("include_confidence", False):
        out["overall_confidence"] = canonical_record.get("overall_confidence")
        out["provenance"] = canonical_record.get("provenance")
        
    return out