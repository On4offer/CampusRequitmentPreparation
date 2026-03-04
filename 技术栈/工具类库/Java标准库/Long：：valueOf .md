## Long::valueOf 方法引用详解

### 1. 基本概念

`Long::valueOf` 是 Java 8 引入的**方法引用**（Method Reference）语法，它是 Lambda 表达式的简化写法。

### 2. 语法结构

```java
// 方法引用语法
ClassName::methodName
```


- **Long**：类名
- **::**：方法引用操作符
- **valueOf**：静态方法名

### 3. 等价关系

```java
// 方法引用写法
Long::valueOf

// 等价的 Lambda 表达式写法
(s) -> Long.valueOf(s)

// 等价的传统匿名类写法
new Function<String, Long>() {
    @Override
    public Long apply(String s) {
        return Long.valueOf(s);
    }
}
```


### 4. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
```


这行代码的完整执行流程：

```java
// 1. top5 是 Set<String> 类型，包含用户ID字符串
Set<String> top5 = {"1001", "1002", "1003"};

// 2. 创建流
Stream<String> stream = top5.stream();  // 流中元素: "1001", "1002", "1003"

// 3. 使用 map 和 Long::valueOf 进行转换
Stream<Long> longStream = stream.map(Long::valueOf);
// 转换过程:
// "1001" -> Long.valueOf("1001") -> 1001L
// "1002" -> Long.valueOf("1002") -> 1002L
// "1003" -> Long.valueOf("1003") -> 1003L

// 4. 收集结果
List<Long> ids = longStream.collect(Collectors.toList());
// 结果: [1001L, 1002L, 1003L]
```


### 5. Long.valueOf() 方法说明

```java
// Long 类中的 valueOf 方法
public static Long valueOf(String s) {
    return Long.valueOf(parseLong(s));
}

// 使用示例
Long result1 = Long.valueOf("1001");  // 返回 Long 对象，值为 1001
Long result2 = Long.valueOf("abc");   // 抛出 NumberFormatException
```


### 6. 方法引用的类型

Java 中有四种方法引用：

| 类型             | 语法                      | 示例                  | 等价 Lambda                  |
| ---------------- | ------------------------- | --------------------- | ---------------------------- |
| 静态方法引用     | `ClassName::staticMethod` | `Long::valueOf`       | `s -> Long.valueOf(s)`       |
| 实例方法引用     | `instance::method`        | `System.out::println` | `x -> System.out.println(x)` |
| 特定类型实例方法 | `ClassName::method`       | `String::length`      | `s -> s.length()`            |
| 构造方法引用     | `ClassName::new`          | `ArrayList::new`      | `() -> new ArrayList<>()`    |

### 7. 在当前项目中的应用

#### (1) 数据类型转换

```java
// 从 Redis 获取的是字符串类型的用户ID
Set<String> top5 = stringRedisTemplate.opsForZSet().range(key, 0, 4);
// 示例: {"1001", "1002", "1003"}

// 需要转换为 Long 类型用于数据库查询
List<Long> ids = top5.stream()
    .map(Long::valueOf)  // 每个 String 元素调用 Long.valueOf() 转换
    .collect(Collectors.toList());
// 结果: [1001L, 1002L, 1003L]
```


#### (2) 为什么使用方法引用

```java
// 方式1：方法引用（推荐）
.map(Long::valueOf)

// 方式2：Lambda 表达式（功能相同，但更冗长）
.map(s -> Long.valueOf(s))

// 方式3：传统方式（最冗长）
List<Long> ids = new ArrayList<>();
for (String s : top5) {
    ids.add(Long.valueOf(s));
}
```


### 8. 执行过程详解

```java
// 假设 top5 = {"1001", "1002", "1003"}

top5.stream()                           // 创建流: ["1001", "1002", "1003"]
    .map(Long::valueOf)                 // 应用转换:
                                        // Long.valueOf("1001") -> 1001L
                                        // Long.valueOf("1002") -> 1002L
                                        // Long.valueOf("1003") -> 1003L
    .collect(Collectors.toList());      // 收集结果: [1001L, 1002L, 1003L]
```


### 9. 注意事项

#### (1) 异常处理

```java
// 如果字符串不是有效数字，会抛出 NumberFormatException
Set<String> top5 = {"1001", "invalid", "1003"};

try {
    List<Long> ids = top5.stream()
        .map(Long::valueOf)
        .collect(Collectors.toList());
} catch (NumberFormatException e) {
    // 处理转换异常
}
```


#### (2) 空值处理

```java
// 方法引用不会处理 null 值
Set<String> top5 = {"1001", null, "1003"};  // 包含 null

List<Long> ids = top5.stream()
    .filter(Objects::nonNull)              // 先过滤掉 null
    .map(Long::valueOf)
    .collect(Collectors.toList());
```


在当前项目中，`Long::valueOf` 方法引用用于将从 Redis 查询到的用户 ID 字符串转换为长整型，这是一种简洁、高效的类型转换方式，充分利用了 Java 8 Stream API 和方法引用的特性。