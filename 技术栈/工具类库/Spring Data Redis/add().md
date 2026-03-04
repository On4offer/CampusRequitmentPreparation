## add() 方法介绍

### 1. 基本定义

`add()` 是 Spring Data Redis 框架中 `ZSetOperations` 接口提供的方法，用于向 Redis 有序集合（ZSet）中添加成员和对应的分数。

### 2. 所属工具和类

- **工具/框架**：Spring Data Redis
- **接口**：`org.springframework.data.redis.core.ZSetOperations`
- **方法签名**：`Boolean add(K key, V value, double score)`

### 3. 方法功能

向 Redis 有序集合中添加一个或多个成员，每个成员关联一个分数值。如果成员已存在，则更新其分数。

### 4. 参数说明

- **key**：有序集合的键名
- **value**：要添加的成员值
- **score**：成员的分数值
- **返回值**：如果添加了新元素返回 `true`，如果只是更新了已有元素的分数返回 `false`

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
@Override
public Result likeBlog(Long id) {
    // ...
    if (score == null) {
        // 3.如果未点赞，可以点赞
        // 3.1.数据库点赞数 + 1
        boolean isSuccess = update().setSql("liked = liked + 1").eq("id", id).update();
        // 3.2.保存用户到Redis的set集合  zadd key value score
        if (isSuccess) {
            stringRedisTemplate.opsForZSet().add(key, userId.toString(), System.currentTimeMillis());
        }
    }
    // ...
}
```


以及在保存博客时：

```java
@Override
public Result saveBlog(Blog blog) {
    // ...
    // 4.推送笔记id给所有粉丝
    for (Follow follow : follows) {
        // 4.1.获取粉丝id
        Long userId = follow.getUserId();
        // 4.2.推送
        String key = FEED_KEY + userId;
        stringRedisTemplate.opsForZSet().add(key, blog.getId().toString(), System.currentTimeMillis());
    }
    // ...
}
```


### 6. Redis 原生命令对应关系

Spring Data Redis 的 `add()` 方法对应 Redis 的原生命令：

```bash
# Redis 原生命令
ZADD key score member

# 示例
ZADD blog:liked:1001 1640000000000 "1001"
ZADD feed:1002 1640000000000 "2001"
```


### 7. 相关方法

| 方法                                          | 功能             |
| --------------------------------------------- | ---------------- |
| `add(K key, V value, double score)`           | 添加单个成员     |
| `add(K key, Set<TypedTuple<V>> tuples)`       | 批量添加多个成员 |
| `remove(K key, Object... values)`             | 移除指定成员     |
| `score(K key, Object member)`                 | 获取成员分数     |
| `range(K key, long start, long end)`          | 按排名范围查询   |
| `rangeByScore(K key, double min, double max)` | 按分数范围查询   |

### 8. 使用场景

#### (1) 点赞功能实现

```java
// 用户点赞时调用
@Override
public Result likeBlog(Long id) {
    // ...
    if (isSuccess) {
        // 将用户ID和当前时间戳作为分数添加到有序集合
        stringRedisTemplate.opsForZSet().add(key, userId.toString(), System.currentTimeMillis());
    }
    // ...
}
```


#### (2) Feed流推送

```java
// 保存博客时推送给粉丝
@Override
public Result saveBlog(Blog blog) {
    // ...
    for (Follow follow : follows) {
        Long userId = follow.getUserId();
        String key = FEED_KEY + userId;
        // 将博客ID和发布时间推送给粉丝的收件箱
        stringRedisTemplate.opsForZSet().add(key, blog.getId().toString(), System.currentTimeMillis());
    }
    // ...
}
```


### 9. 在当前项目中的具体应用

#### (1) 点赞操作

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
            // 添加用户ID和时间戳到点赞有序集合
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


#### (2) Feed流推送

```java
@Override
public Result saveBlog(Blog blog) {
    // 1.获取登录用户
    UserDTO user = UserHolder.getUser();
    blog.setUserId(user.getId());

    // 2.保存探店笔记
    boolean isSuccess = save(blog);
    if(!isSuccess){
        return Result.fail("新增笔记失败!");
    }

    // 3.查询笔记作者的所有粉丝 select * from tb_follow where follow_user_id = ?
    List<Follow> follows = followService.query().eq("follow_user_id", user.getId()).list();

    // 4.推送笔记id给所有粉丝
    for (Follow follow : follows) {
        // 4.1.获取粉丝id
        Long userId = follow.getUserId();
        // 4.2.推送
        String key = FEED_KEY + userId;
        // 将博客ID和当前时间戳添加到粉丝的feed流中
        stringRedisTemplate.opsForZSet().add(key, blog.getId().toString(), System.currentTimeMillis());
    }

    // 5.返回id
    return Result.ok(blog.getId());
}
```


### 10. 注意事项

#### (1) 时间复杂度

```java
// ZSet 的 add 操作时间复杂度为 O(log(N))
stringRedisTemplate.opsForZSet().add(key, value, score);
```


#### (2) 分数值的使用

```java
// 使用时间戳作为分数，实现按时间排序
long timestamp = System.currentTimeMillis();
stringRedisTemplate.opsForZSet().add(key, userId.toString(), timestamp);

// 使用其他数值作为分数，实现按权重排序
double weight = 10.5;
stringRedisTemplate.opsForZSet().add(key, memberId, weight);
```


#### (3) 批量操作

```java
// 批量添加多个成员
Set<ZSetOperations.TypedTuple<String>> tuples = new HashSet<>();
tuples.add(new DefaultTypedTuple<>("member1", 1.0));
tuples.add(new DefaultTypedTuple<>("member2", 2.0));
stringRedisTemplate.opsForZSet().add(key, tuples);
```


在当前项目中，`add()` 方法是实现点赞功能和Feed流推送系统的核心方法，充分利用了 Redis ZSet 数据结构的有序性和高效性。