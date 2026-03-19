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

    # Server
    host: str = "0.0.0.0"    # 服务器监听的主机地址，默认值为 "0.0.0.0"，表示监听所有可用的网络接口。
    port: int = 8000    # 服务器监听的端口号，默认值为 8000。  

    debug: bool = False


settings = Settings()

