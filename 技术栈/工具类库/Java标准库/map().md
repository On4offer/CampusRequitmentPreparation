## map() 方法介绍

### 1. 基本定义

`map()` 是 Java 8 Stream API 中的中间操作方法，用于将流中的每个元素通过指定的函数转换为另一种类型或值。

### 2. 所属工具和类

- **工具/框架**：Java 标准库 (Java SE 8+)
- **接口**：`java.util.stream.Stream`
- **方法签名**：`<R> Stream<R> map(Function<? super T, ? extends R> mapper)`

### 3. 方法功能

对流中的每个元素应用给定的转换函数，将元素从类型 T 转换为类型 R，返回一个新的流。

### 4. 参数说明

- **mapper**：`Function<? super T, ? extends R>` 类型的转换函数
- **返回值**：`Stream<R>` 类型的新流，其中包含转换后的元素

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
// 2.解析出其中的用户id
List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
```


### 6. 相关 Stream 方法

| 方法                                                         | 功能           |
| ------------------------------------------------------------ | -------------- |
| `map(Function mapper)`                                       | 一对一转换元素 |
| `flatMap(Function mapper)`                                   | 一对多转换元素 |
| [filter(Predicate predicate)](file://cn\hutool\core\text\CharSequenceUtil.java#L207-L207) | 过滤元素       |
| `collect(Collector collector)`                               | 收集结果       |
| `forEach(Consumer action)`                                   | 遍历元素       |

### 7. 使用场景

#### (1) 类型转换

```java
// 将 Set<String> 转换为 List<Long>
Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
List<Long> ids = top5.stream()
    .map(Long::valueOf)           // String -> Long 转换
    .collect(Collectors.toList());
```


### 8. 在当前项目中的具体应用

#### (1) 数据类型转换

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
    List<Long> ids = top5.stream()           // 创建流: {"1001", "1002", "1003"}
        .map(Long::valueOf)                  // 转换: 1001, 1002, 1003
        .collect(Collectors.toList());       // 收集为 List<Long>
    // ...
}
```


### 9. 详细示例

#### (1) 基本类型转换

```java
// String -> Long 转换
Set<String> stringIds = Set.of("1001", "1002", "1003");
List<Long> longIds = stringIds.stream()
    .map(Long::valueOf)                    // 方法引用
    .collect(Collectors.toList());

// 等价于 Lambda 表达式
List<Long> longIds2 = stringIds.stream()
    .map(s -> Long.valueOf(s))            // Lambda 表达式
    .collect(Collectors.toList());
```


#### (2) 对象属性提取

```java
List<User> users = Arrays.asList(
    new User(1L, "Alice"),
    new User(2L, "Bob")
);

// 提取用户ID
List<Long> userIds = users.stream()
    .map(User::getId)                     // 提取 id 属性
    .collect(Collectors.toList());

// 提取用户名
List<String> userNames = users.stream()
    .map(User::getName)                   // 提取 name 属性
    .collect(Collectors.toList());
```


#### (3) 复杂对象转换

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// 转换为大写
List<String> upperNames = names.stream()
    .map(String::toUpperCase)
    .collect(Collectors.toList());

// 转换为 User 对象
List<User> userList = names.stream()
    .map(name -> new User(name))
    .collect(Collectors.toList());
```


### 10. 在项目中的处理流程

```java
// 1. 从 Redis 获取点赞用户ID集合（String类型）
Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
// 结果示例: {"1001", "1002", "1003"}

// 2. 使用 map 进行类型转换
List<Long> ids = top5.stream()              // 创建流: {"1001", "1002", "1003"}
    .map(Long::valueOf)                     // 转换函数: "1001" -> 1001L
    .collect(Collectors.toList());          // 收集结果: [1001L, 1002L, 1003L]
```


### 11. map() 与 flatMap() 的区别

```java
// map(): 一对一转换
List<String> words = Arrays.asList("hello", "world");
List<Integer> lengths = words.stream()
    .map(String::length)                   // hello->5, world->5
    .collect(Collectors.toList());         // [5, 5]

// flatMap(): 一对多转换
List<String> sentences = Arrays.asList("hello world", "java stream");
List<String> words2 = sentences.stream()
    .flatMap(s -> Arrays.stream(s.split(" ")))  // 拆分为多个单词
    .collect(Collectors.toList());              // ["hello", "world", "java", "stream"]
```


### 12. 注意事项

#### (1) 方法引用 vs Lambda 表达式

```java
// 方法引用（推荐，更简洁）
.map(Long::valueOf)

// Lambda 表达式（功能相同）
.map(s -> Long.valueOf(s))
```


#### (2) 异常处理

```java
List<String> ids = Arrays.asList("1001", "invalid", "1003");
List<Long> validIds = ids.stream()
    .map(s -> {
        try {
            return Long.valueOf(s);
        } catch (NumberFormatException e) {
            return null;
        }
    })
    .filter(Objects::nonNull)
    .collect(Collectors.toList());
```


在当前项目中，`map()` 方法主要用于将从 Redis 查询到的用户 ID 字符串转换为长整型，这是 Stream API 中最常见的使用场景之一，使得数据类型转换变得简洁而高效。