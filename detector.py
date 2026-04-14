"""
detector.py — Auto-detect policy type, insurer, jurisdiction from any PDF
"""

import re
import json


def detect_policy_type(text: str, llm) -> dict:
    """
    Use Gemini to identify policy metadata from the first 3000 chars.

    Returns dict with: policy_type, insurer, policy_name,
                       jurisdiction, regulator, currency, key_features
    """
    sample = text[:3000]

    prompt = f"""
Read the following insurance document excerpt and return a JSON object:
{{
  "policy_type"  : "one of: Health | Life | Term Life | ULIP | Motor | Home/Property | Travel | Commercial | Marine | Personal Accident | Other",
  "insurer"      : "company name or Unknown",
  "policy_name"  : "product/policy name or Unknown",
  "jurisdiction" : "country or region (e.g. India, UK, USA)",
  "regulator"    : "regulatory body (e.g. IRDAI, FCA, NAIC)",
  "currency"     : "currency (e.g. INR, USD, GBP)",
  "key_features" : ["up to 5 short bullet points"]
}}

Return ONLY valid JSON. No markdown, no explanation.

Document excerpt:
{sample}
"""

    raw = llm.generate_content(prompt).text.strip()
    raw = re.sub(r"^```json|^```|```$", "", raw, flags=re.MULTILINE).strip()

    try:
        meta = json.loads(raw)
    except Exception:
        meta = {
            "policy_type" : "Unknown",
            "insurer"     : "Unknown",
            "policy_name" : "Unknown",
            "jurisdiction": "Unknown",
            "regulator"   : "Unknown",
            "currency"    : "Unknown",
            "key_features": [],
        }

    print(f"[detector] Policy type : {meta['policy_type']}")
    print(f"[detector] Insurer     : {meta['insurer']}")
    print(f"[detector] Jurisdiction: {meta['jurisdiction']} | Regulator: {meta['regulator']}")

    return meta
