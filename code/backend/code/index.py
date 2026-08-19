from typing import TypedDict
from pymilvus import MilvusClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langchain_community.chat_models import ChatTongyi
from langgraph.graph import StateGraph, START, END
from typing import Literal



class State(TypedDict, total=False):
    question: str # 用户输入的问题
    search_query: str # llm改写问题
    contexts: list[str] # 检索到的知识库内容（RAG上下文）
    is_relevant: bool # 判断检索结果是否相关
    retry_count: int # 当前重试次数
    answer: str # 最终生成的回答
    # 当前流程阶段[检索\评估\重写\生成\拒绝\结束]
    stage: Literal[
        "retrieve", "grade", "rewrite", "generate", "refuse", "finish"
    ]

def retrieve_node(state: State) -> dict:
    query_text = state.get("search_query", state["question"])
    embeddings = DashScopeEmbeddings(
        model='text-embedding-v3'
    )
    query_vector = embeddings.embed_query(query_text)
    client = MilvusClient(uri="http://localhost:19530")
    results = client.search(
        collection_name="document_chunks_v1",
        data=[query_vector],
        anns_field='vector',
        limit=3,
        output_fields=["text", "document_id", "chunk_index"]
    )
    contexts = [
        hit.get("entity", {}).get("text", "")
        for hit in results[0]
    ]
    return {
        "question": state["question"],
        "contexts": contexts,
        "stage": "retrieve",
    }

def grade_node(state: State) -> dict:
    contexts = state.get("contexts", [])

    if not contexts:
        return {
            "is_relevant": False,
            "stage": "grade"
        }

    prompt = ChatPromptTemplate.from_template("""
判断资料是否能帮助回答问题。
只能返回 yes 或 no。

问题：{question}
资料：{context}
""")

    llm = ChatTongyi(model="qwen3.7-max", temperature=0)
    chain = prompt | llm | StrOutputParser()

    result = chain.invoke({
        "question": state["question"],
        "context": "\n\n".join(contexts)
    })

    return {
        "is_relevant": result.strip().lower().startswith("yes"),
        "stage": "grade"
    }

def answer_node(state: State) -> dict:
    prompt = ChatPromptTemplate.from_template("""
请严格根据资料回答问题。
如果资料不足，请说明无法确定。

资料：
{context}

问题：
{question}
""")
    llm = ChatTongyi(
        model="qwen3.7-max",
        temperature=0.1
    )
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({
        'context': "\n\n".join(state["contexts"]),
        'question': state["question"]
    })
    return {
        "answer": answer,
        "stage": "generate"
    }

def refuse_node(state: State) -> dict:
    return {
        "answer": "知识库中没有与该问题相关的信息。",
        "stage": "refuse"
    }

def route_after_grade(state: State):
    if state.get("is_relevant", False):
        return "answer"

    if state.get("retry_count", 0) < 1:
        return "rewrite"

    return "refuse"

def rewrite_query_node(state: State) -> dict:
    prompt = ChatPromptTemplate.from_template("""
请改写用户问题，使其更适合在法律知识库中检索。
只返回改写后的问题，不要解释。

原问题：
{question}
""")

    llm = ChatTongyi(model="qwen3.7-max", temperature=0)
    chain = prompt | llm | StrOutputParser()

    new_query = chain.invoke({
        "question": state["question"]
    })

    return {
        "search_query": new_query.strip(),
        "retry_count": state.get("retry_count", 0) + 1,
        "stage": "rewrite"
    }


builder = StateGraph(State)

builder.add_node("retrieve", retrieve_node)
builder.add_node("grade", grade_node)
builder.add_node("answer", answer_node)
builder.add_node("refuse", refuse_node)
builder.add_node("rewrite", rewrite_query_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "grade")

builder.add_conditional_edges(
    "grade",
    route_after_grade,
    {
        "answer": "answer",
        "rewrite": "rewrite",
        "refuse": "refuse"
    }
)

builder.add_edge("answer", END)
builder.add_edge("rewrite", "retrieve")
builder.add_edge("refuse", END)

graph = builder.compile()

result = graph.invoke(
    {
    # "question": "伪造身份证件如何处罚？"
    "question": "林黛玉是谁？"
    }
)

from pprint import pprint
pprint(result)