## System.currentTimeMillis() 方法介绍

### 1. 基本定义

`System.currentTimeMillis()` 是 Java 标准库中的静态方法，用于获取当前系统时间的时间戳。

### 2. 所属工具和类

- **工具/框架**：Java 标准库 (Java SE)
- **类**：`java.lang.System`
- **方法签名**：`public static native long currentTimeMillis()`

### 3. 方法功能

返回当前时间距离 1970年1月1日 00:00:00 UTC（Unix纪元）的毫秒数。

### 4. 参数说明

- **无参数**
- **返回值**：`long` 类型，表示当前时间的毫秒时间戳

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
// 点赞功能中使用
if (isSuccess) {
    stringRedisTemplate.opsForZSet().add(key, userId.toString(), System.currentTimeMillis());
}

// Feed流推送中使用
stringRedisTemplate.opsForZSet().add(key, blog.getId().toString(), System.currentTimeMillis());
```


### 6. 时间戳示例

```java
// 获取当前时间戳
long timestamp = System.currentTimeMillis();
System.out.println(timestamp); // 例如: 1640000000000

// 转换为可读时间格式
Date date = new Date(timestamp);
System.out.println(date); // 例如: Mon Dec 20 12:33:20 CST 2021
```


### 7. 相关方法

| 方法                           | 功能                       |
| ------------------------------ | -------------------------- |
| `System.currentTimeMillis()`   | 获取毫秒时间戳             |
| `System.nanoTime()`            | 获取纳秒时间戳（更高精度） |
| `new Date().getTime()`         | 通过 Date 对象获取时间戳   |
| `Instant.now().toEpochMilli()` | Java 8 新时间API获取时间戳 |

### 8. 使用场景

#### (1) 记录操作时间

```java
// 记录用户点赞时间
@Override
public Result likeBlog(Long id) {
    // ...
    if (isSuccess) {
        // 使用时间戳作为ZSet的分数，记录点赞时间
        stringRedisTemplate.opsForZSet().add(key, userId.toString(), System.currentTimeMillis());
    }
}
```


#### (2) Feed流时间排序

```java
// 记录博客发布时间
@Override
public Result saveBlog(Blog blog) {
    // ...
    for (Follow follow : follows) {
        Long userId = follow.getUserId();
        String key = FEED_KEY + userId;
        // 使用时间戳作为分数，实现按时间倒序排列
        stringRedisTemplate.opsForZSet().add(key, blog.getId().toString(), System.currentTimeMillis());
    }
}
```


### 9. 在当前项目中的作用

#### (1) 点赞时间记录

```java
// 点赞时记录时间
stringRedisTemplate.opsForZSet().add("blog:liked:1001", "1001", 1640000000000L);
// 这样可以知道用户1001在时间戳1640000000000时点赞了博客1001
```


#### (2) Feed流排序

```java
// 博客推送时记录发布时间
stringRedisTemplate.opsForZSet().add("feed:1002", "2001", 1640000000000L);
// 粉丝1002的feed流中包含了博客2001，发布时间为1640000000000
```


#### (3) 滚动分页查询

```java
// 基于时间戳实现滚动分页
Set<ZSetOperations.TypedTuple<String>> typedTuples = 
    stringRedisTemplate.opsForZSet()
        .reverseRangeByScoreWithScores(key, 0, max, offset, 2);
// 使用时间戳作为分数进行范围查询
```


### 10. 注意事项

#### (1) 时间精度

```java
// 毫秒级精度
long millis = System.currentTimeMillis();  // 例如: 1640000000123

// 纳秒级精度（相对）
long nanos = System.nanoTime();  // 用于性能测试等场景
```


#### (2) 时区无关

```java
// currentTimeMillis() 返回的是UTC时间戳，与时区无关
long timestamp = System.currentTimeMillis();
// 在任何时区下，这个时间戳都代表同一个时刻
```


#### (3) 系统时钟依赖

```java
// 依赖于系统时钟，如果系统时间被修改，会影响结果
long timestamp1 = System.currentTimeMillis();
// 如果系统时间被调整，可能得到不连续的时间戳
long timestamp2 = System.currentTimeMillis();
```


在当前项目中，`System.currentTimeMillis()` 主要用于：
1. **记录操作时间**：记录用户点赞的时间
2. **实现排序功能**：作为 Redis ZSet 的分数值，实现按时间排序
3. **Feed流推送**：记录博客的发布时间，用于后续的时间排序查询

这是实现时间线功能和排序功能的关键技术点。