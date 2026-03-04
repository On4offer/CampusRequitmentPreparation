## MapRecord 类介绍

### 1. 基本概念
`MapRecord` 是 Spring Data Redis 中用于表示 Redis Stream 消息记录的泛型类，它封装了从 Redis Stream 中读取的消息数据。

### 2. 所属体系
- **包**：`org.springframework.data.redis.connection.stream`
- **框架**：Spring Data Redis
- **类型**：泛型数据容器类
- **JDK 版本**：Spring Data Redis 2.2+

### 3. 功能作用
`MapRecord` 类用于：
1. **封装消息数据**：存储从 Redis Stream 读取的消息记录
2. **提供访问接口**：提供获取消息 ID、键值对等信息的方法
3. **类型安全**：通过泛型确保类型安全
4. **数据传输**：作为消息在应用间传输的载体

### 4. 类结构定义

```java
public class MapRecord<K, HK, HV> implements Record<K, Map<HK, HV>> {
    private final K stream;
    private final RecordId id;
    private final Map<HK, HV> value;
    
    // 构造方法、getter方法等...
}
```


### 5. 泛型参数说明

```java
MapRecord<String, Object, Object>
//         ↑     ↑      ↑
//         │     │      └── Value类型 (消息值的类型)
//         │     └───────── Key类型 (消息键的类型)  
//         └─────────────── Stream Key类型 (Stream名称类型)
```


### 6. 在代码中的使用

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
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
                );
                
                // 2.判断订单信息是否为空
                if (list == null || list.isEmpty()) {
                    continue;
                }
                
                // 3.解析数据
                MapRecord<String, Object, Object> record = list.get(0);  // ← 使用 MapRecord
                Map<Object, Object> value = record.getValue();           // ← 获取消息内容
                VoucherOrder voucherOrder = BeanUtil.fillBeanWithMap(value, new VoucherOrder(), true);
                
                // ...
            } catch (Exception e) {
                // ...
            }
        }
    }
}
```


### 7. 主要方法

#### (1) 获取基本信息
```java
// 获取消息 ID
RecordId getId();

// 获取 Stream 名称
String getStream();

// 获取消息内容
Map<HK, HV> getValue();
```


#### (2) 使用示例
```java
// 从 Stream 读取消息
List<MapRecord<String, Object, Object>> records = stringRedisTemplate.opsForStream().read(
    StreamOffset.fromStart("mystream")
);

if (!records.isEmpty()) {
    MapRecord<String, Object, Object> record = records.get(0);
    
    // 获取消息 ID
    RecordId recordId = record.getId();  // 例如: 1640995200000-0
    
    // 获取 Stream 名称
    String streamName = record.getStream();  // 例如: "mystream"
    
    // 获取消息内容
    Map<Object, Object> messageData = record.getValue();
    // 例如: {voucherId=1, userId=1001, orderId=12345}
}
```


### 8. 在秒杀系统中的应用

```java
private class VoucherOrderHandler implements Runnable {
    @Override
    public void run() {
        while (true) {
            try {
                // 1. 读取 Stream 消息
                List<MapRecord<String, Object, Object>> list = stringRedisTemplate.opsForStream().read(
                        Consumer.from("g1", "c1"),
                        StreamReadOptions.empty().count(1).block(Duration.ofSeconds(2)),
                        StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
                );
                
                if (list != null && !list.isEmpty()) {
                    // 2. 解析 MapRecord
                    MapRecord<String, Object, Object> record = list.get(0);
                    
                    // 3. 获取消息内容
                    Map<Object, Object> value = record.getValue();
                    // value 内容示例: {id=12345, userId=1001, voucherId=1}
                    
                    // 4. 转换为业务对象
                    VoucherOrder voucherOrder = BeanUtil.fillBeanWithMap(value, new VoucherOrder(), true);
                    
                    // 5. 处理订单
                    createVoucherOrder(voucherOrder);
                    
                    // 6. 确认消息
                    stringRedisTemplate.opsForStream().acknowledge("s1", "g1", record.getId());
                }
            } catch (Exception e) {
                log.error("处理订单异常", e);
            }
        }
    }
}
```


### 9. 与其他 Record 类型的关系

```java
// Spring Data Redis 中的 Record 类型体系
public interface Record<K, V> {
    K getStream();
    RecordId getId();
    V getValue();
}

// MapRecord: 键值对形式的消息
MapRecord<String, Object, Object>

// ObjectRecord: 对象形式的消息
ObjectRecord<String, MyObject>
```


### 10. 优势

1. **类型安全**：通过泛型确保编译时类型检查
2. **结构清晰**：明确区分 Stream 名称、消息 ID 和消息内容
3. **易于使用**：提供直观的 getter 方法
4. **框架集成**：与 Spring Data Redis 无缝集成
5. **扩展性好**：支持自定义序列化和反序列化

### 11. 注意事项

#### (1) 数据转换
```java
// 需要将 Map 转换为业务对象
Map<Object, Object> value = record.getValue();
VoucherOrder voucherOrder = BeanUtil.fillBeanWithMap(value, new VoucherOrder(), true);
```


#### (2) 异常处理
```java
try {
    MapRecord<String, Object, Object> record = list.get(0);
    Map<Object, Object> value = record.getValue();
    // 处理数据
} catch (IndexOutOfBoundsException e) {
    // 处理空列表情况
} catch (Exception e) {
    // 处理转换异常
}
```


### 12. 完整示例

```java
// Redis Stream 消息结构示例
// Stream: stream.orders
// Message: 
//   ID: 1640995200000-0
//   Data: {id=12345, userId=1001, voucherId=1}

// 读取和处理过程
List<MapRecord<String, Object, Object>> records = stringRedisTemplate.opsForStream().read(
    Consumer.from("g1", "c1"),
    StreamReadOptions.empty().count(1),
    StreamOffset.create("stream.orders", ReadOffset.lastConsumed())
);

if (!records.isEmpty()) {
    MapRecord<String, Object, Object> record = records.get(0);
    
    System.out.println("Stream: " + record.getStream());     // stream.orders
    System.out.println("ID: " + record.getId().getValue());  // 1640995200000-0
    
    Map<Object, Object> data = record.getValue();
    System.out.println("Data: " + data);  // {id=12345, userId=1001, voucherId=1}
    
    // 转换为业务对象进行处理
}
```


`MapRecord<String, Object, Object>` 是 Spring Data Redis 中用于处理 Redis Stream 消息的核心数据结构，它封装了消息的完整信息，为异步订单处理提供了可靠的数据传输载体。