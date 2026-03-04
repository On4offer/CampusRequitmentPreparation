# 📌 Flask 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**路由、请求、响应、配置**等日常开发速查。

---

## 一、应用与路由

### 1.1 应用创建与路由注册

| API / 写法 | 说明 | 使用场景 |
|------------|------|----------|
| `Flask(__name__)` | 创建应用实例 | 入口文件 |
| `@app.route("/path", methods=["GET","POST"])` | 注册路由与方法 | 定义接口 |
| `@app.get("/path")`（Flask 2.0+） | 仅 GET | 简洁写法 |
| `@app.post("/path")` | 仅 POST | 提交表单/JSON |
| `app.add_url_rule("/path", view_func=fn)` | 代码方式注册路由 | 动态注册 |

### 1.2 路由参数与转换器

| 写法 | 说明 | 示例 |
|------|------|------|
| `/user/<id>` | 默认字符串 | `id = "abc"` |
| `/user/<int:id>` | 整数 | `id = 123` |
| `/user/<float:score>` | 浮点数 | |
| `/path/<path:subpath>` | 含斜杠的路径 | |
| `/uuid/<uuid:uid>` | UUID | |

---

## 二、请求与响应

### 2.1 请求对象（request）

| API | 说明 | 使用场景 |
|-----|------|----------|
| `request.method` | 请求方法 | 分支处理 |
| `request.args` | GET 查询参数（ImmutableMultiDict） | `request.args.get("key")` |
| `request.form` | 表单数据（POST） | 表单提交 |
| `request.json` | 解析后的 JSON 体 | REST API |
| `request.data` | 原始 body | 非 JSON 时 |
| `request.headers` | 请求头 | 鉴权、Content-Type |
| `request.files` | 上传文件 | 文件上传 |

### 2.2 响应

| API | 说明 | 使用场景 |
|-----|------|----------|
| `return "text"` | 文本，200 | 简单返回 |
| `return jsonify({...})` | JSON 响应，Content-Type: application/json | API 返回 |
| `return make_response(body, status)` | 自定义状态码与体 | 201、404 等 |
| `return redirect(url)` | 重定向 | 登录后跳转 |
| `return render_template("x.html", **ctx)` | 渲染模板 | 页面渲染 |

---

## 三、配置与上下文

### 3.1 配置

| 写法 | 说明 |
|------|------|
| `app.config["KEY"] = value` | 单键配置 |
| `app.config.from_object("config.Config")` | 从类加载 |
| `app.config.from_pyfile("config.py")` | 从文件加载 |
| `app.config.from_envvar("FLASK_CONFIG")` | 从环境变量指向的文件 |

### 3.2 全局对象与钩子

| API | 说明 |
|-----|------|
| `g` | 请求级全局对象，存请求内共享数据 |
| `session` | 服务端会话（需配置 SECRET_KEY） |
| `before_request` / `after_request` | 请求前后钩子 |
| `app.errorhandler(404)` | 统一错误处理 |

---

## 四、常用场景速查

| 场景 | 示例写法 |
|------|----------|
| 返回 JSON + 状态码 | `return jsonify({"ok": True}), 201` |
| 获取 GET 参数 | `request.args.get("page", default=1, type=int)` |
| 获取 JSON body | `data = request.get_json()` |
| 上传文件 | `f = request.files["file"]` → `f.save(path)` |
| 重定向 | `redirect(url_for("index"))` |
