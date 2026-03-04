### `@Component` 注解介绍

------

### 一、背景

在 Spring 框架中，`@Component` 是一个**基础注解**，用于将 Java 类注册为 **Spring 容器中的 Bean**。这样，Spring 就可以自动管理这个类的生命周期并支持依赖注入。

------

### 二、定义

```java
@Target({ElementType.TYPE})
@Retention(RetentionPolicy.RUNTIME)
@Documented
@Component
public @interface Component {
    String value() default "";
}
```

------

### 三、作用

- 告诉 Spring：“**这个类需要托管起来作为 Bean 使用**”
- Spring 在**组件扫描（ComponentScan）**时自动识别并注册该类到容器中。

------

### 四、使用方式

```java
@Component
public class MyService {
    public void doSomething() {
        System.out.println("Doing something");
    }
}
```

然后在其他类中就可以通过注入使用：

```java
@Autowired
private MyService myService;
```

------

### 五、`@Component` 的派生注解（更具体的分类）

| 注解          | 说明                          |
| ------------- | ----------------------------- |
| `@Service`    | 标注在业务逻辑层的类上        |
| `@Repository` | 标注在 DAO 层，用于异常转换等 |
| `@Controller` | 标注在控制层（Web 层）        |

这些注解本质上都是 `@Component` 的衍生，功能一致，但**语义更清晰**。

------

### 六、配合使用：@ComponentScan

```java
@ComponentScan(basePackages = "com.example.service")
```

这段配置告诉 Spring 去扫描 `com.example.service` 包下的类，看哪些标注了 `@Component` 或其派生注解，然后自动注册。

------

是否需要我展示一个完整的 Bean 注册和使用的代码示例？