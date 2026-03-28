# JD 对齐学习路径（以本项目为实战载体）

> **目标**：通过维护、扩展本仓库，系统覆盖 **后端 + LLM 应用 / Agent / RAG** 类岗位 JD 常见技能；缺什么补什么，避免「只跑通 demo 却讲不清」。

---

## 1. 这类岗位 JD 常见关键词（归纳）

| 类别 | 常见关键词 |
|------|------------|
| 语言与 Web | Python、FastAPI/Flask、REST、异步、Pydantic |
| 数据与中间件 | MySQL/PostgreSQL、Redis、（可选）消息队列 |
| AI 工程 | LLM API、Prompt、RAG、向量检索、Embedding、Agent、Tool Calling |
| 框架（可选） | LangChain、LlamaIndex（JD 常写「熟悉其一」） |
| 工程化 | Git、pytest、日志、配置与密钥、Docker |
| 加分 | 评测、可观测（Trace/日志）、限流配额、内容安全 |

**面试本质**：能讲清 **数据流、trade-off、失败与成本**，而不是背名词。

---

## 2. 本项目已覆盖的能力（对照学）

| JD 方向 | 在本仓库里对应哪里 | 建议你刻意练什么 |
|---------|-------------------|------------------|
| Python 异步服务 | FastAPI、`async`/`await`、`chat_turn` | 读一条请求从 route → service 的全链路；改一个小接口并写 pytest |
| API 设计 | `schemas.py`、`routes.py` | 自己加一个只读诊断接口，写 OpenAPI 注释 |
| 关系型数据 | `ltm_sql.py`、`DATABASE_URL` | 本地起 MySQL，看 `ltm_items` 表结构；试着写一条只读 SQL 与 ORM 对照 |
| Redis | `redis_stm.py`、异步 LTM 队列 | 理解 key 设计；用 `redis-cli` 看 STM key |
| RAG | `app/rag/*`、`embedding_provider.py` | 画「用户话 → 改写 → 检索 → 拼 prompt」图；能口述为何用混合检索 |
| LLM 调用 | `app/llm/client.py`、OpenAI 兼容 | 读超时、重试、流式与非流式差异 |
| Agent/工具（轻量） | `app/tools/*`、`decide_mode` | 工具超时、失败怎么回到对话；为何不全上 Autonomous Agent |
| 可观测 | `app/trace/*` | 打开一次完整 trace json，解释每一步 |
| 运营与配置 | `hot_config`、配额 | 热更新与进程内 settings 的关系 |
| 测试 | `tests/`、conftest | 给新功能写一条 mock LLM 的用例 |
| 前端联调（全栈 JD） | `web/`、Vite 代理 | 改一个字段从后端到 TS 类型 |
| **LangChain（LCEL）** | `app/langchain/*` | 读 `main_chain`（Prompt→Model→StrOutputParser）、`rag_lcel`、`tools_lc`、`stm_history`；对照《框架化重构指南_LangChain向》 |

**你已有一块「比玩具强」的叙事**：双层记忆 + RAG + 安全 + 配额 + Trace + 评测入口；**主对话编排已统一为 LangChain LCEL**（情绪与隐式 LTM 抽取仍自研 `LLMClient`）。

---

## 3. JD 常写但本项目「弱或未用」的补学清单

按 **性价比** 排序（不必全做深，但要 **能答**）：

| 技能 | 现状 | 建议补法（1～2 周可轮转） |
|------|------|---------------------------|
| **LangChain** | **主链已统一 LCEL**：`app/langchain/`（RAG/工具/STM 适配 + 主 `ChatOpenAI`） | 跟《框架化重构指南》验收清单自查；进阶：官方 **Callback / Agent** 与 `LlmProviderIdCallback` 对照；或补 **20 行独立 Retriever demo** |
| **Docker / Compose** | 弱 | 完成《V1.2迭代规划》compose；能口述「api 依赖 redis/mysql 的启动顺序」 |
| **向量库（Milvus/pgvector）** | 内存索引 | 看三期规划；用 **pgvector 教程** 做最小表 + 一次 `SELECT ... <=>` |
| **压测** | 无 | `locust` 打 `/health` + 限流场景，能解释结果 |
| **结构化日志** | 基础 logging | 可选 `structlog` 或 JSON 一行日志，对接 `trace_id` |
| **OpenAPI → TS** | 手写类型 | 跑 `openapi-typescript`，对比生成文件与手写差异 |
| **算法题** | 与项目无关 | 岗位若考笔试，需 **另排每日时间**，不要用项目替代 |

---

## 4. 推荐学习顺序（12 周可压缩为 6 周加强版）

### 阶段 A：跑通 + 能讲（第 1～2 周）

1. 按 README 起后端 + Web，走完：聊天 → Memory Studio → Trace →（可选）运营台。  
2. 画 **一张架构图**：STM / LTM / RAG / LLM / Trace。  
3. 背不出类名没关系，要能讲 **「用户一句话经过哪些模块」**。

### 阶段 B：深挖 2 条主线（第 3～5 周）

**主线 1 — RAG**  

- 读 `retriever.py`、`query_rewrite.py`、`warm_index.py`。  
- 作业：用固定 user，打印 **改写前后 query + topK id**，写半页笔记「为何这样设计」。

**主线 2 — 工程**  

- 读 `chat_turn.py` 里配额与安全顺序。  
- 作业：给 `GET /health` 或热配加一个小字段并写单测（可对照现有 `ltm_extract_enabled` 与 `test_v5_admin_config.py`）。

### 阶段 C：对齐 JD 缺口（第 6～8 周）

- **LangChain**：读 **`app/langchain/`** + 跑 **`test_langchain_*`** + 看 **`tests/conftest.py` autouse** 如何 mock 主链；能口述 **主链 LCEL** 与 **情绪/抽取 httpx** 的分工。  
- **Docker Compose**：依赖一键起。  
- **评测**：跑 builtin eval，能解释一条样本的 trace。

### 阶段 D：简历与模拟面试（持续）

- 每条项目 bullet 用 **STAR**：场景 + 你做的 + 指标/难点。  
- 准备 **3 个追问**：为何主链用 LangChain 而情绪/抽取仍 httpx、向量存哪、多实例怎么办。（若被问「为何不全用 LangChain」：可答辅助调用不绑进 Agent 循环，便于配额与失败隔离。）

---

## 5. 与仓库内文档的索引

| 文档 | 用途 |
|------|------|
| 《整体规划》 | 终局能力与面试高频答法 |
| 《三期迭代规划》 | pgvector、持久化、界面标杆 |
| 《V1.2迭代规划》 | Docker、OpenAPI、评测指标补强 |
| 《框架化重构指南_LangChain向.md》 | 若 JD 强要求 LangChain |
| 《常用命令》 | 日常命令与 STM/LTM 行为 |

---

## 6. 心态

- **项目不可能覆盖 JD 每一个词**；目标是 **80% 重合 + 对剩余 20% 诚实 + 有补学计划**。  
- 面试官更看重：**你是否理解自己的代码、能否扩展、是否知道业界常见方案**。

---

*版本：v3 — 同步「主链唯一 LangChain、无 legacy 双轨」；可随投递方向增删「补学清单」。*
