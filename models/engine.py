import pandas as pd
import re
from transformers import pipeline

# Load the model once
classifier = pipeline("zero-shot-classification", model="cross-encoder/nli-MiniLM2-L6-H768")

# --- Constants & Patterns ---
BUZZWORDS = ["eco-friendly", "green", "natural", "sustainable", "conscious", "ethical"]
FUTURE_PROMISES = ["aim to", "committed to", "by 2030", "goal is", "pledge"]
EVIDENCE_PATTERNS = [r'\d+%', r'certified', r'gots', r'b-corp', r'iso\s*\d+', r'greenpro']
ENVIRONMENTAL_TOPICS = BUZZWORDS + FUTURE_PROMISES + ["carbon", "emissions", "water", "waste"]
LABELS = ["vague marketing fluff", "objective environmental fact"]

def load_databases():
    """Loads and standardizes certification CSVs from the data folder."""
    bcorp = pd.read_csv("data/bcorp.csv").rename(columns={'certification_type': 'cert_type'}, errors='ignore')
    gots = pd.read_csv("data/gots.csv")
    india = pd.read_csv("data/indian_certifications.csv")
    return bcorp, gots, india

def check_brands(text, bcorp, gots, india):
    """Matches text against known brand databases."""
    matches = []
    for db, name in [(bcorp, "B-Corp"), (gots, "GOTS"), (india, "India")]:
        for _, row in db.iterrows():
            if re.search(r'\b' + re.escape(str(row["brand"]).lower()) + r'\b', text.lower()):
                matches.append({
                    "brand": row["brand"], 
                    "certified": bool(row["certified"]), 
                    "type": str(row.get("cert_type", "None")), 
                    "db": name
                })
    return matches

def audit_product(text, bcorp, gots, india):
    """Calculates the Green-Truth score based on claims and evidence."""
    sentences = [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 10]
    brand_matches = check_brands(text, bcorp, gots, india)
    
    results = []
    for sent in sentences:
        if not any(t in sent.lower() for t in ENVIRONMENTAL_TOPICS):
            results.append({"sentence": sent, "verdict": "Website Noise", "score": 0.0})
            continue
            
        res = classifier(sent, LABELS)
        # Higher score if evidence keywords are found, otherwise rely on AI confidence
        score = 0.9 if any(re.search(p, sent.lower()) for p in EVIDENCE_PATTERNS) else \
                res["scores"][0] if res["labels"][0] == "objective environmental fact" else 0.1
        results.append({"sentence": sent, "verdict": res["labels"][0], "score": score})

    avg_score = sum(r['score'] for r in results) / len(results) if results else 0
    if any(m["certified"] == False for m in brand_matches): 
        avg_score = max(0, avg_score - 0.4)
    
    return {"sentences": results, "final_score": round(avg_score, 2), "brands": brand_matches}
