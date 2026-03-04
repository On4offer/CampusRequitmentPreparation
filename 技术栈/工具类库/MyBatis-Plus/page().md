## page() 方法介绍

### 1. 基本定义

[page()](file://com\baomidou\mybatisplus\extension\service\IService.java#L49-L49) 是 MyBatis-Plus 框架提供的分页查询方法，用于执行带有分页功能的数据库查询操作。

### 2. 所属工具和类

- **工具/框架**：MyBatis-Plus
- **类**：[com.baomidou.mybatisplus.extension.service.impl.ServiceImpl](file://com\baomidou\mybatisplus\extension\service\impl\ServiceImpl.java#L15-L51)（继承自 `com.baomidou.mybatisplus.core.conditions.query.QueryWrapper`）
- **方法签名**：`Page<T> page(Page<T> page, Wrapper<T> queryWrapper)`

### 3. 方法功能

执行分页查询操作，根据传入的分页参数和查询条件，从数据库中获取指定页码和每页记录数的数据。

### 4. 参数说明

- **page**：分页参数对象，包含页码和每页记录数等信息
- **queryWrapper**：查询条件构造器，包含查询条件和排序规则
- **返回值**：包含查询结果和分页信息的 `Page<T>` 对象

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
- 调用 [page()](file://com\baomidou\mybatisplus\extension\service\IService.java#L49-L49) 方法执行分页查询，传入 [Page](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L26-L26) 对象指定当前页码和每页记录数

### 6. 生成的 SQL 示例

上述代码会生成类似以下的 SQL 语句：

```sql
SELECT * FROM blog ORDER BY liked DESC LIMIT 0, 10
```


具体 LIMIT 的参数取决于 [current](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L62-L62) 和 [SystemConstants.MAX_PAGE_SIZE](file://com\baomidou\mybatisplus\core\conditions\Wrapper.java#L43-L43) 的值。

### 7. 相关方法

| 方法                                                         | 功能                     |
| ------------------------------------------------------------ | ------------------------ |
| [page(Page<T> page)](file://com\baomidou\mybatisplus\extension\service\IService.java#L48-L48) | 执行分页查询             |
| `page(Page<T> page, Wrapper<T> queryWrapper)`                | 根据查询条件执行分页查询 |
| `pageMaps(Page<T> page, Wrapper<T> queryWrapper)`            | 分页查询并返回 Map 结果  |

### 8. 使用场景

#### (1) 基础分页查询

```java
// 查询第一页，每页10条记录
Page<Blog> page = new Page<>(1, 10);
Page<Blog> result = page(page);
```


#### (2) 带条件的分页查询

```java
// 查询状态为1的博客，按创建时间倒序排列
Page<Blog> page = new Page<>(1, 10);
Page<Blog> result = query()
    .eq("status", 1)
    .orderByDesc("create_time")
    .page(page);
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
    // ... 其他处理逻辑
    return Result.ok(records);
}
```


### 9. 注意事项

#### (1) Page 对象初始化

```java
// 第一个参数是当前页码（从1开始），第二个参数是每页记录数
new Page<>(current, SystemConstants.MAX_PAGE_SIZE)
```


#### (2) 返回结果处理

```java
Page<Blog> page = query().page(new Page<>(current, size));
List<Blog> records = page.getRecords(); // 获取当前页数据
long total = page.getTotal(); // 获取总记录数
long pages = page.getPages(); // 获取总页数
```


### 10. 在当前项目中的作用

在 [BlogServiceImpl](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L32-L188) 的 [queryHotBlog](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L57-L71) 方法中，[page()](file://com\baomidou\mybatisplus\extension\service\IService.java#L49-L49) 方法用于：

1. **分页查询热门博客**：结合排序功能，实现热门博客的分页展示
2. **控制数据量**：通过 [SystemConstants.MAX_PAGE_SIZE](file://com\baomidou\mybatisplus\core\conditions\Wrapper.java#L43-L43) 控制每次查询的数据量
3. **提升性能**：避免一次性加载大量数据，提高系统响应速度

这是 MyBatis-Plus 框架中非常核心的分页查询方法，极大地简化了分页功能的实现。