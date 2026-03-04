好，这道题是 **Spring AOP 高频面试题**，我帮你整理成完整的 **面试回答模板**：

------

# 🎯 面试题：Spring 的事务是如何通过 AOP 实现的？为什么有些场景事务会失效？

## 1. 概念解释

- **Spring 事务管理**的本质：通过 **AOP 动态代理** 将事务增强逻辑织入到目标方法执行前后。
- 事务的开启、提交、回滚都由 **代理对象** 在调用目标方法时统一处理，业务代码无需显式编写 `connection.setAutoCommit(false)` 等事务控制语句。

------

## 2. 原理剖析

1. **核心注解**：`@Transactional`
   - 由 `TransactionInterceptor` 负责拦截目标方法。
   - 在方法执行前获取事务管理器，开启事务。
   - 在方法执行成功后提交事务，异常时回滚。
2. **底层实现**
   - Spring AOP 创建代理对象（JDK 动态代理 / CGLIB）。
   - 代理对象在调用目标方法时，先执行 `TransactionInterceptor`：
     - 开启事务（获取连接，绑定到当前线程 ThreadLocal）。
     - 调用目标方法。
     - 判断是否抛异常 → 提交或回滚事务。

👉 可以理解为：**业务方法外层套了一层事务切面**。

------

## 3. 代码示例（简化版）

```java
@Service
public class UserService {

    @Transactional
    public void createUser() {
        // 1. 插入用户
        userDao.insertUser();
        // 2. 插入账户
        accountDao.insertAccount();
        // 如果抛异常，Spring AOP 会捕获并回滚
    }
}
```

底层等价于代理逻辑：

```java
try {
    transactionManager.begin(); // 开启事务
    target.createUser();        // 调用目标方法
    transactionManager.commit();// 提交
} catch (Exception e) {
    transactionManager.rollback();// 回滚
    throw e;
}
```

------

## 4. 事务失效的常见场景

1. **方法修饰符不对**

   - `@Transactional` 只能作用在 **public 方法** 上。
   - 作用在 `private`、`protected`、`final`、`static` 方法上会失效。

2. **自调用（自身调用）问题**

   - 类内方法 A 调用了另一个带事务的方法 B，实际上绕过了代理对象，直接调用了 `this.b()`，导致事务逻辑没有生效。

3. **异常类型不匹配**

   - Spring 默认只在 **运行时异常（RuntimeException）** 或 `Error` 时才回滚。

   - 检查型异常（如 `IOException`）不会触发回滚，除非手动配置：

     ```java
     @Transactional(rollbackFor = Exception.class)
     ```

4. **事务传播行为不当**

   - 比如 A 方法有事务，内部调用的 B 方法设置了 `PROPAGATION_REQUIRES_NEW`，可能导致事务分裂或失效。

5. **数据库引擎不支持事务**

   - MySQL 使用 `MyISAM` 引擎（不支持事务），即使加了 `@Transactional` 也不会生效。

6. **事务未被 Spring 管理**

   - 如果目标类/方法不在 Spring 容器中，或者代理没有生效（比如 `@EnableTransactionManagement` 没配置）。

------

## 5. 面试标准回答（简洁版）

> Spring 事务是通过 AOP 实现的，`@Transactional` 注解会在方法调用时由代理拦截，统一在执行前开启事务，执行成功后提交，抛出异常时回滚。
>  常见失效原因包括：方法不是 public、自调用绕过代理、异常类型不匹配、事务传播设置不当、数据库引擎不支持事务等。

------

## 6. 扩展追问

- 为什么自调用会导致事务失效？如何解决？
- Spring 声明式事务和编程式事务的区别？
- @Transactional 的事务传播机制有几种？各自应用场景是什么？
- 高并发下，事务和分布式事务是如何处理的？

------

要不要我帮你也整理一份 **“自调用导致事务失效的场景及解决方案”** 的专门回答？这个点面试官很喜欢深挖。