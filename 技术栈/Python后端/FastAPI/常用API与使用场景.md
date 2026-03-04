# 📌 FastAPI 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**路由、请求/响应、依赖注入、文档**等日常开发速查。

---

## 一、应用与路由

### 1.1 应用创建与路由

| API / 写法 | 说明 | 使用场景 |
|------------|------|----------|
| `FastAPI()` | 创建应用实例 | 入口文件 |
| `@app.get("/path")` | 注册 GET | 查询接口 |
| `@app.post("/path")` | 注册 POST | 创建资源 |
| `@app.put("/path")` / `@app.patch("/path")` | PUT / PATCH | 更新 |
| `@app.delete("/path")` | DELETE | 删除 |
| `@app.api_route("/path", methods=["GET","POST"])` | 多方法 | 兼容多种方法 |

### 1.2 路径与查询参数

| 写法 | 说明 | 示例 |
|------|------|------|
| `@app.get("/items/{item_id}")` | 路径参数 | `item_id: int` |
| `def f(q: str = Query(None))` | 查询参数，带默认与校验 | `?q=xxx` |
| `Query(default, alias, min_length, max_length)` | 查询校验与别名 | 参数校验 |
| `Path(..., ge=0)` | 路径参数校验 | 数值范围 |

---

## 二、请求体与 Pydantic 模型

### 2.1 请求体

| API | 说明 | 使用场景 |
|-----|------|----------|
| `Body(...)` | 显式声明请求体 | 多个 body 或别名 |
| `class Item(BaseModel): ...` | Pydantic 模型 | 自动校验与文档 |
| `Item` 类型注解 | 自动解析 JSON 为模型 | `item: Item` |
| `List[Item]` | 批量 body | 批量创建 |

### 2.2 常用类型与校验

| 类型 / 写法 | 说明 |
|-------------|------|
| `str, int, float, bool` | 基础类型 |
| `Optional[str] = None` | 可选 |
| `Field(..., min_length=1)` | 字段校验与文档 |
| `ConfigDict`（Pydantic v2） | 模型配置（别名、extra 等） |

---

## 三、响应与状态码

### 3.1 响应

| API | 说明 | 使用场景 |
|-----|------|----------|
| `return {"key": "value"}` | 自动转 JSON | 字典返回 |
| `response_model=Item` | 声明响应模型，影响文档与校验 | 统一结构 |
| `response_model_exclude_unset=True` | 仅返回已设置字段 | 部分字段 |
| `Response()` / `JSONResponse()` | 裸响应 | 自定义 status_code、headers |

### 3.2 状态码

| 写法 | 说明 |
|------|------|
| `status_code=201` | 装饰器级 |
| `return JSONResponse(content=..., status_code=201)` | 响应对象级 |

---

## 四、依赖注入

| API | 说明 | 使用场景 |
|-----|------|----------|
| `Depends(get_xxx)` | 注入依赖 | 鉴权、DB 会话 |
| `def get_db(): ... yield db` | 生成器依赖（推荐） | 数据库会话、资源释放 |
| `Depends()` 无参 | 复用同一依赖 | 子依赖 |

---

## 五、文档与运行

| 能力 | 说明 |
|------|------|
| `/docs` | Swagger UI（默认开启） |
| `/redoc` | ReDoc |
| `openapi_url` | 自定义 OpenAPI JSON 地址 |
| `uvicorn run:app --reload` | 开发时运行 |

---

## 六、常用场景速查

| 场景 | 示例写法 |
|------|----------|
| GET 带查询参数 | `def f(skip: int = 0, limit: int = 10): ...` |
| POST JSON body | `def f(item: Item): ...` |
| 路径参数 + 校验 | `item_id: int = Path(..., ge=1)` |
| 依赖获取当前用户 | `user: User = Depends(get_current_user)` |
| 自定义状态码 | `return item, 201` 或 `JSONResponse(..., status_code=201)` |
