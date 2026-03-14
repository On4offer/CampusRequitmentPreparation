# 带过期缓存 Demo（DelayQueue）

ConcurrentHashMap + DelayQueue 实现 key 过期自动删除。校招可能考“带过期本地缓存怎么实现”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ExpireCache.java` | put 时放入 map 和 delayQueue；后台线程 take 到期的节点并从 map 移除。 |

## 考点速记

- **DelayQueue**：内部 PriorityQueue 按过期时间排序，take() 阻塞到队首元素到期。
- 也可惰性删除：get 时检查是否过期，过期则删除并返回 null。

## 运行方式

```bash
cd demo/expire-cache-demo
javac -d . *.java
java expire_cache_demo.ExpireCache
```

预期：先输出 A，600ms 后输出 null。
