"""Optional Groq AI layer for AquaGuard risk interpretation and mitigation."""
from __future__ import annotations

import os
from typing import Optional


def _api_key() -> Optional[str]:
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY")
        if key:
            return str(key)
    except Exception:
        pass
    return os.getenv("GROQ_API_KEY")


def explain_risk(context: dict, model: Optional[str] = None) -> str:
    key = _api_key()
    if not key:
        return "AI is not configured. Add GROQ_API_KEY to Streamlit Secrets or the environment."

    try:
        from groq import Groq
        client = Groq(api_key=key)
        selected_model = model or os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
        prompt = (
            "You are the AquaGuard AI environmental risk analyst. "
            "Use only the supplied screening context. Explain the main drivers, "
            "uncertainties, and practical mitigation priorities. Do not present "
            "the screening score as a regulatory or official CHRI score.\n\n"
            f"Context:\n{context}"
        )
        response = client.chat.completions.create(
            model=selected_model,
            messages=[
                {"role": "system", "content": "You provide concise engineering decision support."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_completion_tokens=1200,
        )
        return response.choices[0].message.content or "No AI explanation returned."
    except Exception as exc:
        return f"AI request failed: {exc}"
