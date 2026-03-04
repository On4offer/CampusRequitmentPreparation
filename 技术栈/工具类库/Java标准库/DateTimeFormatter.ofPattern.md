## DateTimeFormatter.ofPattern() 方法介绍

### 1. 基本概念
`DateTimeFormatter.ofPattern()` 是 Java 8 时间日期 API 中 `java.time.format.DateTimeFormatter` 类的静态工厂方法，用于创建自定义格式的日期时间格式化器。

### 2. 所属体系
- **类**：`java.time.format.DateTimeFormatter`
- **包**：`java.time.format`（Java 8 时间日期格式化包）
- **JDK 版本**：Java 8+

### 3. 功能作用
`DateTimeFormatter.ofPattern()` 方法用于：
1. **创建格式化器**：根据指定的模式字符串创建 DateTimeFormatter 实例
2. **自定义格式**：支持丰富的日期时间格式模式
3. **可复用性**：创建的格式化器是线程安全的，可重复使用
4. **类型安全**：编译时检查格式模式的有效性

### 4. 方法签名

```java
// 基本版本
public static DateTimeFormatter ofPattern(String pattern);

// 指定区域版本
public static DateTimeFormatter ofPattern(String pattern, Locale locale);
```


### 5. 在代码中的使用

```java
// 在 RedisIdWorker 类中使用
public long nextId(String keyPrefix) {
    // ...
    // 2.生成序列号
    // 2.1.获取当前日期，精确到天
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));  // ← 这里调用 ofPattern() 方法
    // ...
}
```


### 6. 常用格式模式

| 模式                                                         | 含义         | 示例 |
| ------------------------------------------------------------ | ------------ | ---- |
| `yyyy`                                                       | 四位年份     | 2024 |
| `MM`                                                         | 两位月份     | 01   |
| `dd`                                                         | 两位日期     | 15   |
| `HH`                                                         | 24小时制小时 | 14   |
| `mm`                                                         | 分钟         | 30   |
| [ss](file://D:\code\java\hm-dianping\target\classes\com\hmdp\config\MvcConfig.class) | 秒           | 25   |
| `SSS`                                                        | 毫秒         | 123  |

### 7. 使用示例

#### (1) 基本使用
```java
// 创建不同的格式化器
DateTimeFormatter dateFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd");
DateTimeFormatter dateTimeFormatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
DateTimeFormatter timeFormatter = DateTimeFormatter.ofPattern("HH:mm:ss");

LocalDateTime now = LocalDateTime.now();

String dateStr = now.format(dateFormatter);      // 2024-01-15
String dateTimeStr = now.format(dateTimeFormatter); // 2024-01-15 14:30:25
String timeStr = now.format(timeFormatter);      // 14:30:25
```


#### (2) 在代码中的实际应用
```java
// 生成 Redis key 用的日期格式
DateTimeFormatter keyFormatter = DateTimeFormatter.ofPattern("yyyy:MM:dd");
String date = now.format(keyFormatter);  // 2024:01:15

// 构造 Redis key
String redisKey = "icr:" + keyPrefix + ":" + date;  // icr:order:2024:01:15
```


### 8. 预定义格式化器对比

| 预定义常量                | 等价模式                | 输出示例            |
| ------------------------- | ----------------------- | ------------------- |
| `ISO_LOCAL_DATE`          | `yyyy-MM-dd`            | 2024-01-15          |
| `ISO_LOCAL_TIME`          | `HH:mm:ss`              | 14:30:25            |
| `ISO_LOCAL_DATE_TIME`     | `yyyy-MM-dd'T'HH:mm:ss` | 2024-01-15T14:30:25 |
| `ofPattern("yyyy:MM:dd")` | 自定义                  | 2024:01:15          |

### 9. 在 ID 生成器中的作用

```java
public long nextId(String keyPrefix) {
    // ...
    // 2.生成序列号
    // 2.1.获取当前日期，精确到天
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));  // 创建格式化器并格式化
    // 2.2.自增长
    long count = stringRedisTemplate.opsForValue().increment("icr:" + keyPrefix + ":" + date);
    // ...
}
```


### 10. 线程安全性

```java
// DateTimeFormatter 是线程安全的，推荐作为静态常量使用
public class RedisIdWorker {
    // 推荐做法：预定义格式化器
    private static final DateTimeFormatter DATE_FORMATTER = 
        DateTimeFormatter.ofPattern("yyyy:MM:dd");
    
    public long nextId(String keyPrefix) {
        LocalDateTime now = LocalDateTime.now();
        String date = now.format(DATE_FORMATTER);  // 复用格式化器
        // ...
    }
}
```


### 11. 优势

1. **线程安全**：DateTimeFormatter 是不可变类，线程安全
2. **可复用**：创建后可多次使用，性能更好
3. **类型安全**：编译时检查格式模式
4. **灵活性强**：支持丰富的格式模式
5. **国际化支持**：可配合本地化设置使用

### 12. 注意事项

#### (1) 性能优化
```java
// 推荐：预定义并复用
private static final DateTimeFormatter FORMATTER = 
    DateTimeFormatter.ofPattern("yyyy:MM:dd");

// 不推荐：每次都创建新的格式化器
String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));  // 每次都创建新对象
```


#### (2) 异常处理
```java
try {
    DateTimeFormatter formatter = DateTimeFormatter.ofPattern("invalid pattern");
} catch (IllegalArgumentException e) {
    // 处理无效的格式模式
}
```


#### (3) 本地化支持
```java
// 支持本地化
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy年MM月dd日", Locale.CHINESE);
String chineseDate = now.format(formatter);  // 2024年01月15日
```


### 13. 在 Redis Key 设计中的重要性

```java
// 通过 ofPattern 创建格式化器
DateTimeFormatter keyFormatter = DateTimeFormatter.ofPattern("yyyy:MM:dd");

// 格式化日期用于 Redis key
LocalDateTime now = LocalDateTime.now();
String date = now.format(keyFormatter);  // 2024:01:15

// 构造按天分隔的 key
String redisKey = "icr:" + keyPrefix + ":" + date;  // icr:order:2024:01:15

// 这样设计的优势：
// 1. 每天独立计数，避免单个 key 值过大
// 2. 便于数据清理和统计分析
// 3. 符合 Redis 最佳实践
```


`DateTimeFormatter.ofPattern()` 方法在分布式 ID 生成器中用于创建自定义的日期格式化器，将当前日期格式化为 `yyyy:MM:dd` 格式，为生成按天分隔的 Redis key 提供了基础支持，这是实现高并发、可扩展 ID 生成的关键设计之一。