## block() 方法介绍

### 1. 基本概念
`block()` 是 Spring Data Redis 中 `StreamReadOptions` 类的实例方法，用于设置 Redis Stream 读取操作的阻塞超时时间。

### 2. 所属体系
- **类**：`org.springframework.data.redis.connection.stream.StreamReadOptions`
- **框架**：Spring Data Redis
- **Redis 命令等价**：`BLOCK` 选项

### 3. 功能作用
`block()` 方法用于：
1. **设置阻塞超时**：指定读取 Stream 时的阻塞等待时间
2. **避免忙等待**：防止频繁轮询消耗 CPU 资源
3. **提高效率**：在没有新消息时让线程休眠，有消息时立即唤醒
4. **资源优化**：合理利用系统资源

### 4. 方法签名

```java
// 接受 Duration 参数版本
public StreamReadOptions block(Duration timeout) {
    // 设置阻塞超时时间
    this.block = timeout.toMillis();
    return this;
}

// 接受 long 参数版本（已废弃）
@Deprecated
public StreamReadOptions block(long timeout) {
    this.block = timeout;
    return this;
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
                        StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2)),  // ← 这里调用 block() 方法
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
.block(Duration.ofSeconds(2))
//       ↑
//       └── 阻塞超时时间: 2秒

// 其他常用的时间单位
.block(Duration.ofMillis(500))    // 500毫秒
.block(Duration.ofMinutes(1))     // 1分钟
.block(Duration.ofHours(1))       // 1小时
```


### 7. Redis 命令对照

```java
// Java 代码
StreamReadOptions.empty().block(Duration.ofSeconds(2))

// 等价的 Redis 命令
XREADGROUP GROUP g1 c1 BLOCK 2000 STREAMS stream.orders >
//                        ↑
//                        └── block(2秒) = 2000毫秒
```


### 8. 使用示例

#### (1) 基本使用
```java
// 阻塞等待2秒
StreamReadOptions options = StreamReadOptions.empty().block(Duration.ofSeconds(2));

// 阻塞等待500毫秒
StreamReadOptions options = StreamReadOptions.empty().block(Duration.ofMillis(500));
```


#### (2) 链式调用
```java
// 组合多个选项
StreamReadOptions options = StreamReadOptions.empty()
    .count(10)                    // 读取10条消息
    .block(Duration.ofSeconds(5)); // 阻塞等待5秒
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
                            .count(1)                      // 一次读取1条消息
                            .block(Duration.ofSeconds(2)), // 阻塞等待2秒
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
                );
                
                // 工作机制:
                // 1. 如果有消息，立即返回
                // 2. 如果没有消息，阻塞等待最多2秒
                // 3. 2秒后仍无消息，返回空列表
                // 4. 继续下一次循环
                
            } catch (Exception e) {
                log.error("处理订单异常", e);
            }
        }
    }
}
```


### 10. 阻塞与非阻塞对比

#### (1) 阻塞模式
```java
// 阻塞读取
StreamReadOptions.empty().block(Duration.ofSeconds(2))
// 优点: 节省CPU资源，及时响应新消息
// 缺点: 线程在等待期间无法处理其他任务
```


#### (2) 非阻塞模式
```java
// 非阻塞读取（不设置block）
StreamReadOptions.empty().count(1)
// 优点: 线程可以快速返回处理其他逻辑
// 缺点: 频繁轮询消耗CPU资源
```


### 11. 优势

1. **资源友好**：避免忙等待，节省CPU资源
2. **及时响应**：有新消息时能立即唤醒处理
3. **可控超时**：可以设置合理的超时时间
4. **链式调用**：与其他选项组合使用方便
5. **类型安全**：使用 Duration 类型确保时间单位正确

### 12. 注意事项

#### (1) 时间单位
```java
// 推荐使用 Duration（类型安全）
.block(Duration.ofSeconds(2))    // 推荐
.block(Duration.ofMillis(2000))  // 推荐

// 避免直接使用毫秒数（容易出错）
// .block(2000)  // 不推荐，不清楚单位
```


#### (2) 合理设置超时时间
```java
// 太短: 频繁唤醒，消耗资源
.block(Duration.ofMillis(100))  // 可能过于频繁

// 太长: 响应延迟
.block(Duration.ofMinutes(5))   // 可能响应太慢

// 合适: 1-5秒通常比较合理
.block(Duration.ofSeconds(2))   // 推荐
```


#### (3) 异常处理
```java
try {
    List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
        Consumer.from("g1", "c1"),
        StreamReadOptions.empty().block(Duration.ofSeconds(2)),
        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
    );
} catch (Exception e) {
    // 处理网络异常、Redis连接异常等
}
```


### 13. 完整示例

```java
// 不同的阻塞配置示例

// 1. 短时间阻塞（高响应性）
StreamReadOptions options1 = StreamReadOptions.empty()
    .count(1)
    .block(Duration.ofSeconds(1));  // 等待1秒

// 2. 中等时间阻塞（平衡性能）
StreamReadOptions options2 = StreamReadOptions.empty()
    .count(5)
    .block(Duration.ofSeconds(3));  // 等待3秒

// 3. 长时间阻塞（节省资源）
StreamReadOptions options3 = StreamReadOptions.empty()
    .count(10)
    .block(Duration.ofSeconds(10)); // 等待10秒

// 4. 无阻塞（轮询模式）
StreamReadOptions options4 = StreamReadOptions.empty()
    .count(1);
    // 不设置 block，立即返回
```


`block(Duration.ofSeconds(2))` 方法在秒杀系统中用于设置 Stream 读取的阻塞超时时间，通过合理的阻塞等待机制，在没有新订单消息时让处理线程休眠，既节省了系统资源又保证了消息处理的及时性。