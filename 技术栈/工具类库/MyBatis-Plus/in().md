## in() 方法介绍

### 1. 基本定义

[in()](file://com\baomidou\mybatisplus\extension\service\IService.java#L37-L37) 是 MyBatis-Plus 框架提供的查询构造器方法，用于构建 SQL 查询语句中的 `IN` 条件。

### 2. 所属工具和类

- **工具/框架**：MyBatis-Plus
- **类**：[com.baomidou.mybatisplus.extension.service.impl.ServiceImpl](file://com\baomidou\mybatisplus\extension\service\impl\ServiceImpl.java#L15-L51)（继承自查询构造器）
- **方法签名**：`Children in(R column, Collection<?> value)`

### 3. 方法功能

构建 SQL 查询语句中的 `IN` 条件，用于查询指定字段值在给定集合中的记录。

### 4. 参数说明

- **column**：数据库字段名（或实体类属性名）
- **value**：值的集合
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

| 方法                                                         | 功能        |
| ------------------------------------------------------------ | ----------- |
| [in(R column, Collection<?> value)](file://com\baomidou\mybatisplus\extension\service\IService.java#L37-L37) | IN 条件查询 |
| `eq(R column, Object val)`                                   | 等于条件    |
| `ne(R column, Object val)`                                   | 不等于条件  |
| `gt(R column, Object val)`                                   | 大于条件    |
| `lt(R column, Object val)`                                   | 小于条件    |

### 7. 使用场景

#### (1) 批量查询

```java
// 根据多个ID批量查询用户
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);
List<User> users = userService.query()
        .in("id", ids)
        .list();
```


### 8. 在当前项目中的具体应用

#### (1) 批量查询用户信息

```java
@Override
public Result queryBlogLikes(Long id) {
    // ...
    // 2.解析出其中的用户id
    List<Long> ids = top5.stream().map(Long::valueOf).collect(Collectors.toList());
    String idStr = StrUtil.join(",", ids);
    // 3.根据用户id查询用户 WHERE id IN ( 5 , 1 ) ORDER BY FIELD(id, 5, 1)
    List<UserDTO> userDTOS = userService.query()
            .in("id", ids)                    // 当前分析的代码行
            .last("ORDER BY FIELD(id," + idStr + ")")
            .list()
            .stream()
            .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
            .collect(Collectors.toList());
    // ...
}
```


### 9. 生成的 SQL 语句

```java
// Java 代码
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);
List<User> users = userService.query()
        .in("id", ids)
        .list();

// 生成的 SQL 语句
SELECT * FROM user WHERE id IN (1001, 1002, 1003);
```


### 10. 完整示例

#### (1) 基本使用

```java
// 查询指定ID的用户
List<Long> userIds = Arrays.asList(1001L, 1002L, 1003L);
List<User> users = userService.query()
        .in("id", userIds)
        .list();

// 查询指定状态的博客
List<Integer> statuses = Arrays.asList(1, 2);
List<Blog> blogs = blogService.query()
        .in("status", statuses)
        .list();
```


#### (2) 链式调用

```java
List<User> users = userService.query()
        .in("id", ids)
        .eq("status", 1)
        .orderByDesc("create_time")
        .list();
```


### 11. 在项目中的处理流程

```java
// 1. 获取用户ID列表（从Redis点赞记录中解析）
List<Long> ids = Arrays.asList(1001L, 1002L, 1003L);

// 2. 使用 in() 方法构建查询条件
List<User> users = userService.query()
        .in("id", ids)                           // WHERE id IN (1001, 1002, 1003)
        .last("ORDER BY FIELD(id," + idStr + ")") // 保持原始顺序
        .list();

// 3. 转换为 UserDTO 并返回
List<UserDTO> userDTOS = users.stream()
        .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
        .collect(Collectors.toList());
```


### 12. 注意事项

#### (1) 空集合处理

```java
List<Long> emptyIds = Collections.emptyList();
List<User> users = userService.query()
        .in("id", emptyIds)
        .list();
// 生成的 SQL: SELECT * FROM user WHERE id IN ()
// 可能导致 SQL 语法错误
```


#### (2) 安全处理

```java
// 应该检查集合是否为空
if (!ids.isEmpty()) {
    List<User> users = userService.query()
            .in("id", ids)
            .list();
} else {
    // 处理空集合情况
    return Collections.emptyList();
}
```


#### (3) 性能考虑

```java
// IN 条件中的元素不宜过多，建议分批查询
if (ids.size() > 1000) {
    // 分批处理
}
```


在当前项目中，`in()` 方法主要用于根据点赞用户ID列表批量查询用户信息，这是 MyBatis-Plus 提供的便捷查询方法，可以避免编写复杂的 SQL 语句，同时保持代码的可读性和维护性。