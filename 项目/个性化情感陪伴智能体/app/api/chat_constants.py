"""与 /chat 主链路共享的常量（避免 routes 与 chat_turn 循环引用）。"""

SAFE_SYSTEM_PROMPT = (
    "你处于安全模式。用户可能表达了自伤或他伤相关想法。"
    "你必须：表达关心、建议联系现实中的亲友或专业心理/医疗支持，不要追问细节，不要给出任何可能加重风险的建议。"
    "回复简短、温和、明确导向寻求专业帮助。"
)

DEFAULT_QUOTA_DEGRADE_HINT = "（省流模式：请用约120字内简明回答。）"

# RAG / 工具注入 system 的固定标题（与 rag_lcel 注释一致）
LTM_RAG_EVIDENCE_HEADER = "\n\n【以下是与用户相关的长期记忆，请参考】\n"
TOOL_RESULT_SYSTEM_SUFFIX_HEADER = "\n\n【工具调用结果，请基于此回复用户】\n"
