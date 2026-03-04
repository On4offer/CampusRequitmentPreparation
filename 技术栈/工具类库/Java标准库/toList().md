## toList() 方法介绍

### 1. 基本定义

[toList()](file://cn\hutool\json\JSONUtil.java#L50-L50) 是 Java 8 中 `Collectors` 工具类提供的收集器方法，用于将 Stream 中的元素收集到一个 `List` 集合中。

### 2. 所属工具和类

- **工具/框架**：Java 标准库 (Java SE 8+)
- **类**：`java.util.stream.Collectors`
- **方法签名**：`public static <T> Collector<T, ?, List<T>> toList()`

### 3. 方法功能

将 Stream 中的元素收集（收集器操作）到一个 `List` 集合中，保持元素的顺序。

### 4. 参数说明

- **无参数**
- **返回值**：`Collector<T, ?, List<T>>` 类型的收集器

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
// 2.解析出其中的用户id
List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
```


### 6. 相关 Collectors 方法

| 方法                                                    | 功能             |
| ------------------------------------------------------- | ---------------- |
| [toList()](file://cn\hutool\json\JSONUtil.java#L50-L50) | 收集到 List 集合 |
| `toSet()`                                               | 收集到 Set 集合  |
| `toMap()`                                               | 收集到 Map 集合  |
| `joining()`                                             | 连接字符串       |
| `groupingBy()`                                          | 分组收集         |

### 7. 使用场景

#### (1) Stream 结果收集

```java
// 将 Stream 转换为 List
Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
List<Long> ids = top5.stream()
    .map(Long::valueOf)
    .collect(Collectors.toList());  // 收集到 List
```


### 8. 在当前项目中的具体应用

#### (1) 数据转换和收集

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
    List<Long> ids = top5.stream()                    // 创建流
        .map(Long::valueOf)                          // 类型转换
        .collect(Collectors.toList());               // 收集到 List
    // ...
}
```


### 9. 完整示例

#### (1) 基本使用

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// 转换为大写并收集到 List
List<String> upperNames = names.stream()
    .map(String::toUpperCase)
    .collect(Collectors.toList());
// 结果: ["ALICE", "BOB", "CHARLIE"]
```


#### (2) 过滤和收集

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6);

// 过滤偶数并收集到 List
List<Integer> evenNumbers = numbers.stream()
    .filter(n -> n % 2 == 0)
    .collect(Collectors.toList());
// 结果: [2, 4, 6]
```


### 10. 在项目中的处理流程

```java
// 1. 从 Redis 获取点赞用户ID集合（String类型）
Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
// 结果示例: {"1001", "1002", "1003"}

// 2. 使用 Stream 进行处理和收集
List<Long> ids = top5.stream()              // 创建流: {"1001", "1002", "1003"}
    .map(Long::valueOf)                     // 转换: "1001" -> 1001L
    .collect(Collectors.toList());          // 收集: [1001L, 1002L, 1003L]
```


### 11. Java 16+ 的新方式

```java
// Java 16+ 提供了更简洁的方式
import java.util.stream.Collectors;

// 传统方式
List<Long> ids1 = top5.stream()
    .map(Long::valueOf)
    .collect(Collectors.toList());

// Java 16+ 可以使用 toList() 静态导入
import static java.util.stream.Collectors.toList;

List<Long> ids2 = top5.stream()
    .map(Long::valueOf)
    .collect(toList());
```


### 12. 注意事项

#### (1) List 特性

```java
List<String> result = stream.collect(Collectors.toList());
// 1. 保持元素顺序
// 2. 允许重复元素
// 3. 允许 null 元素
```


#### (2) 与 toSet() 的区别

```java
List<String> names = Arrays.asList("Alice", "Bob", "Alice");

// toList() - 保持重复元素
List<String> list = names.stream().collect(Collectors.toList());
// 结果: ["Alice", "Bob", "Alice"]

// toSet() - 去除重复元素
Set<String> set = names.stream().collect(Collectors.toSet());
// 结果: {"Alice", "Bob"}
```


#### (3) 性能考虑

```java
// collect 是终端操作，会触发流的执行
List<Long> ids = top5.stream()
    .map(Long::valueOf)
    .collect(Collectors.toList());  // 此时才真正执行转换操作
```


在当前项目中，`Collectors.toList()` 方法主要用于将 Stream 处理后的结果收集到 List 集合中，这是 Stream API 处理流程的最后一步，将中间处理结果转换为具体的数据结构供后续使用。