### 1. 基本定义

[count()](file://com\baomidou\mybatisplus\extension\conditions\query\QueryChainWrapper.java#L38-L38) 方法是 MyBatis-Plus 框架中用于统计查询结果数量的方法。

### 2. 所属框架和类

- **框架**：MyBatis-Plus（MyBatis 的增强工具）
- **接口**：`com.baomidou.mybatisplus.extension.conditions.query.QueryChainWrapper<T>`
- **包路径**：`com.baomidou.mybatisplus.extension.conditions.query`

### 3. 方法签名

```java
Integer count()
```


### 4. 功能作用

执行查询并返回符合条件的记录总数，生成类似 `SELECT COUNT(*) FROM table WHERE ...` 的 SQL 语句。

### 5. 返回值

- 返回 `Integer` 类型，表示符合条件的记录数量

### 6. 在代码中的使用

```java
int count = query().eq("user_id", userId).eq("voucher_id", voucherId).count();
```


在这段代码中的作用：
- 统计指定用户和指定代金券的订单记录数量
- 用于判断用户是否已经购买过该代金券（"一人一单"限制）
- 如果 count > 0，表示用户已购买，不允许重复下单

### 7. 底层实现原理

```java
// MyBatis-Plus 的 count 方法实现
@Override
public Integer count() {
    return executeSQL(sqlMethod, () -> {
        // 生成 COUNT 查询 SQL
        String sql = this.sqlBuilder.buildCountSql();
        // 执行查询并返回结果
        return this.baseMapper.selectCount(this.wrapper);
    });
}
```


生成的 SQL 语句：
```sql
SELECT COUNT(*) FROM tb_voucher_order WHERE user_id = ? AND voucher_id = ?
```


### 8. 示例代码

```java
@Autowired
private IUserService userService;

// 统计所有用户数量
int totalUsers = userService.query().count();

// 统计满足条件的用户数量
int activeUsers = userService.query()
    .eq("status", 1)
    .gt("age", 18)
    .count();

// 判断是否存在满足条件的记录
boolean exists = userService.query()
    .eq("username", "admin")
    .count() > 0;

// 实现分页前的总数统计
int totalCount = userService.query()
    .eq("department", "IT")
    .count();
```


### 9. 相关方法

| 方法                                                         | 功能             |
| ------------------------------------------------------------ | ---------------- |
| [count()](file://com\baomidou\mybatisplus\extension\conditions\query\QueryChainWrapper.java#L38-L38) | 统计记录数量     |
| [list()](file://com\baomidou\mybatisplus\extension\service\IService.java#L47-L47) | 查询记录列表     |
| `one()`                                                      | 查询单条记录     |
| [page(Page<T> page)](file://com\baomidou\mybatisplus\extension\service\IService.java#L48-L48) | 分页查询         |
| `exists()`                                                   | 判断记录是否存在 |

### 10. 性能优化

```java
// 推荐：只查询数量时使用 count()
int count = userService.query().eq("status", 1).count();

// 不推荐：查询所有记录再统计（性能差）
int count = userService.query().eq("status", 1).list().size();
```


### 11. 注意事项

1. **性能优势**: COUNT 查询比查询所有记录再统计数量更高效
2. **索引优化**: 在经常用于 COUNT 查询的字段上建立索引
3. **NULL 值处理**: COUNT(*) 统计所有行，COUNT(column) 不统计 NULL 值
4. **大数据量**: 对于大表，COUNT 查询也可能较慢，需要合理设计索引

### 12. 实际意义

在您的秒杀系统中，[count()](file://com\baomidou\mybatisplus\extension\conditions\query\QueryChainWrapper.java#L38-L38) 方法确保了：

- 高效地检查用户是否已购买指定代金券
- 实现"一人一单"的业务规则验证
- 避免全表扫描，提高查询性能
- 通过 MyBatis-Plus 自动生成优化的 COUNT SQL

这是数据库查询优化的重要实践，体现了在实际业务场景中对性能和功能的平衡考虑。