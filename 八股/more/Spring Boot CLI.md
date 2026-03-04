### Spring Boot CLI

Spring Boot CLI（Command Line Interface）是一个命令行工具，允许开发者使用Groovy脚本编写和运行Spring Boot应用。Spring Boot CLI使得开发者能够快速原型化和开发Spring Boot应用，无需复杂的构建和打包过程。通过CLI，开发者可以更快速地启动应用、编写和测试Spring Boot应用程序。

Spring Boot CLI的一个显著特点是它支持使用Groovy编写Spring Boot应用，这让开发者能够利用脚本语言快速进行开发和测试，而不需要编译代码。

### 1. **Spring Boot CLI的安装**

#### 1.1 使用SDKMAN安装

SDKMAN是一个多平台的工具，用于管理JVM相关的工具（如Java、Groovy、Maven、Gradle等）。你可以通过SDKMAN来安装Spring Boot CLI。

1. 安装SDKMAN：

   ```bash
   curl -s "https://get.sdkman.io" | bash
   ```

2. 安装Spring Boot CLI：

   ```bash
   sdk install springboot
   ```

3. 验证安装：

   ```bash
   spring --version
   ```

#### 1.2 使用Homebrew（macOS）

如果你使用macOS，可以通过Homebrew安装Spring Boot CLI：

```bash
brew install spring-boot-cli
```

#### 1.3 手动下载

你也可以从[Spring官网](https://spring.io/tools)下载Spring Boot CLI的二进制文件并安装。

### 2. **使用Spring Boot CLI开发应用**

一旦安装了Spring Boot CLI，你可以使用Groovy脚本来创建Spring Boot应用。CLI提供了一些非常有用的功能，比如快速启动Spring Boot应用、集成Spring框架组件、使用Spring Boot特性进行开发。

#### 2.1 创建一个简单的Spring Boot应用

你可以通过以下步骤使用Spring Boot CLI快速创建和运行一个简单的应用。

1. **创建Groovy文件**

创建一个`demo.groovy`文件，内容如下：

```groovy
@RestController
class HelloController {
    @RequestMapping("/")
    String home() {
        return "Hello, Spring Boot CLI!"
    }
}
```

这个文件通过Groovy的注解创建了一个简单的REST控制器，并通过Spring Boot CLI注入了Spring Boot所需的组件。

1. **运行Groovy文件**

使用以下命令运行Spring Boot CLI应用：

```bash
spring run demo.groovy
```

运行后，Spring Boot CLI会自动启动一个内嵌的Tomcat服务器，并监听默认的端口（8080）。你可以访问`http://localhost:8080`来查看输出内容`Hello, Spring Boot CLI!`。

#### 2.2 使用Spring Boot CLI创建项目

Spring Boot CLI也可以用来创建完整的Spring Boot项目。你可以使用`spring init`命令来初始化一个新的Spring Boot项目。

```bash
spring init --dependencies=web my-spring-boot-app
```

这会创建一个名为`my-spring-boot-app`的新项目，并自动包括Web依赖（例如Spring Web）。项目目录结构如下：

```
my-spring-boot-app
 └── src
     └── main
         ├── java
         └── resources
             └── application.properties
 └── pom.xml
 └── ...
```

你可以进入该目录，执行`mvn spring-boot:run`来启动项目。

#### 2.3 通过CLI启动应用

Spring Boot CLI也允许你直接运行已构建的Spring Boot项目。例如，你可以在项目根目录下使用以下命令来运行应用：

```bash
spring run my-spring-boot-app.groovy
```

Spring Boot CLI会自动启动你的应用，并提供开发所需的自动化流程。

### 3. **Spring Boot CLI常用命令**

- **`spring run`**: 运行一个Groovy脚本，启动Spring Boot应用。

  ```bash
  spring run <file.groovy>
  ```

- **`spring init`**: 初始化一个新的Spring Boot项目。可以指定依赖、项目类型等选项。

  ```bash
  spring init --dependencies=web,actuator my-app
  ```

- **`spring jar`**: 将Spring Boot应用打包为JAR文件。

  ```bash
  spring jar my-app.jar <file.groovy>
  ```

- **`spring help`**: 显示Spring Boot CLI的帮助信息。

  ```bash
  spring help
  ```

- **`spring version`**: 显示Spring Boot CLI的版本。

  ```bash
  spring --version
  ```

### 4. **使用Spring Boot CLI开发的优势**

#### 4.1 快速原型开发

Spring Boot CLI支持通过Groovy脚本快速开发和测试Spring Boot应用。由于Groovy是一种动态语言，开发者无需编译代码，可以在命令行上直接编写并执行代码，从而快速实现功能原型。

#### 4.2 提高开发效率

Spring Boot CLI使得开发者能够快速启动和运行Spring Boot应用，无需繁琐的构建、编译和部署流程。这对于开发和测试阶段尤其有帮助，开发者可以立即查看更改的效果。

#### 4.3 简化集成

CLI工具内置了Spring Boot和Spring Framework的所有功能，开发者可以轻松地集成Spring相关的功能（如Web、Data、Security等），并在脚本中使用这些功能。

#### 4.4 简化构建

Spring Boot CLI支持直接运行Groovy脚本，而不需要额外的构建工具，如Maven或Gradle。这使得开发过程更加简单和直接。

### 5. **总结**

Spring Boot CLI是一个非常有用的工具，适用于快速原型开发和开发阶段的测试。它通过支持Groovy脚本和命令行工具，使得开发者能够以更加简便和快速的方式开发和运行Spring Boot应用。CLI支持的功能包括项目初始化、快速启动、简化构建等，特别适用于快速原型开发和短期内的开发任务。