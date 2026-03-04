## getById() 方法介绍

### 1. 基本定义

[getById()](file://com\baomidou\mybatisplus\extension\service\IService.java#L165-L165) 是 MyBatis-Plus 框架提供的方法，用于根据主键 ID 查询单个实体对象。

### 2. 所属工具和类

- **工具/框架**：MyBatis-Plus
- **接口**：[com.baomidou.mybatisplus.extension.service.IService](file://com\baomidou\mybatisplus\extension\service\IService.java#L27-L403)
- **实现类**：[com.baomidou.mybatisplus.extension.service.impl.ServiceImpl](file://com\baomidou\mybatisplus\extension\service\impl\ServiceImpl.java#L15-L51)
- **方法签名**：`T getById(Serializable id)`

### 3. 方法功能

根据主键 ID 从数据库中查询对应的实体对象，是对 MyBatis-Plus 基础查询功能的封装。

### 4. 参数说明

- **id**：实体类的主键 ID，类型为 `Serializable`（可序列化对象）
- **返回值**：返回根据 ID 查询到的实体对象，如果未找到则返回 `null`

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
@Override
public Result queryBlogById(Long id) {
    // 1.查询blog
    Blog blog = getById(id);
    if (blog == null) {
        return Result.fail("笔记不存在！");
    }
    // 2.查询blog有关的用户
    queryBlogUser(blog);
    // 3.查询blog是否被点赞
    isBlogLiked(blog);
    return Result.ok(blog);
}
```


这段代码的作用是：
- 使用 [getById(id)](file://com\baomidou\mybatisplus\extension\service\IService.java#L165-L165) 方法根据博客 ID 查询对应的 [Blog](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\entity\Blog.java#L14-L221) 实体对象
- 如果查询结果为 `null`，返回错误信息
- 否则继续查询博客相关的用户信息和点赞状态

### 6. 生成的 SQL 示例

```java
Blog blog = getById(1L);
```


会生成类似以下的 SQL 语句：

```sql
SELECT id, user_id, title, content, liked, comments, create_time, update_time 
FROM blog 
WHERE id = 1
```


### 7. 相关方法

| 方法                                                         | 功能                     |
| ------------------------------------------------------------ | ------------------------ |
| [getById(Serializable id)](file://com\baomidou\mybatisplus\extension\service\IService.java#L165-L165) | 根据 ID 查询单个实体     |
| `getByIds(Collection<? extends Serializable> idList)`        | 根据 ID 列表批量查询实体 |
| [getOne(Wrapper<T> queryWrapper)](file://com\baomidou\mybatisplus\extension\service\IService.java#L40-L40) | 根据条件查询单个实体     |
| `listByIds(Collection<? extends Serializable> idList)`       | 根据 ID 列表查询实体列表 |

### 8. 使用场景

#### (1) 根据主键查询单个对象

```java
// 查询指定 ID 的用户
User user = userService.getById(1L);

// 查询指定 ID 的博客
Blog blog = blogService.getById(blogId);
```


#### (2) 在业务方法中的使用

```java
@Override
public Result queryBlogById(Long id) {
    // 1.查询blog
    Blog blog = getById(id);
    if (blog == null) {
        return Result.fail("笔记不存在！");
    }
    // 2.查询blog有关的用户
    queryBlogUser(blog);
    // 3.查询blog是否被点赞
    isBlogLiked(blog);
    return Result.ok(blog);
}
```


### 9. 注意事项

#### (1) 返回值检查

```java
Blog blog = getById(id);
if (blog == null) {
    // 处理对象不存在的情况
    return Result.fail("博客不存在");
}
```


#### (2) 主键类型匹配

```java
// 确保传入的 ID 类型与实体类主键类型匹配
Blog blog = getById(1L);     // Long 类型主键
User user = getById("user1"); // String 类型主键
```


### 10. 在当前项目中的作用

在 [BlogServiceImpl](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L32-L216) 的 [queryBlogById](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L76-L88) 方法中，[getById()](file://com\baomidou\mybatisplus\extension\service\IService.java#L165-L165) 方法用于：

1. **查询博客详情**：根据博客 ID 从数据库中获取完整的博客信息
2. **数据验证**：检查博客是否存在，避免空指针异常
3. **业务处理前置**：为后续的用户信息查询和点赞状态检查提供数据基础

这是 MyBatis-Plus 框架中最常用的单实体查询方法之一，简化了根据主键查询数据的操作。