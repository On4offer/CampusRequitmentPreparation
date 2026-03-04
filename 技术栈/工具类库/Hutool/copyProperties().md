## copyProperties() 方法介绍

### 1. 基本定义

[copyProperties()](file://cn\hutool\core\bean\BeanUtil.java#L55-L55) 是 Hutool 工具库中 [BeanUtil](file://cn\hutool\core\bean\BeanUtil.java#L12-L67) 类提供的静态方法，用于将一个 Java Bean 对象的属性值复制到另一个 Bean 对象中。

### 2. 所属工具和类

- **工具/框架**：Hutool（国人开发的Java工具库）
- **类**：[cn.hutool.core.bean.BeanUtil](file://cn\hutool\core\bean\BeanUtil.java#L12-L67)
- **方法签名**：`public static <T> T copyProperties(Object source, Class<T> targetClass)`

### 3. 方法功能

将源对象（source）中的属性值复制到目标对象中，实现对象之间的属性拷贝，常用于 DTO 与实体类之间的转换。

### 4. 参数说明

- **source**：源对象，提供属性值
- **targetClass**：目标类的 Class 对象
- **返回值**：目标类的新实例，包含从源对象复制的属性值

### 5. 在代码中的使用

在当前 [BlogServiceImpl.java](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\service\impl\BlogServiceImpl.java) 文件中：

```java
List<UserDTO> userDTOS = userService.query()
        .in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list()
        .stream()
        .map(user -> BeanUtil.copyProperties(user, UserDTO.class))  // 当前分析的代码行
        .collect(Collectors.toList());
```


### 6. 相关方法

| 方法                                                         | 功能                      |
| ------------------------------------------------------------ | ------------------------- |
| `BeanUtil.copyProperties(Object source, Class<T> targetClass)` | 复制属性并创建新对象      |
| `BeanUtil.copyProperties(Object source, Object target)`      | 复制属性到已有对象        |
| `BeanUtils.copyProperties(Object source, Object target)`     | Spring 框架提供的类似方法 |

### 7. 使用场景

#### (1) DTO 与实体类转换

```java
// 将 User 实体转换为 UserDTO
User user = new User();
user.setId(1L);
user.setName("Alice");
user.setEmail("alice@example.com");

// 使用 Hutool 进行属性拷贝
UserDTO userDTO = BeanUtil.copyProperties(user, UserDTO.class);
```


### 8. 在当前项目中的具体应用

#### (1) 实体类到 DTO 的转换

```java
@Override
public Result queryBlogLikes(Long id) {
    // ...
    // 3.根据用户id查询用户 WHERE id IN ( 5 , 1 ) ORDER BY FIELD(id, 5, 1)
    List<UserDTO> userDTOS = userService.query()
            .in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list()
            .stream()
            .map(user -> BeanUtil.copyProperties(user, UserDTO.class))  // 当前分析的代码行
            .collect(Collectors.toList());
    // 4.返回
    return Result.ok(userDTOS);
}
```


### 9. 完整示例

#### (1) 基本使用

```java
// User 实体类
public class User {
    private Long id;
    private String name;
    private String email;
    private String icon;
    // getters and setters...
}

// UserDTO 类
public class UserDTO {
    private Long id;
    private String name;
    private String icon;
    // getters and setters...
}

// 属性拷贝
User user = new User();
user.setId(1L);
user.setName("Alice");
user.setEmail("alice@example.com");
user.setIcon("avatar.jpg");

// 使用 Hutool 进行拷贝
UserDTO userDTO = BeanUtil.copyProperties(user, UserDTO.class);
// userDTO 包含 id, name, icon 属性值，email 属性被忽略（UserDTO 中没有）
```


#### (2) 与传统方式对比

```java
// 传统手动拷贝方式
UserDTO userDTO1 = new UserDTO();
userDTO1.setId(user.getId());
userDTO1.setName(user.getName());
userDTO1.setIcon(user.getIcon());

// Hutool 方式（更简洁）
UserDTO userDTO2 = BeanUtil.copyProperties(user, UserDTO.class);
```


### 10. 在项目中的处理流程

```java
// 1. 从数据库查询 User 实体列表
List<User> users = userService.query()
        .in("id", Arrays.asList(1001L, 1002L, 1003L))
        .list();

// 2. 使用 Stream 和 BeanUtil 进行批量转换
List<UserDTO> userDTOs = users.stream()
        .map(user -> BeanUtil.copyProperties(user, UserDTO.class))  // 属性拷贝
        .collect(Collectors.toList());

// 3. 转换结果
// User{id=1001, name="Alice", email="alice@example.com", icon="avatar1.jpg"} 
// -> UserDTO{id=1001, name="Alice", icon="avatar1.jpg"}
```


### 11. 拷贝规则

#### (1) 属性匹配规则

```java
// 只拷贝目标类中存在的属性
// User: id, name, email, icon
// UserDTO: id, name, icon
// 拷贝结果: id, name, icon (email 被忽略)
```


#### (2) 类型兼容性

```java
// 只拷贝类型兼容的属性
// 源对象: String name = "Alice"
// 目标对象: String name
// 结果: 成功拷贝

// 源对象: String age = "25"
// 目标对象: Integer age
// 结果: Hutool 会尝试类型转换
```


### 12. 注意事项

#### (1) 性能考虑

```java
// BeanUtil.copyProperties 使用反射实现，性能不如手动拷贝
// 但对于开发效率和代码可维护性有很大提升

// 大量数据时可以考虑缓存 BeanCopier（如 Apache Commons BeanUtils）
```


#### (2) 深拷贝 vs 浅拷贝

```java
// BeanUtil.copyProperties 默认是浅拷贝
User user = new User();
user.setId(1L);
// ...

UserDTO userDTO = BeanUtil.copyProperties(user, UserDTO.class);
// userDTO.getId() == user.getId()  // true (基本类型直接拷贝值)
```


在当前项目中，[BeanUtil.copyProperties()](file://cn\hutool\core\bean\BeanUtil.java#L55-L55) 方法主要用于将从数据库查询到的 [User](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\entity\User.java#L20-L65) 实体对象转换为 [UserDTO](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\dto\UserDTO.java#L4-L9) 对象，这是一种简洁高效的对象转换方式，避免了手动编写大量的 getter/setter 代码。