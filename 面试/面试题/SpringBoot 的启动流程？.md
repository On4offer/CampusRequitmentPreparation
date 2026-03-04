好 ✅，这道题是 **SpringBoot 源码级常考题**，我按照面试答题套路（概念 → 流程 → 项目结合 → 扩展追问）帮你整理成完整模板。

------

# 📌 面试题：SpringBoot 的启动流程是怎样的？从 `main` 方法到 IOC 容器初始化经历了哪些步骤？

### ✅ 一、概念回答

SpringBoot 应用的启动流程，本质是从 `main()` 方法调用 `SpringApplication.run()` 开始，最终完成 **Spring 容器的创建、Bean 的实例化与自动装配**。
 整个过程可以分为 **六大阶段**：

1. 创建 `SpringApplication` 对象
2. 准备运行环境（Environment）
3. 打印启动 Banner
4. 创建 IOC 容器（ApplicationContext）
5. 执行自动装配，完成 Bean 的加载与实例化
6. 调用 `CommandLineRunner` / `ApplicationRunner` 收尾

------

### ✅ 二、详细执行流程

1. **启动入口**

   ```java
   @SpringBootApplication
   public class DemoApplication {
       public static void main(String[] args) {
           SpringApplication.run(DemoApplication.class, args);
       }
   }
   ```

   - `@SpringBootApplication` 触发了自动装配逻辑（组合注解，含 `@EnableAutoConfiguration`）。

2. **创建 SpringApplication 对象**

   - 根据 classpath 推断是 **Servlet Web 应用**、**Reactive 应用** 还是 **普通应用**。
   - 加载初始化器（`ApplicationContextInitializer`）和监听器（`ApplicationListener`）。

3. **准备 Environment**

   - 读取并加载配置文件（`application.yml/properties`），
   - 合并系统属性、环境变量，形成 Environment。

4. **打印 Banner**

   - 控制台打印启动标志（可自定义关闭或修改）。

5. **创建 IOC 容器（ApplicationContext）**

   - 默认创建的是 `AnnotationConfigServletWebServerApplicationContext`（Web 项目）。
   - 触发 BeanDefinition 的扫描与加载。

6. **刷新容器（核心步骤）**

   - 调用 `refresh()`，完成：
     - BeanFactory 创建
     - BeanDefinition 解析
     - BeanPostProcessor 注册
     - **执行自动装配逻辑（@EnableAutoConfiguration → 读取 spring.factories → 加载 AutoConfiguration 类）**
     - 实例化所有单例 Bean
   - 启动内嵌 Web 容器（如 Tomcat）。

7. **执行收尾回调**

   - 调用所有实现了 `CommandLineRunner` 和 `ApplicationRunner` 的 Bean。
   - 标志应用启动完成。

------

### ✅ 三、结合项目经验

- 在 **黑马点评** 项目中，当我们运行 `java -jar` 启动时，SpringBoot 会自动完成：
  - 加载 `application.yml` 中的数据库和 Redis 配置
  - 自动装配 `DataSource`、`RedisTemplate` 等 Bean
  - 初始化内嵌 Tomcat 并绑定端口
- 我们只需要专注于业务逻辑，完全不需要手动配置容器和数据源，大大简化了启动流程。

------

### ✅ 四、扩展追问（可能会问）

1. SpringBoot 是如何推断创建 **哪种 ApplicationContext** 的？
2. `refresh()` 方法中做了哪些核心事情？
3. `@SpringBootApplication` 是如何实现的？
4. 自动装配过程在哪一步执行？
5. 如果我想在 IOC 初始化前后插入逻辑，可以用什么扩展点？（`ApplicationContextInitializer`、`ApplicationRunner`、`BeanFactoryPostProcessor`）

------

⚡ **标准回答模板（面试时可以这样答）：**

> SpringBoot 应用从 `main()` 方法开始调用 `SpringApplication.run()`，会依次完成：创建 SpringApplication 对象、准备 Environment、打印 Banner、创建 ApplicationContext、执行自动装配并加载 Bean、刷新容器、最后调用 Runner 接口收尾。
>  在这个过程中，核心点是 IOC 容器的刷新：SpringBoot 会读取 `spring.factories` 或 `AutoConfiguration.imports` 中的自动配置类，结合条件注解完成 Bean 的装配。比如我在黑马点评项目里，引入 MyBatis-Plus Starter 后，只需要在 yml 里配置数据源，SpringBoot 就会帮我自动装配 DataSource 和 SqlSessionFactory。

------

要不要我接着帮你把 **第四题：SpringBoot 如何实现多环境配置？配置文件优先级如何排序？** 也整理成这种标准模板？