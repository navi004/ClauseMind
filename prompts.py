"""
prompts.py — Adaptive prompt templates for any insurance policy type

All prompts auto-populate with detected policy metadata so the
analysis language always matches the document.
"""


def build_prompts(meta: dict) -> dict:
    """
    Build 8 task-specific prompts adapted to the detected policy.

    Args:
        meta: dict from detector.detect_policy_type()

    Returns:
        dict of {task_name: prompt_template_string}
        Each template has a single {context} placeholder.
    """
    ptype   = meta.get("policy_type",  "insurance")
    insurer = meta.get("insurer",      "the insurer")
    juris   = meta.get("jurisdiction", "the applicable jurisdiction")
    reg     = meta.get("regulator",    "the regulatory body")
    curr    = meta.get("currency",     "the local currency")

    base = (
    f"You are an expert in {ptype} insurance in {juris}, familiar with {reg} guidelines. "
    f"The excerpts are tagged with page numbers like [Excerpt 1 | Page 5]. "
    f"For every point you make, cite the page number in brackets like (Page 5). "
    f"If a point comes from multiple pages, cite all of them like (Page 5, Page 12)."
        )

    return {

        "summary": f"""
        You are an Indian health insurance expert familiar with IRDAI guidelines.
        Based ONLY on the policy excerpts below, provide:
        1. Type of health cover (individual / family floater / both)
        2. Sum insured options available
        3. Top 5 covered treatments with any INR limits
        4. OPD, daycare, and maternity coverage details
        5. Network hospital and cashless claim process

        Policy excerpts:
        {{context}}
        """,

        "weasel_words": f"""
        {base} You are also a consumer protection attorney.
        Identify ALL ambiguous, vague, or insurer-favourable terms ('weasel words') in the excerpts.
        For each term:
        - Exact phrase from the policy
        - Why it is ambiguous or favours {insurer}
        - Risk to the policyholder in plain language
        - Severity: HIGH / MEDIUM / LOW

        Be exhaustive — this is for academic fraud and risk research.

        Policy excerpts:
        {{context}}
        """,

        "exclusions": f"""
        {base} You are a claims specialist.
        Extract ALL exclusions, limitations, and denial clauses from the excerpts.
        For each:
        - Name of the exclusion
        - Exact clause text
        - Severity: HIGH / MEDIUM / LOW
        - Real-world scenario where a valid claim would be denied
        - Whether this complies with {reg} minimum standards

        Policy excerpts:
        {{context}}
        """,

        "waiting_periods": f"""
        {base}
        Extract ALL waiting periods, cooling-off periods, and deferral clauses.
        For each:
        - Type (initial / disease-specific / PED / free-look / lock-in etc.)
        - Duration
        - What is deferred or excluded during this period
        - Whether it can be waived or reduced
        - Impact on the policyholder: HIGH / MEDIUM / LOW

        Policy excerpts:
        {{context}}
        """,

        "financial_limits": f"""
        {base} You are an underwriting expert.
        Extract ALL financial caps, sub-limits, co-payments, deductibles, and proportionate clauses.
        For each:
        - Type (sub-limit / co-pay / deductible / room cap etc.)
        - Amount or percentage (in {curr} where applicable)
        - What it applies to
        - Whether it is above or below typical market norms
        - Policyholder risk: HIGH / MEDIUM / LOW

        Policy excerpts:
        {{context}}
        """,

        "gap_analysis": f"""
        You are a senior health insurance underwriter in India.
        Compare the policy excerpts against the actual IRDAI guidelines provided below.

        For each gap found:
        - What the policy says (quote it)
        - What IRDAI mandates (quote the guideline)
        - Whether the policy meets, exceeds, or falls short
        - Risk to policyholder: HIGH / MEDIUM / LOW

        Focus on: room rent limits, PED waiting periods, free-look period,
        claim settlement timelines, mandatory covers, sub-limits, co-payments.

        Policy excerpts:
        {{context}}

        IRDAI Guidelines:
        {{irdai_context}}
        """,

        "fraud_risk": f"""
        You are a health insurance fraud analyst in India.
        Analyse the excerpts and identify:
        1. Clauses exploitable for fraudulent health claims
        (e.g. fake hospitalisation, inflated bills, unnecessary procedures)
        2. Clauses {insurer} can use to wrongly deny legitimate health claims
        (e.g. PED misuse, treatment not deemed necessary, intimation delays)
        3. Cashless vs reimbursement abuse potential
        4. Overall fraud exposure: HIGH / MEDIUM / LOW with justification

        Policy excerpts:
        {{context}}
        """,    

        "policyholder_rights": f"""
        {base} You are a consumer rights expert.
        From the excerpts, identify:
        - Policyholder rights (free-look, grievance, portability, nomination etc.)
        - Cancellation and refund terms (by insurer AND policyholder)
        - Renewal rights and conditions
        - Any rights that appear weaker than {reg} mandates

        Policy excerpts:
        {{context}}
        """,
    }


# ── Recommended search queries per task ────────────────────────────────────
# Used by the engine to pull the most relevant chunks from FAISS.

TASK_QUERIES = {
    "summary"            : "health coverage hospitalisation benefits sum insured OPD daycare",
    "weasel_words"       : "medically necessary reasonable customary sole discretion as determined",
    "exclusions"         : "exclusions not covered Code Excl PED pre-existing disease treatment",
    "waiting_periods"    : "waiting period 30 days 24 months 36 months PED specific disease maternity",
    "financial_limits"   : "room rent ICU sub-limit co-payment deductible proportionate ambulance",
    "gap_analysis"       : "IRDAI standard health coverage minimum norm mental illness OPD maternity",
    "fraud_risk"         : "fraud inflated bills fake diagnosis cashless denial insurer discretion",
    "policyholder_rights": "free look portability IRDAI grievance renewal loading cancellation",
}
