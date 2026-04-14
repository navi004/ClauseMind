"""
qa.py — Free-form Q&A and two-policy comparison utilities
"""

from engine import ClauseMindEngine
from reporter import print_answer


def interactive_qa(engine: ClauseMindEngine) -> None:
    """
    Start an interactive Q&A session in the terminal.
    Type 'exit' or 'quit' to stop.
    """
    print("\n── ClauseMind Q&A Mode ──────────────────────────────────────")
    print("Ask any question about the loaded policy. Type 'exit' to stop.\n")

    while True:
        try:
            question = input("❓ Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if question.lower() in ("exit", "quit", "q", ""):
            print("Exiting Q&A mode.")
            break

        answer = engine.ask(question)
        print_answer(question, answer)
        print()


def batch_qa(engine: ClauseMindEngine, questions: list[str]) -> dict:
    """
    Run a list of questions and return {question: answer} dict.

    Args:
        engine:    ClauseMindEngine instance
        questions: list of question strings

    Returns:
        dict of {question: answer}
    """
    results = {}
    for q in questions:
        print(f"[qa] Asking: {q[:60]}...")
        results[q] = engine.ask(q)
    return results


def compare_policies(
    engine1: ClauseMindEngine,
    engine2: ClauseMindEngine,
    task: str,
    llm,
    meta1: dict,
    meta2: dict,
) -> str:
    """
    Compare two policies on a specific analysis task.

    Args:
        engine1/2: ClauseMindEngine instances for each policy
        task:      analysis dimension to compare (e.g. 'exclusions')
        llm:       Gemini model instance
        meta1/2:   policy metadata dicts

    Returns:
        Verdict string from Gemini
    """
    from prompts import TASK_QUERIES

    query = TASK_QUERIES.get(task, task.replace("_", " "))

    print(f"[compare] Analysing policy 1: {meta1.get('policy_name', 'Policy 1')} ...")
    r1 = engine1.run_task(task, search_query=query)

    print(f"[compare] Analysing policy 2: {meta2.get('policy_name', 'Policy 2')} ...")
    r2 = engine2.run_task(task, search_query=query)

    verdict_prompt = f"""
Compare these two {task} analyses from two insurance policies.

Policy 1: {meta1.get('policy_name')} by {meta1.get('insurer')}
Policy 2: {meta2.get('policy_name')} by {meta2.get('insurer')}

Policy 1 Analysis:
{r1['answer']}

Policy 2 Analysis:
{r2['answer']}

Give a concise verdict:
- Which policy is more policyholder-friendly on {task}?
- Top 3 key differences
- Overall recommendation
"""

    verdict = llm.generate_content(verdict_prompt).text

    print(f"\n── {meta1.get('policy_name')} ──────────────────────────────")
    print(r1["answer"])
    print(f"\n── {meta2.get('policy_name')} ──────────────────────────────")
    print(r2["answer"])
    print("\n── VERDICT ──────────────────────────────────────────────────")
    print(verdict)

    return verdict
