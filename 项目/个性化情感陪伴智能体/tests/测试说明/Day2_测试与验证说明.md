# Day2 测试与验证说明（Session + STM + Reset）

本项目 Day2 已加入两种验证方式：
- **pytest 单元/接口测试**：不调用真实大模型（mock LLM），可快速回归、0 成本
- **verify 脚本**：调用你本地正在跑的服务（会触发真实 LLM 调用），用于端到端验证

---

## 1) pytest 测试：怎么运行、验证什么、预期效果

### 1.1 前置条件
在项目根目录，确保你使用项目虚拟环境（`.venv`）：

```powershell
.\.venv\Scripts\Activate.ps1
```

安装依赖（包含 pytest）：

```powershell
python -m pip install -r requirements.txt
```

### 1.2 运行命令

```powershell
python -m pytest -q
```

#### 1.2.1 输出中间状态（STM/history 拼接，便于观察）

默认 pytest 会捕获 stdout，且测试不会打印中间状态。若你想观察每次 LLM 调用的 messages（system/history/new user），用下面方式开启：

```powershell
$env:DAY2_TEST_DEBUG=1
python -m pytest -q -s
```

- `DAY2_TEST_DEBUG=1`：开启测试内的调试打印
- `-s`：关闭 pytest 对 stdout 的捕获，让 `print()` 直接显示

你会看到类似输出（示意；当前主对话走 LangChain，**仅情绪分析**会打印到 `fake.calls`）：

```text
[emotion2] messages=...
  00 system: ...情绪识别助手...
  01 user: 你还记得我刚说了什么吗？
```

### 1.3 预期输出
正常情况下应看到类似：

```text
... [100%]
3 passed in <1s
```

### 1.4 这些测试在验证什么
测试文件：`tests/test_day2_sessions.py`

- **test_session_memory_appends_history**
  - 验证同一 `user_id + session_id` 第二轮对话后，**STM**（`GET /sessions/{id}/messages`）含上一轮 user/assistant；主回复为 conftest 固定 mock 文案

- **test_session_isolation**
  - 验证不同 `session_id` 的历史严格隔离（`s1` 不泄漏到 `s2`）

- **test_session_reset_clears_history**
  - 验证 `POST /sessions/reset` 后 STM 不含 reset 前用户句

### 1.5 为什么 pytest 不会消耗 DeepSeek 费用？
测试里 **autouse mock 主链 `ChatOpenAI`**，并替换 **`routes._build_llm_client`**（情绪等），不会发生网络请求。
因此：
- 不依赖 API Key
- 不依赖网络
- 不消耗 token/余额
- 可在 CI/本地随时跑回归

---

## 2) verify 脚本：怎么运行、预期效果

脚本文件：`scripts/verify_day2.py`

### 2.1 前置条件
你需要先把服务跑起来（例如端口 8077）：

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8077
```

并确保 `.env` 已配置好大模型（DeepSeek）相关参数：
- `LLM_BASE_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

### 2.2 运行命令

```powershell
python .\scripts\verify_day2.py http://127.0.0.1:8077
```

（如果你没传 base URL，默认会用 `http://127.0.0.1:8077`）

### 2.3 脚本做了什么
它会按顺序调用：
- `POST /chat`（u1/s1）：“我叫小明，请记住我。”
- `POST /chat`（u1/s1）：“我叫什么？”
- `POST /chat`（u1/s2）：“我叫什么？”（验证隔离）
- `POST /sessions/reset`（u1/s1）
- `POST /chat`（u1/s1）：“我叫什么？”（验证 reset）

### 2.4 预期输出长什么样
控制台会打印类似：

```text
Base: http://127.0.0.1:8077
s1 turn2 reply: ...
s2 reply: ...
reset: {'ok': True, 'existed': True}
s1 after reset reply: ...
Done.
```

### 2.5 如何判断“通过/不通过”
- **隔离是否通过**：`s2 reply` 不应表现出对 `s1` 的记忆（例如不应直接回答“小明”）
- **reset 是否通过**：`reset.existed` 应为 True，且 `s1 after reset reply` 不应复用 reset 前的历史

> 注意：verify 脚本走真实 LLM，输出会有随机性；你应关注“是否明显带入了不该带入的历史”。

---

## 3) 推荐用法（开发节奏）

- **日常改代码**：先跑 `python -m pytest -q`（快、稳定、0 成本）
- **准备演示/联调**：再跑 `verify_day2.py`（端到端、真实效果）

