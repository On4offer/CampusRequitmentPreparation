## range() 方法介绍

### 1. 基本定义

`range()` 是 Spring Data Redis 框架中 `ZSetOperations` 接口提供的方法，用于从 Redis 有序集合（ZSet）中按排名范围获取成员。

### 2. 所属工具和类

- **工具/框架**：Spring Data Redis
- **接口**：`org.springframework.data.redis.core.ZSetOperations`
- **方法签名**：`Set<V> range(K key, long start, long end)`

### 3. 方法功能

按排名顺序（从小到大）从有序集合中获取指定范围的成员。排名从 0 开始，0 表示第一名。

### 4. 参数说明

- **key**：有序集合的键名
- **start**：开始位置（包含），从 0 开始计数
- **end**：结束位置（包含）
- **返回值**：`Set<V>` 类型，包含指定范围内的成员集合

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
@Override
public Result queryBlogLikes(Long id) {
    String key = BLOG_LIKED_KEY + id;
    // 1.查询top5的点赞用户 zrange key 0 4
    Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
    // ...
}
```


### 6. Redis 原生命令对应关系

Spring Data Redis 的 `range()` 方法对应 Redis 的原生命令：

```bash
# Redis 原生命令
ZRANGE key start end

# 示例
ZRANGE blog:liked:1001 0 4  # 获取前5个成员（排名0-4）
ZRANGE blog:liked:1001 0 -1 # 获取所有成员
```


### 7. 相关方法

| 方法                                                 | 功能                     |
| ---------------------------------------------------- | ------------------------ |
| `range(K key, long start, long end)`                 | 按排名范围获取成员       |
| `rangeWithScores(K key, long start, long end)`       | 按排名范围获取成员和分数 |
| `reverseRange(K key, long start, long end)`          | 按排名倒序获取成员       |
| `rangeByScore(K key, double min, double max)`        | 按分数范围获取成员       |
| `reverseRangeByScore(K key, double min, double max)` | 按分数倒序获取成员       |

### 8. 使用场景

#### (1) 获取排行榜

```java
// 获取点赞排行榜前5名用户
@Override
public Result queryBlogLikes(Long id) {
    String key = BLOG_LIKED_KEY + id;
    // 获取排名前5的点赞用户
    Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
    // ...
}
```


### 9. 在当前项目中的具体应用

#### (1) 查询博客点赞用户列表

```java
/**
 * 查询博客点赞用户列表
 * @param id 博客ID
 * @return 返回博客点赞数前5的用户信息列表
 */
@Override
public Result queryBlogLikes(Long id) {
    String key = BLOG_LIKED_KEY + id;
    // 1.查询top5的点赞用户 zrange key 0 4
    Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
    if (top5 == null || top5.isEmpty()) {
        return Result.ok(Collections.emptyList());
    }
    // 2.解析出其中的用户id
    List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
    String idStr = StrUtil.join(",", ids);
    // 3.根据用户id查询用户 WHERE id IN ( 5 , 1 ) ORDER BY FIELD(id, 5, 1)
    List<UserDTO> userDTOS = userService.query()
            .in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list()
            .stream()
            .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
            .collect(Collectors.toList());
    // 4.返回
    return Result.ok(userDTOS);
}
```


### 10. 详细示例

#### (1) Redis 数据结构示例

```bash
# Redis 中的有序集合数据
blog:liked:1001 = {
    "1003" -> 1640000000000,  # 用户1003最先点赞
    "1001" -> 1640000001000,  # 用户1001其次点赞
    "1002" -> 1640000002000,  # 用户1002最后点赞
}

# 按排名查询
ZRANGE blog:liked:1001 0 4
# 返回: {"1003", "1001", "1002"}  # 按分数升序排列
```


#### (2) Java 代码示例

```java
// 获取前5名点赞用户
Set<String> top5 = stringRedisTemplate.opsForZSet().range("blog:liked:1001", 0, 4);

// 遍历结果
for (String userId : top5) {
    System.out.println("用户ID: " + userId);
}

// 获取所有成员
Set<String> allMembers = stringRedisTemplate.opsForZSet().range("blog:liked:1001", 0, -1);
```


### 11. 注意事项

#### (1) 排名顺序

```java
// ZSet 默认按分数升序排列，排名0是分数最小的成员
Set<String> ascending = stringRedisTemplate.opsForZSet().range(key, 0, 4);

// 如果需要按分数降序排列，使用 reverseRange
Set<String> descending = stringRedisTemplate.opsForZSet().reverseRange(key, 0, 4);
```


#### (2) 参数说明

```java
// start 和 end 都是包含的
stringRedisTemplate.opsForZSet().range(key, 0, 4);  // 包含排名 0,1,2,3,4 的成员

// 使用 -1 表示最后一个元素
stringRedisTemplate.opsForZSet().range(key, 0, -1); // 获取所有成员
```


#### (3) 返回值处理

```java
Set<String> result = stringRedisTemplate.opsForZSet().range(key, 0, 4);
if (result == null || result.isEmpty()) {
    // 处理空结果
}
```


在当前项目中，`range()` 方法主要用于实现点赞排行榜功能，获取点赞数最多的前5名用户，为前端展示点赞用户列表提供数据支持。