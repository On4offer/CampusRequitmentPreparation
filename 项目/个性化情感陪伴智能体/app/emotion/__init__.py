"""情绪识别模块（Day4）：LLM 为主、关键词兜底。"""

__all__ = ["analyze_emotion", "EmotionResult"]

from app.emotion.analyzer import EmotionResult, analyze_emotion
