## Redis set 方法介绍

### 1. 基本概念
这里的 [set](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\CacheClient.java#L32-L34) 方法是 Spring Data Redis 提供的操作 Redis 的方法，用于向 Redis 中存储键值对数据。

### 2. 所属体系
- **框架**：Spring Data Redis
- **类**：`org.springframework.data.redis.core.ValueOperations<K, V>`
- **方法签名**：`void set(K key, V value, long timeout, TimeUnit unit)`

### 3. 功能作用
Redis 的 [set](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\CacheClient.java#L32-L34) 方法用于：
1. **存储键值对**：将指定的键值对存储到 Redis 数据库中
2. **设置过期时间**：为存储的键值对设置生存时间（TTL）
3. **原子操作**：保证存储操作的原子性

### 4. 方法定义

```java
// ValueOperations 接口中的 set 方法定义
void set(K key, V value, long timeout, TimeUnit unit);

// 参数说明:
// key: 存储的键
// value: 存储的值
// timeout: 过期时间数值
// unit: 时间单位
```


### 5. 在代码中的使用

```java
// 用于缓存空值，防止缓存穿透
stringRedisTemplate.opsForValue().set(key, "", CACHE_NULL_TTL, TimeUnit.MINUTES);
```


在这段代码中，当数据库查询结果为空时，将空字符串存储到 Redis 中，并设置较短的过期时间，以防止缓存穿透问题。

### 6. 使用示例

#### (1) 基本使用
```java
// 存储字符串值，设置过期时间
stringRedisTemplate.opsForValue().set("username", "张三", 30, TimeUnit.MINUTES);

// 存储空值防止缓存穿透
stringRedisTemplate.opsForValue().set("user:123", "", 2, TimeUnit.MINUTES);
```


#### (2) 不同数据类型存储
```java
// 存储数字
stringRedisTemplate.opsForValue().set("count", "100", 1, TimeUnit.HOURS);

// 存储 JSON 字符串
stringRedisTemplate.opsForValue().set("user:1", "{\"name\":\"张三\"}", 30, TimeUnit.MINUTES);
```


### 7. 在缓存逻辑中的作用

```java
// 防止缓存穿透的关键代码
if (r == null) {
    // 当数据库查询结果为空时，存储空字符串到 Redis
    // 并设置较短的过期时间，防止大量请求直接打到数据库
    stringRedisTemplate.opsForValue().set(key, "", CACHE_NULL_TTL, TimeUnit.MINUTES);
    return null;
}
```


### 8. 相关 Redis 操作方法对比

| 方法                                                         | 用途                             | 是否设置过期时间 |
| ------------------------------------------------------------ | -------------------------------- | ---------------- |
| [set(K key, V value)](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\CacheClient.java#L32-L34) | 存储键值对                       | 否               |
| `set(K key, V value, long timeout, TimeUnit unit)`           | 存储键值对并设置过期时间         | 是               |
| `setIfAbsent(K key, V value)`                                | 仅当键不存在时存储               | 否               |
| `setIfAbsent(K key, V value, long timeout, TimeUnit unit)`   | 仅当键不存在时存储并设置过期时间 | 是               |

### 9. 优势

1. **集成性好**：与 Spring 框架无缝集成
2. **类型安全**：提供泛型支持
3. **功能丰富**：支持多种 Redis 数据结构操作
4. **连接管理**：自动管理 Redis 连接
5. **序列化支持**：支持自定义序列化方式

### 10. 与原生 Redis 命令对比

```java
// Spring Data Redis 写法
stringRedisTemplate.opsForValue().set("key", "value", 30, TimeUnit.MINUTES);

// 等价的原生 Redis 命令
// SETEX key 1800 "value"
// (1800秒 = 30分钟)
```


### 11. 注意事项

```java
// 正确使用
stringRedisTemplate.opsForValue().set(key, "", CACHE_NULL_TTL, TimeUnit.MINUTES);

// 需要注意过期时间设置
// 对于空值缓存，通常设置较短的过期时间
stringRedisTemplate.opsForValue().set(key, "", 2, TimeUnit.MINUTES);

// 需要异常处理
try {
    stringRedisTemplate.opsForValue().set(key, value, timeout, unit);
} catch (Exception e) {
    // 处理 Redis 操作异常
}
```


### 12. 在防缓存穿透中的应用

```java
// 缓存穿透防护机制
public <R,ID> R queryWithPassThrough(...) {
    // ...查询逻辑
    
    // 数据库查询结果为空
    if (r == null) {
        // 存储空值到 Redis，防止相同请求重复查询数据库
        stringRedisTemplate.opsForValue().set(key, "", CACHE_NULL_TTL, TimeUnit.MINUTES);
        return null;
    }
    
    // ...正常数据存储逻辑
}
```


Redis 的 [set](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\CacheClient.java#L32-L34) 方法是 Spring Data Redis 框架提供的核心操作方法之一，在分布式系统中广泛用于缓存数据存储。