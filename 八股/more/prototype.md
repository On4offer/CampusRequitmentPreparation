在 **Spring Framework** 中，`prototype` 是一种 **Bean 的作用域（Scope）**，它意味着每次请求一个 Bean 时，Spring 容器都会创建一个新的 Bean 实例。这与 `singleton` 作用域不同，在 `singleton` 作用域下，Spring 容器只会有一个 Bean 实例，且整个应用程序使用同一个实例。

### 1. **`prototype` 作用域概述**

- **定义**：当一个 Bean 的作用域设置为 `prototype` 时，Spring 容器每次请求该 Bean 时，都会创建一个新的实例。每个请求都会返回一个不同的对象实例。
- **生命周期**：`prototype` Bean 在容器中并不会被容器管理整个生命周期，Spring 仅负责创建 Bean 实例，并将其交给客户端使用，之后由客户端负责销毁。因此，Spring 容器不会在 `prototype` Bean 上执行销毁方法。

### 2. **`prototype` 作用域的工作原理**

当 Bean 的作用域设置为 `prototype` 时，Spring 容器不会在启动时创建该 Bean，而是每次调用 `getBean()` 时都会创建一个新的实例。

#### 示例：使用 `prototype` 作用域的 Bean

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;

@Configuration
public class AppConfig {

    @Bean
    @Scope("prototype")  // 设置作用域为 prototype
    public MyService myService() {
        return new MyService();
    }
}
```

在这个示例中，`myService()` 方法返回一个 `MyService` 的实例。由于它的作用域被设置为 `prototype`，每次调用 `getBean()` 方法时，Spring 会创建并返回一个新的 `MyService` 实例。

### 3. **`prototype` 作用域的特点**

1. **每次请求一个新实例**：
   - 每次通过 `ApplicationContext.getBean()` 请求时，Spring 容器都会创建一个新的 Bean 实例，而不是返回缓存中的实例。
2. **不管理 Bean 销毁**：
   - Spring 容器不会管理 `prototype` Bean 的销毁。它仅在 Bean 被创建时负责生成实例，但不会自动调用销毁方法。开发者需要显式地处理销毁操作，例如手动释放资源。
3. **适用于需要多实例的场景**：
   - 如果一个 Bean 需要保持不同的状态，或者在每次使用时需要不同的数据，可以选择 `prototype` 作用域。比如，一个用于生成报告的 Bean，每个报告实例需要独立的状态或数据。
4. **没有单例的性能优化**：
   - 由于每次请求都会创建新的实例，`prototype` 作用域的 Bean 的创建成本通常比 `singleton` 更高，尤其是在高并发环境中。

### 4. **`prototype` 作用域的生命周期**

- **创建时机**：`prototype` Bean 只有在调用 `getBean()` 时才会被创建，每次请求都会生成新的实例。
- **销毁时机**：Spring 容器不会自动销毁 `prototype` Bean 的实例。Spring 仅负责创建 Bean 实例，并将其交给客户端使用。当容器关闭时，`prototype` Bean 不会被自动销毁。开发者需要显式地进行资源清理。

### 5. **`prototype` 作用域的使用场景**

`prototype` 作用域适用于以下场景：

- **需要多个独立实例的 Bean**：例如，如果你有一个状态相关的 Bean，每次请求都需要一个全新的实例。
- **无共享状态**：当你不希望多个请求共享相同的 Bean 实例时，`prototype` 作用域提供了独立的实例。
- **高性能场景**：当你需要每次创建一个新的 Bean 实例，避免了多线程环境中共享状态的潜在问题。

### 6. **`prototype` 作用域与 `singleton` 作用域的比较**

| 作用域        | 描述                                          | 示例                     |
| ------------- | --------------------------------------------- | ------------------------ |
| **singleton** | 容器中只有一个实例，整个应用程序共享该 Bean。 | 每个 Bean 的实例是唯一的 |
| **prototype** | 每次请求都会创建一个新的 Bean 实例。          | 每次请求 Bean 都是新实例 |

### 7. **`prototype` 作用域的销毁管理**

由于 `prototype` Bean 的生命周期由客户端管理，Spring 容器不会自动处理它们的销毁。这就意味着，**如果需要在 `prototype` Bean 销毁时进行一些清理操作（如关闭数据库连接、清理资源等），需要开发者自己负责销毁**。

#### 销毁方法的处理：

- **手动销毁**：可以在客户端中手动调用销毁方法，或者使用 `@PreDestroy` 注解标记销毁方法。
- **Spring 容器不管理销毁**：与 `singleton` 作用域不同，`prototype` Bean 在销毁时不会由 Spring 自动处理资源释放或销毁方法的调用。

### 8. **`prototype` 作用域的示例：**

#### 8.1 **`prototype` 作用域配置**

```java
import org.springframework.context.ApplicationContext;
import org.springframework.context.annotation.AnnotationConfigApplicationContext;

public class MyApp {
    public static void main(String[] args) {
        // 创建 Spring 容器
        ApplicationContext context = new AnnotationConfigApplicationContext(AppConfig.class);

        // 获取 Bean（每次获取都会创建一个新的实例）
        MyService service1 = context.getBean(MyService.class);
        MyService service2 = context.getBean(MyService.class);

        // 比较两个实例是否相同
        System.out.println(service1 == service2);  // 输出: false
    }
}
```

#### 8.2 **配置类（`AppConfig`）**

```java
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.context.annotation.Scope;

@Configuration
public class AppConfig {

    @Bean
    @Scope("prototype")  // 设置作用域为 prototype
    public MyService myService() {
        return new MyService();
    }
}
```

在这个例子中，每次通过 `getBean()` 方法请求 `MyService` Bean 时，都会返回一个新的实例，而不是共享同一个实例。

### 9. **总结**

- **`prototype` 作用域** 在 Spring 中意味着每次请求都会创建一个新的 Bean 实例。
- 适用于需要每次都创建一个新对象的场景，通常用于需要无共享状态的 Bean。
- Spring 容器不会管理 `prototype` Bean 的销毁，因此开发者需要手动管理销毁逻辑。
- `prototype` 作用域增加了 Bean 的创建开销，并且不会像 `singleton` 那样在容器关闭时自动销毁 Bean，适用于有独立状态的对象。

通过使用 `prototype` 作用域，开发者可以精确控制 Bean 的实例化和生命周期，使得每个请求都可以获得一个独立的 Bean 实例。