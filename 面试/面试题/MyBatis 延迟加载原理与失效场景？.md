好的 ✅ 这道题考察 **MyBatis 延迟加载（Lazy Loading）** 机制，也是高频考点。我帮你整理成完整八股文答题模板：

------

# 🎯 面试题

**MyBatis 的延迟加载（懒加载）原理是什么？在什么场景下会失效？**

------

## 一、概念

- **延迟加载（Lazy Loading）**：也叫懒加载，指的是在真正用到数据时，才去执行对应的 SQL 语句加载数据。
- **应用场景**：多表关联时（如一对一、一对多查询），先查询主表数据，等访问关联对象时再去查询，避免一次性加载所有数据，提高性能。

------

## 二、原理

1. **代理对象实现**

   - MyBatis 会为关联对象（如 `List<Order>` 或 `Address`）生成一个 **JDK 动态代理对象**。
   - 当调用 `getter` 方法时，代理拦截方法调用，执行对应的 SQL，填充真实数据。

2. **延迟加载配置**

   ```xml
   <!-- 在 mybatis-config.xml 中配置 -->
   <settings>
       <!-- 开启全局延迟加载 -->
       <setting name="lazyLoadingEnabled" value="true"/>
       <!-- 积极加载：false 表示按需加载 -->
       <setting name="aggressiveLazyLoading" value="false"/>
   </settings>
   ```

3. **触发机制**

   - 调用关联对象的 `getter` 时触发 SQL 查询。
   - 使用 CGLIB/JDK 动态代理对结果对象增强，实现“按需查询”。

------

## 三、案例

```xml
<!-- 用户表 -->
<select id="selectUser" resultMap="userResultMap">
    select * from user where id = #{id}
</select>

<resultMap id="userResultMap" type="User">
    <id column="id" property="id"/>
    <result column="username" property="username"/>
    <!-- 一对一，延迟加载 -->
    <association property="address" column="address_id" 
                 javaType="Address" select="selectAddress" fetchType="lazy"/>
</resultMap>

<select id="selectAddress" resultType="Address">
    select * from address where id = #{id}
</select>
```

Java 使用：

```java
User user = userMapper.selectUser(1);
// 此时不会查 address
System.out.println(user.getUsername());
// 调用 getAddress() 时才触发 SQL 查询 address
System.out.println(user.getAddress().getCity());
```

------

## 四、使用场景

- **合适**：
  - 用户与订单、一对多关系 → 先查用户，再按需加载订单。
  - 详情页需要展示主表数据，但大字段（如评论列表、历史记录）不一定用到。
- **不合适**：
  - 高频访问的关联字段，延迟加载反而导致 **N+1 查询问题**，性能更差。
  - 需要一次性返回完整数据的接口。

------

## 五、面试模板（标准作答）

> MyBatis 的延迟加载是通过 **代理对象拦截 getter 方法** 来实现的，只有在真正访问关联对象时才执行 SQL，从而避免一次性加载大量数据。
>
> 其底层是基于 **JDK 动态代理** 或 **CGLIB** 来生成代理对象，配合配置项 `lazyLoadingEnabled=true` 和 `fetchType=lazy` 实现。
>
> 延迟加载适合在 **多表关联、数据量较大但不一定用到所有关联数据** 的场景。但在高频访问场景，可能导致 **N+1 查询问题** 或在全局 `aggressiveLazyLoading=true` 时失效。

------

## 六、失效场景

1. **全局配置 aggressiveLazyLoading = true**
   - 所有关联对象会被一次性加载，相当于失去延迟加载的意义。
2. **关闭延迟加载（lazyLoadingEnabled=false）**
   - 全局禁用，所有关联对象立即加载。
3. **序列化对象时**
   - 如果对象被序列化（如存入 Redis），代理失效，可能提前触发加载。
4. **toString()/hashCode()/equals() 方法调用**
   - 如果 `toString()` 打印了懒加载字段，会触发 SQL 查询。
5. **多次关联查询导致的 N+1 问题**
   - 在循环中调用懒加载字段时，每次都会触发一条 SQL，性能比立即加载还差。

------

## 七、扩展追问

1. 延迟加载和 **N+1 查询问题**的关系？如何优化？
    👉 延迟加载可能导致 N+1 问题，可以通过 **join 查询** 或 **批量查询**优化。
2. MyBatis 的延迟加载和 Hibernate 的懒加载有何区别？
    👉 Hibernate 是全 ORM 方案，MyBatis 更灵活，懒加载仅限于配置的关联字段。
3. 在高并发下，延迟加载会带来什么问题？
    👉 可能导致 **频繁的小 SQL 请求**，影响数据库性能，此时更适合用缓存或一次性加载。

------

要不要我再帮你写一份 **“N+1 查询问题及优化方案”** 的面试题？这是延迟加载后面面试官常追问的坑点。