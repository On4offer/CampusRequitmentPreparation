## increment() 方法介绍

### 1. 基本概念
[increment()](file://cn\hutool\json\JSONObject.java#L46-L46) 是 Spring Data Redis 提供的 Redis 操作方法，用于对 Redis 中存储的数值进行原子性递增操作，等价于 Redis 的 `INCR` 命令。

### 2. 所属体系
- **框架**：Spring Data Redis
- **类**：`org.springframework.data.redis.core.ValueOperations<K, V>`
- **Redis 命令等价**：`INCR`、`INCRBY`

### 3. 功能作用
[increment()](file://cn\hutool\json\JSONObject.java#L46-L46) 方法用于：
1. **原子递增**：对指定键的数值进行原子性递增操作
2. **自动初始化**：如果键不存在，自动初始化为 0 后再递增
3. **线程安全**：Redis 单线程特性保证操作的原子性
4. **分布式计数**：在分布式环境中实现安全的计数器

### 4. 方法签名

```java
// 递增1
Long increment(K key);

// 递增指定值
Long increment(K key, long delta);

// 递增指定值（double）
Double increment(K key, double delta);

// 带过期时间的递增
Long increment(K key, long delta, long timeout, TimeUnit unit);
```


### 5. 在代码中的使用

```java
// 在 RedisIdWorker 类中使用
public long nextId(String keyPrefix) {
    // ...
    // 2.生成序列号
    // 2.1.获取当前日期，精确到天
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
    // 2.2.自增长；Redis 执行 INCR 命令
    long count = stringRedisTemplate.opsForValue().increment("icr:" + keyPrefix + ":" + date);  // ← 这里调用 increment() 方法
    // ...
}
```


### 6. Redis 命令对照

```java
// Java 代码
long count = stringRedisTemplate.opsForValue().increment("icr:order:2024:01:15");

// 等价的 Redis 命令
INCR icr:order:2024:01:15
```


### 7. 使用示例

#### (1) 基本递增
```java
// 递增1
Long newValue = stringRedisTemplate.opsForValue().increment("counter");

// 递增指定值
Long newValue = stringRedisTemplate.opsForValue().increment("counter", 5);

// 递增浮点数
Double newValue = stringRedisTemplate.opsForValue().increment("score", 1.5);
```


#### (2) 在 ID 生成器中的应用
```java
// 生成按天分隔的序列号
LocalDateTime now = LocalDateTime.now();
String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
String key = "icr:order:" + date;  // icr:order:2024:01:15

// 原子递增获取序列号
long sequence = stringRedisTemplate.opsForValue().increment(key);
```


### 8. 在 ID 生成器中的作用

```java
public long nextId(String keyPrefix) {
    // 1.生成时间戳
    LocalDateTime now = LocalDateTime.now();
    long nowSecond = now.toEpochSecond(ZoneOffset.UTC);
    long timestamp = nowSecond - BEGIN_TIMESTAMP;
    
    // 2.生成序列号
    // 2.1.获取当前日期，精确到天
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
    // 2.2.自增长；获取当天该业务的序列号
    long count = stringRedisTemplate.opsForValue().increment("icr:" + keyPrefix + ":" + date);
    
    // 3.拼接并返回
    return timestamp << COUNT_BITS | count;
}
```


### 9. 相关 Redis 操作方法对比

| 方法                                                         | Redis 命令         | 功能       |
| ------------------------------------------------------------ | ------------------ | ---------- |
| [increment(key)](file://cn\hutool\json\JSONObject.java#L46-L46) | `INCR key`         | 递增1      |
| [increment(key, delta)](file://cn\hutool\json\JSONObject.java#L46-L46) | `INCRBY key delta` | 递增指定值 |
| `decrement(key)`                                             | `DECR key`         | 递减1      |
| `decrement(key, delta)`                                      | `DECRBY key delta` | 递减指定值 |

### 10. 优势

1. **原子性**：Redis 单线程保证操作原子性
2. **高性能**：基于内存操作，速度极快
3. **分布式支持**：多个应用实例共享同一计数器
4. **自动初始化**：键不存在时自动初始化为0
5. **线程安全**：无需额外同步措施

### 11. 注意事项

#### (1) 键的生命周期
```java
// 可以设置过期时间
long count = stringRedisTemplate.opsForValue().increment(key, 1, 24, TimeUnit.HOURS);
```


#### (2) 返回值类型
```java
// increment 返回 Long 类型
Long count = stringRedisTemplate.opsForValue().increment(key);
```


#### (3) 键不存在的处理
```java
// 如果键不存在，Redis 会自动创建并初始化为 0，然后执行递增
// 第一次调用 increment("newkey") 返回 1
```


### 12. 在分布式系统中的重要性

```java
// 分布式唯一序列号生成
public long nextId(String keyPrefix) {
    LocalDateTime now = LocalDateTime.now();
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
    String key = "icr:" + keyPrefix + ":" + date;
    
    // 多个应用实例共享同一个 Redis 计数器
    // 保证全局唯一性
    long count = stringRedisTemplate.opsForValue().increment(key);
    
    return count;
}
```


### 13. 完整执行流程示例

```java
// 假设有多个应用实例同时调用
// 实例A调用:
long count1 = stringRedisTemplate.opsForValue().increment("icr:order:2024:01:15"); // 返回 1

// 实例B调用:
long count2 = stringRedisTemplate.opsForValue().increment("icr:order:2024:01:15"); // 返回 2

// 实例C调用:
long count3 = stringRedisTemplate.opsForValue().increment("icr:order:2024:01:15"); // 返回 3
```


[increment()](file://cn\hutool\json\JSONObject.java#L46-L46) 方法在分布式 ID 生成器中起到了关键作用，它利用 Redis 的原子性递增操作，为每个业务每天生成唯一的序列号，确保了在高并发分布式环境下的 ID 唯一性。