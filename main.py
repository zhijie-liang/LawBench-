import uvicorn
from fastapi import FastAPI, UploadFile, File, HTTPException

from user_service import register_user, login_user
from document_service import document_save, search_documents, upload_documents, extract_text
from text_processor import clean_text, split_text

app = FastAPI(
    title="LawBench",
    version="1.0",
)

@app.post("/register")
def register(username: str, password: str):
    result = register_user(username, password)
    # return result
    if result:
        return {"message": "注册成功"}
    return {"message": "用户名已存在"}

@app.post("/login")
def login(username: str, password: str):
    return login_user(username, password)

@app.post("/documents")
def save_document(title: str, content: str, doc_type: str = ""):
    document_save(title, content, doc_type)
    return {"message": "文档保存成功"}

@app.get("/documents/search")
def search(keyword: str):
    return search_documents(keyword)

@app.post("/upload")
def upload(file: UploadFile = File(...)):
    if file.content_type != "text/plain":
        raise HTTPException(400, "只支持TXT文件")
    content = extract_text(file.file.read(), file.content_type)
    upload_documents(file.filename, content, file.content_type)
    return {"filename": file.filename}

from document_service import load_documents
from pipeline_store import save_stage, load_stage
@app.get("/pipeline/load")
def pipeline_load():
    documents = load_documents()
    save_stage("loaded", documents)
    return {"count": len(documents), "documents": documents}

@app.post("/pipeline/clean")
def pipeline_clean():
    rows = load_stage("loaded")
    cleaned_rows = []

    for row in rows:
        cleaned_row = row.copy()
        cleaned_row[2] = clean_text(row[2] or "")
        cleaned_rows.append(cleaned_row)

    save_stage("cleaned", cleaned_rows)

    return {
        "count": len(cleaned_rows),
        "documents": cleaned_rows
    }




@app.post("/pipeline/chunk")
def pipeline_chunk():
    rows = load_stage("cleaned")
    all_chunks = []
    for row in rows:
        document_id = row[0]
        for chunk_index, text in enumerate(split_text(row[2])):
            data = [document_id, chunk_index, text]
            all_chunks.append(data)
    save_stage("chunk", all_chunks)
    return {"count": len(all_chunks), "documents": all_chunks}


@app.post("/pipeline/embed")
def pipeline_embed():
    pass

@app.post("/pipeline/index")
def pipeline_index():
    pass

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1",
#                 port=8000, reload=True)