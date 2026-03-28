# 个性化情感陪伴智能体

FastAPI 后端 +（二期）Vite/React 控制台：多轮对话、短期/长期记忆与 RAG、情绪与 Trace、运营与合规接口等。详细愿景与版本规划见 `#Personal_Documents/规划/`。

## 环境要求

- Python 3.11+（推荐 3.12）
- Node.js 18+（仅开发 Web 控制台时需要）

## 后端：首次 setup

在项目根目录：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

编辑 `.env`，至少填写 **`LLM_API_KEY`**（以及按需修改 `LLM_BASE_URL` / `LLM_MODEL`）。其它开关见 `.env.example` 内注释。

**三期可选中间件**：配置 **`REDIS_URL`** 会将会话短期记忆（STM）存到 Redis；配置 **`DATABASE_URL`**（如 `mysql+pymysql://...`）会将 LTM 写入关系库。留空则沿用内存实现。`GET /health` 中的 `redis` / `database` 字段可用来确认连通性（`skipped` | `ok` | `error`）。

启动 API（**端口与二期 Web 默认代理一致，推荐 8076**）：

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8076
```

- Swagger：`http://127.0.0.1:8076/docs`
- `GET /health` 返回 **`ltm_extract_enabled`**（与隐式 LTM 开关一致）及 redis/database 探活
- 未配置 `LLM_API_KEY` 时，`POST /chat` 会返回 500 并提示检查 `.env`

## 前端 Web 控制台（二期）

**须先启动后端**（同上，默认 `127.0.0.1:8076`）。

```powershell
cd web
npm install
npm run dev
```

浏览器访问终端提示的地址（一般为 `http://127.0.0.1:5173`）。开发环境下请求走 **`/api` → Vite 代理** 到后端，代理目标默认为 `http://127.0.0.1:8076`。

- 若后端端口不同：复制 `web/.env.example` 为 `web/.env`，设置 `VITE_DEV_API_TARGET=http://127.0.0.1:<端口>`
- **生产构建**：构建前设置 `VITE_API_BASE` 为后端根 URL（无尾斜杠），见 `web/.env.example`

## 测试（pytest）

**必须在已安装依赖的虚拟环境中执行**（`requirements.txt` 已包含 `pytest`）：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pytest -q
```

测试会 mock LLM，不发起真实外网请求。`tests/conftest.py` 会 **autouse mock `build_chat_openai_from_settings`**（主对话走 LangChain），并清空本地库 URL；情绪与隐式 LTM 抽取仍通过各用例对 **`routes._build_llm_client`** 的 monkeypatch 使用 FakeLLM。更多命令见 `#Personal_Documents/常用命令.md`。

### LangChain 主链路（唯一路径）

- **主回复**：`app/langchain/main_chain.py` 为 **`ChatPromptTemplate` → `ChatOpenAI`（兼容网关）→ `StrOutputParser`**，配置与 **`LLM_BASE_URL` / `LLM_API_KEY` / `LLM_MODEL`** 同源。
- **RAG**：`app/langchain/rag_lcel.py`（**`BaseRetriever` + LCEL**）；底层混合检索仍复用现有 LTM 索引逻辑。
- **工具（V3）**：`TOOL_ENABLED=true` 时时间/天气经 **`StructuredTool.invoke`**（`app/langchain/tools_lc.py`），内部仍为 **`execute_tool`**（超时/重试不变）；`decide_mode` 在链外选工具。
- **STM**：`SessionStoreChatMessageHistory`（`app/langchain/stm_history.py`）加载历史；**`session_store.append`** 写回，与 `trim_messages_by_char_budget` 语义一致。
- **非 LangChain**：情绪分析、隐式 LTM 抽取等仍用自研 **`LLMClient`（httpx）**，避免把辅助调用绑进主 Agent 循环。
- **配置**：`Settings` 使用 **`extra="ignore"`**；若本地 `.env` 仍留有已废弃的 **`CHAT_ORCHESTRATOR`** 等键，会被静默忽略，不影响启动。
- **依赖**：`requirements.txt` 锁定 **`langchain-core` / `langchain-openai`** 次要版本。**Trace / SSE**：供应商 **`request_id`** 由 **`LlmProviderIdCallback.on_llm_end`** 写入（`app/langchain/llm_trace_callback.py`）。
- **回归**：`tests/test_langchain_chat_orchestrator.py`、`tests/test_langchain_*.py`、`tests/orchestrator_mocks.py`。

## 其它入口

| 入口 | 说明 |
|------|------|
| `python -m ui.gradio_app` | Gradio 演示（需先起后端） |
| `#Personal_Documents/常用命令.md` | 端口、pytest、验证脚本、Gradio/Web 说明 |

## 可选：OpenAPI 与前端类型同步（P1-3）

后端运行时，可从 `GET /openapi.json` 拉取模式；使用 [openapi-typescript](https://github.com/drwpow/openapi-typescript) 等工具可生成 TypeScript 类型，减少与手写 `web/src/api/types.ts` 的漂移。示例：

```bash
npx openapi-typescript http://127.0.0.1:8076/openapi.json -o web/src/api/schema.d.ts
```

（需在本地已启动 uvicorn 后执行；生成文件是否纳入版本库由团队约定。）

## 仓库内文档索引

- `#Personal_Documents/规划/二期迭代规划.md` — 二期功能合同与验收
- `#Personal_Documents/规划/V1.2迭代规划.md` — 总体规划/JD 对齐、RAG 与向量形态说明、通向三期
- `#Personal_Documents/规划/框架化重构指南_LangChain向.md` — 若需对齐 JD「LangChain」：分阶段迁移与验收清单
- `#Personal_Documents/规划/JD对齐学习路径_项目驱动.md` — 用本项目系统覆盖 JD 技能：对照表 + 补学顺序 + 与规划文档索引
- `#Personal_Documents/规划/整体检查后迭代规划.md` — 质量与契约收口项
- `#Personal_Documents/常用命令.md` — 日常命令速查
