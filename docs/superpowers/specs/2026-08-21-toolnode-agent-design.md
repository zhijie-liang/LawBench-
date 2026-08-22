# LawBench ToolNode Agent 设计

## 目标

在不破坏现有固定 RAG 流程的前提下，增加一个由 LLM 自主选择法律 Tool 的 LangGraph 闭环，并在独立验证后接入 `/rag/chat`。

## 当前问题

项目已有两个 LangChain Tool 和普通 Python Tool 循环，但 Tool 尚未接入 LangGraph。现有 `rag_graph_chat.py` 是固定的 `retrieve → grade → rewrite/refuse/answer` 流程，不能让模型自主决定是否检索或查询文档详情。

## 设计

新增独立图，使用消息状态：

```text
START → agent → 条件路由
                 ├─ 有 tool_calls → tools → agent
                 └─ 无 tool_calls → END
```

`agent` 只负责调用绑定 Tool 的 LLM；`ToolNode` 负责读取 `AIMessage.tool_calls`、执行工具并追加 `ToolMessage`；条件路由根据最后一条 AIMessage 是否包含工具调用决定循环或结束。两个 `agent` 不是两个节点，而是同一个节点被循环执行两次。

## 状态契约

图状态使用 `messages: list[AnyMessage]`。初始消息为 `HumanMessage`。Agent 输出 `AIMessage`；需要工具时其 `tool_calls` 包含工具名、参数和调用 ID；ToolNode 追加对应的 `ToolMessage`；第二次 Agent 读取完整消息历史并生成最终 `AIMessage`。

## 验收标准

1. 法律问题能够产生 `search_legal_knowledge` 的 `tool_calls`，ToolNode 能执行并追加 `ToolMessage`。
2. 文档详情问题能够选择 `get_document_detail`，参数为文档 ID。
3. 普通问候不调用 Tool，图直接结束并返回回答。
4. 工具执行结果能被第二次 Agent 读取，形成最终回答。
5. 现有 `rag_graph_chat.py` 和 `/rag/chat` 的原有回答、拒答、错误结构在独立图阶段不被修改。
6. 独立图验证通过后，才设计主接口接入，保留 `answer`、`contexts`、`trace`、`stage`、`error` 返回字段。

