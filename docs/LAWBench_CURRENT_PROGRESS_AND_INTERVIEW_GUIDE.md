# LawBench 当前成果、技术地图与面试手册

更新时间：2026-08-22  
当前分支：\`codex/lawbench-v2\`  
当前工作目录：\`D:\codex_project\LawBench(律鉴)\`

## 1. 项目定位

LawBench 是一个法律知识库问答系统，核心目标是：

~~~text
上传法律资料
→ 清洗与切分
→ 向量化并写入 Milvus
→ 用户提问
→ 检索相关资料
→ LLM 根据资料回答
→ 返回答案、依据和处理轨迹
~~~

当前项目已经从普通 RAG 开始学习 LangGraph、Tool 和 Agent，但尚未达到完整企业级。

## 2. 当前已经具备的能力

### 正式代码已有

主入口：\`code/backend/app.py\`

| 接口 | 当前作用 | 状态 |
|---|---|---|
| \`POST /register\` | 用户注册 | 已有代码 |
| \`POST /login\` | 用户登录 | 已有代码 |
| \`POST /rag\` | 上传 TXT、清洗、MySQL 入库、切块、Embedding、Milvus 入库 | 已有代码 |
| \`GET /chat\` | 普通 RAG 检索与回答 | 已有代码 |
| \`GET /rag/chat\` | LangGraph 检索、判断、改写、回答、拒答、错误状态 | 已有代码 |

### 正式 RAG 数据流

~~~text
UploadFile
→ UTF-8 解码
→ 文本清洗
→ MySQL documents
→ LangChain Document
→ RecursiveCharacterTextSplitter
→ DashScope text-embedding-v3
→ Milvus document_chunks_v1
→ 用户问题 Embedding
→ Milvus Top-3
→ Prompt
→ ChatTongyi/Qwen
→ 回答
~~~

### 正式 LangGraph 流程

\`code/backend/workflow/rag_graph_chat.py\` 当前包含：

~~~text
START
→ retrieve
→ grade
→ answer
~~~

如果资料不相关：

~~~text
grade
→ rewrite
→ retrieve
→ grade
→ refuse
~~~

如果检索异常：

~~~text
retrieve
→ error
→ END
~~~

已具备的 State 字段：

~~~text
question
search_query
contexts
is_relevant
retry_count
answer
error
trace
stage
~~~

## 3. 当前已验证的 ToolNode 实验

实验文件：\`code/backend/tests/cs.py\`

该文件是隔离学习代码，尚未接入正式接口。

当前实验图：

~~~text
START
→ agent
→ 条件路由
   ├─ 无 tool_calls → END
   └─ 有 tool_calls → tools
                       ↓
                     agent
                       ↓
                      END
~~~

### Agent 节点

~~~python
llm_qwen(0).bind_tools([search_legal_knowledge])
~~~

Agent 调用模型后，模型可能返回：

~~~text
普通回答：AIMessage.content
工具请求：AIMessage.tool_calls
~~~

### Tool 节点

当前 \`search_legal_knowledge\` 的真实实验流程是：

~~~text
query
→ DashScope Embedding
→ 1024 维向量
→ Milvus document_chunks_v1
→ Top-3
→ 当前返回 contexts[0]["text"]
~~~

### 已验证输出

普通问候：

~~~text
Agent → END
~~~

法律问题：

~~~text
Agent
→ AIMessage.tool_calls
→ tools
→ ToolNode
→ ToolMessage
→ Agent
→ 最终 AIMessage
→ END
~~~

这证明了：

- LLM 可以决定调用 Tool；
- \`tool_calls\` 包含工具名、参数和调用 ID；
- ToolNode 可以执行 Tool；
- Tool 结果可以包装为 ToolMessage；
- 第二次 Agent 可以读取完整消息历史并生成回答。

## 4. 必须诚实说明的当前边界

以下内容目前不能在面试中说成“已经完成”：

| 能力 | 当前状态 |
|---|---|
| 混合检索 | 未实现，当前主要是向量检索 |
| RRF 融合 | 未实现 |
| Reranker | 未实现 |
| 多 Tool 自主选择 | 正在学习，当前实验只绑定一个 Tool |
| Tool 参数校验 | 未完成 |
| Tool 超时与重试 | 未完成 |
| 严格引用校验 | 未完成 |
| 答案事实校验 | 未完成 |
| 评测集与自动评测 | 未完成 |
| Prompt/Tool 全链路追踪 | 仅有实验打印 |
| JWT/RBAC/多租户 | 未完成 |
| 异步入库 | 未完成 |
| 模型网关与降级 | 未完成 |
| 生产级监控部署 | 未完成 |

## 5. 当前最重要的技术问题

### 5.1 Tool 返回结果不完整

当前 Tool 返回：

~~~python
return contexts[0]["text"]
~~~

这会丢失：

~~~text
document_id
chunk_index
其他 Top-K 片段
相似度
标题和来源
~~~

后续应返回结构化结果，而不是只返回第一条文本。

### 5.2 Tool 结果不等于答案依据

即使存在 ToolMessage，LLM 仍可能结合自身知识补充答案。

企业级需要：

~~~text
检索片段编号化
→ 答案强制引用
→ 引用存在性校验
→ 事实支持校验
→ 失败则重写或拒答
~~~

### 5.3 当前 SystemMessage 只是软约束

~~~text
只能根据工具返回的资料回答
~~~

它可以降低幻觉，但不能提供绝对保证。真正可靠的控制需要程序校验和拒答分支。

### 5.4 当前异常处理不足

例如：

- Milvus 搜索失败会抛异常；
- Embedding 失败没有统一返回结构；
- Tool 返回空列表时 \`contexts[0]\` 会报错；
- MySQL 已写入但 Milvus 失败时可能产生半成品；
- Agent 可能重复循环调用 Tool。

## 6. 企业级补齐路线

建议顺序：

~~~text
1. Tool 返回结构化结果
2. Tool 参数校验和异常处理
3. 引用绑定与答案校验
4. 多 Tool 选择与循环限制
5. 混合检索与 Reranker
6. 评测集和自动评测
7. 全链路可观测性
8. 异步入库与任务状态
9. 权限、多租户和审计
10. 模型网关和生产部署
~~~

每个模块统一按照：

~~~text
需求
→ 缺口
→ 方案
→ 实现
→ 正常测试
→ 失败测试
→ 验收
→ 面试总结
~~~

## 7. 针对当前项目的面试题与答案

### Q1：你的项目解决什么问题？

答：LawBench 是法律知识库问答系统。用户上传法律资料后，系统将文本切分、向量化并写入 Milvus；用户提问时将问题向量化，检索相关片段，再交给 Qwen 基于资料生成回答。后续使用 LangGraph 管理检索、相关性判断、问题改写、回答、拒答和错误分支。\n
### Q2：为什么使用 RAG，而不是让大模型直接回答？

答：法律问题需要基于项目资料回答，并且资料可能更新。RAG 先检索外部知识，再把相关片段交给模型，可以降低模型脱离知识库回答的风险，并提供来源依据。当前项目仍需继续补充引用校验，不能声称完全消除幻觉。

### Q3：项目中的 RAG 数据流是什么？

答：上传 TXT 后先解码和清洗，写入 MySQL；再转换为 LangChain Document，使用 RecursiveCharacterTextSplitter 切块；切块通过 DashScope Embedding 转成 1024 维向量，写入 Milvus。查询时对问题做同样的 Embedding，在 Milvus 中检索 Top-3，拼接上下文后交给 Qwen。

### Q4：为什么 MySQL 和 Milvus 都要使用？

答：MySQL 保存文档的结构化主数据和完整正文，适合事务查询；Milvus 保存文本分块向量，适合相似度检索。两者职责不同：MySQL 是文档事实存储，Milvus 是向量检索索引。

### Q5：为什么需要切块？

答：整篇文档直接向量化会导致检索粒度过粗，也可能超过模型上下文限制。切块后可以返回与问题更相关的局部内容。当前使用固定长度和重叠切分，后续还需要按法律条款、章节和语义优化。

### Q6：LangChain 在项目中做了什么？

答：LangChain 负责连接 Prompt、LLM、Embedding、Document、文本切分器、Tool 和消息对象。它减少底层接口适配代码，但它本身不是 Agent；Agent 的决策和流程仍由模型与 LangGraph 共同完成。

### Q7：LangGraph 解决什么问题？

答：LangGraph 把复杂问答流程表示为有状态的图。节点负责具体动作，边负责流程连接，条件边负责分支，State 负责在节点之间传递数据。当前项目用它管理检索、相关性判断、改写、重试、回答、拒答和错误流程。

### Q8：State 在项目中是什么？

答：State 是节点共享的数据结构。当前 RAG State 包含问题、检索结果、相关性、重试次数、答案、错误、阶段和轨迹；ToolNode 实验的 State 主要是 messages。节点返回部分字段，LangGraph 将其合并到共享状态。

### Q9：Agent 和普通 RAG 有什么区别？

答：普通 RAG 的路线由程序固定，例如检索后直接生成；Agent 允许 LLM 根据问题决定是否调用哪个 Tool、传什么参数以及是否继续下一步。当前项目正在从固定 RAG 过渡到 \`agent → tools → agent\`。

### Q10：\`bind_tools()\` 做了什么？

答：它把 Tool 的名称、参数结构和说明绑定给 LLM，使模型能够输出结构化的 \`tool_calls\`。它不会执行 Tool，也不会自动把结果返回给模型。

### Q11：\`tool_calls\` 是什么？

答：它是 AIMessage 中的工具调用请求，包含工具名、参数和调用 ID。例如模型可能输出 \`search_legal_knowledge\`，参数为一个改写后的检索问题。它是模型的请求，不是工具执行结果。

### Q12：ToolNode 做什么？

答：ToolNode 是 LangGraph 的预置节点。它读取 AIMessage 中的 \`tool_calls\`，根据工具名找到对应 Tool，执行工具，将结果包装成 ToolMessage，再交回图的消息 State。LLM 不直接执行 Python 函数。

### Q13：为什么流程中有两个 Agent？

答：不是两个不同 Agent，而是同一个 Agent 节点执行两次。第一次判断是否调用 Tool；ToolNode 执行后，第二次读取 ToolMessage 并生成最终回答。

### Q14：普通问候为什么不调用 Tool？

答：第一次 Agent 返回的 AIMessage 中 \`tool_calls\` 为空，条件路由直接返回 END。法律问题则会产生非空 \`tool_calls\`，路由进入 tools 节点。

### Q15：ToolMessage 为什么必须加入 messages？

答：第二次 LLM 需要知道自己之前请求了什么工具、工具实际返回了什么。ToolMessage 通过 \`tool_call_id\` 与此前的调用对应，形成完整的消息协议。

### Q16：当前回答完全来自知识库吗？

答：不能这样说。当前 Tool 返回了检索片段，LLM 能看到这些资料，但没有完成严格引用和事实校验，因此模型仍可能结合自身知识补充。企业级需要引用绑定、支持性校验和拒答机制。

### Q17：当前 Tool 有什么问题？

答：当前实验 Tool 只返回 \`contexts[0]["text"]\`，丢失其他 Top-K 片段、文档 ID、分数和标题；没有空结果处理、异常处理、超时、权限和重试。下一步应先改成结构化 Tool 输出。

### Q18：Milvus 报“VECTOR_FLOAT 和 VARCHAR 类型不一致”是什么原因？

答：Milvus 的向量字段要求浮点向量，但查询时传入了原始字符串。正确流程是先用 Embedding 将 query 转成 1024 维向量，再以 \`data=[query_vector]\` 搜索。

### Q19：如何防止 Agent 无限调用 Tool？

答：在图 State 中保存 step 或 retry_count，在路由中限制最大次数；超过上限后进入 error 或 refuse 节点。同时给 Tool 设置超时、重试和幂等控制。

### Q20：如何处理 Tool 失败？

答：ToolNode 捕获异常并写入统一错误状态，记录失败阶段、工具名和安全错误信息；不能把完整堆栈、密钥或数据库细节直接返回给前端。必要时允许重试，超过次数后返回可理解的失败结果。

### Q21：为什么要做混合检索？

答：向量检索擅长语义相似，关键词检索擅长法条编号、罪名、专有名词和精确匹配。两者通过 RRF 融合，再用 Reranker 重排，可以提升法律场景的召回和排序质量。

### Q22：如何评估检索质量？

答：建立带标准文档 ID 的问题集，计算 Recall@K、Precision@K、MRR 和 nDCG。答案层面再评估正确性、引用准确率、拒答准确率和幻觉率。每次修改切分、Embedding、检索或 Prompt 后进行回归。

### Q23：如何实现企业级可观测性？

答：为每次请求生成 trace_id，记录 API、Agent、Embedding、Milvus、Tool、LLM 的调用链、耗时、Token、错误和最终状态。可以用 Langfuse/LangSmith 记录 LLM 链路，用 OpenTelemetry 做统一追踪，用 Prometheus/Grafana 做指标和看板。

### Q24：如何实现权限检索？

答：文档保存租户、部门、角色和可见范围；检索前根据当前用户身份生成过滤条件，向量检索必须带权限过滤，不能先检索全部资料再在回答阶段过滤。

### Q25：上传入库为什么要异步化？

答：解析、切分、Embedding 和 Milvus 写入耗时不稳定，不应长期占用 HTTP 请求。上传接口返回 job_id，Worker 异步处理，前端通过任务状态查询进度；失败任务支持重试和断点恢复。

### Q26：当前项目距离企业级最核心的差距是什么？

答：不是缺少某一个框架，而是缺少质量和运行保障：检索质量评测、答案引用校验、Tool 失败恢复、权限控制、全链路观测、异步任务和生产部署。目前已经有技术骨架，但还需要把“能运行”升级为“可证明可靠”。

## 8. 面试表达边界

可以说：

~~~text
我已经完成 FastAPI、MySQL、Milvus、LangChain、LangGraph、基础 RAG 和 ToolNode 闭环，并验证了普通问候与工具调用两条分支。
~~~

不能说：

~~~text
已经完成企业级混合检索、严格防幻觉、完整权限、多租户、自动评测和高可用部署。
~~~

正确表达方式是：

~~~text
当前已完成基础链路，下一步通过结构化 Tool 输出、引用校验、评测体系、权限过滤和异步任务逐步补齐企业级能力。
~~~

## 9. 下一步唯一建议

先完成：

~~~text
Tool 结构化返回
→ 返回多个 contexts 及来源元数据
→ 再做引用约束和答案校验
~~~

不要同时跳到 MCP、多 Agent 或大规模重构。

