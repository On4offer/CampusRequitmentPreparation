好的 ✅ 这道题考察 **MyBatis 插件（Interceptor）机制**，属于面试进阶点。我帮你按照八股文思路整理：

------

# 🎯 面试题

**MyBatis 插件（Interceptor）的工作原理？常见应用场景有哪些？**

------

## 一、概念

- **MyBatis 插件** 是对 MyBatis 核心对象的拦截扩展机制。
- 通过实现 `Interceptor` 接口，可以在 SQL 执行的关键节点插入自定义逻辑（类似 Spring AOP）。
- 核心思想：**动态代理 + 拦截器链**。

------

## 二、原理

1. **拦截点（四大对象）**
    插件可以拦截 MyBatis 的四大核心对象的方法：

   - **Executor**：执行器，负责增删改查。
   - **StatementHandler**：封装 JDBC Statement，处理 SQL 预编译、参数设置。
   - **ParameterHandler**：处理 SQL 参数。
   - **ResultSetHandler**：处理结果集映射。

2. **实现步骤**

   - 实现 `Interceptor` 接口，重写 `intercept()` 方法。
   - 通过 `@Intercepts` 和 `@Signature` 注解声明拦截目标方法。
   - MyBatis 在运行时使用 **JDK 动态代理** 包装目标对象，形成拦截器链。
   - 执行方法时，依次触发拦截器逻辑 → 原始方法执行。

3. **运行机制图解**

   ```
   调用 Mapper 方法
         ↓
   Executor / StatementHandler ...
         ↓ (被代理)
   Plugin.wrap(目标对象)
         ↓
   拦截器链 InterceptorChain
         ↓
   intercept() → proceed() → 原始逻辑
   ```

------

## 三、案例

### 自定义 SQL 打印插件

```java
@Intercepts({
    @Signature(type = StatementHandler.class, method = "prepare", args = {Connection.class, Integer.class})
})
public class SqlPrintInterceptor implements Interceptor {
    @Override
    public Object intercept(Invocation invocation) throws Throwable {
        StatementHandler handler = (StatementHandler) invocation.getTarget();
        String sql = handler.getBoundSql().getSql();
        System.out.println("执行SQL: " + sql);
        return invocation.proceed(); // 继续执行原方法
    }
}
```

在 `mybatis-config.xml` 注册插件：

```xml
<plugins>
    <plugin interceptor="com.example.SqlPrintInterceptor"/>
</plugins>
```

------

## 四、常见应用场景

1. **性能监控**
   - 打印 SQL 执行时间，分析慢 SQL。
2. **多租户实现**
   - 在 SQL 中自动拼接 `tenant_id` 条件，实现租户隔离。
3. **数据权限控制**
   - 在查询 SQL 上拼接用户权限条件，比如“只能查自己部门的数据”。
4. **自动分页**
   - 拦截 SQL，自动拼接 `limit` 分页语句（MyBatis-Plus 的分页插件就是这样实现的）。
5. **SQL 审计/记录**
   - 拦截所有 SQL 并记录日志，便于审计。
6. **分表分库路由**
   - 在执行 SQL 前动态修改表名或数据源，实现读写分离、分库分表。

------

## 五、面试模板（标准作答）

> MyBatis 插件的实现原理是 **基于 JDK 动态代理的拦截器链**，它允许开发者拦截 MyBatis 四大核心对象的方法（Executor、StatementHandler、ParameterHandler、ResultSetHandler）。
>  插件通过实现 `Interceptor` 接口，在 SQL 执行的关键节点（参数设置、SQL 执行、结果映射）插入自定义逻辑。
>  常见应用包括 **性能监控、多租户隔离、数据权限控制、自动分页、SQL 审计** 等。
>  实际项目中（比如苍穹外卖、黑马点评），分页插件和多租户插件就是典型应用。

------

## 六、扩展追问

1. MyBatis 插件和 Spring AOP 有什么区别？
    👉 插件是 **MyBatis 内部的代理机制**，只能拦截四大核心对象；Spring AOP 更通用，能拦截任意 Bean。
2. 插件会不会影响性能？
    👉 会有一定代理开销，但一般可接受；插件逻辑过重时会拖慢执行。
3. MyBatis-Plus 的分页插件是怎么实现的？
    👉 通过拦截 `StatementHandler.prepare()` 方法，在 SQL 语句执行前自动拼接分页 `limit`。
4. 能不能在插件里直接修改 SQL？
    👉 可以，常见于 **多租户、分表分库、动态表名** 场景。

------

要不要我帮你再扩展一题 **“MyBatis 分页插件的实现原理？”**，这个是插件机制里的经典追问点。