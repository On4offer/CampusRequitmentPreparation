# SpringBoot自动装配原理演示项目（小白友好版）

## 一、这是什么？

**简单来说**：这是一个教学用的小项目，专门给初学者解释SpringBoot是如何"自动"帮我们配置各种功能的。

**打个比方**：想象你开一家餐厅，SpringBoot就像是一个聪明的管家，会自动帮你准备好桌椅、餐具、调料等。而我们这个项目就是想让你看看这个管家是怎么工作的。

## 二、为什么要学这个？

- SpringBoot是目前Java开发中最流行的框架之一
- 了解"自动装配"能让你真正搞懂SpringBoot的核心秘密
- 以后你也可以自己开发一些"自动配置"的工具，让其他开发者用起来更方便

## 三、【重要】自定义Starter在哪里？

**注意**：在这个项目中，`my-custom-starter/` 文件夹里的所有内容都是自定义的Starter！这是我们要重点学习的部分！

## 四、项目文件详细说明

### 📁 主项目文件（springboot-autoconfig-demo/）
- `src/main/java/com/example/SpringBootAutoConfigDemoApplication.java` - 应用启动类（主入口）
- `src/main/java/com/example/controller/AutoconfigDemoController.java` - 测试控制器（用于验证Starter功能）
- `application.yml` - 应用配置文件（可以在这里配置我们的自定义Starter）
- `pom.xml` - Maven配置文件（主项目依赖管理）

### 🔴 自定义Starter文件（my-custom-starter/）【重点！】
- `src/main/java/com/example/mycustom/MyCustomProperties.java` - 配置属性类
  - **作用**：接收application.yml中的配置值
  - **核心注解**：`@ConfigurationProperties(prefix = "my-custom")`
  - **可配置项**：message（消息内容）、timeout（超时时间）、enabled（是否启用）

- `src/main/java/com/example/mycustom/MyCustomService.java` - 核心服务类
  - **作用**：实现实际业务逻辑的类
  - **主要方法**：process(String input) - 处理输入内容
  - **依赖**：依赖MyCustomProperties获取配置信息

- `src/main/java/com/example/mycustom/MyCustomAutoConfiguration.java` - 自动配置类
  - **作用**：告诉SpringBoot如何装配这些组件
  - **核心注解**：`@Configuration`、`@EnableConfigurationProperties`、`@ConditionalOnClass`等
  - **核心方法**：`myCustomService()` - 创建服务实例的Bean方法

- `src/main/resources/META-INF/spring.factories` - 自动装配注册文件
  - **作用**：让SpringBoot能找到我们的自动配置类
  - **关键配置**：`org.springframework.boot.autoconfigure.EnableAutoConfiguration=...`

- `pom.xml` - Starter的Maven配置
  - **依赖**：spring-boot-autoconfigure、spring-boot-configuration-processor

## 五、你能学到什么？

1. SpringBoot是如何自动识别并加载各种配置的
2. 如何自己创建一个可以被SpringBoot自动识别的功能模块
3. 如何控制哪些配置需要加载、哪些不需要加载
4. 如何修改配置让功能按我们的需求工作

## 六、从零开始的步骤（适合小白）

### 第一步：先检查你的电脑是否准备好了

你需要先安装：
- JDK 8或更高版本（Java开发环境）
- Maven（项目管理工具）
- 一个IDE（比如IntelliJ IDEA、Eclipse等）

不明白怎么安装？看看这个文件：[COMPILATION_RUN_GUIDE.md](COMPILATION_RUN_GUIDE.md)

## 七、【超详细】如何自己写一个自定义Starter？

### 第1步：创建Maven项目（Starter项目）
1. 使用IDE创建一个新的Maven项目，命名格式通常为`xxx-spring-boot-starter`
2. 在pom.xml中添加必要的依赖：

```xml
<parent>
    <groupId>org.springframework.boot</groupId>
    <artifactId>spring-boot-starter-parent</artifactId>
    <version>2.7.15</version>
</parent>

<dependencies>
    <!-- Spring Boot自动配置核心依赖 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-autoconfigure</artifactId>
    </dependency>
    <!-- 配置处理器，用于生成元数据 -->
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-configuration-processor</artifactId>
        <optional>true</optional>
    </dependency>
</dependencies>
```

### 第2步：创建配置属性类
1. 创建一个类，用于接收application.yml中的配置
2. 示例代码：

```java
import org.springframework.boot.context.properties.ConfigurationProperties;

@ConfigurationProperties(prefix = "my-starter") // 配置前缀
public class MyStarterProperties {
    // 默认值
    private String message = "Hello from my starter";
    private int timeout = 5000;
    private boolean enabled = true;
    
    // Getters and Setters
    public String getMessage() {
        return message;
    }
    public void setMessage(String message) {
        this.message = message;
    }
    public int getTimeout() {
        return timeout;
    }
    public void setTimeout(int timeout) {
        this.timeout = timeout;
    }
    public boolean isEnabled() {
        return enabled;
    }
    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }
}
```

### 第3步：创建服务类
1. 创建一个核心服务类，实现你的业务逻辑
2. 示例代码：

```java
public class MyStarterService {
    private final MyStarterProperties properties;
    
    // 构造函数注入配置属性
    public MyStarterService(MyStarterProperties properties) {
        this.properties = properties;
    }
    
    // 业务方法
    public String doSomething(String input) {
        return "[" + properties.getMessage() + "] Processing: " + input;
    }
}
```

### 第4步：创建自动配置类
1. 这是最重要的一步，告诉SpringBoot如何装配你的组件
2. 示例代码：

```java
import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration // 标记为配置类
@EnableConfigurationProperties(MyStarterProperties.class) // 启用配置属性
@ConditionalOnClass(MyStarterService.class) // 当类路径中有MyStarterService类时生效
@ConditionalOnProperty(prefix = "my-starter", name = "enabled", havingValue = "true", matchIfMissing = true)
public class MyStarterAutoConfiguration {
    
    private final MyStarterProperties properties;
    
    // 构造函数注入配置属性
    public MyStarterAutoConfiguration(MyStarterProperties properties) {
        this.properties = properties;
    }
    
    // 提供Bean实例
    @Bean
    @ConditionalOnMissingBean // 当容器中没有MyStarterService Bean时才创建
    public MyStarterService myStarterService() {
        return new MyStarterService(properties);
    }
}
```

### 第5步：创建spring.factories文件
1. 在resources目录下创建META-INF文件夹
2. 在META-INF文件夹中创建spring.factories文件
3. 添加以下内容：

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=
com.yourpackage.MyStarterAutoConfiguration
```

### 第6步：编译安装
1. 执行`mvn clean install`命令
2. 这会将你的Starter安装到本地Maven仓库

### 第7步：在其他项目中使用
1. 在另一个SpringBoot项目的pom.xml中添加依赖：

```xml
<dependency>
    <groupId>your-group-id</groupId>
    <artifactId>your-starter-artifact-id</artifactId>
    <version>your-version</version>
</dependency>
```

2. 在application.yml中配置：

```yaml
my-starter:
  message: 你好，这是我的自定义配置
  timeout: 3000
```

3. 在代码中注入使用：

```java
@RestController
public class TestController {
    
    @Autowired
    private MyStarterService myStarterService;
    
    @GetMapping("/test")
    public String test() {
        return myStarterService.doSomething("hello");
    }
}
```

### 关键点总结
1. **配置属性类**：使用`@ConfigurationProperties`接收配置
2. **自动配置类**：使用`@Configuration`和条件注解控制装配
3. **spring.factories**：这是SpringBoot找到你的自动配置的关键
4. **条件装配**：使用`@ConditionalOnXxx`注解控制什么条件下装配

## 八、如何运行这个演示项目？

### 第1步：编译并安装自定义Starter

1. 打开命令行工具（Windows上是cmd或PowerShell）
2. 进入项目目录：`cd d:\Java学习\demo\springboot-autoconfig-demo`
3. 进入自定义Starter目录：`cd my-custom-starter`
4. 执行编译命令：`mvn clean install`

这一步会把我们自定义的功能模块安装到本地仓库，让主应用能找到它。

### 第2步：运行主应用

1. 回到主项目目录：`cd ..`
2. 运行应用：`mvn spring-boot:run`

等待一会儿，看到类似"Started SpringBootAutoConfigDemoApplication..."的消息，就说明应用启动成功了！

### 第3步：测试功能

打开浏览器，输入下面的地址，看看会发生什么：

1. `http://localhost:8080/test` - 测试自动装配是否成功
2. `http://localhost:8080/do/hello` - 测试服务功能是否正常
3. `http://localhost:8080/info` - 查看应用信息

## 九、动手实验（超有趣！）

### 实验1：关闭自动装配

1. 找到`application.yml`文件
2. 添加以下内容：

```yaml
my-custom:
  enabled: false
```
3. 重启应用，再次访问`/test`接口，看看有什么变化

### 实验2：修改配置信息

1. 在`application.yml`中添加：

```yaml
my-custom:
  message: 你好，SpringBoot！
  timeout: 3000
```
2. 重启应用，访问`/test`接口，看看返回的消息是否变了

### 实验3：自己创建一个Bean来覆盖自动配置

1. 打开`SpringBootAutoConfigDemoApplication.java`文件
2. 在main方法下面添加这段代码：

```java
@Bean
public MyCustomService myCustomService() {
    MyCustomProperties properties = new MyCustomProperties();
    properties.setMessage("这是我自定义的Bean！");
    return new MyCustomService(properties);
}
```
3. 别忘了在文件顶部添加导入语句：

```java
import com.example.mycustom.MyCustomProperties;
import com.example.mycustom.MyCustomService;
import org.springframework.context.annotation.Bean;
```
4. 重启应用，访问`/test`接口，看看效果

## 十、几个重要概念（用大白话解释）

### 1. 什么是自动装配？

自动装配就是SpringBoot帮你自动创建对象、设置属性、管理依赖关系的过程，让你不需要写大量的配置代码。

### 2. 什么是Starter？

Starter就像是一个功能包，把一组相关的功能和配置打包在一起，让你只需要引入一个依赖就能使用全部功能。

### 3. spring.factories文件是干嘛的？

这个文件就像是一个注册表，告诉SpringBoot："嘿，我这里有个自动配置类，快来看看吧！"

### 4. 条件注解有什么用？

条件注解就像是"如果...那么..."的规则，比如：
- "如果类路径中有某个类，那么就加载这个配置"
- "如果配置文件中设置了某个属性为true，那么就启动这个功能"

## 十一、遇到问题怎么办？

1. 仔细看错误信息，通常错误信息会告诉你哪里出了问题
2. 检查`COMPILATION_RUN_GUIDE.md`文件，里面有常见问题的解决方法
3. 确保你的JDK和Maven版本符合要求
4. 如果还是解决不了，可以找有经验的朋友帮忙看看

## 十二、更多学习资源

- [SpringBoot_Autoconfig_Principle.md](SpringBoot_Autoconfig_Principle.md) - 更详细的原理说明
- [COMPILATION_RUN_GUIDE.md](COMPILATION_RUN_GUIDE.md) - 编译运行的详细指南

## 十四、如何使用和共享我们的自定义Starter？

### 第1步：安装Starter到本地仓库

如果还没有安装，请先执行以下命令：

```bash
cd d:\Java学习\demo\springboot-autoconfig-demo\my-custom-starter
mvn clean install
```

这会将我们的自定义Starter打包并安装到你的本地Maven仓库中。

### 第2步：在其他SpringBoot项目中使用

要在其他SpringBoot项目中使用我们的自定义Starter，只需以下几步：

#### 1. 添加依赖

在其他项目的`pom.xml`文件中添加以下依赖：

```xml
<dependency>
    <groupId>com.example</groupId>
    <artifactId>my-custom-starter</artifactId>
    <version>1.0-SNAPSHOT</version>
</dependency>
```

#### 2. 配置Starter参数

在项目的`application.yml`或`application.properties`文件中添加配置：

```yaml
my-custom:
  message: 这是自定义的消息  # 可选，默认为"Hello from Custom Starter!"
  timeout: 3000            # 可选，默认5000毫秒
  enabled: true           # 可选，默认为true，设为false可禁用此Starter
```

#### 3. 在代码中使用

在你的SpringBoot应用中，直接注入并使用我们的服务：

```java
import com.example.mycustom.MyCustomService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class YourController {
    
    @Autowired  // 自动注入我们的服务
    private MyCustomService myCustomService;
    
    @GetMapping("/test-custom-starter")
    public String test() {
        // 使用我们的服务处理数据
        return myCustomService.process("Hello from another project!");
    }
}
```

### 第3步：共享给其他开发者（进阶）

如果你想让团队里的其他人也能使用你的Starter，可以：

1. **部署到远程Maven仓库**：
   - 配置Maven的settings.xml添加仓库信息
   - 执行`mvn clean deploy`命令部署

2. **上传到公共仓库**：
   - 如Maven中央仓库（需要申请账号）
   - 或使用公司内部的Nexus等仓库管理系统

3. **直接分享jar包**：
   - 可以在`my-custom-starter/target`目录找到生成的jar文件
   - 将jar文件分享给其他人，他们可以通过`mvn install:install-file`命令安装到本地仓库

### 提示

- 记得在使用前检查依赖是否正确引入
- 如果遇到自动装配失败的问题，检查配置是否正确
- 可以在应用启动时添加`--debug`参数，查看自动装配的详细日志

## 十五、写在最后

学习编程最重要的就是动手实践！不要只是看代码，一定要自己试着运行、修改、实验。

这个项目虽然简单，但包含了SpringBoot自动装配的核心思想。搞懂了这个，你对SpringBoot的理解就会上一个大台阶！

祝你学习顺利！
