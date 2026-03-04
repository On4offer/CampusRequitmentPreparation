好，这题是 **Spring vs SpringBoot MVC 对比**的常见面试题，我按照你要求的套路（概念 → 区别 → SpringBoot 简化点 → 项目结合 → 追问）整理标准模板。

------

# 📌 面试题

SpringMVC 和 SpringBoot MVC 的区别？SpringBoot 如何简化 MVC 配置？

------

### ✅ 一、概念回答

- **SpringMVC**：是基于 Servlet 的 MVC 框架，属于 Spring 的一个子模块，核心组件包括 DispatcherServlet、HandlerMapping、HandlerAdapter、ViewResolver 等，主要负责 Web 层的请求分发与响应。
- **SpringBoot MVC**：本质上仍然是 SpringMVC，只是 SpringBoot 在其上做了 **自动装配与默认配置**，通过 `spring-boot-starter-web` 依赖即可开箱即用。

------

### ✅ 二、SpringMVC vs SpringBoot MVC 区别

| 对比点    | SpringMVC                                                    | SpringBoot MVC                                               |
| --------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 依赖引入  | 需要手动引入 SpringMVC + JSON 解析器                         | 一行 `spring-boot-starter-web` 搞定                          |
| 配置方式  | 需要配置 web.xml 或 JavaConfig（DispatcherServlet、组件扫描、视图解析器等） | 自动配置，内置 DispatcherServlet、默认的 Jackson 转换器      |
| 容器      | 需要外部 Tomcat/Jetty                                        | 内嵌 Tomcat/Jetty，`java -jar` 一键启动                      |
| JSON 转换 | 需手动配置 Jackson/Fastjson                                  | 默认整合 Jackson 自动 JSON 序列化                            |
| 静态资源  | 需自己配置 ResourceHandler                                   | 自动映射 `/static`、`/public`、`/resources`、`/META-INF/resources` |
| 视图解析  | 需手动配置 InternalResourceViewResolver                      | 自动配置，支持 Thymeleaf/Freemarker 等模板引擎               |

------

### ✅ 三、SpringBoot 如何简化 MVC 配置

1. **自动注册 DispatcherServlet**，不需要 web.xml。
2. **自动装配消息转换器**（HttpMessageConverters），默认支持 JSON（Jackson）。
3. **自动配置静态资源路径**，无需额外 `ResourceHandler`。
4. **提供全局配置入口**（application.yml），可直接修改 `server.port`、`spring.mvc.*`。
5. **Starter 模块**（spring-boot-starter-web）集成了 Web 必备依赖。

------

### ✅ 四、结合项目经验

- 在 **黑马点评** 项目中：
   使用 `spring-boot-starter-web` 依赖后，SpringBoot 自动装配了 DispatcherServlet 和 JSON 转换器，我们直接写 `@RestController` + `@RequestMapping` 就能返回 JSON，不需要再像传统 SpringMVC 那样写视图解析器配置。
- 在 **苍穹外卖** 项目中：
   静态资源（图片、前端页面）放在 `/static` 目录下即可被自动映射访问，省去了配置 ResourceHandler 的步骤。

------

### ✅ 五、扩展追问

1. SpringBoot 如何自定义 MVC 配置？（答：实现 `WebMvcConfigurer`，而不是继承 `WebMvcConfigurationSupport`）
2. SpringBoot 的默认 JSON 转换器是哪个？如何替换？（Jackson，可用 Gson/Fastjson 替换）
3. 内嵌 Tomcat 如何修改端口、ContextPath？（`server.port`，`server.servlet.context-path`）
4. 如果要拦截请求，SpringMVC 的 Interceptor 和 SpringBoot Filter 有什么区别？
5. SpringBoot 2.6+ 默认路径匹配策略是什么？为什么弃用了 AntPathMatcher？

------

⚡ **标准回答模板（面试时可以这样说）：**

> SpringMVC 是传统的 Web MVC 框架，需要手动配置 DispatcherServlet、视图解析器和 JSON 转换器；SpringBoot MVC 本质还是 SpringMVC，但通过自动装配简化了配置，比如内置 DispatcherServlet、自动 JSON 转换、静态资源映射等。在我的项目中，比如黑马点评，我只需引入 starter 依赖和写少量 yml 配置，就能快速完成 Web 层开发，不需要写额外的 XML 或 JavaConfig，大幅提升了开发效率。

------

要不要我把这几道 SpringBoot 题目（区别 / 自动装配 / 启动流程 / 配置 / MVC）整理成一个 **完整的答题手册 PDF 大纲**，方便你系统背诵？