# Spring 事务失效场景面试指南

本项目演示了开发中最常见的几种 Spring 事务失效场景。理解这些场景是掌握 Spring AOP 和事务管理的核心。

## 1. 运行方式
在 `spring-transaction-invalidation-demo` 目录下运行：
```bash
mvn spring-boot:run
```

## 2. 面试核心：事务失效场景总结

### 场景 1: 同类方法内部调用 (Self-Invocation)
*   **现象**: 一个类中的非事务方法调用同类中标记了 `@Transactional` 的方法。
*   **原因**: Spring 事务是基于 **AOP 动态代理** 实现的。只有当外部通过代理对象调用方法时，事务拦截器才会生效。同类内部方法直接调用（用 `this.xxx`）绕过了代理对象，因此事务失效。
*   **解决方法**: 
    1.  将事务方法移动到另一个 Bean 中。
    2.  在当前类中注入自己（Spring 支持构造器或 Setter 注入自己）。
    3.  使用 `AopContext.currentProxy()` 获取当前代理对象并调用。

### 场景 2: 异常被 try-catch 消化
*   **现象**: 在事务方法内部捕获了异常，但没有重新抛出。
*   **原因**: Spring 事务拦截器只有捕获到方法向上抛出的 **Throwable** 时，才会触发回滚。如果异常在方法内部被 `catch` 掉了，拦截器认为方法执行成功，从而提交事务。
*   **注意**: 如果必须要捕获异常，记得手动调用 `TransactionAspectSupport.currentTransactionStatus().setRollbackOnly()`。

### 场景 3: 方法权限不是 public
*   **现象**: `@Transactional` 标记在 `private`、`protected` 或 `default` 权限的方法上。
*   **原因**: Spring 默认配置下，`TransactionInterceptor` 只会拦截 `public` 方法。虽然可以配置，但这是官方不建议的做法。

### 场景 4: 异常类型错误 (默认规则)
*   **现象**: 抛出了受检异常 (Checked Exception)，但事务没回滚。
*   **原因**: Spring 默认只回滚 `RuntimeException` 及其子类和 `Error`。
*   **解决**: 配置 `@Transactional(rollbackFor = Exception.class)`。

### 场景 5: Bean 没有被 Spring 管理
*   **现象**: 忘记在类上添加 `@Service`、`@Component` 等注解。
*   **原因**: 没有 Bean，就没有代理，自然也就没有事务。

### 场景 6: 数据库引擎不支持
*   **现象**: MySQL 使用了 MyISAM 引擎。
*   **原因**: 事务必须底层数据库支持，MyISAM 不支持事务，改用 InnoDB。

