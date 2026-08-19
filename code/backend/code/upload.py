# ===================== 导入依赖 =====================

# TypedDict：用于定义带类型提示的字典结构（这里是定义 LangGraph 的 State 状态）
from typing import TypedDict

# MilvusClient：向量数据库 Milvus 的客户端，用来存储和检索向量
from pymilvus import MilvusClient

# ChatPromptTemplate：用于构建提示词（Prompt）模板，支持 {变量} 占位符
from langchain_core.prompts import ChatPromptTemplate

# StrOutputParser：把大模型输出的消息对象解析成纯字符串
from langchain_core.output_parsers import StrOutputParser

# DashScopeEmbeddings：阿里云百炼（DashScope）平台的文本向量化模型封装
from langchain_community.embeddings.dashscope import DashScopeEmbeddings

# ChatTongyi：阿里云通义千问大模型的封装
from langchain_community.chat_models import ChatTongyi

# LangGraph 核心：StateGraph（状态图，用于编排多个步骤），START / END（图的起点和终点）
from langgraph.graph import StateGraph, START, END


# ===================== 定义状态结构 =====================

# 定义整个流程中流转的"状态"（State）。
# 它是一个字典，字段类型被 TypedDict 限定。
# total=False 表示这些字段都是"可选"的，不一定每个节点都填写完整。
class State(TypedDict, total=False):
    question: str           # 用户提出的问题
    contexts: list[str]      # 从知识库检索到的相关文本片段
    answer: str              # 最终生成的答案


# ===================== 节点1：检索 retrieve =====================

# LangGraph 中每个节点就是一个函数：接收 State，返回要写回 State 的字段（部分更新）。
def retrieve_node(state: State) -> dict:
    # 从状态里取出用户的问题
    question = state["question"]

    # --- 1. 把问题转换为向量 ---
    # embedding 模型的作用：把一段文字变成一串数字（向量）。
    # 语义相近的文字，向量在空间中的位置也相近，这样就能做"语义检索"（按意思找，而不是按关键词找）。
    embeddings = DashScopeEmbeddings(
        model="text-embedding-v3"   # 指定阿里云的向量化模型
    )
    query_vector = embeddings.embed_query(question)  # 调用 embed_query 把问题文本转成向量
    print(f"问题向量化已完成，长度为：{len(query_vector)}")  # 打印向量维度（长度），方便调试

    # --- 2. 到 Milvus 向量数据库里搜索最相似的文本 ---
    client = MilvusClient(uri="http://localhost:19530")  # 连接本地运行的 Milvus 服务
    results = client.search(
        collection_name="document_chunks_v1",   # 要检索的集合（collection，类似数据库里的"表"）
        data=[query_vector],                    # 要搜索的向量（问题向量）
        anns_field="vector",                    # 集合中存放向量的字段名
        limit=3,                                # 只返回最相似的 3 条（top-3）
        output_fields=["text", "document_id", "chunk_index"]  # 命中后需要返回给我们的字段
    )

    # --- 3. 从检索结果里提取出文本内容 ---
    # results[0]：第一条查询向量对应的命中列表（我们只传了一个向量，所以取 [0]）。
    # 每条 hit 里，"entity" 字段保存了上面 output_fields 要求的原始数据。
    # 这里用列表推导式，把每条命中记录的 text 取出来，组成 contexts。
    contexts = [
        hit.get("entity", {}).get("text", "")   # 取不到就返回空字符串，避免报错
        for hit in results[0]
    ]

    # --- 4. 返回需要写回 State 的数据 ---
    # 只返回本次要更新的字段，LangGraph 会自动合并进 State。
    return {
        "query_vector": query_vector,
        "contexts": contexts
    }

# ===================== 路由函数：检索之后决定走哪条路 =====================

# 这是一个"条件路由"函数，根据状态决定下一步去哪个节点。
# 返回一个字符串，配合 add_conditional_edges 里的映射表使用。
def route_after_retrieve(state: State):
    # 如果 contexts 非空（检索到了内容）→ 走 answer 节点；
    # 否则（空列表是"假"值）→ 走 refuse 节点。

    return "answer" if state.get("contexts") else "refuse"


# ===================== 节点2：拒绝回答 refuse =====================

def refuse_node(state: State):
    # 没检索到相关内容时，直接返回一句固定话术，不再调用大模型
    return {"answer": "知识库中没有相关信息"}


# ===================== 节点3：生成回答 answer =====================

def answer_node(state: State):
    # 构建提示词模板。
    # {context} 和 {question} 是占位符，调用时会被真实内容替换。
    prompt = ChatPromptTemplate.from_template("""
请严格根据资料回答问题。
如果资料不足，请说明无法确定。

资料：
{context}

问题：
{question}
""")

    # 初始化通义千问大模型
    llm = ChatTongyi(
        model="qwen3.7-max",   # 指定使用的模型
        temperature=0.1        # 温度越低回答越稳定/保守，适合"严格根据资料"的场景
    )

    # 用 LCEL 的管道符（|）把步骤串成一条链：提示词 → 大模型 → 解析成字符串
    chain = prompt | llm | StrOutputParser()

    # 调用这条链，把检索到的资料和问题填进模板，得到最终答案
    answer = chain.invoke({
        "context": "\n\n".join(state["contexts"]),  # 把多个片段用空行拼接成一段资料
        "question": state["question"]
    })

    return {"answer": answer}


# ===================== 组装 LangGraph 流程 =====================

# 以 State 为状态结构，创建一个状态图（流程图）
builder = StateGraph(State)

# 往图里添加节点：第一个参数是节点名（自定义），第二个参数是对应的函数
builder.add_node("retrieve", retrieve_node)   # 检索节点
builder.add_node("refuse", refuse_node)       # 拒绝节点
builder.add_node("answer", answer_node)       # 回答节点

# --- 添加边（控制流程的走向）---

# 起点 START → retrieve 节点：流程从检索开始
builder.add_edge(START, "retrieve")

# 条件边：从 retrieve 出发，根据 route_after_retrieve 的返回值决定下一步。
# 第三个参数是映射表：返回值 "answer" → 去 answer 节点，"refuse" → 去 refuse 节点。
builder.add_conditional_edges(
    "retrieve",
    route_after_retrieve,
    {"answer": "answer", "refuse": "refuse"}
)

builder.add_edge("answer", END)   # answer 节点 → 终点 END
builder.add_edge("refuse", END)   # refuse 节点 → 终点 END

# 编译成可执行图（把节点和边固化，之后才能 invoke 运行）
graph = builder.compile()

# 运行整个流程：传入初始状态（只给了 question，其余字段由各节点逐步填写）
result = graph.invoke({
    # "question": "有几个犯罪案例？"
    "question": "林黛玉是谁？"
})

# 打印最终答案（由 answer 或 refuse 节点写入的 answer 字段）
# print(result["answer"])

from pprint import pprint
pprint(result)