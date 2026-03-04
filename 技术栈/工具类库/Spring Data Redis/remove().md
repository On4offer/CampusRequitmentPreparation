## remove() 方法介绍

### 1. 基本定义

[remove()](file://com\baomidou\mybatisplus\extension\service\IService.java#L28-L28) 是 Spring Data Redis 框架中 `ZSetOperations` 接口提供的方法，用于从 Redis 有序集合（ZSet）中移除指定的成员。

### 2. 所属工具和类

- **工具/框架**：Spring Data Redis
- **接口**：`org.springframework.data.redis.core.ZSetOperations`
- **方法签名**：`Long remove(K key, Object... values)`

### 3. 方法功能

从 Redis 有序集合中移除一个或多个指定的成员。如果成员存在于集合中则被移除，否则忽略。

### 4. 参数说明

- **key**：有序集合的键名
- **values**：要移除的成员值（可变参数，可以移除多个成员）
- **返回值**：`Long` 类型，表示实际被移除的成员数量

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
@Override
public Result likeBlog(Long id) {
    // ...
    if (score == null) {
        // 点赞逻辑
        // ...
    } else {
        // 4.如果已点赞，取消点赞
        // 4.1.数据库点赞数 -1
        boolean isSuccess = update().setSql("liked = liked - 1").eq("id", id).update();
        // 4.2.把用户从Redis的set集合移除
        if (isSuccess) {
            stringRedisTemplate.opsForZSet().remove(key, userId.toString());
        }
    }
    // ...
}
```


### 6. Redis 原生命令对应关系

Spring Data Redis 的 `remove()` 方法对应 Redis 的原生命令：

```bash
# Redis 原生命令
ZREM key member [member ...]

# 示例
ZREM blog:liked:1001 "1001"
ZREM feed:1002 "2001" "2002"
```


### 7. 相关方法

| 方法                                                | 功能               |
| --------------------------------------------------- | ------------------ |
| `remove(K key, Object... values)`                   | 移除指定成员       |
| `removeRange(K key, long start, long end)`          | 按排名范围移除成员 |
| `removeRangeByScore(K key, double min, double max)` | 按分数范围移除成员 |
| `add(K key, V value, double score)`                 | 添加成员           |
| `score(K key, Object member)`                       | 获取成员分数       |

### 8. 使用场景

#### (1) 取消点赞功能

```java
// 用户取消点赞时调用
@Override
public Result likeBlog(Long id) {
    // ...
    if (score != null) {
        // 用户已点赞，执行取消点赞操作
        boolean isSuccess = update().setSql("liked = liked - 1").eq("id", id).update();
        if (isSuccess) {
            // 从点赞有序集合中移除用户
            stringRedisTemplate.opsForZSet().remove(key, userId.toString());
        }
    }
    // ...
}
```


### 9. 在当前项目中的具体应用

#### (1) 取消点赞操作

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
            // 移除用户ID从点赞有序集合中
            stringRedisTemplate.opsForZSet().remove(key, userId.toString());
        }
    }
    return Result.ok();
}
```


### 10. 注意事项

#### (1) 返回值处理

```java
// remove 方法返回实际移除的成员数量
Long removedCount = stringRedisTemplate.opsForZSet().remove(key, userId.toString());
if (removedCount > 0) {
    // 成功移除
    System.out.println("成功移除 " + removedCount + " 个成员");
} else {
    // 成员不存在或未被移除
    System.out.println("没有成员被移除");
}
```


#### (2) 批量移除

```java
// 可以同时移除多个成员
String[] members = {"member1", "member2", "member3"};
Long removedCount = stringRedisTemplate.opsForZSet().remove(key, (Object[]) members);
```


#### (3) 异常处理

```java
try {
    Long removedCount = stringRedisTemplate.opsForZSet().remove(key, userId.toString());
} catch (Exception e) {
    // 处理 Redis 连接异常等
    log.error("移除成员失败", e);
}
```


在当前项目中，[remove()](file://com\baomidou\mybatisplus\extension\service\IService.java#L28-L28) 方法主要用于实现取消点赞功能，当用户取消点赞时，需要将用户ID从对应的点赞有序集合中移除，保持数据的一致性。