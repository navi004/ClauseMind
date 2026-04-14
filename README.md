# ClauseMind — Universal Insurance Policy Analyser

RAG-based semantic engine. Drop in **any** insurance PDF (Health, Motor, Life, Travel, Home...) and get an instant deep analysis.

---

## Setup

```bash
pip install -r requirements.txt
```

Get a free Gemini key at https://aistudio.google.com/app/apikey  
Set it in `config.py` or as an env variable:
```bash
export GEMINI_API_KEY=your-key-here
```

Set your PDF path in `config.py`:
```python
PDF_PATH = "star_health_policy.pdf"
```

---

## Usage

```bash
# Full analysis — all 8 tasks
python main.py

# Single task only
python main.py --task exclusions
python main.py --task fraud_risk
python main.py --task summary

# Full analysis + interactive Q&A afterwards
python main.py --qa

# Skip analysis, just ask questions
python main.py --qa-only

# Compare two policies on a task
python main.py --compare second_policy.pdf --task exclusions
```

---

## Project Structure

```
clausemind/
├── main.py          ← entry point & CLI
├── config.py        ← PDF path, API key, all settings
├── loader.py        ← PDF text extraction
├── chunker.py       ← overlapping word-window chunker
├── vectorstore.py   ← sentence-transformer embeddings + FAISS
├── detector.py      ← auto-detect policy type / insurer / regulator
├── prompts.py       ← adaptive prompt templates (8 tasks)
├── engine.py        ← RAG engine: retrieve → augment → generate
├── analyser.py      ← runs all 8 tasks or a single task
├── reporter.py      ← formatted terminal report printer
├── qa.py            ← interactive Q&A + policy comparison
└── requirements.txt
```

---

## Analysis Dimensions

| Task | What it finds |
|---|---|
| `summary` | Plain-language overview, benefits, eligibility |
| `weasel_words` | Vague terms the insurer can use against you |
| `exclusions` | Everything that won't be paid out |
| `waiting_periods` | How long before you can actually claim |
| `financial_limits` | Sub-limits, co-pays, deductibles, room caps |
| `gap_analysis` | What's missing vs. regulatory standards |
| `fraud_risk` | Loopholes exploitable by either side |
| `policyholder_rights` | Cancellation, grievance, portability rights |

---

## Supported Policy Types

Health · Life · Term Life · ULIP · Motor · Home/Property · Travel · Commercial · Marine · Personal Accident

Works with any insurer (Indian or international) — prompts auto-adapt to detected type, jurisdiction, and regulator.
