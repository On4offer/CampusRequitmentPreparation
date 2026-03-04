好 👍，这一题非常经典，尤其是和 MyBatis、Spring AOP 配合时常考。我来帮你整理成面试八股文模板（概念 → 区别 → 原理 → 案例 → 标准回答 → 扩展追问）：

------

# 面试题：FactoryBean 和普通 Bean 的区别？getObject() 的作用是什么？

## 1. 概念解释

- **普通 Bean**
  - 由 Spring 容器通过反射直接实例化，放入 IOC 容器。
  - 获取时：`getBean("beanName")` → 返回的就是该 Bean 实例。
- **FactoryBean**
  - 一种特殊的 Bean，本质是 **工厂类**。
  - 它本身被 Spring 管理，但它的作用是**创建其他对象**。
  - 获取时：
    - `getBean("beanName")` → 返回 `FactoryBean.getObject()` 的结果；
    - `getBean("&beanName")` → 返回 FactoryBean 本身。

------

## 2. 区别对比

| 对比项   | 普通 Bean                      | FactoryBean                                    |
| -------- | ------------------------------ | ---------------------------------------------- |
| 定义     | 普通对象，由容器直接实例化     | 工厂对象，用来创建其他对象                     |
| 获取结果 | `getBean("id")` 返回该对象本身 | `getBean("id")` 返回工厂生产的对象             |
| 特殊符号 | 无                             | 使用 `&id` 可获取工厂本身                      |
| 使用场景 | 常规业务类（Service、Dao 等）  | 框架中需要动态生成对象，如代理对象、ORM Mapper |

------

## 3. 底层原理

- **普通 Bean**：
   Spring 通过 `BeanDefinition` → 反射调用构造器 → 放入 IOC 容器。
- **FactoryBean**：
  1. Spring 创建 `FactoryBean` 实例；
  2. 调用其 `getObject()` 方法，返回实际对象；
  3. 注册到容器时，默认保存的是 `getObject()` 的结果。

所以 `getObject()` 的核心作用就是：**返回 FactoryBean 生产的目标对象**。

------

## 4. 项目应用案例

- **MyBatis 与 Spring 整合**
  - `MapperFactoryBean`：每个 Mapper 接口对应一个 FactoryBean。
  - 它的 `getObject()` 返回的是 **Mapper 的动态代理对象**，而不是接口本身。
  - 所以我们能直接 `@Autowired private UserMapper userMapper;`。
- **Spring AOP**
  - `ProxyFactoryBean`：底层通过 JDK 动态代理或 CGLIB 创建代理对象。
  - `getObject()` 返回的就是增强后的代理对象。

------

## 5. 面试标准回答（简洁版）

> 普通 Bean 是由 Spring 容器直接实例化的对象，而 FactoryBean 是一种特殊的工厂 Bean，本身是由 Spring 管理的工厂类。
>  调用 `getBean("beanName")` 时，如果是普通 Bean，返回的就是对象本身；如果是 FactoryBean，返回的是 `getObject()` 方法创建的对象。若要获取 FactoryBean 本身，可以使用 `&beanName`。
>  `getObject()` 的作用就是返回 FactoryBean 生产的目标对象，这也是 MyBatis、AOP 等框架能无缝集成的关键。

------

## 6. 扩展追问

1. 如何获取 FactoryBean 本身？
    → `getBean("&beanName")`。
2. 为什么 Spring 需要 FactoryBean 机制？
    → 提供灵活的对象创建方式，尤其适合动态代理、复杂对象创建。
3. FactoryBean 和 BeanFactory 的区别？
   - BeanFactory 是 IOC 容器的顶层接口；
   - FactoryBean 是容器里的一种特殊 Bean，用于生产对象。
4. 如果 `getObject()` 返回的是单例，Spring 如何保证只创建一次？
   - FactoryBean 默认也是单例，Spring 会缓存 `getObject()` 的结果，除非 `isSingleton()` 返回 false。

------

要不要我再帮你把 **“@Configuration 与 @Component 的区别？为什么 @Configuration 默认是 CGLIB 代理？”** 整理出来？这题和配置类加载机制、代理增强息息相关，也经常和 FactoryBean 一起被问。