from __future__ import annotations  # 允许在函数注解中使用当前类名

"""FastAPI 应用入口（ASGI app）。"""

from pathlib import Path

from fastapi import FastAPI  # FastAPI 应用类
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.responses import HTMLResponse

from app.api.routes import router as api_router    # API 路由
from app.core.settings import settings
from app.policy import reload_policy_config

# Swagger UI 放大字体，便于浏览器阅读（覆盖默认小字号）
SWAGGER_CUSTOM_CSS = """
<style>
  .swagger-ui { font-size: 20px !important; }
  .swagger-ui .info .title { font-size: 40px !important; }
  .swagger-ui .opblock-summary-path { font-size: 22px !important; }
  .swagger-ui .opblock-summary-method { font-size: 18px !important; }
  .swagger-ui body, .swagger-ui .info p, .swagger-ui .opblock,
  .swagger-ui table, .swagger-ui table th, .swagger-ui table td,
  .swagger-ui .model, .swagger-ui .parameter__name, .swagger-ui .parameter__type,
  .swagger-ui .response-col_status, .swagger-ui .response-col_links,
  .swagger-ui .tab li, .swagger-ui .opblock-body pre, .swagger-ui .model-toggle,
  .swagger-ui input, .swagger-ui select, .swagger-ui .response-col_description { font-size: 20px !important; }
  .swagger-ui .opblock-description-wrapper, .swagger-ui .opblock-external-docs-wrapper,
  .swagger-ui .opblock-title_normal, .swagger-ui .opblock-body .opblock-description-wrapper p,
  .swagger-ui .renderedMarkdown, .swagger-ui .markdown p { font-size: 20px !important; line-height: 1.5 !important; }
  .swagger-ui .markdown p, .swagger-ui .renderedMarkdown p { font-size: 20px !important; }
  .swagger-ui .parameter__name, .swagger-ui .parameter__in { font-size: 20px !important; }
</style>
"""
_HEAD_END = "</head>"


# 应用工厂函数
def create_app() -> FastAPI:
    """
    创建 FastAPI 应用实例。

    约定：
    - 路由统一在 `app.api.routes` 注册
    - 后续可在此处集中挂载中间件（日志/trace/CORS/限流等）
    - /docs 使用自定义 Swagger UI（注入放大字体 CSS）
    """

    app = FastAPI(title="Emotional Companion Agent", version="0.1.0", docs_url=None)
    app.include_router(api_router)

    # V1：启动时加载共情策略配置（POLICY_CONFIG_PATH 非空时从文件加载）
    _project_root = Path(__file__).resolve().parents[1]
    _config_path = (_project_root / settings.policy_config_path) if settings.policy_config_path else None
    reload_policy_config(_config_path)

    @app.get("/docs", include_in_schema=False)
    async def custom_swagger_ui_html():
        html_resp = get_swagger_ui_html(
            openapi_url=app.openapi_url,
            title=app.title + " - Swagger UI",
        )
        body = html_resp.body.decode()
        if _HEAD_END in body:
            body = body.replace(_HEAD_END, SWAGGER_CUSTOM_CSS + _HEAD_END)
        else:
            body = body + SWAGGER_CUSTOM_CSS
        return HTMLResponse(body)

    return app


app = create_app()  # 创建 FastAPI 应用实例

