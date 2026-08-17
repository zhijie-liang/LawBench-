import os
import re
import dashscope

from pipeline_store import load_stage
from milvus_service import get_collection

def clean_text(text):
    text = text.replace("\x00", "")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def split_text(text, size=50, overlap=5):
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end])
        start += size - overlap
    return chunks

def embed_chunks():
    rows = load_stage("chunked")
    dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")

    for row in rows:
        document_id = row[0]
        chunk_index = row[1]
        chunk_text = row[2]
        resp = dashscope.TextEmbedding.call(
            model="text-embedding-v3",
            input=chunk_text,
            dimension=512
        )
        vector = resp.output["embeddings"][0]["embedding"]
        collection = get_collection()
        collection.insert(
            [[document_id], [chunk_index], [chunk_text], [vector]]
        )
    collection.flush()
    return {"message": "向量化并入库成功"}
