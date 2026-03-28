"""Map vendor-specific LLM errors to clearer client-facing messages (Chinese)."""


def llm_error_detail_for_client(exc: BaseException) -> str:
    raw = str(exc)
    if "unsupported_country_region_territory" in raw or "Country, region, or territory not supported" in raw:
        return (
            "当前网络环境无法使用 OpenAI 官方接口（403：地区不支持）。"
            "请在项目根 .env 将 LLM_BASE_URL 改为可用的 OpenAI 兼容网关（如 DeepSeek、通义、SiliconFlow 等），"
            "并同步设置对应的 LLM_API_KEY 与 LLM_MODEL。"
            f" 原始信息：{raw}"
        )
    return raw
