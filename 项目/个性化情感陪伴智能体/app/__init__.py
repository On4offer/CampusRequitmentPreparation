"""
应用包根目录（app）。
- __all__ = [] 表示不允许通过 import * 导入任何内容
- 强制使用者通过明确的模块路径导入所需功能（如 from app.api.routes import router ）
- 提高代码的可维护性和可读性
"""

__all__ = []

