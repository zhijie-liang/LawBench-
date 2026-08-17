# 律鉴 LawBench 项目交接

更新时间：2026-08-14

## 项目目标

从零完成一个面向法律工作者的RAG资料检索与辅助分析MVP，用于周五面试展示。当前优先保证流程可运行、可演示、可讲解；生产级安全和工程能力在闭环后补齐，未实现功能不能描述为已实现。

## 已完成

- Docker Compose启动MySQL、Milvus、etcd、MinIO。
- MySQL用户注册、登录。
- 文本资料保存、TXT上传、正文提取。
- 关键词检索，最多返回3条。
- MySQL文档加载接口：`GET /pipeline/load`。
- 文本清洗函数：`text_processor.clean_text`。
- 文本切块函数：`text_processor.split_text`。
- `text-embedding-v3`调用测试成功，输出512维向量。
- Milvus集合`document_chunks_v2`已创建，字段为：`id`、`document_id`、`chunk_index`、`text`、`vector(512)`。
- 已验证单个切块和批量切块向量写入、向量检索。

## 当前进行中

- 将加载、清洗、切块、向量化、入库分别包装成接口。
- 已采用JSON保存阶段中间结果，避免每一步重复查询MySQL。
- `pipeline_store.py`负责`loaded.json`等阶段文件。

## 本次暂停进度（2026-08-14）

- 已确认`/pipeline/clean`不能直接执行`clean_text(rows)`：`rows`是文档列表，`clean_text`接收单条字符串。
- 已确认`loaded.json`每条记录的正文位于索引`2`。
- 已给出清洗接口参考实现：逐条复制记录、清洗`row[2]`、保存`data/cleaned.json`，并返回数量和结果。
- 已完成验证：调用清洗函数返回4条记录，记录字段保持不变，正文换行已清除，并成功写入`data/cleaned.json`。
- 切块接口已由用户完成并验证：4篇文档生成11条`[document_id, chunk_index, text]`记录；当前代码写入`data/chunk.json`，后续向量化前需统一为约定的`data/chunked.json`。
- 切块模块验证通过后，提醒Git提交推送；推送完成后进入向量化接口。
- 已开始编写向量化函数：读取切块阶段文件、调用`text-embedding-v3`并写入`document_chunks_v2`。
- 已定位Milvus启动日志原因：`main.py`导入`milvus_service`时会执行其顶层连接和集合初始化代码。
- 已完成Milvus懒加载修正：导入`main`不会连接Milvus；首次调用`get_collection()`初始化，后续调用复用同一集合对象。

## 下一步顺序

1. 完成清洗接口：读取`loaded.json`，保存`cleaned.json`。
2. 完成切块接口：读取`cleaned.json`，保存`chunked.json`。
3. 完成向量化接口：读取切块，调用Embedding。
4. 完成入库接口：写入`document_chunks_v2`。
5. 完成向量检索接口。
6. 接入`qwen3.7-max`生成带检索依据的回答。
7. 做完整演示测试并提醒Git提交推送。

## 当前重要约定

- Embedding暂用512维；闭环后若升级维度，需新建集合并重新向量化。
- 不删除旧的4维测试集合，除非明确确认。
- 不把API Key写入代码，使用Windows环境变量。
- 每完成一个可验证模块，先测试，再提醒执行Git push。

## 已知待完善问题

- 闭环后增强任务：为Embedding增加分级降级处理。线上向量模型调用失败时，先明确提示用户检查/启动Ollama服务，再自动切换本地`qwen3-embedding:0.6b`；同时校验本地模型向量维度，维度不一致时切换到对应Milvus集合，禁止混写不同维度向量。
- 2026-08-17：向量化调用出现DashScope`SSLEOFError`。已确认直连`https://dashscope.aliyuncs.com`可返回响应；Key存在于Windows用户环境变量（长度117），但当前PowerShell/Python进程未继承。下次重启终端或在当前进程加载用户变量后，再做一次受控测试，不要重复调用。
- 2026-08-17补充：未改变业务代码并回滚传输层实验后，向量化调用自行恢复；该问题表现为间歇性网络/TLS或代理链路故障，不能记录为代码已修复。
- 当前`/pipeline/load`每次全量读取文档；数据增长后需改为按新增/更新时间或处理状态增量加载，避免重复清洗、切块和向量化。
- 密码哈希、JWT和权限控制。
- 统一异常处理、参数校验、数据库连接池。
- 文件名独立检索和来源字段返回。
- 删除历史误入库的HTML记录。
- 大文件存储、数据库迁移、日志、测试和部署优化。
