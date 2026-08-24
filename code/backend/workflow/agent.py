from langchain_core.messages import HumanMessage, SystemMessage, AnyMessage
from pprint import pprint
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.prebuilt import ToolNode
from pymilvus import MilvusClient
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
from langgraph.graph import StateGraph, START, END
from typing import Literal
from langchain_core.tools import tool
import json
from services.llm import llm_qwen



class Context(TypedDict):
    text: str
    document_id: int
    chunk_index: int

def agent_graph(question: str):
    TraceStage = Literal[
        "agent", "tools", "collect_contexts", "grade", "answer",
        "rewrite", "refuse", "error"
    ]

    class State(TypedDict, total=False):
        question: str  # 用户输入的问题
        messages: Annotated[list[AnyMessage], add_messages]
        contexts: list[Context]  # 检索到的知识库内容（RAG上下文）
        is_relevant: bool  # 判断检索结果是否相关
        retry_count: int  # 当前重试次数
        answer: str  # 最终生成的回答
        error: str
        stage: TraceStage

        search_query: str  # llm改写问题
        trace: list[TraceStage]



    def append_trace(state: State, stage: TraceStage) -> list[TraceStage]:
        return [*state.get("trace", []), stage]

    def content_to_text(content) -> str:
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            return "".join(
                item.get("text", "") if isinstance(item, dict) else str(item)
                for item in content
            )
        return str(content)


    @tool
    def search_legal_knowledge(query: str) -> str:
        """检索法律知识库，返回相关法律资料。"""

        embeddings = DashScopeEmbeddings(
            model="text-embedding-v3"
        )
        query_vector = embeddings.embed_query(query)
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
        contexts = []

        for hit in results[0]:
            entity = hit.get("entity", {})

            contexts.append({
                "text": entity.get("text", ""),
                "document_id": entity.get("document_id"),
                "chunk_index": entity.get("chunk_index")
            })

        return json.dumps(contexts, ensure_ascii=False, indent=2)


    def decision_agent(state: State) -> dict:
        messages = [
            SystemMessage(content="""
    你是法律问答助手。
    普通问候可以直接回答。
    法律问题必须调用 search_legal_knowledge。
    只能根据工具返回的资料回答法律问题。
    """),
            HumanMessage(content=state["question"])
        ]

        try:
            response = llm_qwen(0).bind_tools([
                search_legal_knowledge
            ]).invoke(messages)
        except Exception as exc:
            return {
                "error": str(exc),
                "stage": "error",
                "trace": append_trace(state, "error")
            }

        result = {
            "messages": messages + [response],
            "trace": append_trace(state, "agent")
        }

        if response.tool_calls:
            result["search_query"] = response.tool_calls[0]["args"].get("query", "")
        else:
            result["answer"] = content_to_text(response.content)

        return result


    def tools_node(state: State) -> dict:
        try:
            result = ToolNode([
                search_legal_knowledge
            ]).invoke({
                "messages": state["messages"]
            })
        except Exception as exc:
            return {
                "error": str(exc),
                "stage": "error",
                "trace": append_trace(state, "error")
            }

        return {
            "messages": result["messages"],
            "stage": "tools",
            "trace": append_trace(state, "tools")
        }

    def collect_contexts(state: State) -> dict:
        try:
            contexts = json.loads(state["messages"][-1].content)
        except (TypeError, json.JSONDecodeError) as exc:
            return {
                "error": str(exc),
                "stage": "error",
                "trace": append_trace(state, "error")
            }

        return {
            "contexts": contexts,
            "stage": "collect_contexts",
            "trace": append_trace(state, "collect_contexts")
        }


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
        context_text = "\n\n".join(
            item["text"] for item in state["contexts"]
        )
        result = chain.invoke({
            "question": state["question"],
            "context": context_text
        })

        return {
            "is_relevant": result.strip().lower().startswith("yes"),
            "stage": "grade",
            "trace": append_trace(state, "grade")
        }


    def answer_agent(state: State) -> dict:
        try:
            response = llm_qwen(0).invoke(
                state["messages"]
            )
        except Exception as exc:
            return {
                "error": str(exc),
                "stage": "error",
                "trace": append_trace(state, "error")
            }

        return {
            "messages": [response],
            "answer": content_to_text(response.content),
            "stage": "answer",
            "trace": append_trace(state, "answer")
        }

    def rewrite_agent(state: State) -> dict:
        messages = [
            SystemMessage(content="""
    检索资料无法回答用户问题。
    请重新改写检索问题，并必须调用
    search_legal_knowledge。
    """),
            HumanMessage(content=state["question"])
        ]

        try:
            response = llm_qwen(0).bind_tools([
                search_legal_knowledge
            ]).invoke(messages)
        except Exception as exc:
            return {
                "error": str(exc),
                "stage": "error",
                "trace": append_trace(state, "error")
            }

        result = {
            "messages": messages + [response],
            "retry_count": state.get("retry_count", 0) + 1,
            "trace": append_trace(state, "rewrite"),
            "stage": "rewrite"
        }

        if response.tool_calls:
            result["search_query"] = response.tool_calls[0]["args"].get("query", "")
        else:
            result["error"] = "改写 Agent 未生成工具调用"
            result["stage"] = "error"

        return result

    def refuse_node(state: State) -> dict:
        return {
            "answer": "知识库中没有与该问题相关的信息。",
            "stage": "refuse",
            "trace": append_trace(state, "refuse")
        }


    def error_node(state: State) -> dict:
        return {
            "answer": "系统暂时无法完成问答，请稍后重试。",
            "stage": "error",
            "trace": append_trace(state, "error")
        }

    def route_after_decision(state: State):
        if state.get("error"):
            return "error"

        last_message = state["messages"][-1]
        if getattr(last_message, "tool_calls", []):
            return "tools"

        return "end"

    def route_after_tools(state: State):
        return "error" if state.get("error") else "collect"

    def route_after_collect(state: State):
        return "error" if state.get("error") else "grade"

    def route_after_grade(state: State):
        if state.get("error"):
            return "error"
        if state.get("is_relevant", False):
            return "answer"

        if state.get("retry_count", 0) < 1:
            return "rewrite"

        return "refuse"

    def route_after_rewrite(state: State):
        return "error" if state.get("error") else "tools"


    # def builder_(question: str):
    builder = StateGraph(State)

    builder.add_node("decision_agent", decision_agent)
    builder.add_node("tools", tools_node)
    builder.add_node("collect_contexts", collect_contexts)
    builder.add_node("grade", grade_node)
    builder.add_node("answer", answer_agent)
    builder.add_node("rewrite", rewrite_agent)
    builder.add_node("refuse", refuse_node)
    builder.add_node("error", error_node)

    builder.add_edge(START, "decision_agent")

    builder.add_conditional_edges(
        "decision_agent",
        route_after_decision,
        {
            "tools": "tools",
            "end": END,
            "error": "error"
        }
    )

    builder.add_conditional_edges(
        "tools",
        route_after_tools,
        {
            "collect": "collect_contexts",
            "error": "error"
        }
    )

    builder.add_conditional_edges(
        "collect_contexts",
        route_after_collect,
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
            "refuse": "refuse",
            "error": "error"
        }
    )

    builder.add_conditional_edges(
        "rewrite",
        route_after_rewrite,
        {
            "tools": "tools",
            "error": "error"
        }
    )
    builder.add_edge("answer", END)
    builder.add_edge("refuse", END)
    builder.add_edge("error", END)

    graph = builder.compile()

    result = graph.invoke({
        "question": question,
        "retry_count": 0,
        "trace": []
    })

    pprint(result)
    return result




# if __name__ == "__main__":
#     print("=== 测试普通问题 ===")
#     agent_graph("你好啊")
#
#     print("=== 测试法律问题 ===")
#     agent_graph("砍伐的林木销售给别人犯什么罪？")
