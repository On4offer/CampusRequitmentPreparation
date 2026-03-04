好 👌，这题很考察 Spring 底层机制，我来给你整理完整面试八股文答案（概念 → 区别 → 原理 → 案例 → 标准回答 → 扩展追问）：

------

# 面试题：@Configuration 与 @Component 有什么区别？为什么 @Configuration 默认是 CGLIB 代理？

## 1. 概念解释

- **@Component**
  - 通用组件注解，标记在类上，表明该类交给 Spring 管理。
  - 没有额外语义，只是一个普通 Bean。
- **@Configuration**
  - 特殊的 @Component，通常用来声明配置类。
  - 里面定义的 `@Bean` 方法会交由 Spring 容器管理，保证单例和依赖关系。

------

## 2. 区别对比

| 对比项        | @Component               | @Configuration                               |
| ------------- | ------------------------ | -------------------------------------------- |
| 所属关系      | 基础注解                 | 组合注解，本身也带有 @Component              |
| 主要用途      | 普通 Bean                | 配置类，声明 @Bean 方法                      |
| Bean 方法效果 | 普通方法调用，返回新对象 | Spring 会拦截方法调用，返回 IOC 容器中的单例 |
| 代理机制      | 无                       | 默认 CGLIB 代理增强，保证 @Bean 单例         |

------

## 3. 为什么 @Configuration 默认是 CGLIB 代理？

- **问题场景**

  ```java
  @Configuration
  public class AppConfig {
      @Bean
      public UserService userService() {
          return new UserService(orderService());
      }
  
      @Bean
      public OrderService orderService() {
          return new OrderService();
      }
  }
  ```

  - 如果 @Configuration 只是一个普通 @Component：
     每次调用 `orderService()`，都会 `new` 出一个对象，导致不是单例。

- **Spring 的解决方案**

  - 给 @Configuration 类生成 **CGLIB 子类代理**：
    - 拦截对 `@Bean` 方法的调用；
    - 如果 IOC 容器已有对应 Bean，就直接从容器获取；
    - 避免重复创建，保证单例。

- **底层实现**

  - 由 `ConfigurationClassPostProcessor` 在解析配置类时，使用 **CGLIB 动态代理**增强配置类。
  - 代理类会覆盖 `@Bean` 方法，改为先查容器再决定是否创建。

------

## 4. 项目应用案例

- **黑马点评**

  - Redis 配置类：

    ```java
    @Configuration
    public class RedisConfig {
        @Bean
        public RedisTemplate redisTemplate() {
            return new RedisTemplate();
        }
    }
    ```

    如果没有 CGLIB 代理，每次调用 `redisTemplate()` 都会 new 一个对象，不符合单例要求。

- **苍穹外卖**

  - 全局 Jackson 配置、Knife4j 配置等都是 @Configuration 类，Spring 保证其中的 @Bean 方法返回单例对象。

------

## 5. 面试标准回答（简洁版）

> `@Configuration` 本质上是 `@Component` 的一种特殊形式，但它专门用来定义配置类，里面的 `@Bean` 方法会被 Spring 容器管理。
>  普通 `@Component` 类的方法调用就是普通的 Java 调用，会返回新对象；而 `@Configuration` 默认使用 **CGLIB 代理**，在调用 `@Bean` 方法时会被拦截，从容器中返回单例 Bean，保证依赖的一致性。

------

## 6. 扩展追问

1. 如果把 @Configuration 换成 @Component，会发生什么？
   - @Bean 方法不再被代理，每次调用都会 new 新对象。
2. 为什么用 CGLIB 而不是 JDK 动态代理？
   - JDK 只能代理接口，而配置类没有接口，只能用 CGLIB。
3. 能关闭 @Configuration 的代理模式吗？
   - 可以：`@Configuration(proxyBeanMethods = false)`，称为 **Lite 模式**，不会进行方法拦截，适合无依赖的 Bean。
4. @Bean 方法之间有依赖时，为什么必须用 Full 模式？
   - 因为 Lite 模式不会代理方法，可能导致依赖的 Bean 被多次实例化。

------

要不要我接着帮你整理 **“Spring 中单例 Bean 是如何保证线程安全的？一定安全吗？”** 这一题？这道题和 IOC 生命周期、Bean 创建过程也经常连环问。