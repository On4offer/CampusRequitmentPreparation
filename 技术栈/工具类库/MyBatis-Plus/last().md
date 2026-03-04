## last() 方法介绍

### 1. 基本定义

[last()](file://com\baomidou\mybatisplus\core\conditions\query\ QueryWrapper.java#L36-L36) 是 MyBatis-Plus 框架提供的查询构造器方法，用于在生成的 SQL 语句末尾追加自定义的 SQL 片段。

### 2. 所属工具和类

- **工具/框架**：MyBatis-Plus
- **类**：`com.baomidou.mybatisplus.core.conditions.query.QueryWrapper`
- **方法签名**：`Children last(String lastSql)`

### 3. 方法功能

在生成的 SQL 语句末尾追加自定义的 SQL 片段，通常用于添加 `ORDER BY`、`LIMIT` 等子句。

### 4. 参数说明

- **lastSql**：要追加的 SQL 片段字符串
- **返回值**：查询构造器对象，支持链式调用

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
List<UserDTO> userDTOS = userService.query()
        .in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list()
        .stream()
        .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
        .collect(Collectors.toList());
```


### 6. 相关方法

| 方法                                                         | 功能                    |
| ------------------------------------------------------------ | ----------------------- |
| [last(String lastSql)](file://com\baomidou\mybatisplus\core\conditions\query\ QueryWrapper.java#L36-L36) | 在SQL末尾追加自定义片段 |
| `orderByAsc(R... columns)`                                   | 按字段升序排序          |
| `orderByDesc(R... columns)`                                  | 按字段降序排序          |
| `limit(Long limit)`                                          | 限制查询结果数量        |

### 7. 使用场景

#### (1) 自定义排序

```java
// 使用 MySQL 的 FIELD 函数保持特定顺序
String idStr = "1003,1001,1002";
List<User> users = userService.query()
        .in("id", Arrays.asList(1001L, 1002L, 1003L))
        .last("ORDER BY FIELD(id," + idStr + ")")
        .list();
```


### 8. 在当前项目中的具体应用

#### (1) 保持点赞用户顺序

```java
@Override
public Result queryBlogLikes(Long id) {
    // ...
    // 2.解析出其中的用户id
    List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
    String idStr = StrUtil.join(",", ids);
    // 3.根据用户id查询用户 WHERE id IN ( 5 , 1 ) ORDER BY FIELD(id, 5, 1)
    List<UserDTO> userDTOS = userService.query()
            .in("id", ids)
            .last("ORDER BY FIELD(id," + idStr + ")")  // 当前分析的代码行
            .list()
            .stream()
            .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
            .collect(Collectors.toList());
    // ...
}
```


### 9. MySQL FIELD 函数说明

```sql
-- FIELD 函数语法
FIELD(str, str1, str2, str3, ...)

-- 示例
SELECT FIELD('b', 'a', 'b', 'c');  -- 返回 2
SELECT FIELD('d', 'a', 'b', 'c');  -- 返回 0

-- 在 ORDER BY 中使用
SELECT * FROM user WHERE id IN (1, 2, 3)
ORDER BY FIELD(id, 3, 1, 2);
-- 结果按 id=3, id=1, id=2 的顺序返回
```


### 10. 生成的 SQL 语句

```java
// Java 代码
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);
String idStr = "1003,1001,1002";
List<User> users = userService.query()
        .in("id", ids)
        .last("ORDER BY FIELD(id," + idStr + ")")
        .list();

// 生成的 SQL 语句
SELECT * FROM user 
WHERE id IN (1001, 1002, 1003) 
ORDER BY FIELD(id, 1003, 1001, 1002);
```


### 11. 完整示例

#### (1) 基本使用

```java
// 添加自定义 ORDER BY
List<User> users = userService.query()
        .eq("status", 1)
        .last("ORDER BY create_time DESC")
        .list();

// 添加 LIMIT
List<User> users2 = userService.query()
        .eq("status", 1)
        .last("LIMIT 10")
        .list();

// 组合使用
List<User> users3 = userService.query()
        .eq("status", 1)
        .last("ORDER BY create_time DESC LIMIT 10")
        .list();
```


### 12. 在项目中的处理流程

```java
// 1. 从 Redis 获取点赞用户ID（按时间顺序）
Set<String> top5 = {"1003", "1001", "1002"};  // 按点赞时间排序

// 2. 转换为 List<Long>
List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
// 结果: [1003L, 1001L, 1002L]

// 3. 转换为逗号分隔字符串
String idStr = StrUtil.join(",", ids);
// 结果: "1003,1001,1002"

// 4. 使用 last() 保持原始顺序
List<User> users = userService.query()
        .in("id", ids)                           // WHERE id IN (1003, 1001, 1002)
        .last("ORDER BY FIELD(id," + idStr + ")") // ORDER BY FIELD(id, 1003, 1001, 1002)
        .list();
// 查询结果保持点赞时间顺序: 1003, 1001, 1002
```


### 13. 注意事项

#### (1) SQL 注入风险

```java
// 注意防止 SQL 注入
String userInput = "1001; DROP TABLE user; --";
// 不要直接拼接用户输入到 last() 方法中

// 应该验证和清理输入
if (StrUtil.isNumeric(userInput)) {
    query.last("ORDER BY FIELD(id," + userInput + ")");
}
```


#### (2) 数据库兼容性

```java
// FIELD 函数是 MySQL 特有的
// 在其他数据库中可能需要使用不同的方式实现
.last("ORDER BY CASE id WHEN 1003 THEN 1 WHEN 1001 THEN 2 WHEN 1002 THEN 3 END")
```


在当前项目中，`last()` 方法主要用于在 SQL 查询末尾添加 `ORDER BY FIELD` 子句，确保从数据库查询出的用户信息保持与 Redis 中点赞顺序一致，这是实现点赞排行榜功能的关键技术点。