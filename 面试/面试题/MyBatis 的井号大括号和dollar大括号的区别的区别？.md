好的 👍 这道题在面试里 **高频必考**，我帮你整理成标准答题模板：

------

# 🎯 面试题

**`#{}` 和 `${}` 的区别？分别适合什么场景？**

------

## 一、概念对比

1. **`#{}` 占位符（预编译参数占位）**
   - 底层会被 **PreparedStatement 的 `?` 占位符**替代。
   - MyBatis 会自动进行 **参数预编译 + 类型转换 + SQL 注入防护**。
   - **安全性高**，推荐日常查询和更新都使用。
2. **`${}` 占位符（字符串拼接）**
   - 底层会进行 **字符串直接拼接**，不会做预编译。
   - 可能导致 **SQL 注入风险**。
   - 常用于 **动态生成对象名、列名、排序字段** 等场景。

------

## 二、原理解析

- **`#{}` 工作原理**

  ```sql
  select * from user where id = #{id};
  ```

  假设 id=1，MyBatis 会转换成：

  ```sql
  select * from user where id = ?;
  ```

  并通过 `PreparedStatement.setInt(1, 1)` 设置参数。

- **`${}` 工作原理**

  ```sql
  select * from ${table} where name = '${name}';
  ```

  假设 `table=user`，`name=Tom`，最终拼接成：

  ```sql
  select * from user where name = 'Tom';
  ```

------

## 三、使用案例

```xml
<!-- 使用 #{}，防止 SQL 注入 -->
<select id="selectUser" resultType="User">
    select * from user where id = #{id}
</select>

<!-- 使用 ${}，动态表名或排序 -->
<select id="selectOrder" resultType="Order">
    select * from ${tableName} order by ${columnName} desc
</select>
```

------

## 四、区别总结（面试表格）

| 特性     | `#{}`                      | `${}`                          |
| -------- | -------------------------- | ------------------------------ |
| 处理方式 | 占位符，预编译             | 字符串拼接                     |
| 底层实现 | `?` + PreparedStatement    | 直接拼接 SQL                   |
| 安全性   | 高，防止 SQL 注入          | 低，存在注入风险               |
| 使用场景 | 传递普通参数（id、条件值） | 表名、列名、排序字段、动态 SQL |
| 性能     | 支持预编译，效率高         | 无预编译，每次都拼接 SQL       |

------

## 五、使用场景

- **`#{}`**
  - 常规参数绑定（id、用户名、密码等）。
  - Insert/Update/Delete 中的条件和字段值。
- **`${}`**
  - 动态 SQL，如动态表名、动态排序字段。
  - 批量插入时拼接字段名。

------

## 六、扩展追问

1. 如果我在 `where` 条件里用了 `${}`，会有什么风险？
    👉 可能导致 **SQL 注入攻击**。
2. MyBatis 是如何防止 `#{}` 注入的？
    👉 使用 JDBC `PreparedStatement` 的预编译机制。
3. 在高并发场景下，`#{}` 和 `${}` 对性能的影响？
    👉 `#{}` 预编译可复用 SQL，提高性能；`${}` 每次都要重新拼接 SQL，缓存命中率低。

------

要不要我再帮你整理一份 **“SQL 注入攻击案例”**，把 `${}` 的风险用例子展示出来？这样面试时讲会更有亮点。