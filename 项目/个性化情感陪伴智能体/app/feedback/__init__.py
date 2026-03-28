"""V5 用户反馈（点赞/点踩/纠错）落盘与查询。"""

from app.feedback.store import append_feedback_row, read_feedback_tail

__all__ = ["append_feedback_row", "read_feedback_tail"]
