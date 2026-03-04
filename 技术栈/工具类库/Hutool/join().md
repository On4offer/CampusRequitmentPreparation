## join() 方法介绍

### 1. 基本定义

[join()](file://cn\hutool\core\text\CharSequenceUtil.java#L224-L224) 是 Hutool 工具库中 [StrUtil](file://cn\hutool\core\util\StrUtil.java#L11-L43) 类提供的静态方法，用于将集合或数组中的元素连接成一个字符串。

### 2. 所属工具和类

- **工具/框架**：Hutool（国人开发的Java工具库）
- **类**：[cn.hutool.core.util.StrUtil](file://cn\hutool\core\util\StrUtil.java#L11-L43)
- **方法签名**：`public static String join(CharSequence conjunction, Object... objs)`

### 3. 方法功能

将多个对象或集合中的元素使用指定的分隔符连接成一个字符串。

### 4. 参数说明

- **conjunction**：连接符/分隔符
- **objs**：要连接的对象（可变参数）
- **返回值**：连接后的字符串

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
String idStr = StrUtil.join(",", ids);
```


### 6. 相关方法

| 方法                                                         | 功能            |
| ------------------------------------------------------------ | --------------- |
| `StrUtil.join(CharSequence conjunction, Object... objs)`     | 连接对象数组    |
| `StrUtil.join(CharSequence conjunction, Iterable<?> iterable)` | 连接可迭代对象  |
| `String.join(CharSequence delimiter, CharSequence... elements)` | Java 8 原生方法 |

### 7. 使用场景

#### (1) 构造 SQL IN 子句

```java
// 将 List<Long> 转换为逗号分隔的字符串
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);
String idStr = StrUtil.join(",", ids);
// 结果: "1001,1002,1003"

// 用于 SQL 查询
String sql = "SELECT * FROM user WHERE id IN (" + idStr + ")";
// 结果: "SELECT * FROM user WHERE id IN (1001,1002,1003)"
```


### 8. 在当前项目中的具体应用

#### (1) 构造 ORDER BY FIELD 语句

```java
@Override
public Result queryBlogLikes(Long id) {
    // ...
    // 2.解析出其中的用户id
    List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
    String idStr = StrUtil.join(",", ids);  // 当前分析的代码行
    // 3.根据用户id查询用户 WHERE id IN ( 5 , 1 ) ORDER BY FIELD(id, 5, 1)
    List<UserDTO> userDTOS = userService.query()
            .in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list()
            .stream()
            .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
            .collect(Collectors.toList());
    // ...
}
```


### 9. 完整示例

#### (1) 基本使用

```java
// 连接数字列表
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);
String result1 = StrUtil.join(",", ids);
// 结果: "1001,1002,1003"

// 连接字符串数组
String[] names = {"Alice", "Bob", "Charlie"};
String result2 = StrUtil.join("-", names);
// 结果: "Alice-Bob-Charlie"

// 使用不同的分隔符
List<String> words = Arrays.asList("hello", "world", "java");
String result3 = StrUtil.join(" ", words);
// 结果: "hello world java"
```


#### (2) 与 Java 8 原生方法对比

```java
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);

// Hutool 方式
String result1 = StrUtil.join(",", ids);

// Java 8 原生方式
String result2 = ids.stream()
    .map(String::valueOf)
    .collect(Collectors.joining(","));
```


### 10. 在项目中的处理流程

```java
// 1. 获取用户ID列表
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);

// 2. 使用 StrUtil.join 连接为字符串
String idStr = StrUtil.join(",", ids);
// 结果: "1001,1002,1003"

// 3. 用于 SQL ORDER BY FIELD 语句
String sqlFragment = "ORDER BY FIELD(id," + idStr + ")";
// 结果: "ORDER BY FIELD(id,1001,1002,1003)"
```


### 11. MySQL ORDER BY FIELD 说明

```sql
-- ORDER BY FIELD 的作用是按照指定顺序排列结果
SELECT * FROM user WHERE id IN (1001, 1002, 1003) 
ORDER BY FIELD(id, 1003, 1001, 1002);

-- 结果会按照 1003, 1001, 1002 的顺序返回
```


### 12. 注意事项

#### (1) 空值处理

```java
List<Long> ids = Arrays.asList(1001L, null, 1003L);
String result = StrUtil.join(",", ids);
// 结果: "1001,null,1003"
```


#### (2) 空集合处理

```java
List<Long> emptyIds = Collections.emptyList();
String result = StrUtil.join(",", emptyIds);
// 结果: ""
```


#### (3) SQL 注入风险

```java
// 在实际使用中要注意 SQL 注入风险
String idStr = StrUtil.join(",", ids);
// 确保 ids 中的值是安全的数字，而不是用户输入的内容
```


在当前项目中，`StrUtil.join()` 方法主要用于将用户ID列表转换为逗号分隔的字符串，以便在 SQL 查询的 `ORDER BY FIELD` 子句中保持用户ID的原始顺序，确保查询结果按照点赞时间的顺序返回。