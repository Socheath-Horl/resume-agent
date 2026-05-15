from pathlib import Path

from pypdf import PdfReader
from docx import Document


def extract_text(file_path: str | Path) -> str:
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _extract_pdf(path)
    elif suffix == ".docx":
        return _extract_docx(path)
    elif suffix == ".txt":
        return _extract_txt(path)
    else:
        raise ValueError(f"Unsupported file format: {suffix}")


def _extract_pdf(path: Path) -> str:
    reader = PdfReader(path)
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _extract_docx(path: Path) -> str:
    doc = Document(path)
    return "\n".join(p.text for p in doc.paragraphs)


def _extract_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")
