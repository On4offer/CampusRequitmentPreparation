好，这道题经常考察 **SpringBoot 内嵌容器原理** + **传统容器对比**，我帮你整理成标准的面试答题模板（概念 → 原理 → 区别 → 项目结合 → 追问）。

------

# 📌 面试题

SpringBoot 如何实现内嵌 Tomcat？和传统外部容器部署的区别？

------

### ✅ 一、概念回答

- **传统方式**：SpringMVC 项目通常打包成 **war 包**，放到外部容器（Tomcat、Jetty）中运行，需要容器负责加载和启动。
- **SpringBoot**：默认打包成 **可执行 jar 包**，内嵌 Servlet 容器（Tomcat/Jetty/Undertow），应用本身包含容器，运行时直接通过 `java -jar` 启动，无需额外部署。

------

### ✅ 二、SpringBoot 内嵌 Tomcat 原理

1. **starter 依赖**
   - 引入 `spring-boot-starter-web`，会带上 `spring-boot-starter-tomcat`。
2. **ServletWebServerFactory**
   - SpringBoot 在自动装配阶段加载 `TomcatServletWebServerFactory`（`xxxAutoConfiguration`）。
   - 这是一个工厂类，负责创建内嵌 Tomcat 实例。
3. **容器创建**
   - 在 `SpringApplication.run()` → `refresh()` → `onRefresh()` → `createWebServer()` 中，调用工厂类启动 Tomcat。
4. **Servlet 注册**
   - SpringBoot 会自动注册 `DispatcherServlet` 到 Tomcat 的 `ServletContext` 中。
   - 完成请求映射、拦截器链、HandlerMapping 等 MVC 组件的绑定。
5. **最终效果**
   - 应用启动后，Tomcat 在同一个进程中运行，监听配置的端口（默认 8080），对外提供 HTTP 服务。

------

### ✅ 三、与传统外部容器部署的区别

| 对比点     | 外部容器（传统 war 包）                  | 内嵌容器（SpringBoot jar 包）             |
| ---------- | ---------------------------------------- | ----------------------------------------- |
| 部署方式   | 应用打 war，部署到 Tomcat/Jetty 安装目录 | 应用打 jar，自带 Tomcat，直接 `java -jar` |
| 容器管理   | 容器由运维统一管理，支持多应用共享       | 每个应用自带容器，独立运行                |
| 启动速度   | 需要容器启动 + 部署                      | 启动更快，一步到位                        |
| 升级维护   | 容器与应用解耦，运维可独立升级容器       | 应用与容器强绑定，升级需重打包            |
| 微服务支持 | 不灵活，适合单体应用                     | 天然支持微服务架构（Docker/K8s 容器化）   |

------

### ✅ 四、结合项目经验

- 在 **苍穹外卖** 项目中，我们通过 `spring-boot-starter-web` 内嵌 Tomcat，打成 jar 包，用 `java -jar` 即可启动服务。
- 生产部署时，直接把 jar 放到服务器或 Docker 镜像中，免去了额外安装 Tomcat 的步骤，更适合微服务场景。

------

### ✅ 五、扩展追问

1. SpringBoot 的内嵌容器除了 Tomcat，还有哪些？（Jetty、Undertow）
2. 如果要替换内嵌 Tomcat，该怎么做？（排除 tomcat 依赖，引入 jetty/undertow starter）
3. 如何修改内嵌 Tomcat 的端口、线程数、请求大小限制？（`application.yml` 配置 `server.*`）
4. SpringBoot 能否仍然打包成 war？怎么做？
5. 内嵌 Tomcat 在高并发场景下的调优参数有哪些？

------

⚡ **标准回答模板（面试时可直接说）：**

> SpringBoot 内嵌 Tomcat 的原理是通过自动装配 `TomcatServletWebServerFactory` 创建并启动 Tomcat，再把 DispatcherServlet 注册到容器中。和传统的外部容器部署不同，SpringBoot 是把应用和容器打包在一个可执行 jar 里，运行时直接 `java -jar` 启动，不依赖外部 Tomcat。这种方式大大简化了部署，也更适合微服务和容器化场景。在我的苍穹外卖项目中，我们就是用内嵌 Tomcat 直接部署到服务器，无需单独安装 Tomcat，部署效率更高。

------

要不要我顺便帮你整理 **如何自定义内嵌 Tomcat 的配置**（比如端口、线程池、拦截器）？这一般是追问点。