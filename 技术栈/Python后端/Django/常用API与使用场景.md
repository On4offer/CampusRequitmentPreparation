# 📌 Django 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**项目命令、模型、视图、URL、配置**等日常开发速查。

---

## 一、项目与应用

### 1.1 常用命令

| 命令 | 说明 | 使用场景 |
|------|------|----------|
| `django-admin startproject myproject` | 创建项目 | 新项目 |
| `python manage.py startapp myapp` | 创建应用 | 新模块 |
| `python manage.py runserver` | 开发服务器 | 本地调试 |
| `python manage.py migrate` | 执行迁移 | 建表/更新表结构 |
| `python manage.py makemigrations` | 生成迁移文件 | 改 Model 后 |
| `python manage.py createsuperuser` | 创建管理员 | 使用 Admin 前 |
| `python manage.py shell` | 带 ORM 的 Python Shell | 调试、脚本 |

### 1.2 项目结构（简要）

```
myproject/
├── manage.py
├── myproject/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── myapp/
    ├── models.py
    ├── views.py
    ├── urls.py
    └── admin.py
```

---

## 二、模型（Model）

### 2.1 常用字段

| 字段 | 说明 |
|------|------|
| `CharField(max_length=...)` | 字符串 |
| `TextField()` | 长文本 |
| `IntegerField()` / `BigAutoField()` | 整数 / 自增主键 |
| `BooleanField()` | 布尔 |
| `DateTimeField(auto_now_add=True)` | 创建时间 |
| `DateTimeField(auto_now=True)` | 更新时间 |
| `ForeignKey(OtherModel, on_delete=CASCADE)` | 外键 |
| `ManyToManyField(OtherModel)` | 多对多 |

### 2.2 查询常用 API

| API | 说明 | 使用场景 |
|-----|------|----------|
| `Model.objects.all()` | 全表 | 列表 |
| `Model.objects.get(pk=id)` | 单条（不存在抛异常） | 详情 |
| `Model.objects.filter(**kwargs)` | 过滤 | 条件查询 |
| `Model.objects.exclude(**kwargs)` | 排除 | 反向条件 |
| `Model.objects.create(**kwargs)` | 创建并保存 | 新增 |
| `obj.save()` | 更新 | 修改后保存 |
| `obj.delete()` | 删除 | 删除 |
| `.order_by("-created_at")` | 排序 | 列表排序 |
| `.values("id", "name")` | 指定字段 | 减少字段 |
| `.count()` | 数量 | 分页 total |

---

## 三、视图与 URL

### 3.1 视图

| 写法 | 说明 |
|------|------|
| `def view(request): return HttpResponse(...)` | 函数视图 |
| `class View(TemplateView)` | 类视图（模板） |
| `class View(ListView)` | 列表类视图 |
| `class View(DetailView)` | 详情类视图 |
| `request.GET.get("key")` | GET 参数 |
| `request.POST.get("key")` | POST 参数 |
| `JsonResponse({...})` | JSON 响应 |
| `redirect("name")` / `redirect("/path/")` | 重定向 |

### 3.2 URL 配置

| 写法 | 说明 |
|------|------|
| `path("articles/", views.list_view)` | 路由到视图 |
| `path("articles/<int:id>/", views.detail_view)` | 路径参数 |
| `path("", include("myapp.urls"))` | 子路由包含 |
| `urlpatterns` | 路由列表 |
| `reverse("name")` | 根据 name 反解 URL |

---

## 四、配置（settings.py）常用项

| 配置 | 说明 |
|------|------|
| `DEBUG` | 调试模式（生产必须 False） |
| `ALLOWED_HOSTS` | 允许的 Host |
| `INSTALLED_APPS` | 已安装应用 |
| `DATABASES` | 数据库配置 |
| `SECRET_KEY` | 密钥（勿泄露） |
| `STATIC_URL` / `STATIC_ROOT` | 静态文件 |
| `MIDDLEWARE` | 中间件列表 |

---

## 五、常用场景速查

| 场景 | 示例 |
|------|------|
| 按 id 查一条 | `User.objects.get(pk=user_id)` |
| 条件 + 排序 + 分页 | `User.objects.filter(active=True).order_by("-created_at")[start:end]` |
| 新增 | `User.objects.create(name="x", email="x@x.com")` |
| 更新 | `u = User.objects.get(pk=1); u.name = "y"; u.save()` |
| 返回 JSON | `return JsonResponse({"id": 1})` |
