好的 ✅ 这道题是 **MyBatis-Plus 面试高频点**，我来帮你整理成完整八股文答题模板：

------

# 🎯 面试题

**MyBatis-Plus 的分页插件是如何实现的？和传统分页方式相比有何优势？**

------

## 一、概念

- MyBatis-Plus 提供了 **分页插件（PaginationInterceptor / MybatisPlusInterceptor）**，通过拦截 SQL 自动拼接分页语句，无需手写 `limit`。
- 本质：**基于 MyBatis 插件机制（Interceptor）+ SQL 改写**。

------

## 二、原理

1. **拦截点**

   - 插件拦截 `StatementHandler.prepare()` 方法（SQL 执行前）。

2. **SQL 改写**

   - 解析原始 SQL（如 `SELECT * FROM user`）。
   - 自动拼接分页条件：`SELECT * FROM user LIMIT ?, ?`。
   - 不同数据库方言（MySQL、Oracle、PostgreSQL）自动适配。

3. **总数统计**

   - 若需要总数，会自动生成 `COUNT` SQL：

     ```sql
     SELECT COUNT(*) FROM user
     ```

   - 先执行 count 查询，再执行分页 SQL。

4. **执行流程**

   - 调用 `selectPage(Page, Wrapper)` → 插件拦截 SQL → 改写 SQL → 执行并返回结果 → 封装到 `Page` 对象中（包含 `records`、`total`、`pages`、`current` 等）。

------

## 三、案例

### 配置分页插件（3.x 新版）

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
    return interceptor;
}
```

### 使用分页查询

```java
Page<User> page = new Page<>(1, 10); // 第1页，每页10条
Page<User> result = userMapper.selectPage(page, new QueryWrapper<User>().eq("age", 18));

System.out.println(result.getRecords()); // 当前页数据
System.out.println(result.getTotal());   // 总记录数
System.out.println(result.getPages());   // 总页数
```

生成 SQL：

```sql
SELECT COUNT(*) FROM user WHERE age = 18;
SELECT * FROM user WHERE age = 18 LIMIT 0, 10;
```

------

## 四、和传统分页方式的区别

| 对比项   | 传统分页（手写 SQL）                         | MyBatis-Plus 分页插件                    |
| -------- | -------------------------------------------- | ---------------------------------------- |
| SQL 编写 | 手写 `limit`，需维护两条 SQL（count + data） | 自动生成分页 SQL                         |
| 代码冗余 | 每个 Mapper 都要写分页方法                   | 通用 `selectPage` 方法                   |
| 适配性   | 不同数据库方言需手动处理                     | 内置方言处理（MySQL/Oracle/Postgres 等） |
| 返回结果 | 只返回数据列表                               | 返回数据 + 总数 + 页数 + 当前页等信息    |
| 易用性   | 繁琐，易出错                                 | 简单，开箱即用                           |

------

## 五、使用场景

- **苍穹外卖**：后台管理系统的订单列表、菜品列表分页。
- **黑马点评**：商户点评列表分页、用户关注/粉丝分页。
- 常见的 **后台管理系统**、**电商平台**、**内容管理系统**。

------

## 六、面试模板（标准作答）

> MyBatis-Plus 的分页插件是基于 **MyBatis 拦截器机制**实现的。
>  它会拦截 `StatementHandler.prepare()` 方法，在执行 SQL 前自动拼接 `limit` 语句，并根据配置自动生成 `count` SQL 来统计总数。
>
> 相比传统分页方式，它的优势是：**减少重复 SQL 编写、内置数据库方言支持、返回结构更丰富（总数/页数）**，大大简化了分页开发。
>  在实际项目（如订单列表、点评列表）中非常适用。

------

## 七、扩展追问

1. **分页插件为什么要执行两条 SQL？**
    👉 一条 `count` 统计总数，一条 `limit` 获取分页数据。
2. **在高并发下，count 查询会不会成为性能瓶颈？如何优化？**
    👉 是的，可以使用缓存、分库分表统计、索引优化等方式减少压力。
3. **MyBatis-Plus 分页插件和 PageHelper 的区别？**
    👉 PageHelper 是通用插件（基于 ThreadLocal），而 MP 分页插件与 MP CRUD 紧密结合，返回对象更友好。

------

要不要我再帮你扩展一题 **“MyBatis-Plus 分页插件在高并发场景下的优化方案？”**？这个是面试官很喜欢的追问点。