# 编译和运行指南

由于当前环境没有安装Maven，本指南将帮助您在自己的环境中完成SpringBoot自动装配演示项目的编译和运行。

## 一、环境准备

### 1. 安装JDK

确保您的系统已安装JDK 8或更高版本：

```bash
# 检查JDK版本
java -version
```

输出示例：
```
java version "1.8.0_301"
Java(TM) SE Runtime Environment (build 1.8.0_301-b09)
Java HotSpot(TM) 64-Bit Server VM (build 25.301-b09, mixed mode)
```

### 2. 安装Maven

下载并安装Maven：

1. 从[Maven官网](https://maven.apache.org/download.cgi)下载最新版本的Maven
2. 解压到本地目录
3. 配置环境变量：
   - 添加`MAVEN_HOME`：指向Maven的安装目录
   - 将`%MAVEN_HOME%\bin`添加到`PATH`环境变量

验证Maven安装：

```bash
mvn -version
```

输出示例：
```
Apache Maven 3.8.6 (84538c9988a25aec085021c365c560670ad80f63)
Maven home: D:\apache-maven-3.8.6
Java version: 1.8.0_301, vendor: Oracle Corporation, runtime: C:\Program Files\Java\jdk1.8.0_301\jre
Default locale: zh_CN, platform encoding: GBK
OS name: "windows 10", version: "10.0", arch: "amd64", family: "windows"
```

## 二、编译和安装自定义Starter

### 1. 进入自定义Starter目录

```bash
cd d:/Java学习/demo/springboot-autoconfig-demo/my-custom-starter
```

### 2. 编译并安装到本地Maven仓库

```bash
mvn clean install
```

输出示例（成功安装）：
```
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  3.256 s
[INFO] Finished at: 2023-12-15T10:00:00+08:00
[INFO] ------------------------------------------------------------------------
```

## 三、运行主应用

### 1. 返回主应用目录

```bash
cd d:/Java学习/demo/springboot-autoconfig-demo
```

### 2. 编译并运行SpringBoot应用

```bash
mvn spring-boot:run
```

或者使用IDE运行主类：`SpringBootAutoConfigDemoApplication`

输出示例（成功启动）：
```
.   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
 :: Spring Boot ::                (v2.7.15)

2023-12-15 10:00:00.000  INFO 12345 --- [           main] c.e.SpringBootAutoConfigDemoApplication  : Starting SpringBootAutoConfigDemoApplication using Java 1.8.0_301 on DESKTOP-ABCDEF with PID 12345
2023-12-15 10:00:00.000  INFO 12345 --- [           main] c.e.SpringBootAutoConfigDemoApplication  : No active profile set, falling back to 1 default profile: "default"
2023-12-15 10:00:00.000 DEBUG 12345 --- [           main] o.s.b.a.AutoConfigurationImportSelector  : Loaded 111 auto configuration classes from location class path resource [META-INF/spring.factories]
2023-12-15 10:00:00.000 DEBUG 12345 --- [           main] o.s.b.a.AutoConfigurationImportSelector  : Filtered 111 auto configuration classes to 111
2023-12-15 10:00:00.000 DEBUG 12345 --- [           main] o.s.b.a.AutoConfigurationImportSelector  : Successfully resolved 111 auto configuration class names
2023-12-15 10:00:00.000 DEBUG 12345 --- [           main] o.s.b.a.AutoConfigurationImportSelector  : Selected 111 auto configuration classes
=== MyCustomAutoConfiguration初始化 ===
配置属性: MyCustomProperties{enabled=true, message='Hello from Custom Starter!', timeout=5000}
=== 创建MyCustomService Bean ===
2023-12-15 10:00:00.000  INFO 12345 --- [           main] c.e.SpringBootAutoConfigDemoApplication  : Started SpringBootAutoConfigDemoApplication in 1.234 seconds (JVM running for 2.345)

=== SpringBoot自动装配演示应用启动成功 ===
应用名称: springboot-autoconfig-demo
应用端口: 8080
=== 自动装配的Bean列表（部分） ===
  - org.springframework.boot.autoconfigure.internalCachingMetadataReaderFactory
  - org.springframework.boot.autoconfigure.web.servlet.WebMvcAutoConfiguration$EnableWebMvcConfiguration
  - myCustomService
```

## 四、测试API接口

### 1. 测试自动装配的服务

```bash
curl http://localhost:8080/test
```

输出示例：
```
自动装配演示：Hello from Custom Starter!
```

### 2. 测试自动装配服务的功能

```bash
curl http://localhost:8080/do/hello
```

输出示例：
```
[Hello from Custom Starter!] Processing 'hello' with timeout 5000ms
```

### 3. 获取应用的自动装配信息

```bash
curl http://localhost:8080/info
```

输出示例：
```
SpringBoot自动装配演示应用
- 使用自定义Starter演示自动装配原理
- 通过@SpringBootApplication开启自动装配
- 支持通过application.yml配置自定义服务
- 支持通过@Conditional注解控制装配条件
```

## 五、常见问题解决

### 1. Maven命令未找到

**问题**：`mvn : 无法将“mvn”项识别为 cmdlet、函数、脚本文件或可运行程序的名称。`

**解决方法**：确保已正确安装Maven并将其添加到环境变量中。

### 2. 自定义Starter依赖无法解析

**问题**：`Could not find artifact com.example:my-custom-starter:jar:1.0-SNAPSHOT`

**解决方法**：确保已成功安装自定义Starter到本地Maven仓库。

### 3. 应用启动失败

**问题**：应用启动时出现错误。

**解决方法**：检查应用配置和依赖是否正确，查看日志输出定位问题。

### 4. API接口无法访问

**问题**：`curl: (7) Failed to connect to localhost port 8080: Connection refused`

**解决方法**：确保应用已成功启动，检查端口是否被占用。

## 六、手动编译替代方案

如果没有Maven环境，可以使用IDE（如IntelliJ IDEA、Eclipse）来编译和运行项目：

### 1. 使用IntelliJ IDEA

1. 打开项目目录：`d:/Java学习/demo/springboot-autoconfig-demo`
2. 等待IDEA导入Maven项目
3. 右键点击`my-custom-starter`模块，选择`Maven` -> `Install`
4. 右键点击`SpringBootAutoConfigDemoApplication`类，选择`Run 'SpringBootAutoConfigDemoApplication'`

### 2. 使用Eclipse

1. 导入项目：`File` -> `Import` -> `Existing Maven Projects`
2. 选择项目目录：`d:/Java学习/demo/springboot-autoconfig-demo`
3. 等待Eclipse导入项目
4. 右键点击`my-custom-starter`模块，选择`Run As` -> `Maven install`
5. 右键点击`SpringBootAutoConfigDemoApplication`类，选择`Run As` -> `Java Application`

## 七、代码验证

即使没有运行环境，您仍然可以通过阅读代码来验证自动装配的工作原理：

1. 查看`SpringBootAutoConfigDemoApplication.java`中的`@SpringBootApplication`注解
2. 查看`MyCustomAutoConfiguration.java`中的条件注解和`@Bean`方法
3. 查看`MyCustomProperties.java`中的`@ConfigurationProperties`注解
4. 查看`META-INF/spring.factories`文件的配置
5. 查看`application.yml`中的配置项

通过阅读这些代码，您可以深入理解SpringBoot自动装配的工作原理，而无需实际运行项目。

## 八、总结

本指南提供了在本地环境中编译和运行SpringBoot自动装配演示项目的详细步骤：

1. 环境准备：安装JDK和Maven
2. 编译和安装自定义Starter
3. 运行SpringBoot应用
4. 测试API接口
5. 解决常见问题
6. 使用IDE编译和运行的替代方案

希望本指南能够帮助您顺利完成项目的编译和运行，深入理解SpringBoot自动装配的工作原理！