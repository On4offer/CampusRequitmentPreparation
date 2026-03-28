from __future__ import annotations

"""
配置管理（Settings）。

使用 pydantic-settings 从环境变量与 `.env` 加载配置。
关键点：
- `.env` 使用“绝对路径”定位，避免 IDE/工作目录差异导致读取失败
- 所有可调参数集中管理，便于后续做“运营配置台/灰度参数”
"""

# 项目根目录（项目根目录下的所有文件路径都是相对于项目根目录的）
# pathlib.Path 是 Python 标准库中的路径操作类，用于处理文件路径。
# 作用：提供跨平台的文件路径操作方法，避免手动拼接路径时的平台差异问题。
from pathlib import Path

# pydantic_settings 是 pydantic 库中的一个插件，用于从环境变量与 `.env` 文件加载配置。
# 作用：简化配置管理，将配置参数定义为类属性，自动从环境变量与 `.env` 文件中加载值。
from pydantic_settings import BaseSettings, SettingsConfigDict


# _PROJECT_ROOT 是项目根目录的路径。
# 作用：项目根目录下的所有文件路径都是相对于项目根目录的，使用该变量可以方便地定位项目中的其他文件。
# Path(__file__).resolve().parents[2] 表示当前文件（settings.py）的上两级目录，即项目根目录。
# __file__ 是当前正在执行的 Python 文件的路径。
# resolve() 方法用于获取绝对路径，确保路径是唯一的，避免路径差异导致的读取失败。
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
# _DEFAULT_ENV_FILE 是默认的环境变量配置文件路径。
# 作用：指定默认的 `.env` 文件路径，用于加载项目的配置参数。
# _PROJECT_ROOT / ".env" 表示项目根目录下的 `.env` 文件。
_DEFAULT_ENV_FILE = _PROJECT_ROOT / ".env"


class Settings(BaseSettings):   # 传入 BaseSettings 类，用于定义配置参数。
    """项目配置对象（启动时实例化为单例 `settings`）。"""

    model_config = SettingsConfigDict(  # SettingsConfigDict 是 pydantic 库中的一个配置类，用于配置 BaseSettings 类的行为。
        # Use an absolute path so IDE/working-directory differences won't break loading.
        # 作用：确保在不同的 IDE 或工作目录下，加载的 `.env` 文件路径是一致的，避免读取失败。
        env_file=str(_DEFAULT_ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # LLM (OpenAI-compatible)
    # 作用：定义与 LLM 相关的配置参数，用于与 LLM 进行交互。
    llm_base_url: str = "https://api.openai.com"    # LLM 的 base_url，用于与 LLM 进行交互。
    llm_api_key: str = ""    # LLM 的 API 密钥，用于身份验证。
    llm_model: str = "gpt-4o-mini"    # LLM 的模型名称，用于指定使用的 LLM 模型。
    llm_timeout_s: float = 60.0    # LLM 请求的超时时间（秒），用于控制请求的响应时间。

    # Short-term memory (rough budget)
    stm_max_chars: int = 6000    # 短期记忆的最大字符数，用于限制短期记忆的大小。

    # Trace storage (Day3)
    trace_dir: str = "data/trace"    # Trace 落盘目录（相对/绝对路径均可）

    # Policy / 共情策略（V1 可配置）
    # 非空时从该路径加载 mode_prompts / explicit_rules / emotion_to_mode；空则使用代码内默认
    policy_config_path: str = ""

    # 情绪落盘（V1 占位：为情绪曲线/回访预留）
    # True 时每轮 /chat 成功后在 emotion_log_path 追加一条 JSONL
    emotion_log_enabled: bool = False
    emotion_log_path: str = "data/emotion_log.jsonl"

    # 策略开关（V1 配置外置）：通过环境变量切换，无需改代码
    safety_force_listen: bool = True   # 高风险时是否强制 mode=倾听
    watch_tier_force_listen: bool = True   # 关注档是否优先 mode=倾听

    # V2 RAG（最小检索）开关与参数
    rag_enabled: bool = False
    rag_top_k: int = 3
    rag_min_score: float = 0.0
    rag_max_chars: int = 1200

    # V4 混合检索（向量 + BM25）
    rag_use_hybrid: bool = False
    rag_bm25_top_k: int = 5
    rag_fusion_method: str = "rrf"

    # V4 Query 改写/重试
    rag_rewrite_enabled: bool = False
    rag_rewrite_min_score: float = 0.0

    # V1.1 P2：RAG 向量可选 OpenAI 兼容 /embeddings（空则稀疏本地 embed）
    rag_embedding_api_base: str = ""
    rag_embedding_api_key: str = ""
    rag_embedding_model: str = "text-embedding-3-small"
    rag_embedding_timeout_s: float = 30.0

    # V3 工具（Function Calling + 护栏）
    tool_enabled: bool = False
    tool_timeout_s: float = 5.0
    tool_retry_times: int = 1

    # Server
    host: str = "0.0.0.0"    # 服务器监听的主机地址，默认值为 "0.0.0.0"，表示监听所有可用的网络接口。
    port: int = 8000    # 服务器监听的端口号，默认值为 8000。  

    # 二期 Web：浏览器跨域；逗号分隔多个 Origin；空则启用内置开发默认（Vite 5173/4173）
    cors_origins: str = ""

    debug: bool = False

    # V5 用户隔离：为 True 时访问 trace/LTM 单条等必须带 user_id 且与资源一致
    strict_user_isolation: bool = False

    # V5 配额与限流（quota_token_per_user_per_day / quota_qps 为 0 表示不限制）
    quota_enabled: bool = False
    quota_token_per_user_per_day: int = 0
    quota_qps_per_user: float = 0.0
    # 日字符预算在主 LLM 前将超限时：False=429；True=去掉 RAG 注入并尝试更短 system（仍超则 429）
    quota_degrade_on_exhaust: bool = False
    # 降级时追加在 system 末尾；空字符串则使用服务端内置短提示
    quota_degrade_system_hint: str = ""

    # V5 内容安全：输入规则扫描 + 输出关键词脱敏（与情绪高风险关键词互补）
    content_safety_enabled: bool = True
    content_safety_filter_output: bool = True

    # V5 反馈闭环（POST /feedback）
    feedback_enabled: bool = True
    feedback_log_path: str = "data/feedback.jsonl"
    # 点踩或带纠错文本时，额外追加到评测样本 JSONL
    feedback_eval_mirror_enabled: bool = True
    feedback_eval_log_path: str = "data/feedback_for_eval.jsonl"

    # V5 运营热配置：PATCH /admin/config 写入并同步到内存 settings；启动时从文件加载
    hot_config_path: str = "data/hot_config.json"
    # 非空则 GET/PATCH /admin/config 必须带请求头 X-Admin-Token；为空则仅允许本机访问
    admin_config_token: str = ""

    # 三期：STM → Redis、LTM → 关系库（留空则沿用进程内实现，pytest 默认不配置）
    redis_url: str = ""
    database_url: str = ""

    # V1.1：对话隐式写入 LTM 的抽取管线总开关（关则不调抽取 LLM、不写隐式记忆）
    ltm_extract_enabled: bool = False
    # 每完成 N 轮对话（按 assistant 条数计）触发一次抽取；<=0 表示不按轮次触发（等价关闭周期触发）
    ltm_extract_every_n_turns: int = 3
    ltm_extract_min_confidence: float = 0.55
    ltm_extract_max_items: int = 5
    ltm_extract_char_budget: int = 6000
    ltm_extract_llm_temperature: float = 0.2
    # V1.1 P1：与近期 LTM 文本相似时跳过新建，或合并更新已有行（difflib 比值）
    ltm_extract_dedup_enabled: bool = True
    ltm_extract_dedup_skip_ratio: float = 0.90
    ltm_extract_dedup_merge_ratio: float = 0.76
    ltm_extract_dedup_lookback: int = 80
    # V1.1 P1：与 QUOTA_ENABLED 同时开启时，抽取 LLM 是否计入日字符预算（预检 + 成功后扣减）
    ltm_extract_count_toward_quota: bool = True
    ltm_extract_quota_reply_estimate: int = 400
    # V1.1 P2：抽取在对话返回后异步执行（须 REDIS_URL：入队 + lifespan worker）；无 Redis 时记录 warning 并同步抽取
    ltm_extract_async: bool = False

settings = Settings()

