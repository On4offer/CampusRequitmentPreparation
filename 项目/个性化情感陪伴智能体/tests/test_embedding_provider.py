"""V1.1 P2：RAG 远程 embedding 回退与归一化。"""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from app.core import settings as core_settings
from app.rag.embedding_provider import embed_for_rag


def test_embed_for_rag_sparse_when_base_empty(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "rag_embedding_api_base", "")
    v = embed_for_rag("你好世界")
    assert isinstance(v, dict)
    assert len(v) > 0


def test_embed_for_rag_remote_normalizes(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "rag_embedding_api_base", "https://api.example.com/v1")
    monkeypatch.setattr(core_settings.settings, "rag_embedding_api_key", "k")
    monkeypatch.setattr(core_settings.settings, "rag_embedding_model", "m")

    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    mock_resp.json.return_value = {"data": [{"embedding": [3.0, 4.0]}]}
    mock_cm = MagicMock()
    mock_cm.__enter__.return_value.post.return_value = mock_resp
    mock_cm.__exit__ = MagicMock(return_value=None)

    with patch("httpx.Client", return_value=mock_cm):
        v = embed_for_rag("hi")
    assert len(v) == 2
    assert abs(v["0"] - 0.6) < 1e-6
    assert abs(v["1"] - 0.8) < 1e-6
