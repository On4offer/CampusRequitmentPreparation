## list() 方法介绍

### 1. 基本定义

[list()](file://com\baomidou\mybatisplus\extension\service\IService.java#L31-L31) 是 MyBatis-Plus 框架提供的查询方法，用于执行查询并返回结果列表。

### 2. 所属工具和类

- **工具/框架**：MyBatis-Plus
- **接口**：[com.baomidou.mybatisplus.extension.service.IService](file://com\baomidou\mybatisplus\extension\service\IService.java#L27-L403)
- **实现类**：[com.baomidou.mybatisplus.extension.service.impl.ServiceImpl](file://com\baomidou\mybatisplus\extension\service\impl\ServiceImpl.java#L15-L51)
- **方法签名**：`List<T> list(Wrapper<T> queryWrapper)`

### 3. 方法功能

执行查询操作并返回符合条件的实体对象列表。

### 4. 参数说明

- **queryWrapper**：查询条件构造器（可选参数）
- **返回值**：`List<T>` 类型，包含查询结果的实体对象列表

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
List<UserDTO> userDTOS = userService.query()
        .in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list()  // 当前分析的代码行
        .stream()
        .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
        .collect(Collectors.toList());
```


### 6. 相关方法

| 方法                                                         | 功能                   |
| ------------------------------------------------------------ | ---------------------- |
| [list()](file://com\baomidou\mybatisplus\extension\service\IService.java#L31-L31) | 查询并返回列表         |
| [list(Wrapper<T> queryWrapper)](file://com\baomidou\mybatisplus\extension\service\IService.java#L32-L32) | 根据条件查询并返回列表 |
| [getOne(Wrapper<T> queryWrapper)](file://com\baomidou\mybatisplus\extension\service\impl\ServiceImpl.java#L44-L44) | 查询并返回单个对象     |
| `page(Page<T> page, Wrapper<T> queryWrapper)`                | 分页查询               |
| [count(Wrapper<T> queryWrapper)](file://cn\hutool\core\text\CharSequenceUtil.java#L175-L175) | 统计查询结果数量       |

### 7. 使用场景

#### (1) 查询多条记录

```java
// 查询所有用户
List<User> allUsers = userService.list();

// 根据条件查询用户
List<User> activeUsers = userService.query()
        .eq("status", 1)
        .list();
```


### 8. 在当前项目中的具体应用

#### (1) 批量查询用户信息

```java
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
            .in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list()  // 当前分析的代码行
            .stream()
            .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
            .collect(Collectors.toList());
    // 4.返回
    return Result.ok(userDTOS);
}
```


### 9. 生成的 SQL 语句

```java
// Java 代码
List<User> users = userService.query()
        .in("id", Arrays.asList(1001L, 1002L, 1003L))
        .last("ORDER BY FIELD(id, 1003, 1001, 1002)")
        .list();

// 生成的 SQL 语句
SELECT * FROM user 
WHERE id IN (1001, 1002, 1003) 
ORDER BY FIELD(id, 1003, 1001, 1002);
```


### 10. 完整示例

#### (1) 基本使用

```java
// 查询所有记录
List<User> allUsers = userService.list();

// 带条件查询
List<User> activeUsers = userService.query()
        .eq("status", 1)
        .list();

// 复杂条件查询
List<User> users = userService.query()
        .in("id", Arrays.asList(1L, 2L, 3L))
        .eq("status", 1)
        .orderByDesc("create_time")
        .list();
```


#### (2) 与其他方法对比

```java
// list() - 返回列表
List<User> userList = userService.query().eq("status", 1).list();

// getOne() - 返回单个对象
User user = userService.query().eq("id", 1L).getOne();

// count() - 返回数量
Long count = userService.query().eq("status", 1).count();
```


### 11. 在项目中的处理流程

```java
// 1. 构造查询条件
QueryWrapper<User> queryWrapper = new QueryWrapper<>();
queryWrapper.in("id", Arrays.asList(1001L, 1002L, 1003L));
queryWrapper.last("ORDER BY FIELD(id, 1003, 1001, 1002)");

// 2. 执行查询
List<User> users = userService.list(queryWrapper);

// 3. 转换为 DTO
List<UserDTO> userDTOS = users.stream()
        .map(user -> BeanUtil.copyProperties(user, UserDTO.class))
        .collect(Collectors.toList());
```


### 12. 注意事项

#### (1) 空结果处理

```java
List<User> users = userService.query().eq("id", -1L).list();
// 如果没有匹配的记录，返回空列表而不是 null
if (users.isEmpty()) {
    // 处理空结果
}
```


#### (2) 大量数据查询

```java
// 对于大量数据，建议使用分页查询
Page<User> page = userService.page(
    new Page<>(1, 100),
    new QueryWrapper<User>().eq("status", 1)
);
```


#### (3) 性能考虑

```java
// 只查询需要的字段
List<User> users = userService.query()
        .select("id", "name", "avatar")  // 只查询指定字段
        .eq("status", 1)
        .list();
```


在当前项目中，[list()](file://com\baomidou\mybatisplus\extension\service\IService.java#L47-L47) 方法用于执行最终的数据库查询操作，将前面构造的查询条件（IN 条件和自定义 ORDER BY）应用到数据库查询中，返回符合条件的用户列表，然后进一步转换为 UserDTO 对象返回给前端。