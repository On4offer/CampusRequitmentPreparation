好的，我们继续用结构化的 **面试回答模板** 来整理这道题：

------

# 🎯 面试题：JDK 动态代理和 CGLIB 动态代理的区别？SpringBoot 如何选择？

## 1. 概念解释

- **JDK 动态代理**：Java 自带的代理机制，基于 **接口**，通过 `InvocationHandler` + `Proxy.newProxyInstance` 在运行时生成代理类。
- **CGLIB 动态代理**：基于 **字节码增强（ASM 库）**，通过生成目标类的子类并重写方法来实现代理，不依赖接口。

------

## 2. 区别对比表格

| 对比点          | JDK 动态代理                         | CGLIB 动态代理                             |
| --------------- | ------------------------------------ | ------------------------------------------ |
| **依赖**        | 必须有接口                           | 不需要接口，基于继承                       |
| **实现方式**    | 反射调用 `invoke()`                  | ASM 字节码生成子类，重写方法               |
| **性能**        | 生成代理快，方法调用稍慢（反射开销） | 生成代理慢，方法调用快（直接调用字节码）   |
| **限制**        | 只能代理接口方法                     | 不能代理 `final` 类和 `final/private` 方法 |
| **应用场景**    | 业务接口较多的类                     | 没有接口的类，如工具类、实体类             |
| **Spring 默认** | 有接口时优先选择                     | 没有接口时使用                             |

------

## 3. SpringBoot 的选择策略

- **默认规则**：

  - **有接口** → 使用 **JDK 动态代理**。
  - **没有接口** → 使用 **CGLIB 动态代理**。

- **可配置强制使用 CGLIB**：

  ```yaml
  spring:
    aop:
      proxy-target-class: true
  ```

- **为什么默认选 JDK？**

  - 因为 JDK 动态代理是 JDK 原生支持，轻量、稳定，避免了 CGLIB 的依赖和字节码开销。

------

## 4. 案例说明

```java
// JDK 动态代理：需要接口
public interface UserService { void save(); }
public class UserServiceImpl implements UserService {
    public void save() { System.out.println("保存用户"); }
}

// CGLIB 动态代理：没有接口时
public class OrderService {
    public void createOrder() { System.out.println("创建订单"); }
}
```

- **在 SpringBoot 项目中**：
  - `UserServiceImpl` 默认会走 **JDK 动态代理**。
  - `OrderService` 没有接口，会走 **CGLIB 动态代理**。

------

## 5. 面试标准回答（简洁版）

> JDK 动态代理基于接口实现，CGLIB 基于继承生成子类。
>  JDK 代理生成速度快，但只能代理接口；CGLIB 方法调用效率更高，但不能代理 final 类/方法。
>  SpringBoot 默认：如果目标类实现了接口，用 JDK 动态代理；如果没有接口，则用 CGLIB，也可以通过 `spring.aop.proxy-target-class=true` 强制使用 CGLIB。

------

## 6. 扩展追问

- 如果目标类同时有接口和非接口方法，Spring 代理的行为是什么？
- 在高并发场景下，JDK 和 CGLIB 的性能差异如何？
- 为什么事务注解 `@Transactional` 在 `private/final` 方法上会失效？
- 除了 JDK 和 CGLIB，你能说说 **静态代理** 和 **字节码增强（Javassist、ByteBuddy）** 的区别吗？

------

要不要我帮你把 **Spring 事务是如何通过 AOP 实现的？为什么有些场景事务会失效？** 也整理成这种完整回答？这是 AOP 高频面试题里最重要的一道。