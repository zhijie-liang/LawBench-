# ToolNode Agent Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add and verify a LangGraph ToolNode agent loop, then connect the verified behavior to the project chat flow without losing the current response contract.

**Architecture:** First create an isolated message-based graph using the existing two Tools. The graph will loop through one `agent` node and one `ToolNode`; conditional routing checks the last AI message for tool calls. Only after the isolated graph passes its tests will the main `/rag/chat` flow be changed.

**Tech Stack:** Python, LangGraph, LangChain Core, LangChain Tools, FastAPI, pytest, existing DashScope/Qwen/Milvus/MySQL services.

**Spec:** `docs/superpowers/specs/2026-08-21-toolnode-agent-design.md`

## Global Constraints

- Preserve existing `code/backend/workflow/rag_graph_chat.py` behavior during isolated graph work.
- Reuse `code/backend/services/tools.py`; do not create duplicate legal-search or document-detail implementations.
- Keep the current `/rag/chat` response fields: `answer`, `contexts`, `trace`, `stage`, and `error`.
- Do not use `git add .`; stage only files belonging to this feature when the user later requests a commit.

---

### Task 1: Define the isolated message-state graph contract

**Files:**
- Create: `code/backend/workflow/tool_graph.py`
- Test: `code/backend/tests/test_tool_graph.py`

**Interfaces:**
- Consumes: `search_legal_knowledge` and `get_document_detail` from `code/backend/services/tools.py`.
- Produces: `run_tool_graph(question: str) -> dict` returning `messages`, `answer`, `tool_names`, and `trace`.

- [ ] **Step 1: Write the failing tests for state and routing**

```python
def test_tool_graph_returns_final_answer_without_tool_call(monkeypatch):
    result = run_with_fake_model("你好")
    assert result["tool_names"] == []
    assert result["trace"] == ["agent"]


def test_tool_graph_routes_tool_call_to_tools_then_agent(monkeypatch):
    result = run_with_fake_model("劳动合同如何解除？")
    assert result["tool_names"] == ["search_legal_knowledge"]
    assert result["trace"] == ["agent", "tools", "agent"]
    assert result["messages"][-1].type == "ai"
```

- [ ] **Step 2: Run the focused tests and confirm they fail because the graph module is absent**

Run: `python -m pytest code/backend/tests/test_tool_graph.py -q`

Expected: collection/import failure for `code.backend.workflow.tool_graph` or the requested runner function.

- [ ] **Step 3: Implement the initial message state and agent node**

Use `MessagesState` or an equivalent `TypedDict` with `messages`. Bind the existing Tools to the model. The agent node must append one model message and record `agent` in an internal trace field.

- [ ] **Step 4: Add ToolNode and conditional routing**

Use one `ToolNode([search_legal_knowledge, get_document_detail])`. Route to `tools` only when the last `AIMessage.tool_calls` is non-empty; otherwise route to `END`.

- [ ] **Step 5: Compile and invoke the isolated graph**

Start with `{"messages": [HumanMessage(content=question)]}` and return the final messages plus a simple trace. Do not call `/rag/chat` in this task.

- [ ] **Step 6: Run the focused tests and confirm they pass**

Run: `python -m pytest code/backend/tests/test_tool_graph.py -q`

Expected: all isolated routing tests pass.

### Task 2: Make ToolNode behavior observable for learning and verification

**Files:**
- Modify: `code/backend/workflow/tool_graph.py`
- Modify: `code/backend/tests/test_tool_graph.py`

**Interfaces:**
- Consumes: the graph from Task 1.
- Produces: deterministic tests proving tool selection, tool execution, message handoff, and no-tool completion.

- [ ] **Step 1: Add a fake model test for `search_legal_knowledge`**

Assert the first AI message contains the expected tool name and arguments, the ToolNode output is a `ToolMessage`, and the second AI message is the final answer.

- [ ] **Step 2: Add a fake model test for `get_document_detail`**

Assert the selected tool receives an integer document ID and the final agent sees the returned document detail.

- [ ] **Step 3: Add a no-tool test**

Assert a greeting produces one AI response, no `ToolMessage`, and no tool name.

- [ ] **Step 4: Add tool execution failure coverage**

Patch one Tool to raise an exception and assert the graph returns a controlled error result or a clearly documented failure state instead of hiding the failure.

- [ ] **Step 5: Run the focused tests**

Run: `python -m pytest code/backend/tests/test_tool_graph.py -q`

Expected: tests prove both branches and the message sequence.

### Task 3: Connect the verified agent loop to the main chat endpoint

**Files:**
- Modify: `code/backend/workflow/rag_graph_chat.py`
- Modify: `code/backend/app.py` only if the response adapter requires it.
- Modify: `code/backend/tests/test_tool_graph.py` or create `code/backend/tests/test_rag_chat_contract.py`.

**Interfaces:**
- Consumes: the verified `run_tool_graph` result from Task 2.
- Produces: `/rag/chat` responses retaining `answer`, `contexts`, `trace`, `stage`, and `error`.

- [ ] **Step 1: Write contract tests before changing the endpoint**

Assert that a successful tool-assisted answer still has all five response fields; a refusal remains distinguishable from a system error.

- [ ] **Step 2: Choose the integration boundary**

Keep the existing fixed RAG graph available as the controlled retrieval path. Adapt ToolNode results into the existing `ContextResponse` shape instead of leaking raw Milvus or `ToolMessage` objects through FastAPI.

- [ ] **Step 3: Add the smallest adapter**

Map tool results to `contexts`, map the message sequence to `trace`, and set `stage` based on answer, refusal, or error. Do not change authentication or database schemas in this task.

- [ ] **Step 4: Run endpoint contract tests**

Run: `python -m pytest code/backend/tests -q`

Expected: new ToolNode tests and existing backend tests pass.

- [ ] **Step 5: Perform one controlled runtime verification**

Use one legal question and one ordinary greeting. Confirm the legal question records `agent → tools → agent`; confirm the greeting does not invoke a Tool. Do not repeat paid model calls unnecessarily.

### Task 4: Update the handoff and record acceptance evidence

**Files:**
- Modify: `HANDOFF.md`

**Interfaces:**
- Consumes: test and runtime evidence from Tasks 1–3.
- Produces: a concise continuation point for the next Tool/MCP learning step.

- [ ] **Step 1: Record the implemented file and graph path**

Document the exact `START → agent → tools → agent → END` behavior and the response adapter boundary.

- [ ] **Step 2: Record what remains unimplemented**

State whether ToolNode is integrated into `/rag/chat`, whether runtime calls succeeded, and that MCP and multi-agent remain out of scope.

- [ ] **Step 3: Run the final verification command**

Run: `python -m pytest code/backend/tests -q`

Expected: all relevant tests pass before claiming the module is complete.

