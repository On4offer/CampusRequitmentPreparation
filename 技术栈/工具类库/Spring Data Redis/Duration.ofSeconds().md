## Duration.ofSeconds() 方法介绍

### 1. 基本概念
`Duration.ofSeconds()` 是 Java 8 引入的 `java.time.Duration` 类的静态工厂方法，用于创建表示秒数时间间隔的 Duration 对象。

### 2. 所属体系
- **类**：`java.time.Duration`
- **包**：`java.time`（Java 8 新的时间日期 API）
- **JDK 版本**：Java 8+

### 3. 功能作用
`Duration.ofSeconds()` 方法用于：
1. **创建时间间隔**：创建表示指定秒数的时间间隔对象
2. **类型安全**：提供类型安全的时间间隔表示
3. **API 统一**：为需要时间间隔参数的方法提供标准输入
4. **可读性强**：代码意图明确，易于理解

### 4. 方法签名

```java
// 基本版本：只指定秒数
public static Duration ofSeconds(long seconds) {
    return create(seconds, 0);
}

// 精确版本：指定秒数和纳秒
public static Duration ofSeconds(long seconds, long nanoAdjustment) {
    long secs = addExact(seconds, floorDiv(nanoAdjustment, NANOS_PER_SECOND));
    int nos = (int) floorMod(nanoAdjustment, NANOS_PER_SECOND);
    return create(secs, nos);
}
```


### 5. 在代码中的使用

```java
// 在 VoucherOrderHandler 类中使用
private class VoucherOrderHandler implements Runnable {
    @Override
    public void run() {
        while (true) {
            try {
                // 1.获取消息队列中的订单信息
                List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
                        Consumer.from("g1", "c1"),
                        StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2)),  // ← 这里调用 Duration.ofSeconds() 方法
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
                );
                // ...
            } catch (Exception e) {
                // ...
            }
        }
    }
}
```


### 6. 参数说明

```java
Duration.ofSeconds(2)
//                 ↑
//                 └── 秒数: 2秒

// 其他示例
Duration.ofSeconds(1)     // 1秒
Duration.ofSeconds(5)     // 5秒
Duration.ofSeconds(30)    // 30秒
Duration.ofSeconds(60)    // 1分钟
```


### 7. Duration 类的其他工厂方法

```java
// 不同时间单位的工厂方法
Duration.ofMillis(500)      // 500毫秒
Duration.ofMinutes(2)       // 2分钟
Duration.ofHours(1)         // 1小时
Duration.ofDays(1)          // 1天

// 通过两个时间点创建
LocalDateTime start = LocalDateTime.now();
// ... 一些操作
LocalDateTime end = LocalDateTime.now();
Duration duration = Duration.between(start, end);  // 计算时间差
```


### 8. 使用示例

#### (1) 基本使用
```java
// 创建不同时间间隔
Duration timeout1 = Duration.ofSeconds(2);    // 2秒
Duration timeout2 = Duration.ofSeconds(30);   // 30秒
Duration timeout3 = Duration.ofSeconds(60);   // 1分钟
```


#### (2) 在 Spring Data Redis 中使用
```java
// Stream 读取阻塞时间
StreamReadOptions.empty().block(Duration.ofSeconds(2));

// Redis 锁的超时时间
redisTemplate.opsForValue().setIfAbsent(key, value, Duration.ofSeconds(10));
```


### 9. 在秒杀系统中的应用

```java
private class VoucherOrderHandler implements Runnable {
    @Override
    public void run() {
        while (true) {
            try {
                List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
                        Consumer.from("g1", "c1"),
                        StreamReadOptions.empty()
                            .count(1)
                            .block(Duration.ofSeconds(2)),  // 阻塞等待2秒
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
                );
                
                // 工作机制:
                // 1. 如果有消息，立即返回处理
                // 2. 如果没有消息，最多等待2秒
                // 3. 2秒内有消息则立即处理
                // 4. 2秒后仍无消息则返回空列表继续循环
                
            } catch (Exception e) {
                log.error("处理订单异常", e);
            }
        }
    }
}
```


### 10. 与旧时间 API 的对比

#### (1) 旧的方式（不推荐）
```java
// 使用 long 毫秒数（容易混淆单位）
long timeout = 2000;  // 2000毫秒 = 2秒？不直观

// 使用 int 秒数（类型不统一）
int timeout = 2;      // 2秒？还是2毫秒？不明确
```


#### (2) 新的方式（推荐）
```java
// 使用 Duration（明确且类型安全）
Duration timeout = Duration.ofSeconds(2);  // 明确表示2秒
```


### 11. 优势

1. **类型安全**：编译时检查时间单位
2. **可读性强**：方法名明确表示时间单位
3. **API 统一**：所有需要时间间隔的地方使用统一类型
4. **防止错误**：避免毫秒和秒的单位混淆
5. **功能丰富**：Duration 类提供了丰富的操作方法

### 12. Duration 的常用操作

```java
Duration duration = Duration.ofSeconds(2);

// 获取时间单位
long seconds = duration.getSeconds();     // 2
long millis = duration.toMillis();        // 2000
long nanos = duration.toNanos();          // 2000000000

// 时间计算
Duration doubled = duration.multipliedBy(2);  // 4秒
Duration half = duration.dividedBy(2);        // 1秒

// 比较
boolean isLonger = duration.compareTo(Duration.ofSeconds(1)) > 0;  // true
```


### 13. 注意事项

#### (1) 单位明确
```java
// 推荐：明确指定单位
Duration.ofSeconds(2)     // 2秒
Duration.ofMillis(2000)   // 2000毫秒

// 避免：容易混淆
// long timeout = 2000;  // 是秒还是毫秒？
```


#### (2) 合理设置时间
```java
// 太短：频繁唤醒，消耗资源
Duration.ofMillis(100)    // 可能过于频繁

// 太长：响应延迟
Duration.ofMinutes(5)     // 可能响应太慢

// 合适：根据业务场景调整
Duration.ofSeconds(2)     // 平衡性能和响应性
```


### 14. 完整示例

```java
// 不同的时间间隔配置示例

// 1. 短时间间隔（高响应性）
StreamReadOptions.empty().block(Duration.ofSeconds(1));     // 1秒
StreamReadOptions.empty().block(Duration.ofMillis(500));    // 500毫秒

// 2. 中等时间间隔（平衡性能）
StreamReadOptions.empty().block(Duration.ofSeconds(2));     // 2秒
StreamReadOptions.empty().block(Duration.ofSeconds(5));     // 5秒

// 3. 长时间间隔（节省资源）
StreamReadOptions.empty().block(Duration.ofSeconds(10));    // 10秒
StreamReadOptions.empty().block(Duration.ofSeconds(30));    // 30秒

// 4. 其他时间单位
StreamReadOptions.empty().block(Duration.ofMinutes(1));     // 1分钟
StreamReadOptions.empty().block(Duration.ofMillis(100));    // 100毫秒
```


`Duration.ofSeconds(2)` 方法在秒杀系统中用于创建表示2秒时间间隔的 Duration 对象，作为 Redis Stream 读取操作的阻塞超时时间，通过类型安全的方式明确指定阻塞等待的时间长度，避免了时间单位混淆的问题。