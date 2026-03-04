# Spring 事务管理面试指南 & Demo 说明

本项目演示了 Spring 中如何使用 `@Transactional` 进行声明式事务管理。

## 1. 如何运行 Demo

1.  确保已安装 JDK 17+ 和 Maven。
2.  进入目录 `spring-transaction-basic-demo`。
3.  运行命令：`mvn spring-boot:run`。
4.  观察控制台输出，对比不同场景下的余额变化。

---

## 2. 面试必考：Spring 事务管理面试题总结

### Q1: Spring 支持哪几种事务管理方式？
-   **编程式事务管理**：通过 `TransactionTemplate` 或 `TransactionManager` 手动控制事务的开始、提交和回滚。优点是灵活性高，缺点是代码耦合度高。
-   **声明式事务管理**（推荐）：通过 AOP 实现，常用 `@Transactional` 注解。优点是开发简单、非侵入性，符合关注点分离原则。

### Q2: `@Transactional` 的实现原理？
Spring 事务基于 **Spring AOP (动态代理)** 实现：
1.  Spring 启动时，为标记了 `@Transactional` 的类或方法生成代理对象。
2.  当外部调用该方法时，实际上调用的是代理对象。
3.  **事务拦截器 (TransactionInterceptor)** 会在方法执行前开启事务。
4.  执行业务逻辑。
5.  如果方法正常结束，提交事务；如果抛出异常，根据配置判断是否回滚。

### Q3: Spring 事务在什么情况下会失效？（高频）
1.  **内部方法直接调用**：同一个类中，一个非事务方法调用另一个带有 `@Transactional` 的方法，事务会失效（因为绕过了代理对象）。
2.  **方法不是 public**：Spring 默认只对 `public` 方法开启事务。
3.  **异常被捕获处理了**：如果在业务逻辑中 `try-catch` 了异常且没有抛出，事务拦截器感知不到异常，会视为成功。
4.  **默认只回滚 RuntimeException**：Spring 默认只对 `RuntimeException` 及其子类和 `Error` 进行回滚。**受检异常 (Checked Exception)** 默认不回滚（如 `IOException`, `Exception`）。可以通过 `rollbackFor = Exception.class` 配置。
5.  **数据库不支持事务**：如 MySQL 的 MyISAM 引擎（不支持事务）。
6.  **Bean 没有被 Spring 管理**：即该类没有加 `@Service` 或 `@Component` 注解。

### Q4: 事务传播行为 (Propagation) 有哪些？
最常用的几种：
-   **REQUIRED** (默认)：如果当前有事务，加入；没有则新建。
-   **REQUIRES_NEW**：无论当前是否有事务，都新建事务。如果当前有事务，将其挂起。
-   **NESTED**：嵌套事务。如果当前有事务，则在当前事务中创建一个保存点 (Savepoint)；如果主事务失败，子事务随之回滚；如果子事务失败，可以只回滚到保存点而不影响主事务。

### Q5: 事务隔离级别 (Isolation) 有哪些？
-   **DEFAULT**：使用数据库默认隔离级别。
-   **READ_UNCOMMITTED**：读未提交（可能导致脏读）。
-   **READ_COMMITTED**：读已提交（可能导致不可重复读）。
-   **REPEATABLE_READ**：可重复读（可能导致幻读）。
-   **SERIALIZABLE**：串行化。

---

## 3. Demo 关键代码解析

### 3.1 成功提交
```java
@Transactional
public void transferSuccess(...) {
    // 方法正常结束 -> 自动提交
}
```

### 3.2 运行时异常自动回滚
```java
@Transactional
public void transferWithRuntimeException(...) {
    // 抛出 RuntimeException -> 自动回滚
    throw new RuntimeException("..."); 
}
```

### 3.3 受检异常处理
```java
// 默认不回滚
@Transactional
public void transferWithCheckedException(...) throws Exception {
    throw new Exception("..."); 
}

// 配置回滚
@Transactional(rollbackFor = Exception.class)
public void transferWithCheckedExceptionAndRollback(...) throws Exception {
    throw new Exception("..."); 
}
```

