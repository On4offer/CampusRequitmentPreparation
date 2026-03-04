# 📌 Redis（Python 客户端）常用 API 与使用场景速查

> 配合《学习笔记》使用；Redis 服务端命令与原理见《Java后端/Redis》同目录文档。此处侧重 **redis-py** 的常用 API。

---

## 一、连接

| API | 说明 | 使用场景 |
|-----|------|----------|
| `redis.Redis(host, port, db, decode_responses=True)` | 同步连接 | Flask、脚本 |
| `redis.asyncio.Redis(...)` | 异步连接 | FastAPI |
| `r.ping()` | 检查连接 | 健康检查 |
| `r.close()` | 关闭连接 | 退出或池外单连接 |

---

## 二、String

| API | 说明 | 使用场景 |
|-----|------|----------|
| `r.set("key", "value")` | 设置 | 缓存、分布式锁 |
| `r.set("key", "value", ex=60)` | 设置 + 过期（秒） | 带 TTL 缓存 |
| `r.get("key")` | 获取，无则 None | 读缓存 |
| `r.setnx("key", "value")` | 不存在才设置 | 简单锁 |
| `r.incr("key")` / `r.decr("key")` | 自增/自减 | 计数、限流 |
| `r.mget(keys)` / `r.mset(mapping)` | 批量 get/set | 批量缓存 |

---

## 三、Hash

| API | 说明 | 使用场景 |
|-----|------|----------|
| `r.hset("key", "field", "value")` | 单字段 | 对象缓存 |
| `r.hget("key", "field")` | 取单字段 | |
| `r.hgetall("key")` | 取全部字段（字典） | 整表缓存 |
| `r.hincrby("key", "field", 1)` | 字段自增 | 计数 |

---

## 四、List

| API | 说明 | 使用场景 |
|-----|------|----------|
| `r.lpush("key", "a")` / `r.rpush("key", "b")` | 左/右推入 | 队列、栈 |
| `r.lpop("key")` / `r.rpop("key")` | 左/右弹出 | 消费队列 |
| `r.lrange("key", 0, -1)` | 范围查询 | 列表页、历史 |
| `r.llen("key")` | 长度 | 队列长度 |

---

## 五、Set / ZSet

| API | 说明 | 使用场景 |
|-----|------|----------|
| `r.sadd("key", "a", "b")` | 添加成员 | 去重、标签 |
| `r.smembers("key")` | 全部成员 | |
| `r.zadd("key", {"m1": 90, "m2": 80})` | 有序集合添加 | 排行榜 |
| `r.zrevrange("key", 0, 9, withscores=True)` | 倒序取 Top N | 排行榜 |

---

## 六、过期与通用

| API | 说明 |
|-----|------|
| `r.expire("key", 60)` | 设置过期（秒） |
| `r.ttl("key")` | 剩余 TTL |
| `r.delete("key")` | 删除 |
| `r.exists("key")` | 是否存在 |

---

## 七、管道与事务

| API | 说明 |
|-----|------|
| `r.pipeline()` | 管道，批量命令减少 RTT |
| `pipe = r.pipeline(); pipe.set(...); pipe.get(...); pipe.execute()` | 批量执行 |
| `r.transaction(func, *keys)` | 事务（MULTI/EXEC） |

---

## 八、常用场景速查

| 场景 | 示例 |
|------|------|
| 简单缓存 | `r.set("k", v, ex=300); r.get("k")` |
| 分布式锁 | `r.set("lock", "1", nx=True, ex=10)` |
| 限流计数 | `r.incr("rate:user:1"); r.expire("rate:user:1", 60)` |
| 排行榜 | `r.zadd("rank", {uid: score}); r.zrevrange("rank", 0, 9)` |
