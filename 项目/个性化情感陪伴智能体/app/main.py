from __future__ import annotations  # 允许在函数注解中使用当前类名

"""FastAPI 应用入口（ASGI app）。"""

from fastapi import FastAPI  # FastAPI 应用类

from app.api.routes import router as api_router    # API 路由


# 应用工厂函数
def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例。

    约定：
    - 路由统一在 `app.api.routes` 注册
    - 后续可在此处集中挂载中间件（日志/trace/CORS/限流等）
    """

    app = FastAPI(title="Emotional Companion Agent", version="0.1.0")
    app.include_router(api_router)
    return app


app = create_app()  # 创建 FastAPI 应用实例

