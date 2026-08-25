# LawBench Tool + LangGraph 后续任务计划

更新时间：2026-08-25

## 当前基准

- 当前 Tool 实验文件：`code/backend/tests/cs.py`
- 当前正式流程：`code/backend/workflow/rag_graph_chat.py`
- 当前正式接口：`/rag/chat`
- 当前原则：先完成隔离实验，再接入正式接口；不直接修改接口。
- 当前实际不存在：`cs1.py`、`services/tools.py`

## 最终目标

将正式流程从：

```text
固定 retrieve → grade → rewrite → answer
```

升级为：

```text
Agent 决定是否检索
→ ToolNode 执行工具
→ 保存结构化 contexts
→ 判断资料相关性
→ 必要时重写问题并重试
→ Agent 根据资料回答
```

## 任务顺序

### 任务 1：冻结当前 ToolNode 基线

文件：`code/backend/tests/cs.py`

验收：

- 普通问候不产生 `tool_calls`；
- 法律问题产生 `tool_calls`；
- `ToolNode` 生成 `ToolMessage`；
- 第二次 Agent 根据 `ToolMessage` 输出答案。

本任务不增加新节点，只确认现有基础链路没有回退。

### 任务 2：在隔离图中保存完整状态

文件：`code/backend/tests/cs.py`

增加并验证：

- `messages`：保存完整消息链；
- `search_query`：保存 Agent 实际生成的检索问题；
- `contexts`：保存多个检索片段及来源字段；
- `trace`：保存经过的节点；
- `retry_count`：限制重试次数；
- `stage`、`error`：保存最终阶段和异常。

验收：最终输出中能同时看到答案、contexts、search_query、trace。

### 任务 3：补齐隔离图的完整分支

节点：

```text
decision_agent
→ tools
→ collect_contexts
→ grade
├─ answer_agent
├─ rewrite_agent → tools
├─ refuse
└─ error
```

验收四条路径：

1. 普通问候；
2. 正常检索并回答；
3. 资料不相关，重写一次后回答或拒答；
4. 模型、Milvus、JSON 解析异常。

### 任务 4：隔离图运行验收

仍只运行 `cs.py`，输出每个节点的输入、输出和最终 State。

只有以下结果全部成立，才进入正式文件：

- ToolNode 实际执行成功；
- `contexts` 没有丢失；
- `trace` 顺序正确；
- 普通问题不会检索；
- 法律问题不会绕过 Tool 直接回答；
- 异常能够落到 `error`。

### 任务 5：把隔离图迁移到正式工作流

文件：`code/backend/workflow/rag_graph_chat.py`

迁移原则：

- 不从接口层调用测试文件；
- 将已验证的 Tool 和节点逻辑写入正式工作流；
- 保留正式 State 的 `contexts`、`trace`、`stage`、`error`；
- 保留原有 `ChatResponse` 所需字段；
- 暂不修改 `app.py`。

### 任务 6：接入 `/rag/chat`

只有任务 5 的正式工作流独立运行通过后，才检查接口返回：

- `answer`；
- `contexts`；
- `trace`；
- `stage`；
- `error`。

验收普通问候、法律问题、无相关资料、异常四种请求。

## 当前唯一小目标

先完成任务 1：运行当前 `cs.py`，确认 ToolNode 基线没有问题。完成后再进入状态字段，不同时修改多个模块。
