"""
Day6：Gradio 最小可演示 UI。

布局：
- **对话**：左侧 Chatbot + 输入；右侧诊断（emotion、mode、trace、token）。
- **运营台**：热参数表单、配额快照、最近反馈、风险事件（依赖后端 /admin/* 与文件 Trace）。

需先启动后端：python -m uvicorn app.main:app --host 127.0.0.1 --port 8076
启动 UI：python -m ui.gradio_app  （API 地址见 API_BASE）
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


def _admin_headers(admin_token: str) -> dict[str, str]:
    t = (admin_token or "").strip()
    return {"X-Admin-Token": t} if t else {}


def _post(path: str, body: dict, headers: dict[str, str] | None = None) -> dict:
    with httpx.Client(timeout=60.0) as c:
        r = c.post(f"{API_BASE}{path}", json=body, headers=headers or {})
        r.raise_for_status()
        return r.json()


def _get(path: str, params: dict | None = None, headers: dict[str, str] | None = None) -> dict:
    with httpx.Client(timeout=30.0) as c:
        r = c.get(f"{API_BASE}{path}", params=params or {}, headers=headers or {})
        r.raise_for_status()
        return r.json()


def _patch(path: str, body: dict, headers: dict[str, str] | None = None) -> dict:
    with httpx.Client(timeout=20.0) as c:
        r = c.patch(f"{API_BASE}{path}", json=body, headers=headers or {})
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
    tool_summary = body.get("tool_summary") or {}
    if tool_summary:
        diagnosis_lines.append("**工具调用**：{} | 状态={} | 耗时={}ms".format(
            tool_summary.get("tool", "-"),
            tool_summary.get("status", "-"),
            tool_summary.get("elapsed_ms", "-"),
        ))
        if tool_summary.get("error"):
            diagnosis_lines.append("  - 错误：{}".format(tool_summary["error"]))
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
            t = _get(f"/trace/{trace_id}", params={"user_id": user_id})
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


def ops_refresh(admin_token: str, quota_user_id: str) -> tuple:
    """拉取运营台数据并刷新表单默认值。"""
    h = _admin_headers(admin_token)
    err = ""
    cfg: dict = {}
    quota: dict = {}
    risk: dict = {}
    fb: dict = {}

    try:
        cfg = _get("/admin/config", headers=h)
    except Exception as e:
        err = f"**接口错误**（配置）：`{e}`\n\n"

    quid = (quota_user_id or "").strip() or None
    try:
        quota = _get("/admin/quota", params={"user_id": quid}, headers=h)
    except Exception as e:
        err += f"**接口错误**（配额）：`{e}`\n\n"
        quota = {}

    try:
        risk = _get("/admin/risk_events", params={"limit": 30, "scan_lines": 600}, headers=h)
    except Exception as e:
        err += f"**接口错误**（风险）：`{e}`\n\n"
        risk = {"items": [], "note": str(e), "count": 0}

    try:
        fb = _get("/feedback/recent", params={"limit": 25})
    except Exception as e:
        err += f"**接口错误**（反馈）：`{e}`\n\n"
        fb = {"items": []}

    quota_md = err + (
        f"### 配额快照\n"
        f"- **user_id**：`{quota.get('user_id', '-')}`\n"
        f"- **quota_enabled**：{quota.get('quota_enabled', '-')}\n"
        f"- **used_today**（字符近似）：{quota.get('used_today', '-')}\n"
        f"- **limit_per_day**：{quota.get('limit_per_day', '-')}\n"
        f"- **qps_per_user**：{quota.get('qps_per_user', '-')}\n"
    )

    fb_lines = ["### 最近反馈"]
    for it in fb.get("items") or []:
        tid = str(it.get("trace_id", ""))[:10]
        cor = it.get("correction")
        extra = f" · 纠错 `{cor[:40]}…`" if cor and len(str(cor)) > 40 else (f" · 纠错 `{cor}`" if cor else "")
        fb_lines.append(
            f"- `{tid}…` · **{it.get('rating', '-')}** · user=`{it.get('user_id', '-')}`{extra}"
        )
    if len(fb_lines) == 1:
        fb_lines.append("_暂无_")
    fb_md = "\n".join(fb_lines)

    risk_lines = [
        "### 风险 / 安全事件",
        f"_说明：{risk.get('note', '-')} · storage=`{risk.get('storage', '-')}` · count={risk.get('count', 0)}_\n",
    ]
    for it in risk.get("items") or []:
        tid = str(it.get("trace_id", ""))[:10]
        risk_lines.append(
            f"- `{tid}…` · user=`{it.get('user_id', '-')}` · safety_mode={it.get('safety_mode')} · "
            f"{(it.get('reason') or '')[:100]}"
        )
    if not risk.get("items"):
        risk_lines.append("_（无匹配记录，或当前为内存 Trace 存储）_")
    risk_md = "\n".join(risk_lines)

    config_md = "### 当前热配置（只读 JSON）\n```json\n"
    try:
        config_md += json.dumps(cfg, ensure_ascii=False, indent=2) if cfg else "{}"
    except Exception:
        config_md += "{}"
    config_md += "\n```"

    def gv(key: str, default):
        return cfg.get(key, default)

    return (
        quota_md,
        fb_md,
        risk_md,
        config_md,
        gr.update(value=bool(gv("rag_enabled", False))),
        gr.update(value=int(gv("rag_top_k", 3))),
        gr.update(value=bool(gv("rag_rewrite_enabled", False))),
        gr.update(value=bool(gv("tool_enabled", False))),
        gr.update(value=bool(gv("quota_enabled", False))),
        gr.update(value=int(gv("quota_token_per_user_per_day", 0))),
        gr.update(value=float(gv("quota_qps_per_user", 0.0))),
        gr.update(value=int(gv("stm_max_chars", 6000))),
        gr.update(value=bool(gv("content_safety_enabled", True))),
        gr.update(value=bool(gv("content_safety_filter_output", True))),
        gr.update(value=bool(gv("feedback_enabled", True))),
        gr.update(value=bool(gv("ltm_extract_enabled", False))),
        gr.update(value=int(gv("ltm_extract_every_n_turns", 0))),
        gr.update(value=bool(gv("ltm_extract_dedup_enabled", True))),
        gr.update(value=bool(gv("ltm_extract_count_toward_quota", True))),
        gr.update(value=bool(gv("ltm_extract_async", False))),
    )


def ops_apply(
    admin_token: str,
    quota_user_id: str,
    rag_enabled: bool,
    rag_top_k: float,
    rag_rewrite_enabled: bool,
    tool_enabled: bool,
    quota_enabled: bool,
    quota_token_per_user_per_day: float,
    quota_qps_per_user: float,
    stm_max_chars: float,
    content_safety_enabled: bool,
    content_safety_filter_output: bool,
    feedback_enabled: bool,
    ltm_extract_enabled: bool,
    ltm_extract_every_n_turns: float,
    ltm_extract_dedup_enabled: bool,
    ltm_extract_count_toward_quota: bool,
    ltm_extract_async: bool,
) -> tuple:
    h = _admin_headers(admin_token)
    body = {
        "rag_enabled": rag_enabled,
        "rag_top_k": int(rag_top_k),
        "rag_rewrite_enabled": rag_rewrite_enabled,
        "tool_enabled": tool_enabled,
        "quota_enabled": quota_enabled,
        "quota_token_per_user_per_day": int(quota_token_per_user_per_day),
        "quota_qps_per_user": float(quota_qps_per_user),
        "stm_max_chars": int(stm_max_chars),
        "content_safety_enabled": content_safety_enabled,
        "content_safety_filter_output": content_safety_filter_output,
        "feedback_enabled": feedback_enabled,
        "ltm_extract_enabled": ltm_extract_enabled,
        "ltm_extract_every_n_turns": int(ltm_extract_every_n_turns),
        "ltm_extract_dedup_enabled": ltm_extract_dedup_enabled,
        "ltm_extract_count_toward_quota": ltm_extract_count_toward_quota,
        "ltm_extract_async": ltm_extract_async,
    }
    try:
        _patch("/admin/config", body, headers=h)
    except Exception as e:
        fail = (
            f"**应用失败**：`{e}`\n\n"
            "若后端配置了 `ADMIN_CONFIG_TOKEN`，请在上方填写 **管理 Token**。\n"
        )
        tup = ops_refresh(admin_token, quota_user_id)
        return (fail + tup[0],) + tup[1:]
    return ops_refresh(admin_token, quota_user_id)


def build_ui() -> gr.Blocks:
    with gr.Blocks(title="情感陪伴智能体") as demo:
        gr.Markdown("# 情感陪伴智能体 · 对话 + 运营台")

        with gr.Tabs():
            with gr.Tab("对话"):
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

            with gr.Tab("运营台"):
                gr.Markdown(
                    "从后端读取/写入 **热配置**（`data/hot_config.json`）。"
                    "若 `.env` 中设置了 `ADMIN_CONFIG_TOKEN`，须填写下方 **管理 Token**；"
                    "未设置时仅允许本机访问接口（Gradio 与 API 均为 127.0.0.1 时一般可直接用）。"
                )
                admin_token_in = gr.Textbox(
                    label="管理 Token（X-Admin-Token，可选）",
                    type="password",
                    placeholder="与 ADMIN_CONFIG_TOKEN 一致；未配置服务端 token 可留空",
                )
                quota_uid_in = gr.Textbox(label="配额查看 user_id", value="default", placeholder="查看该用户当日用量")
                refresh_btn = gr.Button("刷新运营数据", variant="secondary")
                apply_btn = gr.Button("应用下方热参数（PATCH /admin/config）", variant="primary")

                with gr.Row():
                    with gr.Column():
                        ops_quota_md = gr.Markdown("点击「刷新运营数据」")
                        ops_fb_md = gr.Markdown()
                    with gr.Column():
                        ops_risk_md = gr.Markdown()
                        ops_config_md = gr.Markdown()

                gr.Markdown("### 可调热参数（勾选/数字后点「应用」）")
                with gr.Row():
                    with gr.Column():
                        op_rag_en = gr.Checkbox(label="rag_enabled", value=False)
                        op_rag_topk = gr.Number(label="rag_top_k", value=3, precision=0)
                        op_rag_rw = gr.Checkbox(label="rag_rewrite_enabled", value=False)
                        op_tool = gr.Checkbox(label="tool_enabled", value=False)
                    with gr.Column():
                        op_q_en = gr.Checkbox(label="quota_enabled", value=False)
                        op_q_day = gr.Number(label="quota_token_per_user_per_day", value=0, precision=0)
                        op_q_qps = gr.Number(label="quota_qps_per_user", value=0.0)
                        op_stm = gr.Number(label="stm_max_chars", value=6000, precision=0)
                    with gr.Column():
                        op_cs_en = gr.Checkbox(label="content_safety_enabled", value=True)
                        op_cs_out = gr.Checkbox(label="content_safety_filter_output", value=True)
                        op_fb_en = gr.Checkbox(label="feedback_enabled", value=True)

                gr.Markdown(
                    "### 隐式 LTM（V1.1，与 Web `/ops`、PATCH /admin/config 一致）\n"
                    "`ltm_extract_every_n_turns=0` 表示不按 assistant 轮次触发；合法范围 0–20。"
                )
                with gr.Row():
                    op_ltm_en = gr.Checkbox(label="ltm_extract_enabled", value=False)
                    op_ltm_dedup = gr.Checkbox(label="ltm_extract_dedup_enabled", value=True)
                    op_ltm_quota = gr.Checkbox(label="ltm_extract_count_toward_quota", value=True)
                    op_ltm_n = gr.Number(label="ltm_extract_every_n_turns", value=0, precision=0)
                    op_ltm_async = gr.Checkbox(label="ltm_extract_async", value=False)

                refresh_outputs = [
                    ops_quota_md,
                    ops_fb_md,
                    ops_risk_md,
                    ops_config_md,
                    op_rag_en,
                    op_rag_topk,
                    op_rag_rw,
                    op_tool,
                    op_q_en,
                    op_q_day,
                    op_q_qps,
                    op_stm,
                    op_cs_en,
                    op_cs_out,
                    op_fb_en,
                    op_ltm_en,
                    op_ltm_n,
                    op_ltm_dedup,
                    op_ltm_quota,
                    op_ltm_async,
                ]
                refresh_btn.click(
                    ops_refresh,
                    [admin_token_in, quota_uid_in],
                    refresh_outputs,
                )
                apply_btn.click(
                    ops_apply,
                    [
                        admin_token_in,
                        quota_uid_in,
                        op_rag_en,
                        op_rag_topk,
                        op_rag_rw,
                        op_tool,
                        op_q_en,
                        op_q_day,
                        op_q_qps,
                        op_stm,
                        op_cs_en,
                        op_cs_out,
                        op_fb_en,
                        op_ltm_en,
                        op_ltm_n,
                        op_ltm_dedup,
                        op_ltm_quota,
                        op_ltm_async,
                    ],
                    refresh_outputs,
                )

        gr.Markdown("---\n后端需已启动：`python -m uvicorn app.main:app --host 127.0.0.1 --port 8076`")

    return demo


def main() -> None:
    demo = build_ui()
    demo.launch(server_name="127.0.0.1", server_port=7860, theme=gr.themes.Soft())


if __name__ == "__main__":
    main()
