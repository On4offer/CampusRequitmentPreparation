# PyCharm 一键运行未加载 `.env`，导致 `Missing LLM_API_KEY`

日期：2026-03-18  
项目：个性化情感陪伴智能体（FastAPI/uvicorn + DeepSeek）

---

## 1. 现象（Symptoms）

在浏览器 `http://127.0.0.1:<port>/docs` 中调用 `POST /chat`，返回：

- HTTP 500
- Response body：

```json
{
  "detail": "Missing LLM_API_KEY. Create a .env file (see .env.example)."
}
```

但项目根目录 `.env` 中已经配置了：
- `LLM_BASE_URL=https://api.deepseek.com`
- `LLM_API_KEY=sk-...`
- `LLM_MODEL=deepseek-chat`

并且在命令行启动时可以正常读取与调用（`/chat` 返回 200）。

---

## 2. 影响（Impact）

- 无法在 PyCharm “一键运行”模式下调通大模型调用
- 误以为 API Key 无效或代码逻辑有问题，浪费排查时间

---

## 3. 根因（Root Cause）

PyCharm 的 Run Configuration 未显式加载项目根目录 `.env`（配置项 “`.env 文件路径`” 为空），导致运行时环境未注入 `LLM_API_KEY`。

虽然代码侧使用 `pydantic-settings` 读取 `.env`，但 IDE 启动的工作目录/进程环境与命令行不同，可能出现：
- `.env` 未被读取
- 或读取到的并非目标项目根目录的 `.env`

最终表现为 `settings.llm_api_key == ""`，触发服务端在构建 LLMClient 时抛出 `Missing LLM_API_KEY`。

---

## 4. 复现步骤（Repro）

1. 在项目根目录已存在 `.env`，填好 `LLM_API_KEY`
2. 使用 PyCharm Run Configuration 启动服务，但不填写 “`.env 文件路径`”
3. 打开 `/docs` 调用 `POST /chat`
4. 观察到 500 与 `Missing LLM_API_KEY`

---

## 5. 解决方案（Fix）

在 PyCharm：

1. `Run → Edit Configurations...`
2. 选择用于启动服务的配置（例如 `fast2`）
3. 在 “`.env 文件路径`” 处填入项目根目录 `.env` 的绝对路径，例如：

```text
D:\Users\hzr08\Desktop\研二下\校招学习\项目\个性化情感陪伴智能体\.env
```

4. Stop 服务 → 重新 Run
5. 再次在 `/docs` 调用 `POST /chat`，应返回 200（含 `reply`、`trace_id`）

---

## 6. 验证方法（Verify）

### 6.1 快速验证（推荐）
- `/docs` → `POST /chat` → 传入：

```json
{ "message": "你好" }
```

预期：200 OK，响应包含 `reply`。

### 6.2 程序验证（命令行）
在项目根目录执行：

```powershell
python -c "from app.core.settings import settings; print(len(settings.llm_api_key or ''))"
```

预期：输出大于 0。

---

## 7. 预防建议（Prevention）

- 新建 PyCharm Run Configuration 时，将 “`.env 文件路径`” 作为必填项
- 避免多个项目/多个工作目录同时运行，导致读取到错误 `.env`
- `.env` 不要提交到 Git（使用 `.env.example` 作为模板）

