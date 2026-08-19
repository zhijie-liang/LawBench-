import os
from dotenv import load_dotenv
from fastapi import FastAPI, UploadFile, File, HTTPException
from pymilvus import MilvusClient
import pymysql
from pymysql.err import IntegrityError
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from workflow.rag_graph import run_rag_graph
from pydantic import BaseModel, Field


class ChatResponse(BaseModel):
    answer: str = ""
    contexts: list[str] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
    stage: str = ""
app = FastAPI(title="LawBench", version="2.0")

load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("请在 .env 中配置 DASHSCOPE_API_KEY")

# =========================================================
# 1. 注册
# =========================================================
@app.post("/register")
def register(username: str, password: str):
    """注册接口。

    参数:
        username: 用户名。
        password: 密码。
    """
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    cursor = db.cursor()
    try:
        cursor.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (username, password))
        db.commit()
        return {"username": username, "password": password}
    except IntegrityError:
        db.rollback()
        return "用户名已存在，注册失败！"
    finally:
        cursor.close()
        db.close()

# =========================================================
# 2. 登录
# =========================================================
@app.post("/login")
def login(username: str, password: str):
    """用户登录接口。

    参数:
        username: 用户名。
        password: 密码。
    """
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    cursor = db.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
        row = cursor.fetchone()
        if row is None:
            return {"message": "用户名错误"}
        if row[2] != password:
            return {"message": "密码错误"}
        return {"message": "登录成功"}
    finally:
        cursor.close()
        db.close()

# =========================================================
# 3. RAG 上传、加载文档、清洗、入mysql库、切块、向量化、入milvus库
# =========================================================
@app.post("/rag")
def rag(file: UploadFile = File(...)):
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
    db = pymysql.connect(host="localhost", user="lvjian",
                         password="123456", database="lvjian")
    cursor = db.cursor()
    cursor.execute(
        """ INSERT INTO documents(title, content, doc_type) VALUES(%s,%s,%s) """,
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
    embeddings = DashScopeEmbeddings(model="text-embedding-v3", dashscope_api_key=api_key)
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

# =========================================================
# 4. RAG llm检索
# =========================================================
@app.get("/chat")
def chat(question: str):
    # 1. 问题向量化
    embeddings = DashScopeEmbeddings(model="text-embedding-v3", dashscope_api_key=api_key)
    query_vector = embeddings.embed_query(question)
    # 2. Milvus检索
    client = MilvusClient(uri="http://localhost:19530")
    print("Milvus连接成功")
    results = client.search(
        collection_name="document_chunks_v1",
        data=[query_vector],
        anns_field="vector",
        limit=3,
        output_fields=["text", "document_id", "chunk_index"]
    )
    # 3. 拼接检索结果
    context = "\n\n".join(
        hit["entity"]["text"]
        for hit in results[0]
    )
    # 4. Prompt
    prompt = ChatPromptTemplate.from_template("""
    你是一个企业知识库问答助手。

    请严格根据下面资料回答。
    如果资料中没有答案，请回答“知识库中没有相关信息”。

    知识库资料：
    {context}

    用户问题：
    {question}

    回答：
    """)
    # 5. LLM
    llm = ChatTongyi(
        model="qwen3.7-max",
        temperature=0.1
    )
    chain = prompt | llm | StrOutputParser()

    return chain.invoke({
        "context": context,
        "question": question
    })

# =========================================================
# 5. LangGraph接入
# =========================================================
@app.get("/rag/chat", response_model=ChatResponse)
def langgraph(question: str):
    result = run_rag_graph(question)
    return result
    # return ChatResponse(
    #     answer=result.get("answer", ""),
    #     contexts=result.get("contexts", []),
    #     trace=result.get("trace", []),
    #     stage=result.get("stage", "")
    # )