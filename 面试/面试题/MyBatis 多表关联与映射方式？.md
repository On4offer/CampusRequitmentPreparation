好的 ✅ 这道题考察 **MyBatis 多表关联映射**，面试常见点是 **一对一、一对多、多对多的映射方式**。我来给你写成完整的八股文答题模板：

------

# 🎯 面试题

**MyBatis 是如何处理映射文件中的关联查询（多表关联）的？**

------

## 一、概念

- MyBatis 是半自动 ORM 框架，**不会自动进行多表关联**，而是通过 **`<resultMap>` + `<association>` / `<collection>`** 标签完成对象关系映射。
- **目标**：解决多表查询时结果集与 Java 对象的映射问题。

------

## 二、原理

1. **`<association>`** —— 用于 **一对一** 映射
   - 表示对象属性的映射，如 `User` 对应一个 `Address`。
   - 可选择 **嵌套结果映射**（join 一次查询结果）或 **嵌套查询**（延迟加载）。
2. **`<collection>`** —— 用于 **一对多** 映射
   - 表示集合属性的映射，如 `User` 对应多个 `Order`。
   - 同样支持嵌套结果或嵌套查询。
3. **嵌套结果（Nested Result）**
   - 使用 **join 查询** 一次性查出所有数据，然后通过 `resultMap` 映射。
   - 性能好，但可能有数据冗余。
4. **嵌套查询（Nested Query）**
   - 先查主表，再根据外键去查询子表（懒加载可用）。
   - 避免数据冗余，但可能出现 **N+1 查询问题**。

------

## 三、案例

### 1. 一对一（用户-地址）

```xml
<resultMap id="userResultMap" type="User">
    <id property="id" column="id"/>
    <result property="username" column="username"/>
    <!-- 一对一关联 -->
    <association property="address" javaType="Address" column="address_id"
                 select="selectAddress" fetchType="lazy"/>
</resultMap>

<select id="selectUser" resultMap="userResultMap">
    select * from user where id = #{id}
</select>

<select id="selectAddress" resultType="Address">
    select * from address where id = #{id}
</select>
```

### 2. 一对多（用户-订单）

```xml
<resultMap id="userOrderResultMap" type="User">
    <id property="id" column="id"/>
    <result property="username" column="username"/>
    <!-- 一对多 -->
    <collection property="orders" ofType="Order"
                column="id" select="selectOrdersByUserId"/>
</resultMap>

<select id="selectOrdersByUserId" resultType="Order">
    select * from orders where user_id = #{id}
</select>
```

------

## 四、使用场景

- **苍穹外卖项目**
  - 用户与订单：一对多
  - 订单与明细：一对多
  - 菜品与分类：多对一
- **黑马点评项目**
  - 商户与点评：一对多
  - 用户与关注列表：多对多（通过中间表实现）

------

## 五、面试模板（标准作答）

> MyBatis 处理多表关联主要依赖 **`<resultMap>`** 映射机制。
>  一对一关系使用 `<association>`，一对多关系使用 `<collection>`。
>  它既可以采用 **嵌套结果（一次 join 查询返回所有数据）**，也可以采用 **嵌套查询（延迟加载，按需查询）**。
>
> 嵌套结果避免了 N+1 问题，但可能带来冗余数据；嵌套查询更灵活，但在高并发下容易导致大量 SQL。
>  在实际项目中，通常结合 **缓存（Redis）、分页、分库分表** 等方式优化。

------

## 六、扩展追问

1. 在高并发下，**为什么嵌套查询会导致性能问题**？
    👉 因为每次访问子对象都要额外执行 SQL，可能导致 N+1 查询问题。
2. 如何选择 **嵌套结果 vs 嵌套查询**？
    👉 数据量小且频繁查询 → 嵌套结果；数据量大且部分字段不常用 → 嵌套查询。
3. MyBatis 能否自动处理多对多关系？
    👉 不能，需要通过 **中间表** 配置 `<collection>` 来实现。
4. 如果想避免 N+1 查询问题，怎么做？
    👉 使用 **一次 join 查询** 或 **批量查询** + **缓存**。

------

要不要我再帮你整理一份 **“N+1 查询问题及优化方案”** 专题？这个是 MyBatis 多表关联后面面试官最喜欢追问的点。