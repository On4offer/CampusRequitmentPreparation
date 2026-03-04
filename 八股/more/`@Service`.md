### `@Service` 注解介绍

------

### 一、背景

在 Spring 框架中，`@Service` 是一个**用于标注业务逻辑层组件**的注解，属于 Spring 的 **组件标注注解** 之一。它的作用和 `@Component` 相同，都是将类注册为 Spring 容器的 Bean，但语义更明确。

------

### 二、定义（本质上是 `@Component` 的特化）

```java
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Component
public @interface Service {
    String value() default "";
}
```

------

### 三、作用

- 表示这个类是 **业务服务组件**；
- 在使用 `@ComponentScan` 或 `@SpringBootApplication` 时，会自动被扫描并注册为 Bean；
- 方便开发人员理解：**它是处理业务逻辑的类，而不是控制器或 DAO 层类**。

------

### 四、使用示例

```java
@Service
public class OrderService {
    public void processOrder() {
        // 业务逻辑处理
    }
}
```

然后在 Controller 或其他地方使用：

```java
@Autowired
private OrderService orderService;
```

------

### 五、对比其他组件注解

| 注解          | 用于标注的层级       | 本质                              |
| ------------- | -------------------- | --------------------------------- |
| `@Component`  | 通用组件             | Bean 注册                         |
| `@Service`    | 业务逻辑层           | `@Component` 派生                 |
| `@Repository` | 数据访问层           | `@Component` 派生（还带异常转换） |
| `@Controller` | 表现层（Web 控制器） | `@Component` 派生                 |

------

是否需要我一并介绍 `@Repository` 或 `@Controller`？