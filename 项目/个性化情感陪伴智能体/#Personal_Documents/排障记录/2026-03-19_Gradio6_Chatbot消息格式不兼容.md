# Gradio 6.x Chatbot 消息格式不兼容导致前端报错

日期：2026-03-19  
项目：个性化情感陪伴智能体（Gradio UI / Day6）

---

## 1. 现象（Symptoms）

- 启动 Gradio UI（`python -m ui.gradio_app`）后，在页面发送一条消息，前端报错：
- 控制台 Traceback 中出现：
  ```
  gradio.exceptions.Error: "Data incompatible with messages format. Each message should be a dictionary with 'role' and 'content' keys or a ChatMessage object."
  ```
- 同时可能看到警告：`The parameters have been moved from the Blocks constructor to the launch() method in Gradio 6.0: theme.`

---

## 2. 影响（Impact）

- 对话区无法正常展示历史消息，发送后界面报错，无法完成「多轮对话 → 诊断面板」的演示流程。

---

## 3. 根因（Root Cause）

Gradio 在 6.0 版本对 **Chatbot** 组件的**消息格式**做了变更：

- **旧格式**（Gradio 4.x/5.x）：`history` 为「二元组列表」`[[user_msg, bot_msg], [user_msg, bot_msg], ...]`。
- **新格式**（Gradio 6.x）：`history` 为「消息对象列表」，每条必须为 `{"role": "user"|"assistant", "content": "..."}` 或等价的 ChatMessage 对象。

项目中原先按旧格式传入 `history + [[message, reply]]`，在新版中被判定为不合法，触发 `Data incompatible with messages format`。

此外，Gradio 6.0 将 `theme` 等参数从 `gr.Blocks(...)` 移到了 `demo.launch(...)`，故在 Blocks 构造里写 `theme=gr.themes.Soft()` 会触发弃用警告。

---

## 4. 解决方案（Solution）

1. **统一使用新消息格式**
   - 定义辅助函数，例如：`_msg(role, content)` 返回 `{"role": role, "content": content}`。
   - 在 `chat_turn` 中，不再使用 `history + [[message, reply]]`，改为：
     - 成功：`history + [_msg("user", message), _msg("assistant", reply)]`
     - 失败：`history + [_msg("user", message), _msg("assistant", "请求失败：...")]`
   - 清空对话时仍返回 `[]`（空消息列表）。

2. **Theme 警告**
   - 将 `theme=gr.themes.Soft()` 从 `gr.Blocks(title="...", theme=...)` 中移除，改为在 `demo.launch(..., theme=gr.themes.Soft())` 中传入。

修改文件：`ui/gradio_app.py`。

---

## 5. 预防 / 参考

- 使用 Gradio Chatbot 时，优先查阅当前版本的 [Gradio Chatbot 文档](https://www.gradio.app/docs/chatbot)，确认 `value` / 历史消息的合法结构。
- 若从旧版 Gradio 升级到 6.x，需检查所有向 Chatbot 传入的列表格式，并改为 `{role, content}` 消息列表。
