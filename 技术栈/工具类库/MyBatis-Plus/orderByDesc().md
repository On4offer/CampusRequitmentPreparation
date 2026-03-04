## orderByDesc 方法介绍

### 1. 基本定义

`orderByDesc` 是 MyBatis-Plus 框架提供的链式调用方法，用于构建 SQL 查询语句中的 ORDER BY 子句，实现按指定字段降序排序。

### 2. 所属工具和类

- **工具/框架**：MyBatis-Plus
- **类**：[com.baomidou.mybatisplus.extension.service.impl.ServiceImpl](file://com\baomidou\mybatisplus\extension\service\impl\ServiceImpl.java#L15-L51)（继承自 `com.baomidou.mybatisplus.core.conditions.query.QueryWrapper`）
- **方法签名**：`Children orderByDesc(R... columns)`

### 3. 方法功能

用于构建 SQL 查询语句，按照指定的列进行降序（DESC）排序。

### 4. 参数说明

- **columns**：可变参数，指定需要按降序排序的字段名
- **返回值**：返回当前查询构造器对象，支持链式调用

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
Page<Blog> page = query()
        .orderByDesc("liked")
        .page(new Page<>(current, SystemConstants.MAX_PAGE_SIZE));
```


这段代码的作用是：
- 使用 [query()](file://com\baomidou\mybatisplus\extension\service\IService.java#L60-L60) 方法创建一个查询构造器
- 调用 `orderByDesc("liked")` 按照 "liked" 字段降序排序
- 通过 [page()](file://com\baomidou\mybatisplus\extension\service\IService.java#L49-L49) 方法执行分页查询

### 6. 生成的 SQL 示例

上述代码会生成类似以下的 SQL 语句：

```sql
SELECT * FROM blog ORDER BY liked DESC LIMIT 0, 10
```


### 7. 相关方法

| 方法                                                      | 功能                   |
| --------------------------------------------------------- | ---------------------- |
| `orderByDesc(R... columns)`                               | 按指定字段降序排序     |
| `orderByAsc(R... columns)`                                | 按指定字段升序排序     |
| `orderBy(boolean condition, boolean isAsc, R... columns)` | 根据条件和排序方式排序 |

### 8. 使用场景

#### (1) 查询热门数据

```java
// 查询点赞数最高的博客
List<Blog> hotBlogs = query()
    .orderByDesc("liked")
    .list();
```


#### (2) 时间倒序查询

```java
// 查询最新发布的博客
List<Blog> latestBlogs = query()
    .orderByDesc("create_time")
    .list();
```


#### (3) 多字段排序

```java
// 先按点赞数降序，再按创建时间降序
List<Blog> blogs = query()
    .orderByDesc("liked", "create_time")
    .list();
```


### 9. 注意事项

#### (1) 字段名称

```java
// 使用数据库字段名（通常是下划线命名）
.orderByDesc("create_time")

// 或使用实体类字段名（驼峰命名）
.orderByDesc("createTime")
```


#### (2) 链式调用

```java
// 支持链式调用
Page<Blog> page = query()
    .eq("status", 1)
    .orderByDesc("liked")
    .page(new Page<>(current, size));
```


### 10. 在当前项目中的作用

在 [BlogServiceImpl](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L32-L188) 的 [queryHotBlog](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L57-L71) 方法中，`orderByDesc("liked")` 用于：

1. **热门博客查询**：按照博客的点赞数降序排列
2. **分页展示**：结合分页功能，展示最受欢迎的博客列表
3. **用户体验优化**：让用户优先看到最受欢迎的内容

这是 MyBatis-Plus 框架中非常实用的链式查询方法，简化了 SQL 排序语句的编写。