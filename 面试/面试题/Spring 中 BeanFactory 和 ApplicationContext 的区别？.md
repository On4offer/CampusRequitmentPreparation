好，这道题也是 **Spring 基础必问点**，我帮你整理成 **标准面试答题模板**（概念 → 区别 → 应用场景 → 项目结合 → 扩展追问），保证你能完整应答。

------

# 📌 面试题

Spring 中 BeanFactory 和 ApplicationContext 的区别？

------

### ✅ 一、概念回答

- **BeanFactory**：Spring 最基本的 **IOC 容器接口**，提供了 Bean 的基本管理功能（创建、获取、依赖注入等），是 Spring 容器的核心。
- **ApplicationContext**：在 BeanFactory 的基础上进行了扩展，是 **更高级的 IOC 容器实现**，提供国际化（i18n）、事件发布、AOP、自动 BeanPostProcessor 注册等功能。

------

### ✅ 二、主要区别

| 对比点       | BeanFactory                                      | ApplicationContext                                           |
| ------------ | ------------------------------------------------ | ------------------------------------------------------------ |
| 加载方式     | **延迟加载（Lazy Loading）**：用到 Bean 时才创建 | **预加载（Eager Loading）**：启动时就实例化单例 Bean         |
| 功能         | 只提供基础的 IOC 功能                            | 扩展功能更多（事件机制、国际化、自动 BeanPostProcessor 注册等） |
| AOP/事务支持 | 不支持，需要手动配置                             | 内置 AOP/事务功能，开箱即用                                  |
| 适用场景     | 资源受限的环境（IoT、移动端）                    | 常规企业应用开发（Web/微服务）                               |
| 常见实现类   | `XmlBeanFactory`（已废弃）                       | `ClassPathXmlApplicationContext`、`AnnotationConfigApplicationContext`、`SpringBoot` 默认的 `AnnotationConfigServletWebServerApplicationContext` |

------

### ✅ 三、典型使用场景

- **BeanFactory**：适合资源紧张或只需简单容器的场景（IoT、轻量级应用），现在实际开发中基本不用。
- **ApplicationContext**：适合绝大多数 Web 项目、企业级项目，SpringBoot 默认就是基于它的实现。

------

### ✅ 四、结合项目经验

- 在 **黑马点评** 和 **苍穹外卖** 项目中，使用的都是基于 **ApplicationContext** 的 IOC 容器。
- 例如，在 SpringBoot 启动过程中，默认创建的是 `AnnotationConfigServletWebServerApplicationContext`，它除了加载 Bean，还帮我们自动注册 Web 环境、国际化配置、事件广播器等，不需要我们手动管理。

------

### ✅ 五、扩展追问（可能会问到）

1. 为什么 SpringBoot 默认使用 ApplicationContext？
2. ApplicationContext 的刷新过程（`refresh()`）做了哪些事情？
3. 单例 Bean 在 ApplicationContext 中是如何提前实例化的？
4. BeanFactory 和 FactoryBean 有什么区别？
5. 如果我要在容器初始化前修改 Bean 定义，可以用什么扩展点？（`BeanFactoryPostProcessor`）

------

⚡ **标准回答模板（面试时可直接说）：**

> BeanFactory 是 Spring 最基础的 IOC 容器，只提供 Bean 的基本管理，采用延迟加载；ApplicationContext 是 BeanFactory 的子接口，功能更强大，支持国际化、事件机制、AOP、事务等，并且会在容器启动时就预加载所有单例 Bean。实际开发中，比如我在黑马点评项目里，SpringBoot 默认使用的就是 ApplicationContext 的实现类，它能保证 Web 环境、Bean 装配和自动配置的完整功能。

------

要不要我帮你把 **Bean 的生命周期流程** 也整理成这种标准模板？这是和这个问题经常连着问的。