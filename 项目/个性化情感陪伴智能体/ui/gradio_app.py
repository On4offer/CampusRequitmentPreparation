"""
Day6：Gradio 最小可演示 UI。

布局：左侧对话区（Chatbot + 输入）；右侧诊断面板（emotion、mode、trace_id、latency、token、trace JSON）。
需先启动后端：python -m uvicorn app.main:app --host 127.0.0.1 --port 8076
启动 UI：python -m ui.gradio_app  或  gradio ui/gradio_app.py（API 地址见下方 API_BASE）
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING

import gradio as gr
import httpx

# 后端 API 根地址（与常用命令.md 中端口一致）
API_BASE = "http://127.0.0.1:8076"

if TYPE_CHECKING:
    from typing import Any


def _post(path: str, body: dict) -> dict:
    with httpx.Client(timeout=60.0) as c:
        r = c.post(f"{API_BASE}{path}", json=body)
        r.raise_for_status()
        return r.json()


def _get(path: str) -> dict:
    with httpx.Client(timeout=10.0) as c:
        r = c.get(f"{API_BASE}{path}")
        r.raise_for_status()
        return r.json()


def _msg(role: str, content: str) -> dict:
    """Gradio Chatbot 要求每条为 {role, content}。"""
    return {"role": role, "content": content}


def chat_turn(
    message: str,
    history: list[dict],
    user_id: str,
    session_id: str,
) -> tuple[list[dict], str, str]:
    """发送一条消息，调用 /chat，再拉取 trace 更新诊断面板。"""
    if not (message or "").strip():
        return history, "", ""

    user_id = (user_id or "").strip() or "default"
    session_id = (session_id or "").strip() or "default"

    try:
        body = _post("/chat", {"message": message.strip(), "user_id": user_id, "session_id": session_id})
    except Exception as e:
        return history + [_msg("user", message), _msg("assistant", f"请求失败：{e}")], "", ""

    reply = body.get("reply", "")
    trace_id = body.get("trace_id", "")
    history = history + [_msg("user", message), _msg("assistant", reply)]

    diagnosis_lines = [
        f"**trace_id**：`{trace_id}`",
        f"**user_id**：{body.get('user_id', '')}",
        f"**session_id**：{body.get('session_id', '')}",
    ]
    citations = body.get("citations") or []
    diagnosis_lines.append(f"**命中记忆数**：{len(citations)}")
    if citations:
        diagnosis_lines.append("**citations**：")
        for c in citations[:5]:
            diagnosis_lines.append(
                "- id=`{}` type=`{}` score={}".format(
                    c.get("id", "-"),
                    c.get("type", "-"),
                    c.get("score", "-"),
                )
            )
    trace_json_str = ""

    if trace_id:
        try:
            t = _get(f"/trace/{trace_id}")
            decision = t.get("decision") or {}
            metrics = t.get("metrics") or {}
            emotion = decision.get("emotion") or {}
            msg_preview = (t.get("message") or "")[:80]
            if len((t.get("message") or "")) > 80:
                msg_preview += "…"
            diagnosis_lines.extend([
                "",
                "**本轮消息**：{}".format(msg_preview or "-"),
                "",
                "**情绪**：{} (强度 {})".format(emotion.get("label", "-"), emotion.get("intensity", "-")),
                "**风险**：{}".format(emotion.get("risk_tier", "-")),
                "**模式**：{}".format(decision.get("mode", "-")),
                "**原因**：{}".format(decision.get("mode_reason", "-")),
                "**安全模式**：{}".format(decision.get("safety_mode", False)),
                "",
                "**耗时**：{} ms".format(metrics.get("latency_ms", "-")),
                "**token**：in {} / out {}".format(metrics.get("token_in", "-"), metrics.get("token_out", "-")),
            ])
            trace_json_str = json.dumps(t, ensure_ascii=False, indent=2)
        except Exception as e:
            diagnosis_lines.append(f"\n拉取 trace 失败：{e}")

    diagnosis_md = "\n".join(diagnosis_lines)
    return history, diagnosis_md, trace_json_str


def reset_session(user_id: str, session_id: str) -> tuple[str, str]:
    """清空该会话的短期记忆，并清空诊断与 trace 展示。"""
    user_id = (user_id or "").strip() or "default"
    session_id = (session_id or "").strip() or "default"
    try:
        _post("/sessions/reset", {"user_id": user_id, "session_id": session_id})
    except Exception as e:
        return f"重置失败：{e}", ""
    return "会话已重置，可继续对话。", ""


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="情感陪伴智能体") as demo:
        gr.Markdown("# 情感陪伴智能体 · 聊天 + 诊断")

        with gr.Row():
            with gr.Column(scale=2):
                chatbot = gr.Chatbot(label="对话", height=400)
                msg = gr.Textbox(
                    label="输入消息",
                    placeholder="输入后回车或点击发送",
                    lines=2,
                )
                with gr.Row():
                    submit_btn = gr.Button("发送", variant="primary")
                    clear_btn = gr.Button("清空对话")

            with gr.Column(scale=1):
                gr.Markdown("### 本轮诊断")
                user_id_in = gr.Textbox(label="user_id", value="u1", placeholder="留空为 default")
                session_id_in = gr.Textbox(label="session_id", value="s1", placeholder="留空为 default")
                reset_btn = gr.Button("重置会话（清空记忆）")
                diagnosis_md = gr.Markdown("发送一条消息后此处显示 emotion / mode / trace_id / 耗时 / token")
                trace_json = gr.Code(label="Trace JSON", language="json", lines=12, interactive=False)

        def submit(user_msg: str, hist: list, uid: str, sid: str):
            new_hist, diag, trace = chat_turn(user_msg, hist, uid, sid)
            return new_hist, "", diag, trace

        def clear_chat():
            return [], "", "", ""

        msg.submit(submit, [msg, chatbot, user_id_in, session_id_in], [chatbot, msg, diagnosis_md, trace_json])
        submit_btn.click(submit, [msg, chatbot, user_id_in, session_id_in], [chatbot, msg, diagnosis_md, trace_json])
        clear_btn.click(clear_chat, outputs=[chatbot, msg, diagnosis_md, trace_json])
        reset_btn.click(
            reset_session,
            [user_id_in, session_id_in],
            [diagnosis_md, trace_json],
        )

        gr.Markdown("---\n后端需已启动：`python -m uvicorn app.main:app --host 127.0.0.1 --port 8076`")

    return demo


def main() -> None:
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860, theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
