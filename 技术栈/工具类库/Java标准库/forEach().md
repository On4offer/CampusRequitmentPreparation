## forEach() 方法介绍

### 1. 基本定义

[forEach()](file://C:\Users\Enzo\AppData\Local\Programs\Java\jdk-8\src.zip!\java\lang\Iterable.java#L1-L1) 是 Java 8 引入的 Iterable 接口的默认方法，用于对集合中的每个元素执行指定的操作。

### 2. 所属工具和类

- **工具/框架**：Java 标准库 (Java SE)
- **接口**：`java.lang.Iterable`
- **方法签名**：`default void forEach(Consumer<? super T> action)`

### 3. 方法功能

对集合中的每个元素执行给定的操作，这是 Java 8 引入的函数式编程特性之一，用于简化集合遍历操作。

### 4. 参数说明

- **action**：要对每个元素执行的操作，是一个 `Consumer` 函数式接口
- **返回值**：无返回值（void）

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
List<Blog> records = page.getRecords();
// 查询用户信息并判断博客是否被当前用户点赞
records.forEach(blog -> {
    this.queryBlogUser(blog);
    this.isBlogLiked(blog);
});
```


这段代码的作用是：
- 获取分页查询结果中的博客列表 [records](file://com\baomidou\mybatisplus\extension\plugins\pagination\Page.java#L8-L8)
- 使用 [forEach()](file://C:\Users\Enzo\AppData\Local\Programs\Java\jdk-8\src.zip!\java\lang\Iterable.java#L1-L1) 方法遍历每篇博客
- 对每篇博客执行 [queryBlogUser(blog)](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L182-L190) 和 [isBlogLiked(blog)](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L96-L107) 操作

### 6. Lambda 表达式示例

[forEach()](file://C:\Users\Enzo\AppData\Local\Programs\Java\jdk-8\src.zip!\java\lang\Iterable.java#L1-L1) 方法通常与 Lambda 表达式一起使用：

```java
List<String> names = Arrays.asList("Alice", "Bob", "Charlie");

// 传统方式
for (String name : names) {
    System.out.println(name);
}

// 使用 forEach 和 Lambda 表达式
names.forEach(name -> System.out.println(name));

// 使用方法引用
names.forEach(System.out::println);
```


### 7. 相关方法

| 方法                                                         | 功能                   |
| ------------------------------------------------------------ | ---------------------- |
| [forEach(Consumer<? super T> action)](file://C:\Users\Enzo\AppData\Local\Programs\Java\jdk-8\src.zip!\java\lang\Iterable.java#L1-L1) | 对每个元素执行指定操作 |
| `iterator()`                                                 | 返回迭代器             |
| `spliterator()`                                              | 返回可分割迭代器       |

### 8. 使用场景

#### (1) 简化集合遍历

```java
List<User> users = userService.list();
users.forEach(user -> {
    // 处理每个用户
    processUser(user);
});
```


#### (2) 与 Stream API 结合使用

```java
List<Blog> blogs = blogService.list();
blogs.stream()
     .filter(blog -> blog.getStatus() == 1)
     .forEach(blog -> {
         // 处理状态为1的博客
         handleBlog(blog);
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

#### (1) 不能在 forEach 中修改集合结构

```java
List<String> names = new ArrayList<>();
names.add("Alice");
names.add("Bob");

// 错误：在遍历过程中修改集合结构会导致 ConcurrentModificationException
names.forEach(name -> {
    if ("Bob".equals(name)) {
        names.remove(name); // 危险操作
    }
});
```


#### (2) 与传统 for-each 循环的对比

```java
List<Blog> records = page.getRecords();

// 传统方式
for (Blog blog : records) {
    queryBlogUser(blog);
    isBlogLiked(blog);
}

// 使用 forEach（更简洁）
records.forEach(blog -> {
    queryBlogUser(blog);
    isBlogLiked(blog);
});
```


### 10. 在当前项目中的作用

在 [BlogServiceImpl](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L32-L188) 的 [queryHotBlog](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java#L57-L71) 方法中，[forEach()](file://C:\Users\Enzo\AppData\Local\Programs\Java\jdk-8\src.zip!\java\lang\Iterable.java#L1-L1) 方法用于：

1. **简化数据处理**：遍历分页查询得到的博客列表
2. **批量处理**：对每篇博客执行用户信息查询和点赞状态检查
3. **提高代码可读性**：相比传统 for 循环，[forEach()](file://C:\Users\Enzo\AppData\Local\Programs\Java\jdk-8\src.zip!\java\lang\Iterable.java#L1-L1) 使代码更加简洁易读

这是 Java 8 引入的现代集合遍历方式，是函数式编程在 Java 中的重要体现。