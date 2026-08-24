from fastapi import UploadFile, File, HTTPException
from pymilvus import MilvusClient
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from services.mysql_connect import mysql_connect
from workflow.embedding import embedding_dashscope


def rag_up_milvus(file: UploadFile = File(...)):
    """RAG 入库接口：上传 TXT 文件，清洗、切块、向量化后写入 MySQL 与 Milvus。

        参数:
            file: 上传的 TXT 文件对象。
        """
    if file.content_type != "text/plain":
        raise HTTPException(400, "只支持TXT文件")
    # 1. 加载文本
    content = file.file.read().decode("utf-8")
    print("已加载文档")
    # 2. 清洗
    content = content.strip()  # 去首尾空格
    content = content.replace("\n\n", "\n")  # 简单去空行
    print("已清洗，去首尾空格，简单去空行")
    # 3. 存 MySQL
    db = mysql_connect()
    cursor = db.cursor()
    cursor.execute(
        """ INSERT INTO documents(title, content, doc_type)
            VALUES (%s, %s, %s) """,
        (file.filename, content, file.content_type)
    )
    db.commit()
    print("存MySQL")
    document_id = cursor.lastrowid
    # 4. 转 Document 对象
    document = Document(
        page_content=content,
        metadata={"title": file.filename, "type": file.content_type}
    )
    print("转Document对象")
    # 5. 文本切块
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents([document])
    print("文本切块")
    cursor.close()
    db.close()
    print("关闭mysql实例")
    # 6. Embedding 向量化
    embeddings = embedding_dashscope()
    texts = [
        chunk.page_content
        for chunk in chunks
    ]
    vectors = embeddings.embed_documents(texts)
    print("Embedding向量化")
    # 7. 写入 Milvus
    data = []
    for i, chunk in enumerate(chunks):
        data.append({
            "document_id": document_id,
            "chunk_index": i,
            "text": chunk.page_content,
            "vector": vectors[i]
        })
    client = MilvusClient(uri="http://localhost:19530")
    print("Milvus连接成功")
    client.insert(
        collection_name="document_chunks_v1",
        data=data
    )
    print(f"Milvus入库完成，共{len(data)}条")
    return f"Milvus入库完成，共{len(data)}条"