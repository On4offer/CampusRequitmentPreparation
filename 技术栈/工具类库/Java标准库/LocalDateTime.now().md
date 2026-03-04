## LocalDateTime.now() 方法介绍

### 1. 基本概念
`now()` 是 Java 8 引入的 `java.time.LocalDateTime` 类的静态方法，用于获取当前日期和时间。

### 2. 所属体系
- **类**：`java.time.LocalDateTime`
- **包**：`java.time`（Java 8 新的时间日期 API）
- **JDK 版本**：Java 8+

### 3. 功能作用
`now()` 方法用于：
1. **获取当前时间**：获取系统当前的日期和时间
2. **时区相关**：返回系统默认时区的当前时间
3. **不可变对象**：返回不可变的 LocalDateTime 实例

### 4. 方法签名

```java
// 获取系统默认时区的当前日期时间
public static LocalDateTime now();

// 获取指定时钟的当前日期时间
public static LocalDateTime now(Clock clock);
```


### 5. 在代码中的使用

```java
// 在 RedisIdWorker 类中使用
public long nextId(String keyPrefix) {
    // 1.生成时间戳
    LocalDateTime now = LocalDateTime.now();  // ← 这里调用 now() 方法
    long nowSecond = now.toEpochSecond(ZoneOffset.UTC);
    long timestamp = nowSecond - BEGIN_TIMESTAMP;
    
    // ...
}
```


### 6. Java 8 时间 API 体系

```java
// 主要的时间类
LocalDateTime.now()     // 本地日期时间（无时区信息）
LocalDate.now()         // 仅日期
LocalTime.now()         // 仅时间
ZonedDateTime.now()     // 带时区的日期时间
Instant.now()           // 时间戳
```


### 7. 使用示例

#### (1) 基本使用
```java
// 获取当前日期时间
LocalDateTime now = LocalDateTime.now();
System.out.println(now); // 2024-01-15T14:30:25.123

// 格式化输出
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
System.out.println(now.format(formatter)); // 2024-01-15 14:30:25
```


#### (2) 指定时区
```java
// 获取指定时区的当前时间
LocalDateTime tokyoTime = LocalDateTime.now(ZoneId.of("Asia/Tokyo"));
LocalDateTime utcTime = LocalDateTime.now(ZoneId.of("UTC"));
```


### 8. 在 ID 生成器中的作用

```java
public long nextId(String keyPrefix) {
    // 1.生成时间戳
    LocalDateTime now = LocalDateTime.now();  // 获取当前时间
    long nowSecond = now.toEpochSecond(ZoneOffset.UTC);  // 转换为 UTC 时间戳
    long timestamp = nowSecond - BEGIN_TIMESTAMP;  // 计算相对时间戳
    
    // 2.生成序列号
    String date = now.format(DateTimeFormatter.ofPattern("yyyy:MM:dd"));
    long count = stringRedisTemplate.opsForValue().increment("icr:" + keyPrefix + ":" + date);
    
    // 3.拼接并返回
    return timestamp << COUNT_BITS | count;
}
```


### 9. 与旧时间 API 的对比

#### (1) 旧的 Date API
```java
// 旧的方式（不推荐）
Date date = new Date();
SimpleDateFormat sdf = new SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
System.out.println(sdf.format(date));
```


#### (2) 新的 LocalDateTime API
```java
// 新的方式（推荐）
LocalDateTime now = LocalDateTime.now();
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
System.out.println(now.format(formatter));
```


### 10. 优势

1. **线程安全**：LocalDateTime 是不可变类，线程安全
2. **API 设计良好**：方法命名清晰，使用方便
3. **性能优秀**：避免了旧 API 的同步开销
4. **类型安全**：编译时检查日期时间类型
5. **时区支持**：更好的时区处理能力

### 11. 注意事项

#### (1) 时区考虑
```java
// 默认使用系统时区
LocalDateTime now = LocalDateTime.now();

// 如需指定时区，应使用 ZonedDateTime
ZonedDateTime utcNow = ZonedDateTime.now(ZoneOffset.UTC);
```


#### (2) 与时间戳转换
```java
// LocalDateTime 转时间戳
LocalDateTime now = LocalDateTime.now();
long timestamp = now.toEpochSecond(ZoneOffset.UTC);

// 时间戳转 LocalDateTime
LocalDateTime dateTime = LocalDateTime.ofEpochSecond(timestamp, 0, ZoneOffset.UTC);
```


### 12. 在 ID 生成中的重要性

```java
// 时间戳部分确保全局唯一性
LocalDateTime now = LocalDateTime.now();
long nowSecond = now.toEpochSecond(ZoneOffset.UTC);
long timestamp = nowSecond - BEGIN_TIMESTAMP;  // 相对时间戳

// 结合自增序列号确保高并发下的唯一性
// timestamp << 32 | sequenceNumber
```

`LocalDateTime.now()` 是 Java 8 时间 API 的核心方法之一，在分布式 ID 生成器中用于获取当前时间，为生成全局唯一 ID 提供时间基础。