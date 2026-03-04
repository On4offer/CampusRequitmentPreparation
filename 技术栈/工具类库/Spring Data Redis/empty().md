## StreamReadOptions.empty() 方法介绍

### 1. 基本概念
`empty()` 是 Spring Data Redis 中 `StreamReadOptions` 类的静态工厂方法，用于创建一个空的（默认的）流读取选项对象。

### 2. 所属体系
- **类**：`org.springframework.data.redis.connection.stream.StreamReadOptions`
- **框架**：Spring Data Redis
- **类型**：静态工厂方法

### 3. 功能作用
`empty()` 方法用于：
1. **创建默认选项**：创建一个不包含任何特殊配置的 Stream 读取选项对象
2. **链式调用起点**：作为链式调用的起点，可以继续添加其他选项
3. **简化配置**：提供简洁的 API 来构建读取选项

### 4. 方法签名

```java
// 静态工厂方法
public static StreamReadOptions empty() {
    return new StreamReadOptions();
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
                        StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2)),  // ← 这里调用 empty() 方法
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


### 6. StreamReadOptions 类结构

```java
public class StreamReadOptions {
    private Long block;
    private Long count;
    private Boolean noack;
    
    // 私有构造函数
    private StreamReadOptions() {}
    
    // 静态工厂方法
    public static StreamReadOptions empty() {
        return new StreamReadOptions();
    }
    
    // 链式配置方法
    public StreamReadOptions count(long count) { /* ... */ }
    public StreamReadOptions block(Duration timeout) { /* ... */ }
    public StreamReadOptions noack() { /* ... */ }
    
    // getter 方法
    public Optional<Long> getCount() { /* ... */ }
    public Optional<Long> getBlock() { /* ... */ }
    public boolean isNoack() { /* ... */ }
}
```


### 7. 链式调用示例

#### (1) 基本使用
```java
// 创建默认选项并添加配置
StreamReadOptions options = StreamReadOptions.empty()
    .count(10)                    // 读取10条消息
    .block(Duration.ofSeconds(5)); // 阻塞等待5秒
```


#### (2) 各种组合
```java
// 仅限制数量
StreamReadOptions options1 = StreamReadOptions.empty().count(1);

// 仅阻塞等待
StreamReadOptions options2 = StreamReadOptions.empty().block(Duration.ofSeconds(2));

// 数量+阻塞+无确认模式
StreamReadOptions options3 = StreamReadOptions.empty()
    .count(5)
    .block(Duration.ofSeconds(10))
    .noack();  // 不需要确认消息
```


### 8. Redis 命令对照

```java
// Java 代码
StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2))

// 等价的 Redis 命令
XREADGROUP GROUP g1 c1 COUNT 1 BLOCK 2000 STREAMS stream.orders >
//                        ↑      ↑
//                        │      └── block(2秒)
//                        └───────── count(1)
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
                        StreamReadOptions.empty()           // 创建默认选项
                            .count(1)                      // 一次只读取1条消息
                            .block(Duration.ofSeconds(2)), // 阻塞等待2秒
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
                );
                
                // 这样配置的好处:
                // 1. count(1): 避免一次性处理过多消息导致阻塞
                // 2. block(2): 避免频繁轮询，节省CPU资源
            } catch (Exception e) {
                // ...
            }
        }
    }
}
```


### 10. 相关方法对比

| 方法                        | 用途       | 特点                             |
| --------------------------- | ---------- | -------------------------------- |
| `StreamReadOptions.empty()` | 创建空选项 | 默认配置，可链式调用             |
| `new StreamReadOptions()`   | 直接构造   | 功能相同，但推荐使用静态工厂方法 |

### 11. 优势

1. **流畅API**：支持链式调用，代码可读性强
2. **类型安全**：编译时检查配置选项
3. **不可变性**：返回的对象是不可变的
4. **默认安全**：提供合理的默认行为
5. **扩展性好**：易于添加新的配置选项

### 12. 注意事项

#### (1) 链式调用
```java
// 推荐方式：链式调用
StreamReadOptions options = StreamReadOptions.empty()
    .count(1)
    .block(Duration.ofSeconds(2));

// 不推荐：多次调用 empty()
// StreamReadOptions.empty().count(1);
// StreamReadOptions.empty().block(Duration.ofSeconds(2)); // 前面的配置会丢失
```


#### (2) 参数类型
```java
// block 接受 Duration 类型
.block(Duration.ofSeconds(2))
.block(Duration.ofMillis(500))

// count 接受 long 类型
.count(1)
.count(10L)
```


### 13. 完整示例

```java
// 不同的配置选项示例

// 1. 基本配置：读取1条消息，阻塞2秒
StreamReadOptions options1 = StreamReadOptions.empty()
    .count(1)
    .block(Duration.ofSeconds(2));

// 2. 批量处理：读取10条消息，阻塞5秒
StreamReadOptions options2 = StreamReadOptions.empty()
    .count(10)
    .block(Duration.ofSeconds(5));

// 3. 无确认模式：读取消息后不需要手动确认
StreamReadOptions options3 = StreamReadOptions.empty()
    .count(5)
    .noack();  // 消息读取后自动确认

// 4. 纯轮询：立即返回，不阻塞
StreamReadOptions options4 = StreamReadOptions.empty()
    .count(1);
    // 不设置 block，立即返回结果
```


`StreamReadOptions.empty()` 方法在秒杀系统中用于创建 Stream 读取的配置选项，通过链式调用的方式灵活配置读取消息的数量和阻塞等待时间，实现了高效且资源友好的消息处理机制。