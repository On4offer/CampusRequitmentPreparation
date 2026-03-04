### 手动创建 Bean

在 Spring 框架中，**手动创建 Bean** 是指通过手动配置或编程方式将对象实例化并注册到 Spring 容器中。虽然 Spring 通常通过注解（如 `@Component`）或 XML 配置来自动扫描和注册 Bean，但在某些特殊场景中，手动创建 Bean 是有用的，比如动态注册 Bean、在运行时根据条件创建 Bean 或进行更细粒度的控制。

手动创建 Bean 的方式主要有两种：

1. **通过 Java 配置手动创建 Bean**（基于 `@Configuration` 和 `@Bean` 注解）
2. **通过 `ApplicationContext` 手动注册 Bean**

下面详细介绍这两种手动创建 Bean 的方式。

### 1. **通过 Java 配置手动创建 Bean**

Spring 提供了基于 Java 配置的方式来手动创建 Bean。通过 `@Configuration` 注解定义一个配置类，并使用 `@Bean` 注解显式地定义 Bean。

#### 1.1 **通过 `@Bean` 注解手动创建 Bean**

在 Java 配置类中，使用 `@Bean` 注解的方法可以手动注册 Bean。此方法适用于不依赖注解扫描的情况，或者需要显式控制 Bean 创建的场景。

**示例**：

```java
@Configuration
public class AppConfig {

    @Bean
    public Engine engine() {
        return new Engine();
    }

    @Bean
    public Car car() {
        return new Car(engine());  // 使用 Engine Bean 创建 Car Bean
    }
}
```

在这个示例中：

- `@Configuration` 注解标记类为配置类。
- `@Bean` 注解标记的方法会被 Spring 容器视为 Bean 的定义，并将其注册到容器中。
- `car()` 方法通过调用 `engine()` 方法，显式地创建了 `Car` Bean 并注入了 `Engine` Bean 作为依赖。

#### 1.2 **手动创建并注册 Bean（条件化注册）**

你还可以根据条件来决定是否创建某个 Bean。例如，在不同的环境下创建不同的 Bean，或者根据某些配置创建 Bean。

**示例**：

```java
@Configuration
public class AppConfig {

    @Value("${app.engine.type}")
    private String engineType;

    @Bean
    public Engine engine() {
        if ("V8".equals(engineType)) {
            return new V8Engine();  // 创建 V8 类型的发动机
        } else {
            return new V6Engine();  // 创建 V6 类型的发动机
        }
    }

    @Bean
    public Car car() {
        return new Car(engine());
    }
}
```

在这个例子中：

- `engine()` 方法根据 `engineType` 的值来选择创建 `V8Engine` 或 `V6Engine`，这就是条件化注册 Bean。

### 2. **通过 `ApplicationContext` 手动注册 Bean**

除了通过注解配置，Spring 还允许通过编程的方式手动注册 Bean。你可以通过 `ApplicationContext` 或 `BeanFactory` 手动注册 Bean 实例。通常这在动态创建 Bean 或自定义 Bean 配置时非常有用。

#### 2.1 **通过 `AnnotationConfigApplicationContext` 手动注册 Bean**

你可以使用 `AnnotationConfigApplicationContext` 手动注册 Java 配置类或 Bean。这样可以在运行时动态地注册 Bean。

**示例**：

```java
public class Main {
    public static void main(String[] args) {
        AnnotationConfigApplicationContext context = new AnnotationConfigApplicationContext();
        
        // 手动注册 Java 配置类
        context.register(AppConfig.class);
        
        // 手动注册单个 Bean
        context.registerBean("car", Car.class);

        // 启动 Spring 容器
        context.refresh();
        
        // 获取 Bean
        Car car = context.getBean(Car.class);
        car.start();
        
        context.close();
    }
}
```

在这个例子中：

- 使用 `AnnotationConfigApplicationContext` 创建 Spring 上下文。
- 使用 `registerBean()` 方法手动注册 `Car` Bean。
- 调用 `context.getBean()` 获取并使用手动注册的 Bean。

#### 2.2 **通过 `DefaultListableBeanFactory` 手动注册 Bean**

`DefaultListableBeanFactory` 是 Spring 中最基础的容器类，它可以用来手动注册 Bean。你可以直接将 Bean 定义添加到 `BeanFactory` 中，并通过 `getBean()` 方法获取它。

**示例**：

```java
public class Main {
    public static void main(String[] args) {
        DefaultListableBeanFactory beanFactory = new DefaultListableBeanFactory();
        
        // 手动注册 Bean
        beanFactory.registerBeanDefinition("car", new RootBeanDefinition(Car.class));
        
        // 获取 Bean
        Car car = beanFactory.getBean(Car.class);
        car.start();
    }
}
```

在这个例子中：

- 使用 `DefaultListableBeanFactory` 手动注册了一个 `Car` Bean。
- `RootBeanDefinition` 是 Spring 用来定义 Bean 的元数据的对象，包含了 Bean 的类信息等。

### 3. **手动创建 Bean 的使用场景**

手动创建 Bean 适用于以下几种场景：

1. **动态注册 Bean**：当 Bean 的创建依赖于运行时条件或配置时，可以通过手动注册来动态创建和注册 Bean。
2. **根据特定配置创建 Bean**：例如，根据不同的环境或配置（如 `application.properties`）来创建不同的 Bean 实例。
3. **在没有注解扫描的情况下管理 Bean**：当项目需要与一些没有注解支持的库集成时，手动创建 Bean 可以确保 Spring 容器管理这些对象。
4. **高级自定义**：需要对 Bean 的创建过程进行更精细的控制，如使用代理、调整 Bean 的初始化过程等。

### 4. **总结**

- **手动创建 Bean** 是一种编程方式，允许开发者在 Spring 容器中动态注册 Bean，而不是通过注解或 XML 配置文件自动扫描和注册 Bean。
- **通过 `@Bean` 注解**：使用 Java 配置类和 `@Bean` 注解来手动注册 Bean。
- **通过 `ApplicationContext` 或 `BeanFactory`**：可以在应用运行时，通过 `AnnotationConfigApplicationContext` 或 `DefaultListableBeanFactory` 手动注册 Bean。
- 手动创建 Bean 在动态条件下、与其他框架集成时或者需要高级自定义的场景中非常有用。