# 框架化重构指南（LangChain 向 · 与主流 JD 对齐）

> **目的**：在 **不推翻现有业务价值**（Trace、配额、热配、隐式 LTM、运营接口）的前提下，把 **对话主链路** 落在 **LangChain（LCEL）** 上，使简历与面试能明确写出「LangChain / Runnable / Retriever / Tool」等 JD 关键词。  
> **现状（仓库已收敛）**：**`legacy` 编排与 `CHAT_ORCHESTRATOR` / `chat_orchestrator` 热配已移除**；主回复、RAG、工具执行、STM 加载均为 **唯一 LangChain 路径**；情绪与隐式 LTM 抽取仍用自研 **`LLMClient`（httpx）**。  
> **历史**：曾采用绞杀者双轨迁移；完成后删除旧分支，避免配置与代码长期分叉。  
> **关联**：《V1.2迭代规划》偏工程与 Docker/OpenAPI；本文偏 **AI 编排层**；**三期** 仍负责 pgvector、持久向量库等。

---

## 目录

1. [与其它文档及学习路径的关系](#1-与其它文档及学习路径的关系)  
2. [目标与边界](#2-目标与边界)（简历表述 · 保留自研 · 框架选型）  
3. [总体架构（迁移后）](#3-总体架构迁移后)  
4. [模块对照表（实施前先定位代码）](#4-模块对照表实施前先定位代码)  
5. [分阶段路线图](#5-分阶段路线图)（阶段 0～6）  
6. [测试与回归策略](#6-测试与回归策略)  
7. [风险与应对](#7-风险与应对)  
8. [验收清单](#8-验收清单)  
9. [简历 / 面试话术（诚实版）](#9-简历--面试话术诚实版)

---

## 1. 与其它文档及学习路径的关系

| 文档 | 关系 |
|------|------|
| 《JD对齐学习路径_项目驱动.md》 | **何时学 LangChain**：阶段 C 建议「小 demo 或本文阶段 0～2」；本文是 **JD 强要求 LangChain 时的实施手册**。 |
| 《V1.2迭代规划》 | Docker、OpenAPI、评测指标；可与本文 **并行**，但注意人力排期。 |
| 《三期迭代规划》 | pgvector、持久向量、Eval 持久化；**框架迁移不替代三期**。 |
| 《整体规划》 | 终局能力不变；框架是 **实现手段** 之一。 |

**建议阅读顺序**：若尚未跑通主链路，先按《JD对齐学习路径》阶段 A～B；JD 明确写 LangChain 时，再打开本文从 **§4 模块对照** + **阶段 0** 动手。

---

## 2. 目标与边界

### 2.1 重构完成后应能写进简历的表述（示例）

- 「对话与 RAG 检索链路基于 **LangChain LCEL**（`Runnable` 串联 LLM、自定义 **Retriever**、**StructuredTool**），业务侧保留 **FastAPI + 自研 Trace/配额/热配置**。」
- 「**自定义 Retriever**：封装现有 LTM 混合检索（向量 + BM25），与 **LangChain** `invoke` 生命周期一致。」

### 2.2 建议保留为自研（不要强行塞进 LC）

| 模块 | 理由 |
|------|------|
| `TraceRecord` / `FileTraceStore` | 与现有 API、前端 Trace 页强耦合；用 **Callback / 中间件** 往 Trace 写即可。 |
| 配额、QPS、`hot_config` | 与 LC 无关，继续在 `prepare_chat_until_llm` 前后硬控。 |
| 隐式 LTM 抽取、`ltm_extract_async` | 独立 LLM 调用与队列；可单独用 `ChatOpenAI` 一条链，不必并进主 Agent。 |
| `POST /admin/*`、合规导出 | 纯 HTTP，不动。 |

### 2.3 框架选型

| 方案 | 适用 |
|------|------|
| **LangChain**（本文默认） | JD 出现频率最高；Agent、Tool、LCEL 叙事统一。 |
| **LlamaIndex** | 若以「海量文档索引 + 查询引擎」为主可并行引入；**本仓库当前是记忆条 RAG**，可二期再评估。 |
| **Haystack** | 偏搜索/NLP 团队栈；与现有代码重叠大，**不推荐**作为第一迁移目标。 |

**版本建议**：以 **`langchain-core` + `langchain-openai`（或社区版 chat 模型）** 为主，跟紧官方 **0.3.x / 1.x** 文档；在 `requirements.txt` **锁次要版本**，避免 CI 被动升级炸 API。

---

## 3. 总体架构（迁移后）

```
请求 → FastAPI /chat
     → [自研] 鉴权、配额、情绪、策略、STM 加载、安全扫描
     → [LangChain] RAG 子链：Retriever → prompt 模板 → ChatModel →（可选）Tool 循环
     → [自研] 输出脱敏、写 STM、Trace 落盘、隐式 LTM 调度
```

- **LangChain 只负责「从检索上下文到模型输出（+可选工具）」这一段**；入口出口仍是你熟悉的 Python。

---

## 4. 模块对照表（实施前先定位代码）

| 当前位置（示意） | LangChain 侧落点 |
|------------------|------------------|
| `app/llm/client.py` | `ChatOpenAI` 或 `BaseChatModel` 包装 |
| `app/rag/retriever.py` + `query_rewrite.py` | `BaseRetriever` + `Runnable` 前置改写 |
| `app/services/chat_turn.py`（RAG 块注入段） | LCEL 链 + 与 STM 合并的 prompt 构建 |
| `app/tools/*` | `StructuredTool` |
| `app/policy/decide_mode` | 链外仍先决策；Agent 内仅执行允许的工具 |

---

## 5. 分阶段路线图（推荐顺序）

### 阶段 0：基建与开关（0.5～1 天）

| 任务 | 验收 |
|------|------|
| 增加依赖：`langchain-core`、`langchain-openai`（或与现有 OpenAI 兼容基座一致） | `pip install` 无冲突 |
| ~~双轨开关~~（已删除） | 主链固定 LangChain；见根 `README` §LangChain |
| 文档：本指南 + README | 新人知架构边界（主链 LC / 辅助 httpx） |

### 阶段 1：封装「模型调用」为 LangChain ChatModel（1～2 天）

| 任务 | 说明 |
|------|------|
| 用 **`ChatOpenAI`**（`base_url`/`api_key`/`model` 读现有 `settings`）或直接 **自定义 `BaseChatModel`** 内部调用现有 `LLMClient` | 流式 `/chat/stream` 需实现 `astream` 或与 LC 流式 API 对齐 |
| 单测：mock 主链 ChatModel + httpx 辅助 LLM，结构稳定 | 防止静默换行为 |

**JD 关键词**：`ChatModel`、`LCEL` 前置。

### 阶段 2：自定义 Retriever，对接现有 `ltm_retriever`（2～4 天）

| 任务 | 说明 |
|------|------|
| 实现继承 **`BaseRetriever`** 的类，内部调用 `ltm_retriever.retrieve(...)` | `get_relevant_documents` 返回 `Document(page_content=..., metadata={id,type,score})` |
| 将现有 **query 改写** 接到链前：`RunnableLambda` 或独立 step | 与现网 `rag_rewrite_*` 行为一致 |
| 单测：固定 user/query，**Hit 的 id 列表** 与 `ltm_retriever.retrieve` 一致 | 检索回归（`test_langchain_rag.py`） |

**JD 关键词**：`Retriever`、`RAG`、`Document`。

### 阶段 3：RAG 链（LCEL）替换 prompt 拼装（2～3 天）

| 任务 | 说明 |
|------|------|
| 用 **`ChatPromptTemplate`** + **`StrOutputParser`**（或直接 message list）组装 system + STM 摘要 + 检索块 | 与当前 `prepare_chat_until_llm` 里注入 RAG 块的格式对齐 |
| 链形态示例：`retriever | format_docs | prompt | llm`（按你实际变量名调整） | 可读、可单测 |
| Trace：用 **`langchain.callbacks`** 或包装 Runnable，把 **检索片段 id、改写 query** 写入现有 `TraceStep` | 可观测不丢 |

**JD 关键词**：`LCEL`、`Runnable`、`PromptTemplate`。

### 阶段 4：工具（Tools）与可选 Agent（3～5 天）

| 任务 | 说明 |
|------|------|
| 把现有 `execute_tool` 封装为 **`StructuredTool`**，参数用 Pydantic | 与现网工具名、超时一致 |
| **优先**：`bind_tools` + **单次/有限次**工具调用（与你现有「模式决定工具」一致），避免 LC Agent 默认循环失控 | 保留 `tool_retry_times` 等护栏 |
| 若上 **Agent**：显式 **`max_iterations`** / 自定义 stop，对齐现有安全策略 | 与 `decide_mode` 的优先级写进文档 |

**JD 关键词**：`Tool calling`、`Agent`（谨慎表述「受控 Agent」）。

### 阶段 5：记忆与历史（可选，工作量大）

| 任务 | 说明 |
|------|------|
| STM → **`BaseChatMessageHistory`** 适配器，底层仍调 `session_store` | 多会话、Redis 逻辑不变 |
| **不建议** 用 LC 的「向量记忆」替代你已有 LTM；LTM 仍以自研 CRUD + Retriever 为准 | 避免双写 |

### 阶段 6：清理与默认切换（1～2 天）

| 任务 | 说明 |
|------|------|
| ~~灰度 legacy~~（已完成：legacy 已删） | 单一真相路径 |
| 删除重复 prompt 字符串与死代码 | 减维护面（持续） |
| 更新《整体规划》/简历项目描述截图 | 投递材料一致 |

---

## 6. 测试与回归策略

1. **契约测试**：对同一组 `ChatRequest` fixture，断言 **citations 的 id 集合**、**tool_summary** 结构稳定（允许文案微小差异可配置）。  
2. **Trace**：保留 `llm_call`、`retrieve_ltm`、`memory_hits` 等等价信息。  
3. **流式**：对比首包延迟、完整拼接文本 hash（mock LLM）。  
4. **pytest**：`tests/conftest.py` **autouse mock 主链 ChatModel**；辅助 LLM 仍 patch **`routes._build_llm_client`**。

---

## 7. 风险与应对

| 风险 | 应对 |
|------|------|
| LangChain 版本升级改 API | 锁版本；升级单独 PR + 对照官方 migration 文档 |
| 异步与 Starlette 事件循环 | 优先 **`ainvoke` / `astream`**；避免在 sync 链里阻塞 |
| observability 变弱 | 强制 Callback → 映射到现有 Trace |
| bundle/依赖变重 | 只引子包，避免 `langchain` 全家桶通配 |

---

## 8. 验收清单（整项重构完成时）

- [x] 默认路径可走通 `/chat` 与 `/chat/stream`（`tests/test_langchain_chat_orchestrator.py` + `conftest` autouse mock）。  
- [x] README 标明 LangChain 子包版本区间与 **唯一主链** 说明（无编排开关）。  
- [x] 单测覆盖：`test_langchain_rag.py`（Retriever+LCEL）、`test_langchain_chat_orchestrator.py`、`test_llm_trace_callback.py`。  
- [x] Trace：`/trace/{id}` 回放能力保持（既有用例 + `llm_call` 断言）。  
- [x] **legacy 双轨已删除**：无 `chat_orchestrator` / `CHAT_ORCHESTRATOR`；`GET /health` 仅 **`ltm_extract_enabled`** 与中间件探活。  
- [ ] 隐式 LTM、运营热配、撤销 extract **行为一致**（持续依赖 `test_v11_ltm_extract_*` 与手工清单）。**进展**：`tests/orchestrator_mocks.py` 的 **`patch_llm_client`** + **`FakeLCMainChatModel`**（含 **`_astream`**）。

---

## 9. 简历 / 面试话术（诚实版）

- 「**主对话编排**为 **LangChain LCEL**；**Trace、配额、热配** 与 **情绪/隐式 LTM 抽取** 仍自研（httpx），避免把运营与成本敏感逻辑绑进 Agent 默认循环。」  
- 「**Retriever 自研封装**，底层仍是现有混合检索，不是简单换库；后续向量进 **pgvector** 时只需替换向量后端，链式接口可不变。」

---

*文档版本：v2 — 结构重排，内容与 v1 等价；实施时请以当时 LangChain 官方文档为准校准 API 名称。*

**实施备忘（与本仓库同步）**：主链固定 **`ChatPromptTemplate | ChatModel | StrOutputParser`**（`app/langchain/main_chain.py`）；RAG 为 **`app/langchain/rag_lcel.py`**；Trace/SSE 供应商 id 由 **`LlmProviderIdCallback.on_llm_end`**（`app/langchain/llm_trace_callback.py`）。**`extract_provider_request_id`** 见 **`tests/test_llm_trace_callback.py`**。单测：**`tests/conftest.py` autouse** mock **`build_chat_openai_from_settings`** → **`FakeLCMainChatModel`**；**`patch_llm_client`** 仅换 **`routes._build_llm_client`**（情绪/隐式抽取）。**`GET /health`** 含 **`ltm_extract_enabled`** 与 redis/database 探活。
