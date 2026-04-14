"""
config.py — ClauseMind settings
Edit PDF_PATH and GEMINI_API_KEY, then run main.py
"""

import os
from dotenv import load_dotenv
load_dotenv()


# ── REQUIRED: set these two ─────────────────────────────────────────────────
PDF_PATH       = "policies\Policy_Super_Star_V_3_80e5dd8988.pdf"                          # path to any insurance PDF
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# ────────────────────────────────────────────────────────────────────────────

#LLM_MODEL   = "llama-3.3-70b-versatile"  # free, fast, large context
LLM_MODEL   = "llama-3.1-8b-instant"
#LLM_MODEL   = "gemma2-9b-it"
EMBED_MODEL = "all-MiniLM-L6-v2"         # local, unchanged
CHUNK_SIZE  = 300
OVERLAP     = 60
TOP_K       = 3
SECTOR = "Health Insurance"   # locked sector
IRDAI_PDF = "policies\Master Circular on Health Insurance Business.pdf.pdf"   # add this line
PDF_PATH  = "policies\Policy_Super_Star_V_3_80e5dd8988.pdf"
