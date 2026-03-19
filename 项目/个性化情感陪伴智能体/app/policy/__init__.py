"""策略/状态机模块（Day5）：mode 判定与共情 prompt 模板。"""

__all__ = ["decide_mode", "get_system_prompt_for_mode"]

from app.policy.state_machine import decide_mode, get_system_prompt_for_mode
