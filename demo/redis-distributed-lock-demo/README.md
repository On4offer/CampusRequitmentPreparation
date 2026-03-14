# Redis 分布式锁 Demo（模拟 + 口述/伪代码）

用 **ConcurrentHashMap 模拟 Redis**，实现 setNX+过期、唯一 value 防误删、解锁前校验；真实环境需替换为 Redis 的 SET NX PX、Lua 原子解锁。便于秋招口述与伪代码对照。

## 文件说明

| 文件 | 说明 |
|------|------|
| `RedisLockPseudocode.java` | 本地模拟 Redis（putIfAbsent、过期），实现 tryLock/lock/unlock；value 用 UUID 防误删。 |

## 真实 Redis 对应关系

| 本 demo（模拟） | 真实 Redis |
|-----------------|------------|
| setIfAbsent(key, value, expireMs) | `SET key value NX PX expireMs` |
| get(key) / del(key) | `GET` / `DEL` |
| unlock 时 if value 相等再 del | **必须用 Lua** 保证原子：见下。 |

### Lua 原子解锁（真实实现必用）

```lua
-- 只删除自己持有的锁，避免误删他人锁
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
```

- 调用：`EVAL script 1 lockKey lockValue`

## 考点速记

- **为什么 value 要唯一**：防止线程 A 过期后删掉线程 B 刚加的锁；解锁时只有 value 相等才 del。
- **为什么要 Lua**：GET 与 DEL 分两条命令非原子，中间可能过期被别的客户端加锁，Lua 在 Redis 内原子执行。
- **看门狗（Redisson）**：业务执行时间可能超过锁 TTL，Redisson 会后台定时续期，避免业务未执行完锁过期。

## 运行方式

```bash
cd demo/redis-distributed-lock-demo
javac -d . *.java
java redis_distributed_lock_demo.RedisLockPseudocode
```

预期：打印「执行业务」。
