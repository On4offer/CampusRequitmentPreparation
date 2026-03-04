### 1. 基本定义

[gt()](file://com\baomidou\mybatisplus\extension\conditions\AbstractChainWrapper.java#L66-L66) 方法是 MyBatis-Plus 框架中用于构建大于条件的链式查询/更新方法。

### 2. 所属框架和类

- **框架**：MyBatis-Plus（MyBatis 的增强工具）
- **接口**：`com.baomidou.mybatisplus.core.conditions.Wrapper<T>`
- **实现类**：`com.baomidou.mybatisplus.extension.conditions.AbstractChainWrapper<T, R>`
- **包路径**：`com.baomidou.mybatisplus.extension.conditions`

### 3. 方法签名

```java
R gt(String column, Object val)
```


### 4. 功能作用

构建 SQL 查询或更新中的大于（>）条件，用于指定字段值大于给定值的条件筛选。

### 5. 参数说明

- **column**: 数据库字段名
- **val**: 要比较的值

### 6. 在代码中的使用

```java
boolean success = seckillVoucherService.update()
        .setSql("stock = stock - 1") // set stock = stock - 1
        .eq("voucher_id", voucherId).gt("stock", 0) // where id = ? and stock > 0
        .update();
```


在这段代码中的作用：
- 构建更新条件：`stock > 0`
- 确保只有在库存大于0时才执行扣减操作
- 防止库存出现负数，避免超卖问题

### 7. 底层实现原理

```java
// MyBatis-Plus 的 gt 方法实现
@Override
public R gt(String column, Object val) {
    return gt(true, column, val);
}

public R gt(boolean condition, String column, Object val) {
    if (condition) {
        // 添加大于条件到条件列表中
        this.addCondition(column, SqlKeyword.GT, val);
    }
    return typedThis;
}
```


生成的 SQL 条件：
```sql
WHERE voucher_id = ? AND stock > 0
```


### 8. 示例代码

```java
@Autowired
private IUserService userService;

// 查询年龄大于18的用户
List<User> adults = userService.query()
    .gt("age", 18)
    .list();

// 更新年龄大于60的用户的折扣
boolean success = userService.update()
    .set("discount", 0.8)
    .gt("age", 60)
    .update();

// 多条件组合
List<User> users = userService.query()
    .gt("age", 18)
    .lt("age", 60)
    .gt("salary", 5000)
    .list();

// 带条件判断的大于查询
Integer minAge = getMinAge(); // 可能为 null
List<User> users2 = userService.query()
    .gt(minAge != null, "age", minAge)
    .list();
```


### 9. 相关方法

| 方法                                                         | 功能     |
| ------------------------------------------------------------ | -------- |
| [gt(String column, Object val)](file://com\baomidou\mybatisplus\extension\conditions\AbstractChainWrapper.java#L66-L66) | 大于     |
| `ge(String column, Object val)`                              | 大于等于 |
| `lt(String column, Object val)`                              | 小于     |
| `le(String column, Object val)`                              | 小于等于 |
| [eq(String column, Object val)](file://com\baomidou\mybatisplus\extension\conditions\AbstractChainWrapper.java#L58-L58) | 等于     |
| `ne(String column, Object val)`                              | 不等于   |

### 10. 重载版本

```java
// 基础版本
R gt(String column, Object val)

// 带条件判断版本
R gt(boolean condition, String column, Object val)

// 示例
query().gt(minScore != null, "score", minScore) // 只有当 minScore 不为 null 时才添加条件
```


### 11. 注意事项

1. **SQL 注入防护**: MyBatis-Plus 自动处理参数绑定，防止 SQL 注入
2. **类型匹配**: 确保比较值的类型与数据库字段类型兼容
3. **NULL 值处理**: 注意 NULL 值在比较中的特殊行为
4. **索引优化**: 在经常用于比较的字段上建立索引以提高查询性能

### 12. 实际意义

在您的秒杀系统中，[gt()](file://com\baomidou\mybatisplus\extension\conditions\AbstractChainWrapper.java#L66-L66) 方法确保了：

- 实现了库存安全检查，防止超卖现象
- 通过数据库层面的条件控制保证数据一致性
- 提高了库存扣减操作的原子性和安全性
- 避免了应用层先查询再判断可能带来的并发问题

这是数据库操作安全控制的重要实践，体现了在高并发场景下对数据完整性的保护措施。