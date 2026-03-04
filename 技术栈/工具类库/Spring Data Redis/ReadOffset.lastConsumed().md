## ReadOffset.lastConsumed() 方法介绍

### 1. 基本概念
`ReadOffset.lastConsumed()` 是 Spring Data Redis 中 `ReadOffset` 类的静态工厂方法，用于创建表示"读取未消费消息"的偏移量对象，主要用于 Redis Stream 的消费组模式。

### 2. 所属体系
- **类**：`org.springframework.data.redis.connection.stream.ReadOffset`
- **框架**：Spring Data Redis
- **Redis 命令等价**：`>` 符号

### 3. 功能作用
`ReadOffset.lastConsumed()` 方法用于：
1. **指定读取位置**：指示从 Redis Stream 中未被当前消费组消费的消息开始读取
2. **消费组支持**：配合消费组模式使用，实现消息的负载均衡分发
3. **避免重复消费**：确保每条消息只被消费组内的一个消费者处理
4. **Pending List 管理**：与消息确认机制配合，管理未确认的消息

### 4. 方法签名

```java
// 静态工厂方法
public static ReadOffset lastConsumed() {
    return new ReadOffset(CONSUMED_ONCE);  // CONSUMED_ONCE = ">"
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
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())  // ← 这里调用 lastConsumed() 方法
                );
                // ...
            } catch (Exception e) {
                // ...
            }
        }
    }
}
```


### 6. Redis 命令对照

```java
// Java 代码
ReadOffset.lastConsumed()

// 等价的 Redis 命令
XREADGROUP GROUP g1 c1 STREAMS stream.orders >
//                                    ↑
//                                    └── lastConsumed() 对应 ">"
```


### 7. ReadOffset 类的其他静态方法

```java
// 不同的读取偏移量类型
ReadOffset.lastConsumed()        // > : 未消费的消息
ReadOffset.fromStart()           // $ : Stream 开始位置
ReadOffset.latest()              // $ : 最新消息
ReadOffset.from("12345-0")       // 12345-0 : 特定消息ID
ReadOffset.from("0")             // 0 : Pending List 消息
```


### 8. 使用示例

#### (1) 消费组模式读取
```java
// 读取未消费的消息
StreamOffset.create("mystream", ReadOffset.lastConsumed());

// 等价的 Redis 命令
XREADGROUP GROUP mygroup myconsumer STREAMS mystream >
```


#### (2) 不同读取模式对比
```java
// 1. 消费组模式 - 读取未消费消息
StreamOffset.create("orders", ReadOffset.lastConsumed());  // XREADGROUP ... STREAMS orders >

// 2. 普通模式 - 从开始读取
StreamOffset.create("orders", ReadOffset.fromStart());     // XREAD ... STREAMS orders 0

// 3. 普通模式 - 读取最新消息
StreamOffset.create("orders", ReadOffset.latest());        // XREAD ... STREAMS orders $

// 4. 消费组模式 - 处理异常消息
StreamOffset.create("orders", ReadOffset.from("0"));       // XREADGROUP ... STREAMS orders 0
```


### 9. 在秒杀系统中的应用

```java
// 正常订单处理
private class VoucherOrderHandler implements Runnable {
    @Override
    public void run() {
        while (true) {
            try {
                List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
                        Consumer.from("g1", "c1"),  // 消费组: g1, 消费者: c1
                        StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2)),
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())  // 读取未消费的消息
                );
                
                // 工作机制:
                // 1. Redis 自动分配未消费的消息给当前消费者
                // 2. 消息被标记为"正在处理"状态
                // 3. 如果处理成功，需要手动确认 (XACK)
                // 4. 如果处理失败，消息进入 Pending List
                
            } catch (Exception e) {
                log.error("处理订单异常", e);
                handlePendingList();  // 处理异常消息
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


### 10. 消费组工作机制

```java
// Redis Stream 消费组工作流程示例

// 1. 创建消费组
XGROUP CREATE mystream mygroup 0

// 2. 添加消息
XADD mystream * field1 value1  // 生成ID: 1640995200000-0
XADD mystream * field2 value2  // 生成ID: 1640995200001-0

// 3. 消费者1读取消息
XREADGROUP GROUP mygroup consumer1 COUNT 1 STREAMS mystream >
// 返回: 1640995200000-0 (消息被分配给 consumer1)

// 4. 消费者2读取消息
XREADGROUP GROUP mygroup consumer2 COUNT 1 STREAMS mystream >
// 返回: 1640995200001-0 (消息被分配给 consumer2)

// 5. 确认消息处理完成
XACK mystream mygroup 1640995200000-0
```


### 11. 优势

1. **负载均衡**：消费组内的多个消费者自动分配消息
2. **故障恢复**：未确认的消息可以被其他消费者处理
3. **消息可靠性**：通过 Pending List 机制确保消息不丢失
4. **类型安全**：提供类型安全的偏移量表示
5. **API 统一**：与其他 Stream 操作无缝集成

### 12. 注意事项

#### (1) 消息确认
```java
// 读取消息后必须确认
List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
    Consumer.from("g1", "c1"),
    StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
);

if (!list.isEmpty()) {
    MapRecord<String, Object, Object> record = list.get(0);
    // 处理消息...
    
    // 必须确认消息处理完成
    stringRedisTemplate.opsForStream().acknowledge("stream.orders", "g1", record.getId());
}
```


#### (2) Pending List 处理
```java
// 定期处理未确认的消息
StreamOffset.create("stream.orders", ReadOffset.from("0"));  // 读取 Pending List
```


### 13. 完整示例

```java
// 不同的 ReadOffset 使用场景

// 1. 消费组模式 - 正常消费
StreamOffset.create("orders", ReadOffset.lastConsumed());  // 读取未消费消息

// 2. 消费组模式 - 处理异常
StreamOffset.create("orders", ReadOffset.from("0"));       // 读取 Pending List

// 3. 普通模式 - 从头开始
StreamOffset.create("orders", ReadOffset.fromStart());     // 从 Stream 开始读取

// 4. 普通模式 - 实时监听
StreamOffset.create("orders", ReadOffset.latest());        // 只读取新消息

// 5. 指定位置读取
StreamOffset.create("orders", ReadOffset.from("1640995200000-0"));  // 从特定ID开始
```


`ReadOffset.lastConsumed()` 方法在秒杀系统中用于指定从 Redis Stream 的未消费消息开始读取，配合消费组模式实现订单消息的分布式处理，确保每条订单消息只被一个消费者处理且不会丢失。