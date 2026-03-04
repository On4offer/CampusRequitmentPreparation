# SpringBoot启动流程演示教学文档

## 目录

- [1. 项目概述](#1-项目概述)
  - [1.1 学习目标](#11-学习目标)
- [2. 项目结构详解](#2-项目结构详解)
- [3. SpringBoot启动流程详解](#3-springboot启动流程详解)
- [4. 关键组件详解](#4-关键组件详解)
  - [4.1 事件监听机制](#41-事件监听机制)
  - [4.2 自动装配机制](#42-自动装配机制)
  - [4.3 扩展点使用指南](#43-扩展点使用指南)
    - [4.3.1 ApplicationContextInitializer](#431-applicationcontextinitializer)
    - [4.3.2 BeanFactoryPostProcessor](#432-beanfactorypostprocessor)
    - [4.3.3 BeanPostProcessor](#433-beanpostprocessor)
  - [4.4 internalAutoProxyCreator Bean的产生机制](#44-internalautoproxycreator-bean的产生机制)
  - [4.5 CommandLineRunner/ApplicationRunner](#45-commandlinerunnerapplicationrunner)
- [5. 运行项目](#5-运行项目)
  - [5.1 前提条件](#51-前提条件)
  - [5.2 运行步骤](#52-运行步骤)
  - [5.3 验证应用启动](#53-验证应用启动)
- [6. 运行日志解析](#6-运行日志解析)
- [7. 常见面试题解析](#7-常见面试题解析)
  - [7.1 SpringBoot是如何推断创建哪种ApplicationContext的？](#71-springboot是如何推断创建哪种applicationcontext的)
  - [7.2 `refresh()`方法中做了哪些核心事情？](#72-refresh方法中做了哪些核心事情)
  - [7.3 自动装配过程在哪一步执行？](#73-自动装配过程在哪一步执行)
  - [7.4 为什么日志中会打印demoService、demoController等Bean的处理过程？](#74-为什么日志中会打印demoservicedemocontroller等bean的处理过程)
  - [7.5 为什么会打印CONDITIONS EVALUATION REPORT报告？](#75-为什么会打印conditions-evaluation-report报告)
  - [7.6 什么是internalAutoProxyCreator？它的产生机制是什么？](#76-什么是internalautoproxycreator它的产生机制是什么)
  - [7.7 CONDITIONS EVALUATION REPORT中的各分类含义](#77-conditions-evaluation-report中的各分类含义)
  - [7.8 Spring中Bean的生命周期是什么样的？](#78-spring中bean的生命周期是什么样的)
- [8. 扩展练习](#8-扩展练习)
- [9. 总结](#9-总结)

## 1. 项目概述

本项目是一个专注于演示SpringBoot启动流程的教学示例，旨在通过代码和日志输出，直观展示SpringBoot应用从`main`方法调用到IOC容器完全初始化的整个过程。通过学习本项目，您将深入理解SpringBoot的核心启动机制，为面试和实际开发奠定坚实基础。

### 1.1 学习目标

- 掌握SpringBoot启动的六大核心阶段
- 理解SpringBoot中的各种扩展点及其触发时机
- 深入理解自动装配（AutoConfiguration）机制
- 能够在实际项目中合理利用各个扩展点进行功能定制

## 2. 项目结构详解

本项目采用标准的Maven+SpringBoot架构，主要代码组织如下：

```
springboot-startup-demo
├── pom.xml                          # Maven配置文件
├── src/
│   ├── main/
│   │   ├── java/com/example/demo/
│   │   │   ├── SpringBootStartupDemoApplication.java   # 主应用类
│   │   │   ├── autoconfigure/      # 自动配置相关
│   │   │   │   └── DemoAutoConfiguration.java
│   │   │   ├── controller/         # REST控制器
│   │   │   │   └── DemoController.java
│   │   │   ├── initializer/        # 初始化器
│   │   │   │   └── DemoApplicationContextInitializer.java
│   │   │   ├── listener/           # 监听器
│   │   │   │   └── DemoApplicationListener.java
│   │   │   ├── processor/          # 处理器
│   │   │   │   ├── DemoBeanFactoryPostProcessor.java
│   │   │   │   └── DemoBeanPostProcessor.java
│   │   │   └── runner/             # 启动器回调
│   │   │       ├── DemoApplicationRunner.java
│   │   │       └── DemoCommandLineRunner.java
│   │   └── resources/
│   │       ├── META-INF/
│   │       │   └── spring.factories  # 自动配置声明
│   │       └── application.yml       # 应用配置
│   └── test/                       # 测试代码
│       └── java/com/example/demo/
│           └── SpringBootStartupDemoApplicationTests.java
```

## 4. SpringBoot启动流程详解

SpringBoot的启动流程可以分为以下六大核心阶段，每个阶段对应代码中的不同组件和扩展点：

### 4.1 阶段一：创建SpringApplication对象

**核心流程：**
1. 在`main`方法中调用`SpringApplication.run()`
2. 创建`SpringApplication`实例
3. 推断应用类型（Web/Reactive/普通）
4. 加载初始化器和监听器

**代码演示：**
```java
public static void main(String[] args) {
    System.out.println("[启动阶段1] ======== 开始SpringBoot应用启动流程 ========");
    ConfigurableApplicationContext context = SpringApplication.run(SpringBootStartupDemoApplication.class, args);
}
```

### 4.2 阶段二：准备运行环境（Environment）

**核心流程：**
1. 创建`ConfigurableEnvironment`对象
2. 加载配置信息（application.yml/properties）
3. 注册`ApplicationContextInitializer`实现类
4. 发布`ApplicationEnvironmentPreparedEvent`事件

**代码演示：** 通过`DemoApplicationContextInitializer`实现：
```java
public void initialize(ConfigurableApplicationContext applicationContext) {
    System.out.println("[启动阶段2] ======== ApplicationContextInitializer被调用 ========");
    ConfigurableEnvironment environment = applicationContext.getEnvironment();
    // 操作Environment...
}
```

### 4.3 阶段三：打印启动Banner

> 注：本项目通过`application.yml`中配置`banner-mode: off`关闭了默认Banner，以确保日志输出更清晰。

### 4.4 阶段四：创建IOC容器（ApplicationContext）

**核心流程：**
1. 根据应用类型创建相应的`ApplicationContext`实现
2. 准备`ApplicationContext`（设置Environment、注册BeanDefinition等）
3. 执行自动装配（加载`spring.factories`中的自动配置类）

**代码演示：** 通过`DemoBeanFactoryPostProcessor`和`DemoAutoConfiguration`实现：
```java
// BeanDefinitionRegistryPostProcessor
public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) {
    System.out.println("[启动阶段4] ======== BeanDefinitionRegistryPostProcessor被调用 ========");
    System.out.println("[启动阶段4] 当前已注册的BeanDefinition数量: " + registry.getBeanDefinitionCount());
}

// 自动配置类
static {
    System.out.println("[启动阶段4] ======== DemoAutoConfiguration被加载 ========");
    System.out.println("[启动阶段4] 此阶段演示了SpringBoot的自动装配机制");
}
```

### 4.5 阶段五：执行自动装配，完成Bean的加载与实例化

**核心流程：**
1. 调用`ApplicationContext.refresh()`方法
2. 创建BeanFactory
3. 注册BeanPostProcessor
4. 实例化所有单例Bean
5. 执行Bean初始化方法

**代码演示：** 通过`DemoBeanPostProcessor`实现：
```java
public Object postProcessBeforeInitialization(Object bean, String beanName) {
    if (beanName.startsWith("demo")) {
        System.out.println("[启动阶段5] BeanPostProcessor.postProcessBeforeInitialization: " + beanName);
    }
    return bean;
}
```

### 4.6 阶段六：调用CommandLineRunner/ApplicationRunner收尾

**核心流程：**
1. 容器刷新完成后，调用所有实现`CommandLineRunner`和`ApplicationRunner`接口的Bean
2. 发布`ApplicationStartedEvent`和`ApplicationReadyEvent`事件

**代码演示：** 通过`DemoCommandLineRunner`实现：
```java
public void run(String... args) throws Exception {
    System.out.println("[启动阶段6] ======== CommandLineRunner.run被调用 ========");
    System.out.println("[启动阶段6] 此阶段表示SpringBoot应用已经完成了IOC容器的初始化");
}
```

## 5. 关键组件详解

### 5.1 事件监听机制

SpringBoot使用事件机制在启动过程中的各个关键点进行通知，我们通过`DemoApplicationListener`监听并打印了所有主要事件：

- **ApplicationStartingEvent**：应用启动开始时触发
- **ApplicationEnvironmentPreparedEvent**：环境准备完成时触发
- **ApplicationContextInitializedEvent**：ApplicationContext初始化完成时触发
- **ApplicationPreparedEvent**：ApplicationContext准备完成时触发
- **ContextRefreshedEvent**：ApplicationContext刷新完成时触发
- **ApplicationStartedEvent**：Spring容器启动完成时触发
- **ApplicationReadyEvent**：应用准备就绪时触发

### 5.2 自动装配机制

自动装配是SpringBoot的核心特性，本项目通过以下组件演示其工作原理：

1. **DemoAutoConfiguration**：自定义的自动配置类，使用条件注解控制是否生效
2. **spring.factories**：声明自动配置类的位置，供`@EnableAutoConfiguration`扫描
3. **条件注解**：`@ConditionalOnProperty`控制自动配置的激活条件

### 5.3 扩展点使用指南

#### 5.3.1 ApplicationContextInitializer

**作用**：在`ApplicationContext`刷新之前进行初始化工作

**适用场景**：
- 需要在容器刷新前修改Environment配置
- 需要注册自定义的BeanFactoryPostProcessor
- 执行一些预先的系统设置

**使用方式**：
```java
// 1. 实现ApplicationContextInitializer接口
public class MyInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {
    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        // 执行初始化逻辑
    }
}

// 2. 在spring.factories中注册
org.springframework.context.ApplicationContextInitializer=
com.example.MyInitializer
```

#### 4.3.1 ApplicationContextInitializer

**作用**：在`ApplicationContext`刷新之前进行初始化工作

**适用场景**：
- 需要在容器刷新前修改Environment配置
- 需要注册自定义的BeanFactoryPostProcessor
- 执行一些预先的系统设置

**使用方式**：
```java
// 1. 实现ApplicationContextInitializer接口
public class MyInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {
    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        // 执行初始化逻辑
    }
}

// 2. 在spring.factories中注册
org.springframework.context.ApplicationContextInitializer=
com.example.MyInitializer
```

#### 4.3.2 BeanFactoryPostProcessor

**作用**：在Bean实例化之前对BeanDefinition进行修改

**适用场景**：
- 动态注册额外的BeanDefinition
- 修改现有BeanDefinition的属性
- 读取并处理特定类型的BeanDefinition

#### 4.3.3 BeanPostProcessor

**作用**：在Bean初始化前后对Bean实例进行处理

**适用场景**：
- 对Bean进行代理包装（如AOP）
- 在Bean初始化前后注入额外的依赖
- 对Bean的属性进行校验或修改

### 4.4 internalAutoProxyCreator Bean的产生机制

`internalAutoProxyCreator`是Spring AOP框架中的一个关键组件，用于实现切面代理功能。

**详细说明请参考[面试题部分：什么是internalAutoProxyCreator？它的产生机制是什么？](#76-什么是internalautoproxycreator它的产生机制是什么)**

#### 4.3.4 CommandLineRunner/ApplicationRunner

**作用**：应用启动完成后的回调

**适用场景**：
- 初始化数据
- 启动后台任务
- 执行一些需要在应用完全启动后进行的操作

## 5. 运行项目

### 5.1 前提条件

- JDK 1.8 或更高版本
- Maven 3.5 或更高版本
- IDE（推荐IntelliJ IDEA或Eclipse）

### 5.2 运行步骤

**方法一：使用IDE运行**

1. 导入Maven项目
2. 找到`SpringBootStartupDemoApplication`类
3. 右键点击并选择"Run"或"Debug"选项

**方法二：使用Maven命令运行**

```bash
cd springboot-startup-demo
mvn spring-boot:run
```

### 5.3 验证应用启动

1. 观察控制台输出，查看启动流程的各个阶段日志
2. 访问 http://localhost:8080/demo/status 查看应用状态页面

## 6. 运行日志解析

启动项目后，控制台会输出以下日志（按顺序）：

1. **启动阶段1**：`main`方法被调用，`SpringApplication`对象创建
2. **启动阶段2**：Environment准备完成，`ApplicationContextInitializer`被调用
3. **启动阶段3-4**：ApplicationContext创建，BeanDefinition加载，自动配置执行
4. **启动阶段5**：Bean实例化和初始化，BeanPostProcessor执行
5. **启动阶段6**：CommandLineRunner和ApplicationRunner执行
6. **启动阶段7**：应用启动完成

## 7. 常见面试题解析

### 7.1 SpringBoot是如何推断创建哪种ApplicationContext的？

在`SpringApplication`构造函数中，会根据classpath中是否存在特定类来推断应用类型：

- 如果存在`org.springframework.web.context.ConfigurableWebApplicationContext`，则为Web Servlet应用
- 如果存在`org.springframework.web.reactive.config.ConfigurableReactiveWebApplicationContext`，则为Reactive应用
- 否则，为普通应用

### 7.2 `refresh()`方法中做了哪些核心事情？

`refresh()`是Spring容器初始化的核心方法，主要完成以下工作：

1. 准备刷新上下文环境
2. 获取并准备BeanFactory
3. 加载BeanDefinition到BeanFactory
4. 注册BeanPostProcessor
5. 初始化事件处理器和监听器
6. 实例化所有非懒加载的单例Bean
7. 触发容器刷新完成事件

### 7.3 自动装配过程在哪一步执行？

自动装配主要在以下阶段执行：

1. 在`@SpringBootApplication`注解中包含的`@EnableAutoConfiguration`会触发自动装配
2. 在`ApplicationContext`创建并刷新过程中，会加载`spring.factories`中的自动配置类
3. 通过`@Conditional`相关注解进行条件过滤，只加载符合条件的配置类
4. 配置类中的`@Bean`方法会被执行，创建相应的Bean实例

### 7.4 为什么日志中会打印demoService、demoController等Bean的处理过程？

**问题现象**：启动日志中会打印类似 `[启动阶段5] BeanPostProcessor.postProcessBeforeInitialization: demoService` 这样的信息，但项目中似乎没有单独的service文件夹。

**解答**：

1. **demoService**：并不是在单独的service文件夹中定义的，而是作为`DemoAutoConfiguration`类的内部类实现的。在`com.example.demo.autoconfigure.DemoAutoConfiguration.java`文件中，通过`@Bean`注解方法`demoService()`将其注册到Spring容器中。这是Spring Boot自动配置的常见模式，可以在不创建单独文件的情况下定义服务类。

2. **demoController**：在`controller`包下的`DemoController.java`文件中定义，通过`@RestController`注解自动被Spring组件扫描并注册为Bean。

3. **demoApplicationRunner和demoCommandLineRunner**：分别在`runner`包下的`DemoApplicationRunner.java`和`DemoCommandLineRunner.java`文件中定义，通过实现相应接口并被Spring扫描注册。

4. **日志输出**：这些Bean在初始化过程中被`DemoBeanPostProcessor`拦截并记录日志，这就是为什么会在启动日志中看到这些Bean的处理记录。

这种设计展示了Spring Boot的自动配置和组件扫描机制的灵活性，可以通过不同方式注册Bean到IOC容器中，而不一定需要按照传统的目录结构组织代码。

### 7.5 为什么会打印CONDITIONS EVALUATION REPORT报告？

CONDITIONS EVALUATION REPORT（条件评估报告）是Spring Boot启动时输出的一份详细报告，用于展示所有自动配置类的条件评估结果。

#### 为什么会打印这个报告？

在项目的`application.yml`配置文件中，设置了Spring Boot框架日志为DEBUG级别：
```yaml
logging:
  level:
    org.springframework.boot: DEBUG
```

当`org.springframework.boot`包的日志级别设置为DEBUG或TRACE时，Spring Boot会自动输出CONDITIONS EVALUATION REPORT报告，显示：
- 哪些自动配置类成功匹配并被激活（Positive matches）
- 哪些自动配置类因为不满足条件被跳过（Negative matches）
- 每个条件评估的具体原因（如`@ConditionalOnProperty`匹配状态、`@ConditionalOnClass`类是否存在等）

#### 如何控制报告的输出？

1. **控制报告显示**：
   - 设置`org.springframework.boot: DEBUG` - 显示简要报告（只显示Positive matches）
   - 设置`org.springframework.boot: TRACE` - 显示完整报告（包括Positive和Negative matches）
   - 设置`org.springframework.boot: INFO`或更高级别 - 不显示报告

2. **通过启动参数控制**：
   ```
   --debug  # 启用DEBUG模式，显示条件评估报告
   --trace  # 启用TRACE模式，显示更详细的报告
   ```

3. **禁用特定自动配置类**：
   ```yaml
   spring:
     autoconfigure:
       exclude: org.springframework.boot.autoconfigure.aop.AopAutoConfiguration
   ```

#### 报告内容解析

报告中的每个匹配项都显示了详细的条件评估原因，例如：
- `@ConditionalOnProperty` - 显示属性名称和匹配状态
- `@ConditionalOnClass` - 显示需要存在或缺失的类
- `@ConditionalOnMissingBean` - 显示检查的Bean类型和查找策略

### 7.7 CONDITIONS EVALUATION REPORT中的各分类含义

#### 1. Positive matches（匹配成功）

表示这些自动配置类满足所有条件，已被Spring Boot成功激活并应用：

- **含义**：这些自动配置类的所有`@Conditional`相关条件都已满足
- **代表**：系统将加载这些配置类中定义的Bean和功能
- **示例**：如果项目中引入了Redis依赖，且没有禁用Redis自动配置，那么`RedisAutoConfiguration`会出现在这里

#### 2. Negative matches（匹配失败）

表示这些自动配置类因某些条件不满足而未被激活：

- **含义**：这些自动配置类至少有一个`@Conditional`条件未满足
- **代表**：系统不会加载这些配置类的功能，但它们仍然存在于类路径中
- **常见原因**：
  - `@ConditionalOnClass`：缺少必要的依赖类（如示例中的`javax.jms.ConnectionFactory`）
  - `@ConditionalOnMissingBean`：上下文中已存在指定类型的Bean
  - `@ConditionalOnProperty`：配置属性未设置或不满足条件
- **示例**：用户提到的`ActiveMQAutoConfiguration`未匹配是因为缺少JMS相关类

#### 3. Exclusions（排除项）

表示被显式排除的自动配置类：

- **含义**：这些自动配置类被通过配置显式排除，不会参与条件评估
- **代表**：用户不希望使用的特定自动配置
- **排除方式**：
  - 在`@SpringBootApplication`注解中使用`exclude`属性
  - 在配置文件中设置`spring.autoconfigure.exclude`

#### 4. Unconditional classes（无条件类）

表示不需要任何条件即可激活的自动配置类：

- **含义**：这些配置类没有任何`@Conditional`注解限制
- **代表**：Spring Boot核心功能，几乎在所有应用中都需要
- **示例**：
  - `ConfigurationPropertiesAutoConfiguration`：处理`@ConfigurationProperties`注解
  - `PropertyPlaceholderAutoConfiguration`：处理属性占位符
  - `LifecycleAutoConfiguration`：管理Bean生命周期

#### 其他相关分类

除了上述主要分类外，条件评估过程中还有：

1. **ConditionalOnWebApplication/ConditionalOnNotWebApplication**：根据应用是否为Web应用决定是否加载配置
2. **ConditionalOnJndi**：根据JNDI环境是否存在决定是否加载配置
3. **ConditionalOnResource**：根据指定资源是否存在决定是否加载配置
4. **ConditionalOnExpression**：根据SpEL表达式结果决定是否加载配置

这些条件注解共同构成了Spring Boot强大的自动配置机制，使得应用能够根据实际情况智能地加载所需功能。

这些信息对于理解Spring Boot自动配置机制和排查配置问题非常有帮助。

### 7.6 什么是internalAutoProxyCreator？它的产生机制是什么？

**问题**：在Spring Boot日志中常看到internalAutoProxyCreator相关信息，它是什么？如何产生的？

**解答**：

**1. internalAutoProxyCreator的概念**

`internalAutoProxyCreator`是Spring AOP框架自动注册的一个特殊Bean，其类型为`org.springframework.aop.framework.autoproxy.InfrastructureAdvisorAutoProxyCreator`，主要负责：

- **自动检测和识别**上下文中的Advisor、Advice和AspectJ切面
- **为符合条件的Bean创建代理对象**，实现AOP功能
- **处理代理的创建时机**，确保Bean在初始化后被正确代理

**2. 产生机制**

`internalAutoProxyCreator` Bean的产生主要由以下机制控制：

1. **自动配置触发**：
   - 当项目中引入了Spring AOP相关依赖时
   - Spring Boot的`AopAutoConfiguration`会被激活

2. **AOP自动配置逻辑**：
   ```java
   @Configuration
   @ConditionalOnClass({ EnableAspectJAutoProxy.class, Aspect.class, Advice.class })
   @ConditionalOnProperty(prefix = "spring.aop", name = "auto", havingValue = "true", matchIfMissing = true)
   public class AopAutoConfiguration {
       
       @Configuration
       @EnableAspectJAutoProxy(proxyTargetClass = false)
       @ConditionalOnProperty(prefix = "spring.aop", name = "proxy-target-class", havingValue = "false")
       public static class JdkDynamicAutoProxyConfiguration {}
       
       @Configuration
       @EnableAspectJAutoProxy(proxyTargetClass = true)
       @ConditionalOnProperty(prefix = "spring.aop", name = "proxy-target-class", havingValue = "true", matchIfMissing = true)
       public static class CglibAutoProxyConfiguration {}
   }
   ```

3. **代理类型选择**：
   - 可以通过配置`spring.aop.proxy-target-class`属性控制代理方式
   - `false`：使用JDK动态代理（默认，当目标类实现接口时）
   - `true`：使用CGLIB代理（当配置为true或目标类没有实现接口时）

**3. 重要性**

这个Bean是Spring AOP功能的核心基础设施，没有它，Spring AOP的切面功能将无法正常工作。它实现了透明代理，让开发者可以专注于切面逻辑而无需关心代理创建的复杂性。

### 7.8 Spring中Bean的生命周期是什么样的？除了自定义Bean，还有哪些常见的Bean类型？

#### Bean的完整生命周期

1. **实例化（Instantiation）**：通过构造器或工厂方法创建Bean实例
2. **属性赋值（Population）**：设置Bean的属性值和依赖关系
3. **初始化（Initialization）**：
   - 实现Aware接口的方法（如`BeanNameAware`、`BeanFactoryAware`、`ApplicationContextAware`）
   - `BeanPostProcessor.postProcessBeforeInitialization`方法调用
   - 自定义初始化方法（`@PostConstruct`注解方法、`init-method`配置方法）
   - `BeanPostProcessor.postProcessAfterInitialization`方法调用
4. **使用（In Use）**：Bean实例可以被应用程序使用
5. **销毁（Destruction）**：
   - 自定义销毁方法（`@PreDestroy`注解方法、`destroy-method`配置方法）
   - 实现`DisposableBean`接口的`destroy()`方法

#### 常见的Bean类型

除了自定义Bean外，Spring应用中还有以下常见Bean类型：

1. **Spring框架内置Bean**：
   - `beanFactory`：Bean工厂，负责Bean的创建和管理
   - `applicationContext`：应用上下文，提供更多企业级功能
   - `environment`：环境对象，管理配置属性
   - `resourceLoader`：资源加载器，用于加载各种资源文件

2. **Spring Boot自动配置Bean**：
   - 数据源相关（如`dataSource`、`transactionManager`）
   - Web相关（如`dispatcherServlet`、`viewResolver`）
   - 安全相关（如`authenticationManager`、`userDetailsService`）
   - 日志相关（如`logback`或`log4j`的配置Bean）

3. **第三方库提供的Bean**：
   - 数据库连接池（如`hikariDataSource`）
   - ORM框架（如`entityManagerFactory`）
   - 缓存框架（如`cacheManager`）
   - 消息队列（如`rabbitTemplate`、`kafkaTemplate`）

#### 为什么DemoBeanPostProcessor只打印了部分Bean？

在本项目中，`DemoBeanPostProcessor`只打印了名称以`demo`开头的Bean和特定名称的Bean，这是因为在其实现中添加了条件过滤：
```java
if (beanName.startsWith("demo") || beanName.equals("demoApplicationListener") ||
    beanName.equals("demoBeanFactoryPostProcessor")) {
    // 打印日志
}
```

这种设计是为了避免产生过多日志输出，让开发者只关注项目中自定义的demo组件的初始化过程。

## 8. 扩展练习

1. **自定义条件注解**：创建一个自定义的条件注解，用于控制Bean的创建
2. **动态注册Bean**：在`BeanDefinitionRegistryPostProcessor`中动态注册一个Bean
3. **修改Banner**：自定义一个Banner替换默认的SpringBoot Banner
4. **多环境配置**：创建`application-dev.yml`和`application-prod.yml`，演示多环境配置切换

## 9. 总结

通过本项目的学习，您应该能够清晰地理解SpringBoot应用从启动到运行的完整流程，掌握各个扩展点的使用场景和触发时机，这对于深入理解SpringBoot原理以及应对相关面试问题都有很大帮助。

SpringBoot的启动流程虽然复杂，但通过合理利用各种扩展点，我们可以在不同的阶段对其进行定制和扩展，从而满足各种复杂业务场景的需求。