"""
Document Loader for HR Policy Files
------------------------------------
Supports multi-format ingestion: Markdown (.md), Plain Text (.txt),
PDF (.pdf via pypdf), and Microsoft Word (.docx via python-docx).
Extracts document structural metadata, section titles, and page boundaries.
"""

import os
from typing import Dict, Any, List, Optional
import re

class DocumentLoader:
    """
    Loads HR policy documents from the local filesystem or memory,
    normalizing text content and parsing document metadata.
    """

    SUPPORTED_EXTENSIONS = {".md", ".txt", ".pdf", ".docx"}

    @classmethod
    def load_file(cls, file_path: str) -> Dict[str, Any]:
        """
        Loads a single document file, returning structured content and metadata.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document file not found: {file_path}")

        file_name = os.path.basename(file_path)
        ext = os.path.splitext(file_name)[1].lower()

        if ext not in cls.SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported file format '{ext}'. Supported formats: {cls.SUPPORTED_EXTENSIONS}")

        if ext in {".md", ".txt"}:
            return cls._load_text_file(file_path, file_name, ext)
        elif ext == ".pdf":
            return cls._load_pdf_file(file_path, file_name)
        elif ext == ".docx":
            return cls._load_docx_file(file_path, file_name)
        else:
            raise ValueError(f"No parser available for {ext}")

    @classmethod
    def _load_text_file(cls, file_path: str, file_name: str, ext: str) -> Dict[str, Any]:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            raw_text = f.read()

        title = file_name.replace(ext, "").replace("_", " ").title()
        doc_id_match = re.search(r"\*\*Document ID\*\*:\s*([A-Za-z0-9\-]+)", raw_text)
        doc_id = doc_id_match.group(1) if doc_id_match else f"DOC-{file_name.upper().replace(ext.upper(), '')}"

        category_match = re.search(r"\*\*Category\*\*:\s*([A-Za-z0-9\s\&]+)", raw_text)
        category = category_match.group(1).strip() if category_match else "HR Policy"

        # Check for main title header (# Title)
        first_h1 = re.search(r"^#\s+(.+)$", raw_text, re.MULTILINE)
        if first_h1:
            title = first_h1.group(1).strip()

        # Split into pages/sections conceptually (every ~1500 chars represents a page for text/md)
        pages = []
        paragraphs = raw_text.split("\n\n")
        current_page = 1
        current_char_count = 0
        current_page_text: List[str] = []

        for para in paragraphs:
            para_len = len(para)
            if current_char_count + para_len > 1600 and current_page_text:
                pages.append({
                    "page_number": current_page,
                    "text": "\n\n".join(current_page_text)
                })
                current_page += 1
                current_page_text = [para]
                current_char_count = para_len
            else:
                current_page_text.append(para)
                current_char_count += para_len

        if current_page_text:
            pages.append({
                "page_number": current_page,
                "text": "\n\n".join(current_page_text)
            })

        return {
            "document_id": doc_id,
            "document_name": file_name,
            "title": title,
            "category": category,
            "file_type": ext.replace(".", "").upper(),
            "raw_text": raw_text,
            "pages": pages,
            "total_pages": len(pages),
            "file_path": file_path
        }

    @classmethod
    def _load_pdf_file(cls, file_path: str, file_name: str) -> Dict[str, Any]:
        try:
            from pypdf import PdfReader
        except ImportError:
            raise ImportError("pypdf is required to load PDF documents. Install via pip install pypdf.")

        reader = PdfReader(file_path)
        pages = []
        full_text_list = []

        for idx, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            pages.append({
                "page_number": idx + 1,
                "text": text
            })
            full_text_list.append(text)

        raw_text = "\n\n".join(full_text_list)
        title = file_name.replace(".pdf", "").replace("_", " ").title()

        return {
            "document_id": f"DOC-{file_name.upper().replace('.PDF', '')}",
            "document_name": file_name,
            "title": title,
            "category": "HR Policy",
            "file_type": "PDF",
            "raw_text": raw_text,
            "pages": pages,
            "total_pages": len(pages),
            "file_path": file_path
        }

    @classmethod
    def _load_docx_file(cls, file_path: str, file_name: str) -> Dict[str, Any]:
        try:
            import docx
        except ImportError:
            raise ImportError("python-docx is required to load Word documents. Install via pip install python-docx.")

        doc = docx.Document(file_path)
        full_text_list = [p.text for p in doc.paragraphs if p.text.strip()]
        raw_text = "\n\n".join(full_text_list)
        title = file_name.replace(".docx", "").replace("_", " ").title()

        return {
            "document_id": f"DOC-{file_name.upper().replace('.DOCX', '')}",
            "document_name": file_name,
            "title": title,
            "category": "HR Policy",
            "file_type": "DOCX",
            "raw_text": raw_text,
            "pages": [{"page_number": 1, "text": raw_text}],
            "total_pages": 1,
            "file_path": file_path
        }

    @classmethod
    def load_directory(cls, dir_path: str) -> List[Dict[str, Any]]:
        """
        Recursively loads all supported documents from a directory.
        """
        documents = []
        if not os.path.exists(dir_path):
            return documents

        for root, _, files in os.walk(dir_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in cls.SUPPORTED_EXTENSIONS:
                    full_path = os.path.join(root, file)
                    try:
                        doc = cls.load_file(full_path)
                        documents.append(doc)
                    except Exception as e:
                        print(f"[DocumentLoader WARN] Failed to load {full_path}: {e}")
        return documents
