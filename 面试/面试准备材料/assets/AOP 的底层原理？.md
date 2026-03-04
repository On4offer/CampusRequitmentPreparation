好，我们继续按照**面试回答模板（概念 ➝ 原理 ➝ 案例 ➝ 使用场景 ➝ 追问）**来整理：

------

# 🎯 面试题：AOP 的底层原理是什么？基于 JDK 动态代理还是 CGLIB？

## 1. 概念解释

- **Spring AOP 的本质**：基于 **代理模式**（Proxy Pattern），通过生成目标对象的代理对象，在方法执行的前后织入额外逻辑（Advice）。
- 核心思想：**方法增强，而不是修改源码**。

------

## 2. 原理剖析

1. **JDK 动态代理**

   - 利用 **反射机制**（`InvocationHandler` + `Proxy.newProxyInstance`）为接口生成代理类。
   - 前提：目标类必须**实现接口**。
   - 代理对象和目标对象实现相同接口，调用时会先进入 `invoke()` 方法。

2. **CGLIB 动态代理**

   - 基于 **ASM 字节码操作框架**，在运行时生成目标类的子类，并重写方法来实现增强。
   - 不需要接口，但目标类**不能是 final**，方法也不能是 final/private。

3. **Spring 的选择策略**

   - **默认规则**：

     - 如果目标类 **实现了接口** → 默认使用 **JDK 动态代理**；
     - 如果目标类 **没有接口** → 使用 **CGLIB 动态代理**；

   - 如果强制配置：

     ```yaml
     spring:
       aop:
         proxy-target-class: true   # 强制使用 CGLIB
     ```

------

## 3. 代码案例

### JDK 动态代理

```java
public interface UserService {
    void save();
}

public class UserServiceImpl implements UserService {
    public void save() { System.out.println("保存用户"); }
}

public class JdkProxy {
    public static void main(String[] args) {
        UserService target = new UserServiceImpl();
        UserService proxy = (UserService) Proxy.newProxyInstance(
                target.getClass().getClassLoader(),
                target.getClass().getInterfaces(),
                (proxyObj, method, args1) -> {
                    System.out.println("方法前增强");
                    Object result = method.invoke(target, args1);
                    System.out.println("方法后增强");
                    return result;
                });
        proxy.save();
    }
}
```

### CGLIB 动态代理

```java
public class UserService {
    public void save() { System.out.println("保存用户"); }
}

public class CglibProxy {
    public static void main(String[] args) {
        Enhancer enhancer = new Enhancer();
        enhancer.setSuperclass(UserService.class);
        enhancer.setCallback((MethodInterceptor) (obj, method, args, proxy) -> {
            System.out.println("方法前增强");
            Object result = proxy.invokeSuper(obj, args);
            System.out.println("方法后增强");
            return result;
        });
        UserService proxy = (UserService) enhancer.create();
        proxy.save();
    }
}
```

------

## 4. 使用场景对比

- **JDK 动态代理**：适用于**有接口**的业务类，性能略高，生成速度快。
- **CGLIB 动态代理**：适用于**没有接口**的类，但生成代理类开销更大，首次调用性能较低。

------

## 5. 面试标准回答（简洁版）

> Spring AOP 的底层是基于代理模式实现的。
>
> - 当目标类实现了接口时，默认使用 **JDK 动态代理**；反射机制生成接口的代理类。
> - 当目标类没有实现接口时，使用 **CGLIB 动态代理**。字节码框架ASM生成目标类的子类。
> - 也可以通过配置强制使用 CGLIB。
>    两者区别在于：JDK 动态代理基于接口，CGLIB 基于继承字节码增强。

------

## 6. 扩展追问

- JDK 动态代理和 CGLIB 的性能差异？在高并发下哪个更合适？
- 如果目标类既有接口又希望使用 CGLIB，该怎么做？
- 为什么 Spring AOP 默认选择 JDK 动态代理？
- 除了 JDK 和 CGLIB，还有没有其他动态代理实现方式？

------

要不要我帮你也整理一份 **“JDK 动态代理和 CGLIB 动态代理的区别？SpringBoot 如何选择？”** 的完整面试回答？这个问题经常和这一题连着问。