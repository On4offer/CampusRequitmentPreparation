# 📌 Celery 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**应用创建、Task、调用、配置**等日常开发速查。

---

## 一、应用与配置

### 1.1 创建应用

| API | 说明 | 使用场景 |
|-----|------|----------|
| `Celery("myapp", broker="redis://localhost/0")` | 创建 Celery 应用 | 入口或集中配置 |
| `app.conf.broker_url = "redis://..."` | 设置 Broker | 配置 |
| `app.conf.result_backend = "redis://..."` | 设置结果存储 | 需要 get 结果时 |
| `app.conf.timezone = "Asia/Shanghai"` | 时区（Beat 用） | 定时任务 |

### 1.2 常用配置项

| 配置 | 说明 |
|------|------|
| `task_serializer` | 任务序列化（json） |
| `result_expires` | 结果过期时间（秒） |
| `task_routes` | 任务与队列路由 |
| `worker_prefetch_multiplier` | 预取倍数，1 为公平调度 |

---

## 二、Task 定义与调用

### 2.1 定义 Task

| API | 说明 | 使用场景 |
|-----|------|----------|
| `@app.task` | 将函数注册为任务 | 异步任务 |
| `@app.task(bind=True)` | 可访问 `self`（request 等） | 需要 task_id、重试等 |
| `@app.task(acks_late=True)` | 执行完再 ack | 避免执行中崩溃丢任务 |
| `@app.task(max_retries=3)` | 最大重试次数 | 失败重试 |

### 2.2 调用方式

| 方式 | 说明 | 示例 |
|------|------|------|
| `.delay(*args, **kwargs)` | 异步调用，返回 AsyncResult | `add.delay(1, 2)` |
| `.apply_async(args=(), kwargs={}, countdown=10)` | 异步调用，可设延迟/队列 | 延迟、指定队列 |
| 直接 `task(args)` | 同步调用（同普通函数） | 测试或不需要队列时 |

### 2.3 获取结果

| API | 说明 |
|-----|------|
| `result = task.delay(...); result.get()` | 阻塞取结果 |
| `result.get(timeout=5)` | 带超时 |
| `result.ready()` | 是否完成 |
| `result.successful()` | 是否成功 |
| `result.result` | 返回值（未完成可能阻塞） |

---

## 三、启动命令

| 命令 | 说明 | 使用场景 |
|------|------|----------|
| `celery -A myapp worker -l info` | 启动 Worker | 开发/生产 |
| `celery -A myapp worker -l info -Q high,default` | 指定队列 | 多队列 |
| `celery -A myapp beat -l info` | 启动 Beat | 定时任务 |
| `celery -A myapp worker -l info --concurrency=4` | 并发数 | 调优 |

---

## 四、常用场景速查

| 场景 | 示例 |
|------|------|
| 定义简单任务 | `@app.task` + `def add(x, y): return x + y` |
| 异步调用 | `add.delay(1, 2)` |
| 延迟执行 | `add.apply_async(args=(1, 2), countdown=60)` |
| 指定队列 | `add.apply_async(args=(1, 2), queue="high")` |
| 重试 | `self.retry(exc=e, countdown=60)`（bind=True 时） |
