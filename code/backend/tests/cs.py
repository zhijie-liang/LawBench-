from pprint import pprint
from langchain_core.tools import tool
from langchain_core.messages import (HumanMessage, SystemMessage, AnyMessage)
from typing import Annotated, TypedDict
from langgraph.graph.message import add_messages
from services.llm import llm_qwen
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, START, END
from pymilvus import MilvusClient
from langchain_community.embeddings.dashscope import DashScopeEmbeddings
import json

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

def print_messages(title: str, messages: list[AnyMessage]):
    print(f"\n=== {title} ===")

    for index, message in enumerate(messages):
        print(f"[{index}] {type(message).__name__}")
        print("content:")
        pprint(message.content)

        if getattr(message, "tool_calls", []):
            print("tool_calls:")
            pprint(message.tool_calls)

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


def agent_node(state: State):
    print_messages("Agent 输入", state["messages"])

    llm_with_tools = llm_qwen(0).bind_tools([
        search_legal_knowledge
    ])

    response = llm_with_tools.invoke(
        state["messages"]
    )

    print_messages("Agent 输出", [response])

    return {
        "messages": [response]
    }


def tools_node(state: State):
    print_messages("ToolNode 输入", state["messages"])

    tool_node = ToolNode([
        search_legal_knowledge
    ])

    result = tool_node.invoke(state)

    print_messages(
        "ToolNode 输出",
        result["messages"]
    )

    return {
        "messages": result["messages"]
    }


def route_after_agent(state: State):
    last_message = state["messages"][-1]

    if last_message.tool_calls:
        print("\n=== 路由结果：tools ===")
        return "tools"

    print("\n=== 路由结果：END ===")
    return "end"

def builder_(question: str):
    builder = StateGraph(State)

    builder.add_node("agent", agent_node)
    builder.add_node("tools", tools_node)

    builder.add_edge(START, "agent")

    builder.add_conditional_edges(
        "agent",
        route_after_agent,
        {
            "tools": "tools",
            "end": END
        }
    )

    builder.add_edge("tools", "agent")

    graph = builder.compile()

    result = graph.invoke({
        "messages": [
            SystemMessage(content="""
            只能根据 Tool 返回的 JSON 资料回答。
            每条资料包含 text、document_id、chunk_index。
            回答结论必须来自 text，并在相关内容后标注 document_id 和 chunk_index。
            资料没有提到的内容不要补充。
            """),
            HumanMessage(content=question)
        ]
    })

    print_messages(
        "最终消息 State",
        result["messages"]
    )

print("\n========== 分支一：普通问候 ==========")
builder_("你好啊？")

print("\n========== 分支二：法律问题 ==========")
builder_("砍伐的林木销售给别人犯什么罪？")
