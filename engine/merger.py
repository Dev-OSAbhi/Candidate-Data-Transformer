import uuid
from .normalizers import clean_string, norm_phone, norm_skill

def get_base_schema(uid):
    return {
        "candidate_id": uid, "full_name": None, "emails": [], "phones": [],
        "location": {}, "links": {}, "headline": None, "years_experience": None,
        "skills": [], "experience": [], "education": [], "provenance": [],
        "overall_confidence": 0.0, "_conf_scores": []
    }

def merge_records(raw_records):
    profiles = {}
    
    for r in raw_records:
        # Identity Resolution
        uid = r['emails'][0] if r.get('emails') else str(uuid.uuid3(uuid.NAMESPACE_DNS, str(r)))
        if uid not in profiles:
            profiles[uid] = get_base_schema(uid)
            
        p = profiles[uid]
        src, meth, conf = r['source'], r['method'], r['confidence']
        
        def add_prov(field_name):
            p["provenance"].append({"field": field_name, "source": src, "method": meth})
            p["_conf_scores"].append(conf)

        # Merge Name (Highest confidence wins)
        fname = clean_string(r.get('full_name'))
        if fname:
            if not p['full_name'] or conf >= p["_conf_scores"][max(0, len(p["provenance"])-1)]:
                p['full_name'] = fname
                add_prov('full_name')

        # Merge Arrays (Union set)
        for email in r.get('emails', []):
            e = clean_string(email)
            if e and e not in p['emails']:
                p['emails'].append(e)
                add_prov('emails')

        for phone in r.get('phones', []):
            ph = norm_phone(phone)
            if ph and ph not in p['phones']:
                p['phones'].append(ph)
                add_prov('phones')

        # Merge Skills (Canonicalize and group sources)
        for skill_dict in r.get('skills', []):
            sk = norm_skill(skill_dict.get('name'))
            if not sk: continue
            
            existing = next((x for x in p['skills'] if x['name'] == sk), None)
            if not existing:
                p['skills'].append({"name": sk, "confidence": conf, "sources": [src]})
                add_prov('skills')
            else:
                if src not in existing['sources']: existing['sources'].append(src)
                if conf > existing['confidence']: existing['confidence'] = conf

        # Merge Experience
        if r.get('experience'):
            p['experience'].extend(r['experience'])
            add_prov('experience')

    # Finalize Confidence
    for p in profiles.values():
        if p["_conf_scores"]:
            p["overall_confidence"] = round(sum(p["_conf_scores"]) / len(p["_conf_scores"]), 2)
        del p["_conf_scores"]
        
    return list(profiles.values())