# SpringMVC vs SpringBoot MVC 对比演示

这个项目通过两个示例应用程序，直观展示了传统SpringMVC和SpringBoot MVC之间的区别，以及SpringBoot如何简化MVC配置。

## 项目结构

```
springmvc-vs-springboot/
├── springmvc-traditional/  # 传统SpringMVC项目
├── springboot-mvc/         # SpringBoot MVC项目
└── README.md               # 说明文档
```

## 📌 概念解析

### SpringMVC
- 基于Servlet的MVC框架，属于Spring的子模块
- 核心组件：DispatcherServlet、HandlerMapping、HandlerAdapter、ViewResolver等
- 主要负责Web层的请求分发与响应处理
- 需要手动配置大量XML文件

### SpringBoot MVC
- 本质上仍然是SpringMVC，是SpringMVC的简化使用方式
- 通过**自动装配**和**约定优于配置**的理念简化开发
- 内置了Web容器，无需外部Tomcat
- 通过starter依赖一键引入所需组件

## 📊 详细对比

| 对比点 | SpringMVC | SpringBoot MVC |
|-------|-----------|---------------|
| **依赖管理** | 需要手动引入SpringMVC、Jackson、Servlet等依赖 | 一行`spring-boot-starter-web`搞定所有依赖 |
| **配置文件** | 需要web.xml、spring-mvc.xml等多个配置文件 | 仅需application.yml/application.properties，甚至零配置 |
| **Web容器** | 需要外部Tomcat/Jetty服务器 | 内嵌Tomcat/Jetty，`java -jar`直接运行 |
| **组件注册** | 需要手动注册DispatcherServlet、过滤器等 | 自动注册所有必要组件 |
| **视图解析器** | 需手动配置InternalResourceViewResolver | 自动配置Thymeleaf等模板引擎 |
| **静态资源** | 需配置`<mvc:resources>` | 自动映射`/static`、`/public`等目录 |
| **JSON转换** | 需手动配置Jackson消息转换器 | 默认集成Jackson，自动处理JSON转换 |
| **参数绑定** | 需要配置数据绑定器 | 自动配置并支持更多特性 |
| **开发效率** | 配置繁琐，开发效率低 | 快速开发，专注业务逻辑 |
| **部署方式** | 打包为war，部署到外部容器 | 打包为jar，独立运行 |

## ✨ SpringBoot简化MVC配置的核心机制

### 1. 自动装配（Auto-configuration）
- 通过`@EnableAutoConfiguration`注解开启
- SpringBoot启动时会扫描classpath中的jar包
- 根据检测到的依赖自动配置相应组件
- 例如：检测到`spring-webmvc`依赖时，自动配置DispatcherServlet

### 2. 起步依赖（Starter Dependencies）
- 预定义的依赖集合，解决依赖冲突
- `spring-boot-starter-web`包含了Web开发所需的所有依赖
- 自动管理版本，避免版本兼容问题

### 3. 约定优于配置（Convention over Configuration）
- 默认配置项遵循业界最佳实践
- 静态资源默认放在`/static`、`/public`等目录
- 视图模板默认放在`/templates`目录
- Controller默认扫描启动类所在包及子包

### 4. 内嵌容器
- 内置Tomcat、Jetty、Undertow等Web容器
- 可通过配置文件直接修改容器参数
- 支持命令行启动，无需额外部署步骤

## 🚀 项目演示说明

### 传统SpringMVC项目（springmvc-traditional）

**核心配置文件：**
- `pom.xml` - 手动配置所有依赖
- `web.xml` - 配置DispatcherServlet和过滤器
- `spring-mvc.xml` - 配置组件扫描、视图解析器、消息转换器等

**访问地址：**
- 视图页面：`http://localhost:8080/traditional/index`
- JSON接口：`http://localhost:8080/traditional/api/data`
- 健康检查：`http://localhost:8080/traditional/health`

### SpringBoot MVC项目（springboot-mvc）

**核心文件：**
- `pom.xml` - 仅需spring-boot-starter-web依赖
- `SpringBootMvcApplication.java` - 应用入口，一行注解搞定配置
- `application.yml` - 简洁的配置文件

**访问地址：**
- 视图页面：`http://localhost:8081/springboot/springboot/index`
- JSON接口：`http://localhost:8081/springboot/springboot/api/data`
- RESTful API：`http://localhost:8081/springboot/api/v1/users`

## 💡 SpringBoot简化配置的具体示例

### 1. DispatcherServlet配置

**SpringMVC（需要在web.xml中）：**
```xml
<servlet>
    <servlet-name>dispatcherServlet</servlet-name>
    <servlet-class>org.springframework.web.servlet.DispatcherServlet</servlet-class>
    <init-param>
        <param-name>contextConfigLocation</param-name>
        <param-value>classpath:spring-mvc.xml</param-value>
    </init-param>
    <load-on-startup>1</load-on-startup>
</servlet>
<servlet-mapping>
    <servlet-name>dispatcherServlet</servlet-name>
    <url-pattern>/</url-pattern>
</servlet-mapping>
```

**SpringBoot（无需配置）：**
- 自动注册DispatcherServlet到内嵌容器
- 自动映射到`/`路径
- 自动配置所有必要的处理器和适配器

### 2. 视图解析器配置

**SpringMVC（需要在spring-mvc.xml中）：**
```xml
<bean class="org.springframework.web.servlet.view.InternalResourceViewResolver">
    <property name="prefix" value="/WEB-INF/views/"/>
    <property name="suffix" value=".jsp"/>
</bean>
```

**SpringBoot（自动配置）：**
- 检测到Thymeleaf依赖时自动配置ThymeleafViewResolver
- 默认前缀：`classpath:/templates/`
- 默认后缀：`.html`

### 3. 静态资源处理

**SpringMVC（需要在spring-mvc.xml中）：**
```xml
<mvc:resources mapping="/static/**" location="/static/"/>
<mvc:default-servlet-handler/>
```

**SpringBoot（自动映射）：**
- 自动映射以下目录：
  - `classpath:/static/`
  - `classpath:/public/`
  - `classpath:/resources/`
  - `classpath:/META-INF/resources/`

## 🔧 如何运行项目

### 运行传统SpringMVC项目
1. 部署到Tomcat等外部容器
2. 访问 `http://localhost:8080/traditional/index`

### 运行SpringBoot MVC项目
1. 执行主类`SpringBootMvcApplication`的main方法
2. 或使用Maven命令：`mvn spring-boot:run`
3. 或打包后运行：`java -jar springboot-mvc-1.0-SNAPSHOT.jar`
4. 访问 `http://localhost:8081/springboot/springboot/index`

## ❓ 常见面试问题

1. **SpringBoot MVC和SpringMVC的区别是什么？**
   - SpringBoot MVC本质上是带有自动配置的SpringMVC
   - SpringBoot通过starter依赖、自动装配、内嵌容器等特性简化了配置
   - SpringBoot更加关注开发效率，SpringMVC更加灵活可定制

2. **SpringBoot的自动配置原理是什么？**
   - 通过`@EnableAutoConfiguration`注解开启自动配置
   - SpringFactories机制加载`META-INF/spring.factories`中的配置类
   - 条件注解（@Conditional）决定是否应用某个配置

3. **SpringBoot如何自定义MVC配置？**
   - 实现`WebMvcConfigurer`接口（推荐）
   - 不要继承`WebMvcConfigurationSupport`，会禁用自动配置
   - 在application.yml中覆盖默认配置

4. **SpringBoot的静态资源路径有哪些？**
   - `classpath:/static/`
   - `classpath:/public/`
   - `classpath:/resources/`
   - `classpath:/META-INF/resources/`

## 🎯 总结

SpringBoot MVC通过"约定优于配置"和"自动装配"的理念，极大地简化了SpringMVC的使用。开发者不再需要编写繁琐的XML配置，可以专注于业务逻辑的实现，显著提高开发效率。同时，SpringBoot还提供了内嵌容器、starter依赖等特性，使得应用程序的开发、测试和部署更加便捷。

在实际项目中，推荐使用SpringBoot MVC进行开发，特别是对于快速迭代的项目和微服务架构。
