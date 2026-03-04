### Spring Boot的内嵌Web服务器

Spring Boot内嵌Web服务器是Spring Boot框架的重要特性之一，它使得开发者能够以非常简便的方式将Web应用打包为一个独立的可执行JAR或WAR文件，而无需依赖外部的Web服务器（如Tomcat、Jetty或Undertow等）。这种内嵌方式不仅简化了部署流程，也方便了开发和调试。

#### 1. **简介**

Spring Boot默认提供了对多种常见Web服务器的支持，如Tomcat、Jetty和Undertow。通过内嵌Web服务器，Spring Boot应用不再依赖传统的WAR包部署，而是可以直接以JAR包运行，具有独立的Web服务器。

- **默认Web服务器**：Spring Boot的默认内嵌Web服务器是Tomcat。
- **其他支持的Web服务器**：除了Tomcat，还可以使用Jetty和Undertow，开发者可以通过修改依赖来选择不同的Web服务器。

#### 2. **底层实现**

Spring Boot内嵌Web服务器的实现是通过自动配置（Auto Configuration）和Spring的`EmbeddedServletContainer`（嵌入式Servlet容器）来完成的。Spring Boot会根据项目的依赖来自动选择合适的Web服务器并进行配置。

1. **自动配置**： Spring Boot通过`spring-boot-starter-web`或`spring-boot-starter-webflux`等起始器（Starter）来启动Web应用。如果没有特别配置，它会自动根据依赖选择适合的Web服务器（如Tomcat）。
2. **嵌入式Servlet容器**：
   - 在应用启动时，Spring Boot会自动加载嵌入式Web服务器（如Tomcat、Jetty或Undertow），并初始化相应的Servlet容器。
   - 这些服务器都以Java应用的形式嵌入到JAR包中，因此无需外部容器。
3. **启动流程**：
   - `SpringApplication.run()`方法启动应用时，会启动内嵌的Web服务器。
   - 该服务器会自动监听默认端口（通常是8080），并将请求路由到Spring的`DispatcherServlet`进行处理。
4. **配置项**： Spring Boot允许开发者通过`application.properties`或`application.yml`文件配置内嵌服务器的相关属性，如端口、上下文路径、服务器头等。

#### 3. **内嵌Web服务器的选择与切换**

通过修改依赖，可以选择不同的Web服务器。例如，Spring Boot的默认Web服务器是Tomcat，但可以轻松切换为Jetty或Undertow。

- **使用Tomcat**（默认）： 默认情况下，Spring Boot会引入`spring-boot-starter-web`，它包含Tomcat的依赖。

  ```xml
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
  </dependency>
  ```

- **切换为Jetty**： 如果希望使用Jetty替代Tomcat，可以排除Tomcat的依赖并引入Jetty。

  ```xml
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
      <exclusions>
          <exclusion>
              <groupId>org.springframework.boot</groupId>
              <artifactId>spring-boot-starter-tomcat</artifactId>
          </exclusion>
      </exclusions>
  </dependency>
  
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-jetty</artifactId>
  </dependency>
  ```

- **切换为Undertow**： 如果选择Undertow作为Web服务器，可以按如下方式配置：

  ```xml
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-web</artifactId>
      <exclusions>
          <exclusion>
              <groupId>org.springframework.boot</groupId>
              <artifactId>spring-boot-starter-tomcat</artifactId>
          </exclusion>
      </exclusions>
  </dependency>
  
  <dependency>
      <groupId>org.springframework.boot</groupId>
      <artifactId>spring-boot-starter-undertow</artifactId>
  </dependency>
  ```

#### 4. **示例：使用内嵌Web服务器的Spring Boot应用**

创建一个简单的Spring Boot Web应用并使用内嵌Tomcat（默认）运行。

1. **创建Spring Boot应用**： 在`pom.xml`中添加`spring-boot-starter-web`依赖。

   ```xml
   <dependencies>
       <dependency>
           <groupId>org.springframework.boot</groupId>
           <artifactId>spring-boot-starter-web</artifactId>
       </dependency>
   </dependencies>
   ```

2. **创建一个简单的Controller**： 创建一个简单的控制器类，响应HTTP请求。

   ```java
   package com.example.demo;
   
   import org.springframework.web.bind.annotation.GetMapping;
   import org.springframework.web.bind.annotation.RestController;
   
   @RestController
   public class HelloController {
   
       @GetMapping("/")
       public String hello() {
           return "Hello, Spring Boot with Embedded Tomcat!";
       }
   }
   ```

3. **主应用类**： 创建主类并运行应用。

   ```java
   package com.example.demo;
   
   import org.springframework.boot.SpringApplication;
   import org.springframework.boot.autoconfigure.SpringBootApplication;
   
   @SpringBootApplication
   public class DemoApplication {
   
       public static void main(String[] args) {
           SpringApplication.run(DemoApplication.class, args);
       }
   }
   ```

4. **运行应用**： 运行`DemoApplication`类，Spring Boot会自动启动内嵌的Tomcat服务器，应用会在默认的8080端口运行。

   访问[http://localhost:8080](http://localhost:8080/)时，浏览器会显示`Hello, Spring Boot with Embedded Tomcat!`。

#### 5. **配置内嵌Web服务器属性**

可以在`application.properties`或`application.yml`中配置内嵌Web服务器的相关属性：

- **修改端口号**：

  ```properties
  server.port=8081
  ```

- **修改上下文路径**：

  ```properties
  server.servlet.context-path=/myapp
  ```

- **禁用Tomcat**： 如果需要完全禁用内嵌的Web服务器，可以通过配置禁用：

  ```properties
  spring.main.web-application-type=none
  ```

### 总结

Spring Boot的内嵌Web服务器为开发者提供了方便、快速的Web应用部署方式。通过自动配置和灵活的Web服务器选择，开发者可以轻松构建独立运行的Web应用，而无需依赖外部的Web服务器。