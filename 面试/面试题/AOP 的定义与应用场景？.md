好的，我们按照**面试回答模板（概念 ➝ 原理 ➝ 案例 ➝ 使用场景 ➝ 追问）**来整理这道题：

------

# 🎯 面试题：什么是 AOP？它的典型应用场景有哪些？

## 1. 概念解释

- **AOP（Aspect Oriented Programming，面向切面编程）** 是对 OOP（面向对象编程）的补充。
- 它关注的是 **横切关注点**（cross-cutting concerns），例如日志记录、安全校验、事务管理、性能监控等，这些功能往往分散在系统的多个模块里。
- AOP 的核心思想：**把这些通用功能抽取成切面（Aspect），在运行时动态织入目标对象的方法调用中，从而实现功能的解耦和复用。**

------

## 2. 底层原理

- **Spring AOP** 基于 **代理模式** 实现：
  - 如果目标类 **实现了接口** → 默认使用 **JDK 动态代理**；
  - 如果目标类 **没有接口** → 使用 **CGLIB 动态代理**（基于字节码继承）。
- 通过 **代理对象** 在方法执行前后或异常时织入额外逻辑（Advice）。

------

## 3. 代码案例

```java
@Aspect
@Component
public class LogAspect {
    // 定义切点：拦截所有 service 包下的方法
    @Pointcut("execution(* com.example.service..*(..))")
    public void servicePointcut(){}

    // 前置通知
    @Before("servicePointcut()")
    public void beforeMethod(JoinPoint joinPoint) {
        System.out.println("调用方法：" + joinPoint.getSignature());
    }

    // 后置通知
    @AfterReturning("servicePointcut()")
    public void afterMethod() {
        System.out.println("方法执行成功");
    }
}
```

👉 调用 Service 层方法时，日志逻辑会自动织入，无需在每个方法里写 `System.out.println`。

------

## 4. 典型应用场景

1. **日志记录**：记录方法调用时间、参数、执行时长。
2. **事务管理**：Spring 的 `@Transactional` 底层就是 AOP。
3. **安全校验**：在接口调用前统一验证权限/角色。
4. **性能监控**：统计方法执行耗时，监控慢查询。
5. **异常处理**：统一异常捕获和处理。
6. **接口限流/幂等性校验**：如在 Controller 层统一拦截。

------

## 5. 面试标准回答（简洁版）

> AOP 是面向切面编程，用于处理日志、事务、安全等横切关注点。它通过代理模式在方法执行的前后动态织入额外逻辑，从而实现业务逻辑和系统服务的解耦。典型场景包括日志记录、事务管理、安全校验和性能监控等。在 Spring 中，AOP 默认使用 JDK 动态代理，没有接口时使用 CGLIB 代理。

------

## 6. 扩展追问

- JDK 动态代理和 CGLIB 的区别？SpringBoot 如何选择？
- @Transactional 底层是如何通过 AOP 实现的？为什么有些场景会失效？
- Spring AOP 和 AspectJ 有什么区别？
- 高并发场景下，AOP 带来的性能开销怎么优化？

------

要不要我帮你再整理一份 **“事务是如何通过 AOP 实现的？为什么有些场景事务会失效？”** 的完整面试回答？这个在面试中出现频率特别高。