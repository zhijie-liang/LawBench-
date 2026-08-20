from typing import TypedDict
from pprint import pprint
from pymilvus import MilvusClient
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langgraph.graph import StateGraph, START, END
from typing import Literal
from services.llm import llm_qwen


def run_rag_graph(question: str):
    TraceStage = Literal[
        "retrieve", "grade", "rewrite", "generate",
        "refuse", "finish", "error"
    ]

    class State(TypedDict, total=False):
        question: str  # 用户输入的问题
        search_query: str  # llm改写问题
        contexts: list[str]  # 检索到的知识库内容（RAG上下文）
        is_relevant: bool  # 判断检索结果是否相关
        retry_count: int  # 当前重试次数
        answer: str  # 最终生成的回答
        error: str
        trace: list[TraceStage]
        stage: TraceStage

    # 将检索问题向量化并查询 Milvus，返回 Top-K 上下文；失败时写入错误状态
    def retrieve_node(state: State) -> dict:
        try:
            query_text = (
                    state.get("search_query")
                    or state["question"]
            )

            embeddings = DashScopeEmbeddings(
                model="text-embedding-v3"
            )
            query_vector = embeddings.embed_query(query_text)

            client = MilvusClient(
                uri="http://localhost:19530"
            )
            results = client.search(
                collection_name="document_chunks_v1",
                data=[query_vector],
                anns_field="vector",
                limit=3,
                output_fields=[
                    "text",
                    "document_id",
                    "chunk_index"
                ]
            )

            contexts = [
                hit.get("entity", {}).get("text", "")
                for hit in results[0]
            ]

            return {
                "contexts": contexts,
                "stage": "retrieve",
                "trace": append_trace(
                    state, "retrieve"
                )
            }

        except Exception:
            return {
                "error": "知识库检索服务暂时不可用",
                "stage": "error",
                "trace": append_trace(
                    state, "error"
                )
            }

    # 使用大模型判断检索资料是否能够回答用户问题
    def grade_node(state: State) -> dict:
        contexts = state.get("contexts", [])

        if not contexts:
            return {
                "is_relevant": False,
                "stage": "grade",
                "trace": append_trace(state, "grade")
            }

        prompt = ChatPromptTemplate.from_template("""
    判断资料是否能帮助回答问题。
    只能返回 yes 或 no。

    问题：{question}
    资料：{context}
    """)

        llm = llm_qwen(0)
        chain = prompt | llm | StrOutputParser()

        result = chain.invoke({
            "question": state["question"],
            "context": "\n\n".join(contexts)
        })

        return {
            "is_relevant": result.strip().lower().startswith("yes"),
            "stage": "grade",
            "trace": append_trace(state, "grade")
        }

    # 将系统异常转换为安全、统一的用户提示
    def error_node(state: State) -> dict:
        return {
            "answer": "系统暂时无法完成问答，请稍后重试。",
            "stage": "error"
        }

    # 根据用户原问题和相关资料生成最终答案
    def answer_node(state: State) -> dict:
        prompt = ChatPromptTemplate.from_template("""
    请严格根据资料回答问题。
    如果资料不足，请说明无法确定。

    资料：
    {context}

    问题：
    {question}
    """)
        llm = llm_qwen(0.1)
        chain = prompt | llm | StrOutputParser()
        answer = chain.invoke({
            'context': "\n\n".join(state["contexts"]),
            'question': state["question"]
        })
        return {
            "answer": answer,
            "stage": "generate",
            "trace": append_trace(state, "generate")
        }

    # 改写用户问题以提升检索效果，并增加一次重试计数
    def rewrite_query_node(state: State) -> dict:
        prompt = ChatPromptTemplate.from_template("""
    请改写用户问题，使其更适合在法律知识库中检索。
    只返回改写后的问题，不要解释。

    原问题：
    {question}
    """)

        llm = llm_qwen(0)
        chain = prompt | llm | StrOutputParser()

        new_query = chain.invoke({
            "question": state["question"]
        })

        return {
            "search_query": new_query.strip(),
            "retry_count": state.get("retry_count", 0) + 1,
            "stage": "rewrite",
            "trace": append_trace(state, "rewrite")
        }

    # 当知识库资料不相关时，返回统一的业务拒答结果
    def refuse_node(state: State) -> dict:
        return {
            "answer": "知识库中没有与该问题相关的信息。",
            "stage": "refuse",
            "trace": append_trace(state, "refuse")
        }

    # 根据检索是否发生异常，选择进入评估节点或错误节点
    def route_after_retrieve(state: State):
        if state.get("error"):
            return "error"
        return "grade"

    # 在不修改原列表的情况下，将当前阶段追加到流程轨迹
    def append_trace(state: State, stage: TraceStage) -> list[TraceStage]:
        return [*state.get("trace", []), stage]

    # 根据错误状态、相关性和重试次数选择回答、重写、拒答或错误分支
    def route_after_grade(state: State):
        if state.get("is_relevant", False):
            return "answer"

        if state.get("retry_count", 0) < 1:
            return "rewrite"

        return "refuse"



    builder = StateGraph(State)

    builder.add_node("retrieve", retrieve_node)
    builder.add_node("grade", grade_node)
    builder.add_node("answer", answer_node)
    builder.add_node("refuse", refuse_node)
    builder.add_node("rewrite", rewrite_query_node)
    builder.add_node("error", error_node)

    builder.add_edge(START, "retrieve")
    builder.add_conditional_edges(
        "retrieve",
        route_after_retrieve,
        {
            "grade": "grade",
            "error": "error"
        }
    )
    builder.add_conditional_edges(
        "grade",
        route_after_grade,
        {
            "answer": "answer",
            "rewrite": "rewrite",
            "refuse": "refuse"
        }
    )
    builder.add_edge("error", END)
    builder.add_edge("answer", END)
    builder.add_edge("rewrite", "retrieve")
    builder.add_edge("refuse", END)

    graph = builder.compile()
    result = graph.invoke({"question": question})
    pprint(result)
    return {
        "answer": result.get("answer", ""),
        "contexts": result.get("contexts", []),
        "trace": result.get("trace", []),
        "stage": result.get("stage", ""),
        "error": result.get("error", "")
    }

# langgraph_cs("林黛玉犯了什么法？")