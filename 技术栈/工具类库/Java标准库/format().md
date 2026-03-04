## format() 方法介绍

### 1. 基本概念
[format()](file://cn\hutool\core\util\StrUtil.java#L41-L41) 是 Java 8 时间日期 API 中 `java.time.LocalDateTime` 类的实例方法，用于将日期时间对象格式化为指定格式的字符串。

### 2. 所属体系
- **类**：`java.time.LocalDateTime`
- **包**：`java.time`（Java 8 新的时间日期 API）
- **JDK 版本**：Java 8+

### 3. 功能作用
[format()](file://cn\hutool\core\util\StrUtil.java#L41-L41) 方法用于：
1. **日期格式化**：将 LocalDateTime 对象转换为格式化的字符串
2. **自定义格式**：支持各种日期时间格式模式
3. **本地化支持**：可配合本地化设置进行格式化
4. **显示友好**：便于向用户展示日期时间信息

### 4. 方法签名

```java
// 基本版本
public String format(DateTimeFormatter formatter);
```


### 5. 在代码中的使用

```java
// 在 RedisIdWorker 类中使用
public long nextId(String keyPrefix) {
    // ...
    // 2.生成序列号
    // 2.1.获取当前日期，精确到天
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));  // ← 这里调用 format() 方法
    // ...
}
```


### 6. DateTimeFormatter 使用方式

#### (1) 预定义格式
```java
LocalDateTime now = LocalDateTime.now();

// 使用预定义的格式
String isoDate = now.format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);  // 2024-01-15T14:30:25.123
String basicIso = now.format(DateTimeFormatter.BASIC_ISO_DATE);      // 20240115
```


#### (2) 自定义模式
```java
// 使用自定义模式
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
String customDate = now.format(formatter);  // 2024-01-15 14:30:25

// 在代码中的实际使用
String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));  // 2024:01:15
```


### 7. 常用格式模式

| 模式                                                         | 含义         | 示例 |
| ------------------------------------------------------------ | ------------ | ---- |
| `yyyy`                                                       | 四位年份     | 2024 |
| `MM`                                                         | 两位月份     | 01   |
| `dd`                                                         | 两位日期     | 15   |
| `HH`                                                         | 24小时制小时 | 14   |
| `mm`                                                         | 分钟         | 30   |
| [ss](file://D:\code\java\hm-dianping\target\classes\com\hmdp\config\MvcConfig.class) | 秒           | 25   |
| `SSS`                                                        | 毫秒         | 123  |

### 8. 使用示例

#### (1) 基本使用
```java
LocalDateTime now = LocalDateTime.now();

// 常用格式
String date1 = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd"));        // 2024-01-15
String date2 = now.format(DateTimeFormatter.ofPattern("yyyy/MM/dd"));        // 2024/01/15
String datetime = now.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm")); // 2024-01-15 14:30
```


#### (2) 在 Redis Key 中的应用
```java
// 生成按天统计的 Redis key
LocalDateTime now = LocalDateTime.now();
String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
String key = "icr:order:" + date;  // icr:order:2024:01:15
```


### 9. 在 ID 生成器中的作用

```java
public long nextId(String keyPrefix) {
    // 1.生成时间戳
    LocalDateTime now = LocalDateTime.now();
    long nowSecond = now.toEpochSecond(ZoneOffset.UTC);
    long timestamp = nowSecond - BEGIN_TIMESTAMP;
    
    // 2.生成序列号
    // 2.1.获取当前日期，精确到天
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));  // 格式化为: 2024:01:15
    // 2.2.自增长；按天生成不同的 Redis key
    long count = stringRedisTemplate.opsForValue().increment("icr:" + keyPrefix + ":" + date);
    
    // 3.拼接并返回
    return timestamp << COUNT_BITS | count;
}
```


### 10. 相关方法对比

| 方法                                                         | 功能           | 返回类型 | 用途       |
| ------------------------------------------------------------ | -------------- | -------- | ---------- |
| [format(DateTimeFormatter)](file://cn\hutool\core\util\StrUtil.java#L41-L41) | 格式化为字符串 | String   | 显示和存储 |
| `toString()`                                                 | 默认字符串表示 | String   | 调试和日志 |
| `toEpochSecond(ZoneOffset)`                                  | 转换为时间戳   | long     | 计算和比较 |

### 11. 优势

1. **类型安全**：编译时检查格式模式
2. **性能优秀**：DateTimeFormatter 是线程安全且可复用的
3. **灵活性强**：支持丰富的格式模式
4. **国际化支持**：可配合本地化设置使用
5. **不可变性**：LocalDateTime 是不可变对象，线程安全

### 12. 注意事项

#### (1) DateTimeFormatter 复用
```java
// 推荐：预定义并复用 formatter
private static final DateTimeFormatter DATE_FORMATTER = 
    DateTimeFormatter.ofPattern("yyyy:MM:dd");

public long nextId(String keyPrefix) {
    LocalDateTime now = LocalDateTime.now();
    String date = now.format(DATE_FORMATTER);  // 复用 formatter
    // ...
}
```


#### (2) 线程安全性
```java
// DateTimeFormatter 是线程安全的，可以安全地作为静态常量使用
public static final DateTimeFormatter FORMATTER = 
    DateTimeFormatter.ofPattern("yyyy:MM:dd");
```


#### (3) 异常处理
```java
try {
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
} catch (DateTimeException e) {
    // 处理格式化异常
}
```


### 13. 在 Redis Key 设计中的重要性

```java
// 按天分隔的 Redis key 设计
LocalDateTime now = LocalDateTime.now();
String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
String key = "icr:" + keyPrefix + ":" + date;  // icr:order:2024:01:15

// 这样设计的好处：
// 1. 每天的计数器独立，避免单个 key 的计数器过大
// 2. 便于按天统计和分析
// 3. 便于清理过期数据
```


[format()](file://cn\hutool\core\util\StrUtil.java#L41-L41) 方法在分布式 ID 生成器中用于生成按天分隔的 Redis key，通过将日期格式化为 `yyyy:MM:dd` 格式，实现了每天独立计数器的设计，既保证了系统的可扩展性，又便于数据管理和统计分析。