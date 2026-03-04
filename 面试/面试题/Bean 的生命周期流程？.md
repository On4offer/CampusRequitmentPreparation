好 👍，这道是 **Spring 高频八股文**，我帮你整理成结构化面试答案（概念 → 流程 → 回调方法 → 项目应用 → 标准回答 → 扩展追问）：

------

# 面试题：Bean 的生命周期流程是什么？涉及哪些回调方法？

## 1. 概念解释

Spring 中的 **Bean 生命周期** 指的是一个 Bean 从创建到销毁的完整过程。
 Spring 容器通过 **反射、依赖注入、初始化、销毁** 等步骤来管理 Bean，并在不同阶段提供了扩展点（回调方法/接口），方便开发者参与 Bean 的管理。

------

## 2. Bean 生命周期流程（单例 Bean 为例）

1. **实例化**：
   - Spring 通过反射调用构造器，创建 Bean 对象。
2. **依赖注入**：
   - 按照配置或注解（如 `@Autowired`），为 Bean 的属性注入依赖。
3. **设置 BeanName**（可选）：
   - 如果实现了 `BeanNameAware`，会回调 `setBeanName()`，传入 Bean 的 id。
4. **设置 BeanFactory/ApplicationContext**（可选）：
   - 如果实现了 `BeanFactoryAware` 或 `ApplicationContextAware`，会回调相应方法，把容器传进来。
5. **BeanPostProcessor 前置处理**：
   - 调用所有 BeanPostProcessor 的 `postProcessBeforeInitialization()` 方法。
6. **初始化**：
   - 如果实现了 `InitializingBean`，会调用 `afterPropertiesSet()`。
   - 如果配置了 `init-method`，会调用该方法。
7. **BeanPostProcessor 后置处理**：
   - 调用所有 BeanPostProcessor 的 `postProcessAfterInitialization()` 方法。
8. **Bean 就绪，可以使用**
9. **销毁阶段**：
   - 容器关闭时，调用 `DisposableBean.destroy()`。
   - 如果配置了 `destroy-method`，也会执行。

------

## 3. 涉及的回调方法

| 阶段       | 回调接口/方法                                                | 作用                                 |
| ---------- | ------------------------------------------------------------ | ------------------------------------ |
| Aware 接口 | `setBeanName()`、`setBeanFactory()`、`setApplicationContext()` | 获取 Bean 名称、BeanFactory 或上下文 |
| 初始化前   | `postProcessBeforeInitialization()`                          | BeanPostProcessor 前置增强           |
| 初始化     | `afterPropertiesSet()`（InitializingBean）`init-method`      | 自定义初始化逻辑                     |
| 初始化后   | `postProcessAfterInitialization()`                           | BeanPostProcessor 后置增强           |
| 销毁       | `destroy()`（DisposableBean）`destroy-method`                | 自定义销毁逻辑                       |

------

## 4. 项目应用案例

- **黑马点评**：
   `CacheClient` 使用 `@PostConstruct` 注解，在 Bean 初始化完成后执行缓存预热逻辑。
- **苍穹外卖**：
   在全局异常处理器、拦截器配置等类中，常见通过 `@PreDestroy` 在容器关闭时释放资源，比如关闭线程池或连接。

示例代码：

```java
@Component
public class MyBean implements InitializingBean, DisposableBean {

    @Override
    public void afterPropertiesSet() throws Exception {
        System.out.println("初始化逻辑");
    }

    @Override
    public void destroy() throws Exception {
        System.out.println("销毁逻辑");
    }

    @PostConstruct
    public void init() {
        System.out.println("@PostConstruct 初始化逻辑");
    }

    @PreDestroy
    public void cleanup() {
        System.out.println("@PreDestroy 销毁逻辑");
    }
}
```

------

## 5. 面试标准回答（简洁版）

> Spring Bean 的生命周期大致分为 **实例化 → 属性赋值 → Aware 接口回调 → BeanPostProcessor 前置处理 → 初始化（afterPropertiesSet/init-method） → BeanPostProcessor 后置处理 → 使用 → 销毁（destroy/destroy-method）**。
>  常见的回调方法有 `@PostConstruct`、`afterPropertiesSet()`、`init-method`、`destroy()`、`destroy-method`、`@PreDestroy`。

------

## 6. 扩展追问

1. BeanPostProcessor 在生命周期中起什么作用？
    → 用于 AOP 动态代理、Bean 增强。
2. `@PostConstruct` 和 `afterPropertiesSet()` 的区别？
    → 都是初始化阶段调用，前者基于 JSR-250 标准注解，后者是 Spring 特有接口。
3. 单例和原型（prototype）Bean 生命周期的区别？
    → 单例 Bean 会由容器管理销毁，原型 Bean 容器只负责创建，不负责销毁。
4. SpringBoot 中常见的生命周期扩展点有哪些？
    → `ApplicationRunner`、`CommandLineRunner`。

------

要不要我接着帮你整理 **“Spring 中的循环依赖是如何解决的？三级缓存的作用是什么？”** 这一题？这样 IOC 模块就完整了。