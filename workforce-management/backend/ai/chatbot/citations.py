"""
Citation and Source Attribution Engine
---------------------------------------
Formats structured source citations and references for UI display
and conversational response footnotes.
"""

from typing import List, Dict, Any
from backend.ai.chatbot.schemas import CitationSource

class CitationEngine:
    """
    Standardizes and deduplicates citation references across document and database sources.
    """

    @classmethod
    def format_citations_markdown(cls, sources: List[CitationSource]) -> str:
        """
        Generates a human-readable markdown citations footer.
        """
        if not sources:
            return ""

        lines = ["\n\n**Sources & References**:"]
        seen = set()

        for idx, s in enumerate(sources, 1):
            key = f"{s.source_type}_{s.title}_{s.section}_{s.page}"
            if key in seen:
                continue
            seen.add(key)

            if s.source_type == "policy_document":
                doc_name = s.document_name or s.title
                sec = f" — {s.section}" if s.section else ""
                pg = f" — Page {s.page}" if s.page else ""
                lines.append(f"{idx}. 📄 **{doc_name}**{sec}{pg}")
            elif s.source_type == "database_record":
                lines.append(f"{idx}. 🗄️ **{s.title}** ({s.section or 'Live HR Record'})")
            elif s.source_type == "ai_prediction":
                lines.append(f"{idx}. 🧠 **{s.title}** ({s.section or 'Model Prediction'})")

        return "\n".join(lines)

    @classmethod
    def deduplicate_citations(cls, sources: List[CitationSource]) -> List[CitationSource]:
        """
        Deduplicates list of citation objects.
        """
        seen = set()
        deduped = []
        for s in sources:
            key = (s.source_type, s.title, s.section, s.page)
            if key not in seen:
                seen.add(key)
                deduped.append(s)
        return deduped
