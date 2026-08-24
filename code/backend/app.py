
from fastapi import FastAPI, UploadFile, File

from workflow.agent import agent_graph
from workflow.rag_chat import rag_chat
from workflow.rag_up_milvus import rag_up_milvus
from workflow.register import register_user
from workflow.login import login_user
from workflow.rag_graph_chat import run_rag_graph
from pydantic import BaseModel, Field

class ContextResponse(BaseModel):
    text: str
    document_id: int | None = None
    chunk_index: int | None = None

class ChatResponse(BaseModel):
    answer: str = ""
    contexts: list[ContextResponse] = Field(default_factory=list)
    trace: list[str] = Field(default_factory=list)
    stage: str = ""
    error: str = ""
app = FastAPI(title="LawBench", version="2.0")



# =========================================================
# 1. 注册
# =========================================================
@app.post("/register")
def register(username: str, password: str):
    return register_user(username, password)

# =========================================================
# 2. 登录
# =========================================================
@app.post("/login")
def login(username: str, password: str):
    return login_user(username, password)

# =========================================================
# 3. RAG 上传、加载文档、清洗、入mysql库、切块、向量化、入milvus库
# =========================================================
@app.post("/rag")
def rag(file: UploadFile = File(...)):
    return rag_up_milvus(file)

# =========================================================
# 4. RAG llm 检索
# =========================================================
@app.get("/chat")
def chat(question: str):
    return rag_chat(question)

# =========================================================
# 5. LangGraph 接入
# =========================================================
@app.get("/rag/chat", response_model=ChatResponse)
def langgraph(question: str):
    result = run_rag_graph(question)
    return result

# =========================================================
# 6. agent 接入
# =========================================================
@app.get("/agent")
def agent(question: str):
    result = agent_graph(question)
    return result









