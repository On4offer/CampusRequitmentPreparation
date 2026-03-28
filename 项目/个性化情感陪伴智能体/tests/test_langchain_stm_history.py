"""BaseChatMessageHistory 适配器与直接 trim 一致性。"""

from __future__ import annotations

from langchain_core.messages import AIMessage, HumanMessage

from app.langchain.messages import chat_messages_to_lc, lc_base_messages_to_chat
from app.langchain.stm_history import SessionStoreChatMessageHistory
from app.llm.client import ChatMessage
from app.memory.stm import trim_messages_by_char_budget
from app.memory.store import session_store


def test_session_store_history_trim_matches_direct():
    uid, sid = "u_hist_test", "s_hist_test"
    session_store.reset(user_id=uid, session_id=sid)
    session_store.append(user_id=uid, session_id=sid, message=ChatMessage(role="user", content="a"))
    session_store.append(user_id=uid, session_id=sid, message=ChatMessage(role="assistant", content="b"))
    max_c = 6000
    state = session_store.get_or_create(user_id=uid, session_id=sid)
    direct = trim_messages_by_char_budget(state.messages, max_chars=max_c)
    hist = SessionStoreChatMessageHistory(user_id=uid, session_id=sid, max_chars=max_c)
    assert hist.get_trimmed_chat_messages() == direct
    assert len(hist.messages) == len(direct)
    session_store.reset(user_id=uid, session_id=sid)


def test_lc_roundtrip_chat_messages():
    cms = [
        ChatMessage(role="user", content="hi"),
        ChatMessage(role="assistant", content="yo"),
    ]
    lc = chat_messages_to_lc(cms)
    back = lc_base_messages_to_chat(lc)
    assert [m.role for m in back] == ["user", "assistant"]
    assert back[0].content == "hi"
    assert back[1].content == "yo"


def test_history_add_messages_persists():
    uid, sid = "u_hist_add", "s_hist_add"
    session_store.reset(user_id=uid, session_id=sid)
    h = SessionStoreChatMessageHistory(user_id=uid, session_id=sid, max_chars=6000)
    h.add_messages([HumanMessage(content="x"), AIMessage(content="y")])
    st = session_store.get_or_create(user_id=uid, session_id=sid)
    assert len(st.messages) == 2
    assert st.messages[0].content == "x"
    assert st.messages[1].content == "y"
    session_store.reset(user_id=uid, session_id=sid)


def test_history_clear():
    uid, sid = "u_hist_clr", "s_hist_clr"
    session_store.append(user_id=uid, session_id=sid, message=ChatMessage(role="user", content="z"))
    h = SessionStoreChatMessageHistory(user_id=uid, session_id=sid, max_chars=6000)
    h.clear()
    assert session_store.get_messages(user_id=uid, session_id=sid) is None
