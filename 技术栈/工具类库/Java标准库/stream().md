## stream() 方法介绍

### 1. 基本定义

`stream()` 是 Java 8 引入的集合框架中的方法，用于创建顺序流，支持对集合进行函数式编程操作。

### 2. 所属工具和类

- **工具/框架**：Java 标准库 (Java SE 8+)
- **接口**：`java.util.Collection`（及其实现类）
- **方法签名**：`default Stream<E> stream()`

### 3. 方法功能

返回一个顺序的 `Stream`，用于对集合中的元素进行各种流式操作，如过滤、映射、排序、聚合等。

### 4. 参数说明

- **无参数**
- **返回值**：`Stream<E>` 类型，其中 E 是集合元素的类型

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdi\service\impl\BlogServiceImpl.java) 文件中：

```java
@Override
public Result queryBlogLikes(Long id) {
    // ...
    // 2.解析出其中的用户id
    List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
    // ...
}
```


### 6. Stream 相关方法

| 方法                                                         | 功能         |
| ------------------------------------------------------------ | ------------ |
| `stream()`                                                   | 创建顺序流   |
| `parallelStream()`                                           | 创建并行流   |
| `map(Function mapper)`                                       | 转换元素类型 |
| [filter(Predicate predicate)](file://cn\hutool\core\text\CharSequenceUtil.java#L207-L207) | 过滤元素     |
| `collect(Collector collector)`                               | 收集结果     |
| `forEach(Consumer action)`                                   | 遍历元素     |

### 7. 使用场景

#### (1) 数据转换

```java
// 将 Set<String> 转换为 List<Long>
Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
List<Long> ids = top5.stream()
    .map(Long::valueOf)           // 将 String 转换为 Long
    .collect(Collectors.toList()); // 收集为 List
```


### 8. 在当前项目中的具体应用

#### (1) 类型转换处理

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
        .map(Long::valueOf)                          // 转换 String -> Long
        .collect(Collectors.toList());               // 收集为 List
    // ...
}
```


### 9. 完整的 Stream 操作示例

#### (1) 基本流操作

```java
Set<String> top5 = new HashSet<>();
top5.add("1001");
top5.add("1002");
top5.add("1003");

// 传统方式
List<Long> ids1 = new ArrayList<>();
for (String id : top5) {
    ids1.add(Long.valueOf(id));
}

// Stream 方式
List<Long> ids2 = top5.stream()
    .map(Long::valueOf)
    .collect(Collectors.toList());
```


#### (2) 复杂流操作

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");

// 过滤长度大于3的名字，转为大写，按字母排序
List<String> result = names.stream()
    .filter(name -> name.length() > 3)     // 过滤
    .map(String::toUpperCase)              // 转换
    .sorted()                              // 排序
    .collect(Collectors.toList());         // 收集
```


### 10. 在项目中的处理流程

```java
// 1. 从 Redis 获取点赞用户ID集合（String类型）
Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
// 结果示例: {"1001", "1002", "1003"}

// 2. 使用 Stream 进行类型转换
List<Long> ids = top5.stream()        // 创建流: {"1001", "1002", "1003"}
    .map(Long::valueOf)               // 转换: {1001L, 1002L, 1003L}
    .collect(Collectors.toList());    // 收集: [1001L, 1002L, 1003L]
```


### 11. 优势和特点

#### (1) 函数式编程

```java
// 链式调用，代码更简洁
List<Long> ids = top5.stream()
    .map(Long::valueOf)
    .filter(id -> id > 1000)
    .sorted()
    .collect(Collectors.toList());
```


#### (2) 延迟执行

```java
Stream<String> stream = top5.stream()
    .map(s -> {
        System.out.println("Processing: " + s);
        return s.toUpperCase();
    });
// 此时不会输出任何内容

List<String> result = stream.collect(Collectors.toList());
// 只有在 collect 时才执行转换操作
```


### 12. 注意事项

#### (1) 流只能使用一次

```java
Stream<String> stream = top5.stream();
List<String> list1 = stream.collect(Collectors.toList());
// List<String> list2 = stream.collect(Collectors.toList()); // IllegalStateException
```


#### (2) 并行流的使用

```java
// 顺序流
List<Long> ids1 = top5.stream().map(Long::valueOf).collect(Collectors.toList());

// 并行流（适用于大数据集）
List<Long> ids2 = top5.parallelStream().map(Long::valueOf).collect(Collectors.toList());
```


在当前项目中，`stream()` 方法主要用于将从 Redis 查询到的用户 ID 字符串集合转换为长整型列表，以便后续进行数据库查询操作。这是 Java 8 Stream API 的典型应用场景，使代码更加简洁和易读。