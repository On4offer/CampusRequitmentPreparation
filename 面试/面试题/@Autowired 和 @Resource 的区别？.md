好 👍，这一题很常考，我来帮你整理成 **面试八股文模板**（概念 → 区别 → 原理 → 案例 → 标准回答 → 扩展追问）：

------

# 面试题：@Autowired 和 @Resource 的区别是什么？各自底层原理？

## 1. 概念解释

- **@Autowired**
  - Spring 提供的注解，默认按 **类型（byType）** 自动装配。
  - 可以配合 `@Qualifier` 按名称装配。
  - 可以指定 `required=false`，避免找不到 Bean 报错。
- **@Resource**
  - JSR-250 规范（`javax.annotation.Resource`），属于 **Java 标准注解**，Spring 只是支持它。
  - 默认按 **名称（byName）** 注入，找不到再按类型。
  - 没有 `required` 属性。

------

## 2. 区别对比

| 对比项   | @Autowired                        | @Resource                              |
| -------- | --------------------------------- | -------------------------------------- |
| 提供方   | Spring 专属                       | JSR-250 标准（Java 提供，Spring 支持） |
| 默认方式 | 按类型（byType）                  | 按名称（byName），再按类型             |
| 配合注解 | 可配合 `@Qualifier` 指定名称      | 可用 `name` 属性指定 Bean 名称         |
| required | 支持 `required=false`             | 不支持                                 |
| 常见问题 | 同类型多个 Bean → 需 `@Qualifier` | Bean 名称不一致可能找不到              |

------

## 3. 底层原理

- **@Autowired 原理**
  - 核心类：`AutowiredAnnotationBeanPostProcessor`
  - 扫描 Bean 上的 `@Autowired` 注解 → 通过 **反射** 注入依赖。
  - 依赖解析：
    1. 先按类型查找 Bean；
    2. 如果有多个，再按 `@Qualifier` 或参数名匹配；
    3. 没找到且 `required=true` → 抛异常。
- **@Resource 原理**
  - 核心类：`CommonAnnotationBeanPostProcessor`
  - 扫描 `@Resource` → 调用 JDK 的 `InjectionMetadata` 注入依赖。
  - 依赖解析：
    1. 如果指定了 `name` 属性 → 按 Bean 名称找；
    2. 否则按字段名找；
    3. 如果还没找到 → 按类型找；
    4. 都没找到 → 抛异常。

------

## 4. 项目应用案例

- **黑马点评**

  ```java
  @Service
  public class ShopServiceImpl implements ShopService {
      @Autowired
      private StringRedisTemplate stringRedisTemplate; // Redis 缓存操作工具
  }
  ```

- **苍穹外卖**

  ```java
  @Service
  public class OrderServiceImpl implements OrderService {
      @Resource
      private OrderMapper orderMapper; // 默认按名称匹配
  }
  ```

区别在于：如果 Mapper 名称和字段名不一致，`@Resource` 可能报错，而 `@Autowired` 一般没问题。

------

## 5. 面试标准回答（简洁版）

> `@Autowired` 是 Spring 提供的注解，默认按 **类型** 注入，可以配合 `@Qualifier` 指定名称，支持 `required=false`。
>  `@Resource` 是 JSR-250 标准注解，默认按 **名称** 注入，找不到再按类型，不支持 `required`。
>  底层分别通过 `AutowiredAnnotationBeanPostProcessor` 和 `CommonAnnotationBeanPostProcessor` 实现，依赖注入过程基于反射。

------

## 6. 扩展追问

1. 如果一个接口有多个实现，`@Autowired` 怎么处理？
   - 配合 `@Qualifier` 或 `@Primary`。
2. 为什么推荐 `@Autowired` 而不是 `@Resource`？
   - 更灵活（支持 required、Qualifier），与 Spring 生态更贴合。
3. `@Inject` 和 `@Autowired` 的区别？
   - `@Inject` 是 JSR-330 标准，类似 `@Autowired`，但不支持 `required=false`。
4. Spring Boot 推荐哪一个？
   - 推荐 `@Autowired`，因为和 Spring 生态高度兼容。

------

要不要我把 **“BeanFactory 和 ApplicationContext 的区别”** 也整理一份？这样 IOC & Bean 管理这一块的面试题答案会更完整。