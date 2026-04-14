"""
engine.py — ClauseMind RAG engine
Retrieve → Augment → Generate
"""

from vectorstore import VectorStore
from config import TOP_K


class ClauseMindEngine:
    """
    Core RAG engine.
    Given a task name, retrieves relevant chunks from FAISS,
    injects them into the prompt, and calls Gemini.
    """


    def __init__(self, store: VectorStore, prompts: dict, llm, policy_meta: dict, irdai_store=None):
        self.store       = store
        self.prompts     = prompts
        self.llm         = llm
        self.meta        = policy_meta
        self.irdai_store = irdai_store   # second index for IRDAI guidelines

    # ── Internal ──────────────────────────────────────────────────────────


    def _build_context(self, query: str, top_k: int = TOP_K) -> str:
        chunks = self.store.retrieve(query, top_k=top_k)
        parts  = []
        for i, c in enumerate(chunks, 1):
            page_info = f"Page {c['page']}" if c.get("page") else "Unknown page"
            parts.append(f"[Excerpt {i} | {page_info} | sim={c['score']:.3f}]")
            parts.append(c["text"])
            parts.append("")
        return "\n".join(parts)

    # ── Public ────────────────────────────────────────────────────────────


    def run_task(self, task: str, search_query: str = "") -> dict:
        """
        Run a single analysis task.

        Args:
            task:         key from prompts dict (e.g. 'exclusions')
            search_query: optional custom query for FAISS retrieval

        Returns:
            dict with task name and answer text
        """
        query   = search_query or task.replace("_", " ")
        context = self._build_context(query)

        # For gap_analysis, also retrieve from IRDAI index
        if task == "gap_analysis" and self.irdai_store:
            irdai_chunks = self.irdai_store.retrieve(query,top_k=3)
            irdai_context = "\n\n".join([
                f"[IRDAI Guideline {i+1}]\n{c['text']}"
                for i, c in enumerate(irdai_chunks)
            ])
            prompt = self.prompts[task].format(
                context=context,
                irdai_context=irdai_context
            )
        else:
            prompt = self.prompts[task].format(context=context)

        answer = self.llm.generate_content(prompt).text
        return {"task": task, "answer": answer}

    def ask(self, question: str) -> str:
        """
        Free-form Q&A against the loaded policy.

        Args:
            question: natural language question about the policy

        Returns:
            answer string from Gemini
        """
        context = self._build_context(question)
        ptype   = self.meta.get("policy_type", "insurance")

        prompt = f"""You are an expert on {ptype} insurance.
Answer the question using ONLY the policy excerpts below.
If the answer is not in the excerpts, say "Not found in the provided policy text."

Question: {question}

Policy excerpts:
{context}"""

        return self.llm.generate_content(prompt).text
