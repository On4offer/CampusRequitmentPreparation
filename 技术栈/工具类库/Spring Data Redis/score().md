## score() 方法介绍

### 1. 基本定义

`score()` 是 Spring Data Redis 框架中 `ZSetOperations` 接口提供的方法，用于获取 Redis 有序集合（ZSet）中指定成员的分数值。

### 2. 所属工具和类

- **工具/框架**：Spring Data Redis
- **接口**：`org.springframework.data.redis.core.ZSetOperations`
- **方法签名**：`Double score(K key, Object member)`

### 3. 方法功能

返回有序集合中指定成员的分数值。如果成员不存在于有序集合中，则返回 `null`。

### 4. 参数说明

- **key**：有序集合的键名
- **member**：有序集合中的成员
- **返回值**：成员的分数值（Double类型），如果成员不存在则返回 `null`

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
Double score = stringRedisTemplate.opsForZSet().score(key, userId.toString());
```


这段代码的作用是：
- 通过 `stringRedisTemplate.opsForZSet()` 获取 ZSet 操作对象
- 调用 `score()` 方法查询指定用户在点赞有序集合中的分数值
- 分数值存在表示用户已点赞，不存在（null）表示用户未点赞

### 6. Redis 原生命令对应关系

Spring Data Redis 的 `score()` 方法对应 Redis 的原生命令：

```bash
# Redis 原生命令
ZSCORE key member

# 示例
ZSCORE blog:liked:1001 "1001"
# 返回: 1640000000000 (时间戳)
# 或者: (nil) (成员不存在)
```


### 7. 相关方法

| 方法                                          | 功能               |
| --------------------------------------------- | ------------------ |
| `score(K key, Object member)`                 | 获取指定成员的分数 |
| `add(K key, V value, double score)`           | 添加成员和分数     |
| `remove(K key, Object... values)`             | 移除指定成员       |
| `range(K key, long start, long end)`          | 按排名范围查询     |
| `rangeByScore(K key, double min, double max)` | 按分数范围查询     |
| `rank(K key, Object member)`                  | 获取成员的排名     |

### 8. 使用场景

#### (1) 判断用户是否点赞

```java
// 检查用户是否已点赞某篇博客
String key = "blog:liked:" + blogId;
Double score = stringRedisTemplate.opsForZSet().score(key, userId.toString());

if (score != null) {
    // 用户已点赞
    blog.setIsLike(true);
} else {
    // 用户未点赞
    blog.setIsLike(false);
}
```


#### (2) 获取点赞时间

```java
// 获取用户点赞的时间戳
String key = "blog:liked:" + blogId;
Double score = stringRedisTemplate.opsForZSet().score(key, userId.toString());

if (score != null) {
    long likeTime = score.longValue();
    // 处理点赞时间
}
```


### 9. 在当前项目中的具体应用

#### (1) 检查博客点赞状态

```java
private void isBlogLiked(Blog blog) {
    // 1.获取登录用户
    UserDTO user = UserHolder.getUser();
    if (user == null) {
        // 用户未登录，无需查询是否点赞
        return;
    }
    Long userId = user.getId();
    // 2.判断当前登录用户是否已经点赞
    String key = "blog:liked:" + blog.getId();
    Double score = stringRedisTemplate.opsForZSet().score(key, userId.toString());
    blog.setIsLike(score != null); // score不为null表示已点赞
}
```


#### (2) 点赞/取消点赞逻辑

```java
@Override
public Result likeBlog(Long id) {
    // 1.获取登录用户
    Long userId = UserHolder.getUser().getId();
    // 2.判断当前登录用户是否已经点赞
    String key = BLOG_LIKED_KEY + id;
    Double score = stringRedisTemplate.opsForZSet().score(key, userId.toString());
    if (score == null) {
        // 3.如果未点赞，可以点赞
        // 3.1.数据库点赞数 + 1
        boolean isSuccess = update().setSql("liked = liked + 1").eq("id", id).update();
        // 3.2.保存用户到Redis的set集合  zadd key value score
        if (isSuccess) {
            stringRedisTemplate.opsForZSet().add(key, userId.toString(), System.currentTimeMillis());
        }
    } else {
        // 4.如果已点赞，取消点赞
        // 4.1.数据库点赞数 -1
        boolean isSuccess = update().setSql("liked = liked - 1").eq("id", id).update();
        // 4.2.把用户从Redis的set集合移除
        if (isSuccess) {
            stringRedisTemplate.opsForZSet().remove(key, userId.toString());
        }
    }
    return Result.ok();
}
```


### 10. 注意事项

#### (1) 返回值处理

```java
Double score = stringRedisTemplate.opsForZSet().score(key, member);
if (score != null) {
    // 成员存在
} else {
    // 成员不存在
}
```


#### (2) 类型转换

```java
Double score = stringRedisTemplate.opsForZSet().score(key, member);
if (score != null) {
    long timestamp = score.longValue(); // 转换为长整型时间戳
}
```


#### (3) 异常处理

```java
try {
    Double score = stringRedisTemplate.opsForZSet().score(key, userId.toString());
} catch (Exception e) {
    // 处理 Redis 连接异常等
    log.error("查询点赞状态失败", e);
}
```


在当前项目中，`score()` 方法是实现点赞功能的核心方法之一，通过检查用户在有序集合中的分数值来判断用户是否已点赞，这是 Redis ZSet 数据结构的典型应用场景。