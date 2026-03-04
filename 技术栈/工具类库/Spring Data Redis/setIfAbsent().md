## setIfAbsent() 方法介绍

### 1. 基本概念
`setIfAbsent()` 是 Spring Data Redis 提供的 Redis 操作方法，用于实现 Redis 的 `SETNX`（SET if Not eXists）命令功能。

### 2. 所属体系
- **框架**：Spring Data Redis
- **类**：`org.springframework.data.redis.core.ValueOperations<K, V>`
- **Redis 命令等价**：`SET key value NX`

### 3. 功能作用
`setIfAbsent()` 方法用于：
1. **原子操作**：原子性地设置键值对（仅当键不存在时）
2. **分布式锁**：实现简单的分布式锁机制
3. **互斥控制**：确保同一时间只有一个客户端能执行特定操作
4. **幂等性**：保证操作的幂等性

### 4. 方法签名

```java
// 基础版本
Boolean setIfAbsent(K key, V value);

// 带过期时间版本
Boolean setIfAbsent(K key, V value, long timeout, TimeUnit unit);

// 带过期时间版本（Duration）
Boolean setIfAbsent(K key, V value, Duration timeout);
```


### 5. 在代码中的使用

```java
// 在 tryLock 方法中使用
private boolean tryLock(String key) {
    // 设置分布式锁，10秒过期
    Boolean flag = stringRedisTemplate.opsForValue().setIfAbsent(key, "1", 10, TimeUnit.SECONDS);
    return BooleanUtil.isTrue(flag);
}
```


### 6. Redis 命令对照

```java
// Java 代码
stringRedisTemplate.opsForValue().setIfAbsent("lock:key", "1", 10, TimeUnit.SECONDS);

// 等价的 Redis 命令
SET lock:key 1 NX EX 10
```


### 7. 使用示例

#### (1) 基本使用
```java
// 获取锁
Boolean isLocked = stringRedisTemplate.opsForValue().setIfAbsent("lock:user:123", "1");
if (BooleanUtil.isTrue(isLocked)) {
    try {
        // 执行需要互斥的操作
        doSomething();
    } finally {
        // 释放锁
        stringRedisTemplate.delete("lock:user:123");
    }
}
```


#### (2) 带过期时间的锁
```java
// 获取锁，5秒后自动过期
Boolean isLocked = stringRedisTemplate.opsForValue().setIfAbsent(
    "lock:order:456", "1", 5, TimeUnit.SECONDS);
```


### 8. 在分布式锁中的作用

```java
// 分布式锁实现机制
private boolean tryLock(String key) {
    // 1. 尝试设置锁键（仅当不存在时）
    Boolean flag = stringRedisTemplate.opsForValue().setIfAbsent(key, "1", 10, TimeUnit.SECONDS);
    // 2. 返回获取锁的结果
    return BooleanUtil.isTrue(flag);
}

// 使用示例
String lockKey = "lock:shop:1";
if (tryLock(lockKey)) {
    // 获取锁成功，执行临界区代码
    try {
        // 数据库操作、缓存更新等
    } finally {
        // 确保释放锁
        unlock(lockKey);
    }
}
```


### 9. 相关 Redis 操作方法对比

| 方法                                                         | 功能               | 是否检查存在 | 过期时间 |
| ------------------------------------------------------------ | ------------------ | ------------ | -------- |
| [set(K key, V value)](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\CacheClient.java#L32-L34) | 设置键值对         | 否           | 否       |
| `set(K key, V value, timeout, unit)`                         | 设置键值对         | 否           | 是       |
| `setIfAbsent(K key, V value)`                                | 仅当键不存在时设置 | 是           | 否       |
| `setIfAbsent(K key, V value, timeout, unit)`                 | 仅当键不存在时设置 | 是           | 是       |

### 10. 优势

1. **原子性**：Redis 单线程保证操作原子性
2. **高性能**：基于内存操作，速度极快
3. **分布式支持**：多个应用实例共享同一锁
4. **自动过期**：防止死锁问题
5. **简单易用**：API 设计简洁明了

### 11. 注意事项

#### (1) 锁过期时间
```java
// 设置合理的过期时间，防止死锁
setIfAbsent(key, "1", 10, TimeUnit.SECONDS); // 10秒过期
```


#### (2) 锁释放
```java
// 必须在 finally 块中释放锁
try {
    // 业务逻辑
} finally {
    unlock(lockKey); // 确保锁被释放
}
```


#### (3) 锁的值验证
```java
// 更安全的锁释放方式（防止误删他人锁）
private void unlock(String key) {
    String value = stringRedisTemplate.opsForValue().get(key);
    if ("1".equals(value)) {
        stringRedisTemplate.delete(key);
    }
}
```


### 12. 完整的分布式锁示例

```java
// 获取锁
private boolean tryLock(String key, long timeout, TimeUnit unit) {
    Boolean result = stringRedisTemplate.opsForValue().setIfAbsent(key, "1", timeout, unit);
    return BooleanUtil.isTrue(result);
}

// 释放锁
private void unlock(String key) {
    stringRedisTemplate.delete(key);
}

// 使用锁
public void doWithLock(String resourceId) {
    String lockKey = "lock:resource:" + resourceId;
    if (tryLock(lockKey, 30, TimeUnit.SECONDS)) {
        try {
            // 执行需要互斥的操作
            performCriticalOperation(resourceId);
        } finally {
            unlock(lockKey);
        }
    } else {
        // 获取锁失败的处理
        throw new RuntimeException("获取锁失败");
    }
}
```

`setIfAbsent()` 是实现分布式锁的核心方法，在缓存系统中用于防止缓存击穿，确保同一时间只有一个线程执行缓存重建操作。