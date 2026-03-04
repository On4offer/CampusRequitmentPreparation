好 👍，这道题考察的是 **Spring 容器如何启动并加载配置类、扫描 Bean** 的原理。我来帮你整理成标准的面试题答案（概念 → 原理流程 → 代码案例 → 项目应用 → 标准回答 → 扩展追问）：

------

# 面试题：Spring 是如何加载配置类和扫描包路径的？

## 1. 概念解释

- **配置类（@Configuration）**
  - 用于替代 `applicationContext.xml`，标注了 `@Configuration` 的类会被当作 Bean 定义类，由 Spring 容器解析。
- **包扫描（@ComponentScan）**
  - 用于指定扫描哪些包，将其中标注了 `@Component`、`@Service`、`@Repository`、`@Controller` 等注解的类注册为 Bean。

------

## 2. 原理流程

1. **启动容器**
   - 使用 `AnnotationConfigApplicationContext` 或 Spring Boot 的 `SpringApplication.run()`。
2. **加载配置类**
   - Spring 通过 `ConfigurationClassPostProcessor` 解析配置类：
     - 识别 `@Configuration` 注解；
     - 解析 `@Bean` 方法，注册到 BeanDefinitionMap；
     - 解析 `@Import`、`@ImportResource` 等扩展。
3. **扫描包路径**
   - 解析 `@ComponentScan` 注解；
   - 调用 `ClassPathBeanDefinitionScanner`：
     - 扫描指定包路径下的 `.class` 文件；
     - 判断是否有 `@Component` 等注解；
     - 生成 `BeanDefinition` 并注册到容器。
4. **注册 BeanDefinition**
   - 将扫描到的 Bean 信息放入 IOC 容器的 **BeanDefinitionMap**，等待实例化。
5. **实例化与依赖注入**
   - 在容器启动完成后，Spring 根据 BeanDefinition 创建实例并注入依赖。

------

## 3. 代码案例

### 普通 Spring 应用

```java
@Configuration
@ComponentScan("com.example.demo")
public class AppConfig {
    @Bean
    public UserService userService() {
        return new UserService();
    }
}

public static void main(String[] args) {
    AnnotationConfigApplicationContext context =
            new AnnotationConfigApplicationContext(AppConfig.class);
    UserService userService = context.getBean(UserService.class);
}
```

### Spring Boot 应用

```java
@SpringBootApplication // = @SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan
public class DemoApplication {
    public static void main(String[] args) {
        SpringApplication.run(DemoApplication.class, args);
    }
}
```

- 默认扫描 **启动类所在包及其子包**，因此通常把启动类放在项目根包。

------

## 4. 项目应用案例

- **黑马点评**
  - 启动类 `HmDianPingApplication` 上的 `@SpringBootApplication` 会自动扫描 `com.hmdp` 包下的所有组件（Controller、Service、Mapper）。
  - 例如 `ShopServiceImpl` 被 `@Service` 标注，启动时会被扫描并注册到 IOC 容器。
- **苍穹外卖**
  - 启动类 `SkyApplication` 上的 `@SpringBootApplication`，会扫描 `com.sky` 包下的 Bean。
  - Mapper 接口由 `@MapperScan` 单独扫描，注册到容器。

------

## 5. 面试标准回答（简洁版）

> Spring 通过 `ConfigurationClassPostProcessor` 解析 `@Configuration` 配置类，并通过 `@ComponentScan` 调用 `ClassPathBeanDefinitionScanner` 扫描指定包路径，把带有 `@Component`、`@Service`、`@Controller` 等注解的类解析成 BeanDefinition，注册到 IOC 容器中。Spring Boot 默认从启动类所在包及其子包扫描。

------

## 6. 扩展追问

1. Spring Boot 为什么推荐把启动类放在根包？
    → 因为 `@SpringBootApplication` 默认扫描当前包及子包，避免漏扫。
2. 如果有两个配置类，Spring 如何解析加载顺序？
    → 根据 `@Import`、`@Order` 或 `@DependsOn` 控制。
3. `@ComponentScan` 如何自定义过滤规则？
    → 使用 `includeFilters`、`excludeFilters` 参数。
4. Spring 是如何实现类路径扫描的？
    → 基于 ASM 字节码解析，读取类上的注解信息，而不是加载整个类。

------

要不要我接着帮你整理 **“FactoryBean 和普通 Bean 的区别”** 这一题？这样 IOC & Bean 管理这一块就差不多覆盖全了。