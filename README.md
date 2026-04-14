# 🧠 ClauseMind — Health Insurance Policy Analyser

> A RAG-based semantic engine that analyses any health insurance PDF and identifies hidden risks, unfair clauses, exclusions, and coverage gaps — grounded in actual IRDAI guidelines.

---

## 📌 What it does

ClauseMind takes a health insurance PDF, breaks it into chunks, converts them into vector embeddings using a local sentence-transformer model, stores them in a FAISS index, and runs 8 deep analyses by retrieving the most relevant chunks and sending them to an LLM. Every finding is cited with the exact page number from the original policy document.

```
Insurance PDF
      ↓
 PDF Extractor       → PyPDF2
      ↓
 Page-Aware Chunker  → overlapping word windows with page tracking
      ↓
 Embeddings          → all-MiniLM-L6-v2 (local, free)
      ↓
 FAISS Vector Index  → cached to disk after first run
      ↓
 Semantic Retrieval  → top-k most relevant chunks per task
      ↓
 Groq LLM            → llama-3.1-8b-instant
      ↓
 8 Analysis Tasks    → cited with page numbers
      ↓
 Terminal Report + reports/filename.txt
```

---

## 📊 8 Analysis Dimensions

| Task | What it finds |
|---|---|
| 📋 Summary | Plain-language overview, benefits, eligibility |
| ⚠️ Weasel Words | Vague terms the insurer can exploit |
| 🚫 Exclusions | Every denial clause with real-world impact |
| ⏳ Waiting Periods | Initial, PED, disease-specific, maternity |
| 💰 Financial Limits | Sub-limits, co-pay, room rent caps, deductibles |
| 🔍 Gap Analysis | Compared against actual IRDAI guidelines PDF |
| 🔒 Fraud Risk | Loopholes exploitable by policyholder or insurer |
| ⚖️ Policyholder Rights | Free-look, grievance, portability, cancellation |

---

## 🗂️ Project Structure

```
clausemind/
│
├── main.py               ← entry point, run this
├── config.py             ← model settings, PDF paths
├── loader.py             ← PDF text extraction (page by page)
├── chunker.py            ← overlapping page-aware chunker
├── vectorstore.py        ← embeddings + FAISS (save/load cache)
├── detector.py           ← auto-detects policy type via LLM
├── prompts.py            ← 8 health-specific prompt templates
├── engine.py             ← RAG core: retrieve → augment → generate
├── analyser.py           ← runs all 8 tasks or a single task
├── reporter.py           ← prints + saves report to .txt
├── qa.py                 ← interactive Q&A + policy comparison
├── requirements.txt
├── README.md
├── .env                  ← API key (never pushed to GitHub)
├── .gitignore
│
├── policies/             ← put your PDFs here (not pushed)
│   ├── your_policy.pdf
│   └── irdai_guidelines.pdf
│
├── cache/                ← auto-created, FAISS indexes (not pushed)
│   ├── policy_xxxx.index
│   ├── policy_xxxx.chunks
│   ├── irdai_xxxx.index
│   └── irdai_xxxx.chunks
│
└── reports/              ← auto-created, saved reports (not pushed)
    └── Star_Health_report_20250411_143022.txt
```

---

## ⚙️ Setup

### 1. Clone the repo
```bash
git clone https://github.com/navi004/clausemind.git
cd clausemind
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file
```
GROQ_API_KEY=your-groq-key-here
```
Get a free key at: https://console.groq.com

### 4. Add your PDFs
Create a `policies/` folder and add:
- Your health insurance PDF
- IRDAI Master Circular on Health Insurance 2024 (download from irdai.gov.in)

### 5. Update `config.py`
```python
PDF_PATH  = "policies/your_policy.pdf"
IRDAI_PDF = "policies/irdai_guidelines.pdf"
```

---

## ▶️ Usage

```bash
# Full analysis — all 8 tasks
python main.py

# Single task only
python main.py --task summary
python main.py --task exclusions
python main.py --task fraud_risk
python main.py --task weasel_words
python main.py --task waiting_periods
python main.py --task financial_limits
python main.py --task gap_analysis
python main.py --task policyholder_rights

# Full report + interactive Q&A after
python main.py --qa

# Skip analysis, just ask questions
python main.py --qa-only

# Different PDF without changing config.py
python main.py --pdf policies/another_policy.pdf

# Compare two policies on a task
python main.py --compare policies/second_policy.pdf --task exclusions
```

---

## ⚡ Caching

On the first run, embeddings are computed and saved to the `cache/` folder. Every subsequent run loads from cache — skipping the ~15 second embedding step.

Cache is keyed by MD5 hash of the PDF — if you change the PDF, it automatically rebuilds.

---

## 🛠️ Tech Stack

| Component | Tool |
|---|---|
| LLM | Llama 3.1 8B via Groq (free API) |
| Embeddings | all-MiniLM-L6-v2 via sentence-transformers (local) |
| Vector Search | FAISS (local) |
| PDF Parsing | PyPDF2 |
| IRDAI Comparison | Second FAISS index built from IRDAI guidelines PDF |

---

## 📋 Requirements

```
groq
python-dotenv
sentence-transformers
faiss-cpu
PyPDF2
numpy
```

---

## 🎓 Academic Context

Built as a J-Component project for the Risk and Fraud Analysis course at VIT University. Demonstrates applied RAG architecture for document intelligence in the insurance domain, with a focus on consumer protection and fraud risk identification under IRDAI regulations.

---
