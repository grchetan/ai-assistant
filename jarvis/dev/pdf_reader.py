"""
================================================================================
                    JARVIS PDF INTELLIGENCE & READER
================================================================================
Extracts text from PDF documents using PyMuPDF (fitz) for reading aloud
and conversational summarization.
================================================================================
"""

from typing import Optional, List
from pathlib import Path

try:
    import fitz  # PyMuPDF
    _PYMUPDF_AVAILABLE = True
except ImportError:
    _PYMUPDF_AVAILABLE = False

from jarvis.core.logger import get_logger


class PDFReader:
    """PDF text extractor and audiobook assistant."""

    def __init__(self) -> None:
        self.logger = get_logger()

    def extract_text(self, pdf_path: str, max_pages: int = 5) -> Optional[str]:
        """Extract text from the first N pages of a PDF."""
        if not _PYMUPDF_AVAILABLE:
            self.logger.warning("PyMuPDF not installed.", "PDF")
            return None

        p = Path(pdf_path)
        if not p.exists():
            return None

        try:
            doc = fitz.open(str(p))
            extracted_pages = []
            for i in range(min(len(doc), max_pages)):
                page = doc.load_page(i)
                text = page.get_text()
                if text.strip():
                    extracted_pages.append(text.strip())
            doc.close()
            return "\n\n".join(extracted_pages)
        except Exception as e:
            self.logger.error(f"Error reading PDF: {e}", "PDF")
            return None


def get_pdf_reader() -> PDFReader:
    return PDFReader()
