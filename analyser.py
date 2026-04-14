"""
analyser.py — Run all 8 ClauseMind analysis tasks
"""
import time
from engine import ClauseMindEngine
from prompts import TASK_QUERIES


def run_full_analysis(engine: ClauseMindEngine) -> dict:
    """
    Run all 8 analysis tasks sequentially.

    Returns:
        dict of {task_name: answer_string}
    """
    results = {}

    for task, query in TASK_QUERIES.items():
        print(f"[analyser] Running: {task} ...")
        result = engine.run_task(task, search_query=query)
        results[task] = result["answer"]
        print(f"[analyser] Done: {task}")

    print(f"[analyser] All {len(results)} tasks complete")
    return results


def run_single_task(engine: ClauseMindEngine, task: str) -> str:
    """
    Run one specific analysis task and return the answer.

    Args:
        engine: ClauseMindEngine instance
        task:   one of: summary | weasel_words | exclusions |
                        waiting_periods | financial_limits |
                        gap_analysis | fraud_risk | policyholder_rights

    Returns:
        answer string
    """
    query  = TASK_QUERIES.get(task, task.replace("_", " "))
    result = engine.run_task(task, search_query=query)
    time.sleep(2)  #2 seconds delay after each task to avoid rate limiting
    return result["answer"]
