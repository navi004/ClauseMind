"""
main.py — ClauseMind entry point

Usage:
    # Full analysis (all 8 tasks):
    python main.py

    # Single task only:
    python main.py --task exclusions

    # Interactive Q&A after analysis:
    python main.py --qa

    # Compare two policies on a task:
    python main.py --compare second_policy.pdf --task exclusions

    # Skip analysis, just Q&A:
    python main.py --qa-only
"""

import argparse
import sys
import os
import hashlib
from groq import Groq


import config
from loader      import load_pdf, load_pdf_by_page
from chunker     import chunk_document, chunk_by_page
from vectorstore import VectorStore
from detector    import detect_policy_type
from prompts     import build_prompts
from engine      import ClauseMindEngine
from analyser    import run_full_analysis, run_single_task
from reporter    import print_report, print_section
from qa          import interactive_qa, compare_policies


# ── CLI args ──────────────────────────────────────────────────────────────

def parse_args():
    p = argparse.ArgumentParser(description="ClauseMind — Universal Insurance Policy Analyser")
    p.add_argument("--task",    type=str, default=None,
                   help="Run a single task (e.g. exclusions, fraud_risk, summary)")
    p.add_argument("--qa",      action="store_true",
                   help="Start interactive Q&A after analysis")
    p.add_argument("--qa-only", action="store_true",
                   help="Skip analysis, go straight to Q&A")
    p.add_argument("--compare", type=str, default=None, metavar="PDF2",
                   help="Path to a second PDF to compare against")
    p.add_argument("--pdf",     type=str, default=config.PDF_PATH,
                   help=f"Path to PDF (default: {config.PDF_PATH})")
    return p.parse_args()


# ── Bootstrap: load + index a PDF ────────────────────────────────────────
os.makedirs("cache", exist_ok=True)

def bootstrap(pdf_path: str, llm):
    text  = load_pdf(pdf_path)
    pages = load_pdf_by_page(pdf_path)
    chunks = chunk_by_page(pages)  

    pdf_hash   = hashlib.md5(open(pdf_path, "rb").read()).hexdigest()[:8]
    cache_path       = f"cache/policy_{pdf_hash}"

    store = VectorStore()
    if not store.load(cache_path):
        store.build(chunks)
        store.save(cache_path)


    # ── Load IRDAI guidelines into a second index ──────────────
    irdai_store = None
    if os.path.exists(config.IRDAI_PDF):
        print("[main] Loading IRDAI guidelines ...")
        irdai_text   = load_pdf(config.IRDAI_PDF)
        irdai_pages  = load_pdf_by_page(config.IRDAI_PDF)
        irdai_chunks = chunk_by_page(irdai_pages)

        irdai_hash       = hashlib.md5(open(config.IRDAI_PDF, "rb").read()).hexdigest()[:8]
        irdai_cache_path = f"cache/irdai_{irdai_hash}"

        irdai_store = VectorStore()
        if not irdai_store.load(irdai_cache_path):
            irdai_store.build(irdai_chunks)
            irdai_store.save(irdai_cache_path)
        print("[main] IRDAI index ready")
    else:
        print(f"[main] WARNING: {config.IRDAI_PDF} not found — gap analysis will use Groq's built-in knowledge")
    # ───────────────────────────────────────────────────────────

    meta    = detect_policy_type(text, llm)
    prompts = build_prompts(meta)
    engine  = ClauseMindEngine(store, prompts, llm, meta, irdai_store)
    return engine, meta

# ── Main ──────────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # Validate key
    if config.GROQ_API_KEY in ("your-groq-key-here", ""):
        print("[error] Set GROQ_API_KEY in config.py or as an environment variable.")
        print("        Get a free key at: https://aistudio.google.com/app/apikey")
        sys.exit(1)

    class LLMWrapper:
        def __init__(self, api_key, model):
            self._client = Groq(api_key=api_key)
            self._model  = model
        def generate_content(self, prompt):
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
            )
            class _R:
                text = response.choices[0].message.content
            return _R()

    llm = LLMWrapper(config.GROQ_API_KEY, config.LLM_MODEL)
    print(f"[main] LLM: {config.LLM_MODEL}")



    # Load primary policy
    engine, meta = bootstrap(args.pdf, llm)

    # ── Mode: compare two policies ────────────────────────────────────
    if args.compare:
        task = args.task or "exclusions"
        print(f"\n[main] Comparison mode: {args.pdf}  vs  {args.compare}  on task: {task}")
        engine2, meta2 = bootstrap(args.compare, llm)
        compare_policies(engine, engine2, task, llm, meta, meta2)
        return

    # ── Mode: Q&A only ────────────────────────────────────────────────
    if args.qa_only:
        interactive_qa(engine)
        return

    # ── Mode: single task ─────────────────────────────────────────────
    if args.task:
        print(f"\n[main] Running single task: {args.task}")
        answer = run_single_task(engine, args.task)
        print_section(args.task, answer)
        if args.qa:
            interactive_qa(engine)
        return

    # ── Mode: full analysis (default) ─────────────────────────────────
    results = run_full_analysis(engine)
    print_report(results, meta)

    if args.qa:
        interactive_qa(engine)


if __name__ == "__main__":
    main()
