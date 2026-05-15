from pathlib import Path

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from config import settings
from document_processor import extract_text
from rag_pipeline import (
    get_text_splitter,
    build_vector_store,
    load_vector_store,
    build_rag_chain,
)

UPLOAD_DIR = Path("./data/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

_chain = None


app = FastAPI(title="Resume Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str


@app.post("/upload")
async def upload_resume(file: UploadFile):
    if not file.filename:
        raise HTTPException(400, "No file provided")

    ext = Path(file.filename).suffix.lower()
    if ext not in (".pdf", ".docx", ".txt"):
        raise HTTPException(400, f"Unsupported format: {ext}")

    file_path = UPLOAD_DIR / file.filename
    content = await file.read()
    file_path.write_bytes(content)

    text = extract_text(file_path)
    splitter = get_text_splitter()
    chunks = splitter.split_text(text)

    metadatas = [{"source": file.filename, "chunk": i} for i in range(len(chunks))]

    global _chain
    try:
        vs = load_vector_store()
        vs.add_texts(texts=chunks, metadatas=metadatas)
    except Exception:
        vs = build_vector_store(chunks, metadatas=metadatas)

    _chain = build_rag_chain(vs)

    return {
        "filename": file.filename,
        "chunks": len(chunks),
        "message": "Resume processed and indexed",
    }


@app.post("/query")
async def query(req: QueryRequest):
    if _chain is None:
        raise HTTPException(400, "No resumes loaded yet. Upload a resume first.")

    result = _chain.invoke({"input": req.question})
    return {
        "answer": result["answer"],
        "sources": list({
            doc.metadata.get("source", "unknown")
            for doc in result.get("context", [])
        }),
    }
