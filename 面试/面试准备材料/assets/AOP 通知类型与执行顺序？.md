好，这题也很经典，我给你整理一份 **完整面试回答模板**：

------

# 🎯 面试题：AOP 中有哪些通知类型（Advice）？执行顺序是怎样的？

## 1. 概念解释

- 在 **AOP（面向切面编程）** 中，**通知（Advice）** 就是切面要织入到目标方法的增强逻辑。
- Spring AOP 提供了 5 种通知类型，对应方法执行的不同阶段。

------

## 2. 通知类型（Advice）

| 类型                           | 注解              | 作用点                              | 使用场景                                           |
| ------------------------------ | ----------------- | ----------------------------------- | -------------------------------------------------- |
| **前置通知（Before）**         | `@Before`         | 方法执行 **之前**                   | 日志记录、权限校验                                 |
| **后置通知（AfterReturning）** | `@AfterReturning` | 方法 **正常返回之后**               | 记录返回值、性能统计                               |
| **异常通知（AfterThrowing）**  | `@AfterThrowing`  | 方法 **抛出异常之后**               | 异常日志、事务回滚                                 |
| **最终通知（After）**          | `@After`          | 方法执行 **结束后（无论是否异常）** | 释放资源、清理操作                                 |
| **环绕通知（Around）**         | `@Around`         | 方法执行 **前后全流程**             | 最强大的通知，可控制方法是否执行、修改入参和返回值 |

------

## 3. 执行顺序

假设目标方法正常执行，顺序如下：

```
@Around（进入前）
   ↓
@Before
   ↓
【目标方法执行】
   ↓
@AfterReturning
   ↓
@After
@Around（退出后）
```

如果目标方法抛出异常：

```
@Around（进入前）
   ↓
@Before
   ↓
【目标方法异常抛出】
   ↓
@AfterThrowing
   ↓
@After
@Around（退出后）
```

👉 **注意**：

- `@Around` 包裹了整个方法执行，可以决定是否继续执行目标方法。
- `@After` 类似于 `finally`，一定会执行。

------

## 4. 代码示例

```java
@Aspect
@Component
public class LogAspect {

    @Before("execution(* com.example.service..*(..))")
    public void before() {
        System.out.println("前置通知：方法执行前");
    }

    @AfterReturning("execution(* com.example.service..*(..))")
    public void afterReturning() {
        System.out.println("后置通知：方法执行成功后");
    }

    @AfterThrowing("execution(* com.example.service..*(..))")
    public void afterThrowing() {
        System.out.println("异常通知：方法抛出异常后");
    }

    @After("execution(* com.example.service..*(..))")
    public void after() {
        System.out.println("最终通知：方法执行完毕后");
    }

    @Around("execution(* com.example.service..*(..))")
    public Object around(ProceedingJoinPoint pjp) throws Throwable {
        System.out.println("环绕通知：方法执行前");
        Object result = pjp.proceed(); // 执行目标方法
        System.out.println("环绕通知：方法执行后");
        return result;
    }
}
```

------

## 5. 面试标准回答（简洁版）

> AOP 通知分为 5 种：前置通知、后置通知、异常通知、最终通知和环绕通知。
>  正常执行时的顺序是：`@Around → @Before → 方法执行 → @AfterReturning → @After → @Around（后半段）`。
>  出现异常时会进入 `@AfterThrowing`，然后再执行 `@After`。环绕通知最强大，可以控制整个调用链。

------

## 6. 扩展追问

- 如果同时定义了多个切面（多个类），不同切面的执行顺序如何控制？
- `@Order` 注解在 AOP 中的作用是什么？
- 为什么 `@Around` 是功能最强的 Advice？能否实现其他四种通知的功能？
- 如何在 `@Around` 中修改方法的入参和返回值？

------

要不要我帮你顺带整理一份 **“多个切面共存时的执行顺序（@Order 注解原理）”**？这个点经常是这道题的延伸追问。