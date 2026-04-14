"""
reporter.py — Print formatted ClauseMind analysis report to terminal
"""
import re

SECTION_MAP = {
    "summary"            : ("📋", "POLICY SUMMARY"),
    "weasel_words"       : ("⚠️ ", "WEASEL WORDS"),
    "exclusions"         : ("🚫", "EXCLUSIONS & DENIALS"),
    "waiting_periods"    : ("⏳", "WAITING PERIODS"),
    "financial_limits"   : ("💰", "FINANCIAL LIMITS & SUB-LIMITS"),
    "gap_analysis"       : ("🔍", "COVERAGE GAP ANALYSIS"),
    "fraud_risk"         : ("🔒", "FRAUD RISK ASSESSMENT"),
    "policyholder_rights": ("⚖️ ", "POLICYHOLDER RIGHTS"),
}

WIDTH = 65


def print_header(meta: dict) -> None:
    print()
    print("=" * WIDTH)
    print("  ClauseMind — Health Insurance Policy Analysis")
    print(f"  {meta.get('policy_type', '')} | {meta.get('insurer', '')} | {meta.get('policy_name', '')}")
    print(f"  {meta.get('jurisdiction', '')} | Regulator: {meta.get('regulator', '')}")
    print("=" * WIDTH)


def print_section(task: str, answer: str) -> None:
    icon, title = SECTION_MAP.get(task, ("📄", task.upper()))
    print(f"\n{icon}  {title}")
    print("-" * (WIDTH - 2))
    print(answer)


def print_report(results: dict, meta: dict) -> None:
    print_header(meta)

    for task in SECTION_MAP:
        if task in results:
            print_section(task, results[task])

    print("\n" + "=" * WIDTH)
    print("  End of ClauseMind Report")
    print("=" * WIDTH + "\n")

    # ── Save to txt ──────────────────────────────────────────────
    import os, datetime

    insurer = re.sub(r"[^\w]", "_", meta.get("insurer", "policy"))
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    os.makedirs("reports", exist_ok=True)
    filename = f"reports/{insurer}_report_{timestamp}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        f.write("ClauseMind — Insurance Policy Analysis Report\n")
        f.write("=" * WIDTH + "\n")
        f.write(f"Policy   : {meta.get('policy_name', 'Unknown')}\n")
        f.write(f"Insurer  : {meta.get('insurer', 'Unknown')}\n")
        f.write(f"Type     : {meta.get('policy_type', 'Unknown')}\n")
        f.write(f"Regulator: {meta.get('regulator', 'Unknown')}\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * WIDTH + "\n\n")

        for task, (icon, title) in SECTION_MAP.items():
            if task in results:
                f.write(f"{icon}  {title}\n")
                f.write("-" * (WIDTH - 2) + "\n")
                f.write(results[task])
                f.write("\n\n")

        f.write("=" * WIDTH + "\n")
        f.write("End of ClauseMind Report\n")

    print(f"Report saved → {filename}")



def print_answer(question: str, answer: str) -> None:
    """Print a single Q&A pair."""
    print(f"\n❓ {question}")
    print(f"   {answer}")
