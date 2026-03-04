## StreamOffset.create() 方法介绍

### 1. 基本概念
[create()](file://org\redisson\Redisson.java#L86-L86) 是 Spring Data Redis 中 `StreamOffset` 类的静态工厂方法，用于创建表示 Redis Stream 读取偏移量的 StreamOffset 对象。

### 2. 所属体系
- **类**：`org.springframework.data.redis.connection.stream.StreamOffset`
- **框架**：Spring Data Redis

### 3. 功能作用
[create()](file://org\redisson\Redisson.java#L86-L86) 方法用于：
1. **指定读取位置**：指定从 Redis Stream 的哪个位置开始读取消息
2. **关联 Stream**：将偏移量与特定的 Stream 键关联
3. **支持多种偏移量**：支持不同的偏移量类型（开始、结束、特定ID等）
4. **类型安全**：提供类型安全的 Stream 读取位置表示

### 4. 方法签名

```java
// 基本版本：指定 Stream 键和读取偏移量
public static <K> StreamOffset<K> create(K key, ReadOffset offset) {
    return new StreamOffset<>(key, offset);
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
                        StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2)),
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())  // ← 这里调用 create() 方法
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
StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
//                ↑                ↑
//                │                └── 读取偏移量
//                └─────────────────── Stream 键名
```


### 7. ReadOffset 的常用静态方法

```java
// 不同的读取偏移量
ReadOffset.from("1640995200000-0")  // 从指定ID开始读取
ReadOffset.lastConsumed()           // 读取未消费的消息（消费组模式）
ReadOffset.latest()                 // 读取最新消息
ReadOffset.fromStart()              // 从Stream开始位置读取
ReadOffset.fromEnd()                // 从Stream结束位置读取
```


### 8. Redis 命令对照

```java
// Java 代码
StreamOffset.create("stream.orders", ReadOffset.lastConsumed())

// 等价的 Redis 命令
XREADGROUP GROUP g1 c1 STREAMS stream.orders >
//                                    ↑
//                                    └── lastConsumed() 对应 ">"
```


### 9. 使用示例

#### (1) 基本使用
```java
// 从未消费的消息开始读取（消费组模式）
StreamOffset.create("mystream", ReadOffset.lastConsumed());

// 从Stream开始位置读取
StreamOffset.create("mystream", ReadOffset.fromStart());

// 从特定ID开始读取
StreamOffset.create("mystream", ReadOffset.from("1640995200000-0"));
```


#### (2) 不同场景的应用
```java
// 正常消费消息
StreamOffset.create("stream.orders", ReadOffset.lastConsumed());

// 处理异常消息（Pending List）
StreamOffset.create("stream.orders", ReadOffset.from("0"));
```


### 10. 在秒杀系统中的应用

```java
// 正常订单处理
private class VoucherOrderHandler implements Runnable {
    @Override
    public void run() {
        while (true) {
            try {
                List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
                        Consumer.from("g1", "c1"),
                        StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2)),
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())  // 读取未消费的消息
                );
                // ...
            } catch (Exception e) {
                // 处理异常时读取 Pending List
                handlePendingList();
            }
        }
    }
}

// 处理 Pending List（异常消息）
private void handlePendingList() {
    while (true) {
        try {
            List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
                    Consumer.from("g1", "c1"),
                    StreamReadOptions.empty().count(1),
                    StreamOffset.create("stream.orders", ReadOffset.from("0"))  // 读取 Pending List
            );
            // ...
        } catch (Exception e) {
            // ...
        }
    }
}
```


### 11. StreamOffset 的其他静态方法

```java
// 直接创建特定偏移量的 StreamOffset
StreamOffset.create("mystream", "1640995200000-0");  // 等价于 ReadOffset.from()
StreamOffset.fromStart("mystream");                 // 等价于 ReadOffset.fromStart()
StreamOffset.latest("mystream");                    // 等价于 ReadOffset.latest()
```


### 12. 优势

1. **类型安全**：编译时检查 Stream 键和偏移量类型
2. **API 统一**：提供统一的 Stream 读取位置表示
3. **可读性强**：方法名明确表示读取位置意图
4. **功能完整**：支持所有 Redis Stream 读取模式
5. **链式调用**：与其他 Stream 操作无缝集成

### 13. 注意事项

#### (1) 消费组模式
```java
// 消费组模式下使用 lastConsumed()
StreamOffset.create("stream.orders", ReadOffset.lastConsumed());
// 等价于 Redis 命令中的 ">"
```


#### (2) Pending List 处理
```java
// 处理异常消息时使用 "0" 作为偏移量
StreamOffset.create("stream.orders", ReadOffset.from("0"));
// 等价于 Redis 命令中的 "0"
```


#### (3) 普通读取模式
```java
// 普通读取模式使用具体ID
StreamOffset.create("mystream", ReadOffset.from("1640995200000-0"));
```


### 14. 完整示例

```java
// 不同的 StreamOffset 配置示例

// 1. 消费组模式 - 读取未消费消息
StreamOffset.create("stream.orders", ReadOffset.lastConsumed());

// 2. 消费组模式 - 处理 Pending List
StreamOffset.create("stream.orders", ReadOffset.from("0"));

// 3. 普通模式 - 从开始位置读取
StreamOffset.create("mystream", ReadOffset.fromStart());

// 4. 普通模式 - 从特定ID读取
StreamOffset.create("mystream", ReadOffset.from("1640995200000-0"));

// 5. 普通模式 - 读取最新消息
StreamOffset.create("mystream", ReadOffset.latest());
```


`StreamOffset.create("stream.orders", ReadOffset.lastConsumed())` 方法在秒杀系统中用于指定从 Redis Stream 的未消费消息开始读取，配合消费组模式实现订单消息的可靠处理和负载均衡分配。