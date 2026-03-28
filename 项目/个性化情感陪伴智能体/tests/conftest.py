"""
pytest 入口：默认清空 DATABASE_URL / REDIS_URL，避免本地 .env 指向真实库时单测污染数据或依赖外网。

需要连真实 MySQL/Redis 做集成测试时：设置环境变量 PYTEST_USE_REAL_DB=1 后再运行 pytest。
主对话统一走 LangChain：autouse mock `build_chat_openai_from_settings`，避免未配置密钥时外呼。
"""

from __future__ import annotations

import os

import pytest

if os.environ.get("PYTEST_USE_REAL_DB") != "1":
    os.environ["DATABASE_URL"] = ""
    os.environ["REDIS_URL"] = ""
    # 避免本地 .env 打开隐式 LTM 后，/chat 多一次抽取 LLM，打乱「情绪+主对话」调用次数断言
    os.environ["LTM_EXTRACT_ENABLED"] = "false"
    os.environ["LTM_EXTRACT_ASYNC"] = "false"


@pytest.fixture(autouse=True)
def _mock_langchain_main_chat_model(monkeypatch: pytest.MonkeyPatch) -> None:
    from tests.orchestrator_mocks import FakeLCMainChatModel

    monkeypatch.setattr(
        "app.langchain.chat_model.build_chat_openai_from_settings",
        lambda **kw: FakeLCMainChatModel(),
    )
