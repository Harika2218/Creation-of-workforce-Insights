"""
Structural Text Chunker for RAG Documents
------------------------------------------
Splits policy documents into semantically coherent chunks by section headings,
preserving paragraph context, section hierarchy, page numbers, and overlap.
"""

from typing import List, Dict, Any
import re

class TextChunker:
    """
    Chunks document content into manageable pieces with full metadata preservation.
    """

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 80):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(self, doc: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Processes a single document and returns a list of chunk dictionaries.
        """
        chunks = []
        doc_id = doc.get("document_id", "DOC-UNKNOWN")
        doc_name = doc.get("document_name", "Unknown Document")
        doc_title = doc.get("title", doc_name)
        category = doc.get("category", "HR Policy")
        pages = doc.get("pages", [])

        chunk_counter = 1

        for page in pages:
            page_num = page.get("page_number", 1)
            page_text = page.get("text", "")
            if not page_text.strip():
                continue

            # Split text by sections (Markdown headers ## or ###)
            section_blocks = self._split_by_sections(page_text)

            for sec_title, sec_text in section_blocks:
                # If section is small enough, make it a single chunk
                if len(sec_text) <= self.chunk_size:
                    if sec_text.strip():
                        chunks.append({
                            "chunk_id": f"{doc_id}_P{page_num}_C{chunk_counter}",
                            "document_id": doc_id,
                            "document_name": doc_name,
                            "title": doc_title,
                            "section": sec_title,
                            "page": page_num,
                            "category": category,
                            "text": sec_text.strip(),
                            "character_count": len(sec_text.strip())
                        })
                        chunk_counter += 1
                else:
                    # Split longer section with sliding window overlap
                    sub_chunks = self._sliding_window_chunks(sec_text)
                    for sub in sub_chunks:
                        if sub.strip():
                            chunks.append({
                                "chunk_id": f"{doc_id}_P{page_num}_C{chunk_counter}",
                                "document_id": doc_id,
                                "document_name": doc_name,
                                "title": doc_title,
                                "section": sec_title,
                                "page": page_num,
                                "category": category,
                                "text": sub.strip(),
                                "character_count": len(sub.strip())
                            })
                            chunk_counter += 1

        return chunks

    def _split_by_sections(self, text: str) -> List[tuple]:
        """
        Splits text by markdown headings, yielding (section_title, section_text).
        """
        lines = text.split("\n")
        sections = []
        current_section = "Overview"
        current_lines: List[str] = []

        heading_regex = re.compile(r"^(#{1,4})\s+(.+)$")

        for line in lines:
            match = heading_regex.match(line)
            if match:
                # New section detected
                if current_lines:
                    sections.append((current_section, "\n".join(current_lines)))
                    current_lines = []
                current_section = match.group(2).strip()
                current_lines.append(line)
            else:
                current_lines.append(line)

        if current_lines:
            sections.append((current_section, "\n".join(current_lines)))

        return sections

    def _sliding_window_chunks(self, text: str) -> List[str]:
        """
        Splits text into chunks of roughly chunk_size with overlap on word/sentence boundaries.
        """
        paragraphs = text.split("\n\n")
        sub_chunks = []
        current_chunk: List[str] = []
        current_length = 0

        for p in paragraphs:
            p_len = len(p)
            if current_length + p_len > self.chunk_size and current_chunk:
                combined = "\n\n".join(current_chunk)
                sub_chunks.append(combined)

                # Overlap: keep the last paragraph if small, or part of it
                if p_len < self.chunk_size:
                    current_chunk = [p]
                    current_length = p_len
                else:
                    # Paragraph itself exceeds chunk_size, split by sentences
                    sentences = re.split(r"(?<=[.!?])\s+", p)
                    sent_chunk: List[str] = []
                    sent_len = 0
                    for s in sentences:
                        if sent_len + len(s) > self.chunk_size and sent_chunk:
                            sub_chunks.append(" ".join(sent_chunk))
                            sent_chunk = [s]
                            sent_len = len(s)
                        else:
                            sent_chunk.append(s)
                            sent_len += len(s)
                    if sent_chunk:
                        current_chunk = [" ".join(sent_chunk)]
                        current_length = sent_len
                    else:
                        current_chunk = []
                        current_length = 0
            else:
                current_chunk.append(p)
                current_length += p_len

        if current_chunk:
            sub_chunks.append("\n\n".join(current_chunk))

        return sub_chunks
