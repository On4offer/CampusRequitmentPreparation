### 1. 基本定义

[eq()](file://com\baomidou\mybatisplus\extension\conditions\AbstractChainWrapper.java#L58-L58) 方法是 MyBatis-Plus 框架中用于构建等于条件的链式查询方法。

### 2. 所属框架和类

- **框架**：MyBatis-Plus（MyBatis 的增强工具）
- **接口**：`com.baomidou.mybatisplus.core.conditions.Wrapper<T>`
- **实现类**：`com.baomidou.mybatisplus.extension.conditions.AbstractChainWrapper<T, R>`
- **包路径**：`com.baomidou.mybatisplus.extension.conditions`

### 3. 方法签名

```java
R eq(String column, Object val)
```


### 4. 功能作用

构建 SQL 查询中的等于（=）条件，用于指定字段与值相等的查询条件。

### 5. 参数说明

- **column**: 数据库字段名
- **val**: 要比较的值

### 6. 在代码中的使用

```java
int count = query().eq("user_id", userId).eq("voucher_id", voucherId).count();
```


在这段代码中的作用：
- 构建查询条件：`user_id = ? AND voucher_id = ?`
- 用于查询指定用户和指定代金券的订单记录数量
- 实现"一人一单"的业务逻辑判断

### 7. 底层实现原理

```java
// MyBatis-Plus 的 eq 方法实现
@Override
public R eq(String column, Object val) {
    return eq(true, column, val);
}

public R eq(boolean condition, String column, Object val) {
    if (condition) {
        // 添加等于条件到查询条件列表中
        this.addCondition(column, SqlKeyword.EQ, val);
    }
    return typedThis;
}
```


生成的 SQL 条件：
```sql
WHERE user_id = ? AND voucher_id = ?
```


### 8. 示例代码

```java
@Autowired
private IUserService userService;

// 基本等于查询
List<User> users = userService.query()
    .eq("age", 18)
    .list();

// 多条件等于查询
List<User> users2 = userService.query()
    .eq("age", 18)
    .eq("status", 1)
    .eq("city", "北京")
    .list();

// 带条件的等于查询
String name = getName(); // 可能为 null
List<User> users3 = userService.query()
    .eq(name != null && !name.isEmpty(), "name", name)
    .eq("status", 1)
    .list();
```


### 9. 相关方法

| 方法                                                         | 功能     |
| ------------------------------------------------------------ | -------- |
| [eq(String column, Object val)](file://com\baomidou\mybatisplus\extension\conditions\AbstractChainWrapper.java#L58-L58) | 等于     |
| `ne(String column, Object val)`                              | 不等于   |
| `gt(String column, Object val)`                              | 大于     |
| `ge(String column, Object val)`                              | 大于等于 |
| `lt(String column, Object val)`                              | 小于     |
| `le(String column, Object val)`                              | 小于等于 |
| `like(String column, Object val)`                            | 模糊查询 |
| `in(String column, Collection<?> values)`                    | IN 查询  |

### 10. 重载版本

```java
// 基础版本
R eq(String column, Object val)

// 带条件判断版本
R eq(boolean condition, String column, Object val)

// 示例
query().eq(status != null, "status", status) // 只有当 status 不为 null 时才添加条件
```


### 11. 注意事项

1. **SQL 注入防护**: MyBatis-Plus 自动处理参数绑定，防止 SQL 注入
2. **空值处理**: 传入 null 值时会正确处理
3. **类型匹配**: 确保值的类型与数据库字段类型匹配
4. **链式调用**: 支持连续调用多个条件方法

### 12. 实际意义

在您的秒杀系统中，[eq()](file://com\baomidou\mybatisplus\extension\conditions\AbstractChainWrapper.java#L58-L58) 方法确保了：

- 实现了精确的数据库查询条件构建
- 支持用户购买记录的准确查询
- 通过链式调用提高了代码可读性
- 避免了手动拼接 SQL 字符串的安全风险

这是 MyBatis-Plus 查询构造器的核心方法之一，体现了现代 ORM 框架在条件构建方面的便利性和安全性。