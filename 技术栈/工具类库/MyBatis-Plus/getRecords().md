## getRecords() 方法介绍

### 1. 基本定义

[getRecords()](file://com\baomidou\mybatisplus\core\metadata\IPage.java#L14-L14) 是 MyBatis-Plus 框架中 [Page](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L6-L61) 类提供的方法，用于获取分页查询结果中的数据记录列表。

### 2. 所属工具和类

- **工具/框架**：MyBatis-Plus
- **类**：[com.baomidou.mybatisplus.extension.plugins.pagination.Page](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L6-L61)
- **方法签名**：`List<T> getRecords()`

### 3. 方法功能

从分页查询结果中获取当前页的数据记录列表，不包含分页相关的元数据（如总记录数、总页数等）。

### 4. 参数说明

- **返回值**：返回当前页的数据记录列表，类型为 `List<T>`，其中 T 是具体的实体类类型

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
Page<Blog> page = query()
        .orderByDesc("liked")
        .page(new Page<>(current, SystemConstants.MAX_PAGE_SIZE));
// 获取当前页数据
List<Blog> records = page.getRecords();
```


这段代码的作用是：
- 使用 [query()](file://com\baomidou\mybatisplus\extension\service\IService.java#L60-L60) 方法创建查询构造器并执行分页查询
- 调用 [getRecords()](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L24-L24) 方法从分页结果中提取实际的博客数据列表
- 获取到的 [records](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L8-L8) 列表包含当前页的所有博客记录

### 6. Page 类的主要属性和方法

[Page](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L6-L61) 对象不仅包含数据记录，还包含分页相关的元数据：

```java
Page<Blog> page = query().page(new Page<>(current, size));

List<Blog> records = page.getRecords(); // 当前页数据
long total = page.getTotal();           // 总记录数
long size = page.getSize();             // 每页记录数
long current = page.getCurrent();       // 当前页码
long pages = page.getPages();           // 总页数
boolean hasNext = page.hasNext();       // 是否有下一页
boolean hasPrevious = page.hasPrevious(); // 是否有上一页
```


### 7. 相关方法

| 方法                                                         | 功能                   |
| ------------------------------------------------------------ | ---------------------- |
| [getRecords()](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L24-L24) | 获取当前页数据记录列表 |
| [setRecords(List<T> records)](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L25-L25) | 设置当前页数据记录列表 |
| [getTotal()](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L26-L26) | 获取总记录数           |
| [getSize()](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L28-L28) | 获取每页记录数         |
| [getCurrent()](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L30-L30) | 获取当前页码           |
| [getPages()](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L43-L43) | 获取总页数             |

### 8. 使用场景

#### (1) 获取分页数据

```java
Page<User> page = userService.page(new Page<>(1, 10));
List<User> users = page.getRecords(); // 获取第一页的10条用户数据
```


#### (2) 数据处理和转换

```java
Page<Blog> page = blogService.page(new Page<>(1, 5));
List<Blog> blogs = page.getRecords();

// 对数据进行进一步处理
blogs.forEach(blog -> {
    // 处理每条博客数据
    processBlog(blog);
});
```


#### (3) 在业务方法中的使用

```java
@Override
public Result queryHotBlog(Integer current) {
    // 根据点赞数降序排列并分页查询博客数据
    Page<Blog> page = query()
            .orderByDesc("liked")
            .page(new Page<>(current, SystemConstants.MAX_PAGE_SIZE));
    // 获取当前页数据
    List<Blog> records = page.getRecords();
    // 查询用户信息并判断博客是否被当前用户点赞
    records.forEach(blog -> {
        this.queryBlogUser(blog);
        this.isBlogLiked(blog);
    });
    return Result.ok(records);
}
```


### 9. 注意事项

#### (1) 返回值类型

```java
// 返回的是 List<T> 类型，可以直接用于循环遍历
List<Blog> records = page.getRecords();
for (Blog blog : records) {
    // 处理每条博客
}
```


#### (2) 空列表处理

```java
List<Blog> records = page.getRecords();
if (records.isEmpty()) {
    // 处理空数据情况
}
```


### 10. 在当前项目中的作用

在 [BlogServiceImpl](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L32-L188) 的 [queryHotBlog](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L57-L71) 方法中，[getRecords()](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L24-L24) 方法用于：

1. **提取分页数据**：从分页查询结果中提取实际的博客数据列表
2. **数据处理**：获取数据后对每条博客进行用户信息查询和点赞状态检查
3. **结果返回**：将处理后的博客列表封装到 [Result](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\dto\Result.java#L12-L74) 对象中返回给前端

这是 MyBatis-Plus 分页查询中非常关键的方法，用于从分页结果中提取实际需要的数据记录。