好的，下面介绍 **基于 Redis 的分布式锁实现方式**，特别是 `SETNX + EXPIRE` 和 Redisson 的方式，并解释其原理、优缺点及应用场景。

------

## 一、为什么需要分布式锁？

在分布式系统中，多个服务实例可能会同时访问和修改某个共享资源（如库存、优惠券、订单等）。为了保证数据一致性，就需要分布式锁。

------

## 二、基于 Redis 实现分布式锁的两种主流方式

### **1. SETNX + EXPIRE 手动实现**

#### 实现原理：

- **SETNX（Set if Not Exists）**：只在 key 不存在时设置值，确保只有一个线程获得锁。
- **EXPIRE（过期时间）**：给锁设置一个超时时间，避免死锁。
- 为了确保原子性，推荐使用 Redis 2.6.12+ 的 `SET` 命令的一种增强语法：

```bash
SET key value NX EX 30
```

- `NX`：只在 key 不存在时设置
- `EX 30`：设置过期时间为 30 秒

#### Java 示例：

```java
Boolean success = redisTemplate.opsForValue()
    .setIfAbsent("lock:order", "UUID", 30, TimeUnit.SECONDS);
if (Boolean.TRUE.equals(success)) {
    // 获得锁，执行业务逻辑
    try {
        // do something
    } finally {
        redisTemplate.delete("lock:order"); // 释放锁
    }
}
```

#### 问题 & 改进：

- **死锁风险**：如果执行业务过程中异常或宕机，锁不会释放。
  - 解决：设置过期时间，或使用 Lua 脚本保证释放时检查锁的拥有者。
- **锁误删问题**：A 拿到锁执行任务，因耗时锁自动过期，B 抢到锁，此时 A 释放锁会误删 B 的锁。
  - 解决：锁的值设置为唯一 ID（如 UUID），释放锁时验证是否是自己持有的。

#### 释放锁的 Lua 脚本（防误删）：

```lua
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
```

------

### **2. 使用 Redisson 实现**

**Redisson** 是 Redis 的高级客户端，提供了分布式锁、读写锁、信号量、闭锁等功能的封装。

#### 使用示例：

```java
RLock lock = redissonClient.getLock("lock:order");

try {
    // 默认等待时间为 30s，自动续期（看门狗机制）
    lock.lock(); // 阻塞式加锁
    // 或 lock.tryLock(timeout, leaseTime, timeUnit);

    // 执行业务逻辑
} finally {
    lock.unlock(); // 自动检查是否是当前线程持有
}
```

#### Redisson 的优势：

- **自动续期**（watchdog）：如果业务没执行完，Redisson 会自动续租锁的过期时间；
- **线程绑定锁**：每个锁都绑定到当前线程，解锁时会校验；
- 支持公平锁、可重入锁、读写锁等高级功能。

------

## 三、应用场景举例

| 场景             | 说明                                   |
| ---------------- | -------------------------------------- |
| 秒杀/抢购        | 保证库存更新的原子性                   |
| 订单防重复提交   | 用户点击“提交订单”按钮多次，锁住用户ID |
| 定时任务并发控制 | 多节点部署时，保证只有一个任务节点执行 |
| 分布式事务协调   | 在执行阶段通过锁控制多个资源协调提交   |

------

## 四、总结对比

| 方式           | 优点                     | 缺点                       |
| -------------- | ------------------------ | -------------------------- |
| SETNX + EXPIRE | 轻量、跨语言、依赖少     | 容易误删锁、需要手动续期等 |
| Redisson       | 功能完善、自动续期、安全 | 引入依赖、稍重             |

------

### 一句话总结：

> **基于 Redis 的分布式锁可通过原生 SETNX+EXPIRE 实现，或使用 Redisson 封装方案，适合高并发下的数据一致性控制。**

是否需要我提供 Redis 锁相关 Lua 脚本封装、Redisson 的详细配置示例或应用级抽象封装代码？