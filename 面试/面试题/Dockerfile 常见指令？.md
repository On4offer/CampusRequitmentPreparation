好的 ✅ 我来帮你把 **“Dockerfile 的常见指令有哪些？”** 按照面试八股文的风格完整展开：

------

# 面试题：Dockerfile 的常见指令有哪些？

### 一、概念解释

- **Dockerfile**：用于定义如何构建 Docker 镜像的文本文件。
- **核心作用**：把应用代码、依赖、运行环境封装到镜像中，实现“可移植、一致性、自动化”。

------

### 二、常见指令分类与解析

1. **基础镜像与环境设置**

- `FROM`：指定基础镜像（如 `FROM openjdk:17-jdk`）。
- `LABEL`：为镜像添加元数据（作者、版本等）。
- `ENV`：设置环境变量。

1. **文件与目录操作**

- `WORKDIR`：设置工作目录。
- `COPY`：复制文件到镜像（推荐）。
- `ADD`：复制文件并支持自动解压、URL 下载。

1. **依赖安装与命令执行**

- `RUN`：构建镜像时执行命令（如安装依赖 `RUN apt-get install -y vim`）。
- `CMD`：容器启动时执行的默认命令（可被覆盖）。
- `ENTRYPOINT`：容器启动时执行的命令（不易被覆盖，适合定义主进程）。

1. **网络与端口**

- `EXPOSE`：声明容器运行时监听的端口（如 `EXPOSE 8080`）。

1. **数据持久化**

- `VOLUME`：定义数据卷挂载点。

1. **构建优化相关**

- `ARG`：定义构建参数（仅在 build 时生效）。
- `.dockerignore`：忽略不需要打包进镜像的文件。

------

### 三、案例说明

以 **苍穹外卖** SpringBoot 项目为例：

```dockerfile
FROM openjdk:17-jdk
LABEL maintainer="hzr08"
WORKDIR /app
COPY waimai.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

- `FROM openjdk:17-jdk` → 使用官方 JDK 作为基础镜像
- `WORKDIR /app` → 设置工作目录
- `COPY waimai.jar app.jar` → 拷贝应用到镜像
- `EXPOSE 8080` → 声明对外服务端口
- `ENTRYPOINT ["java", "-jar", "app.jar"]` → 容器启动时运行 SpringBoot

------

### 四、使用场景

- **开发测试**：快速构建和部署应用环境。
- **生产运维**：编写高效、体积小的镜像，便于分发。
- **CI/CD**：在流水线中自动构建镜像，保证一致性。

------

### 五、面试标准回答（简洁版）

> Dockerfile 常见指令包括：
>
> - `FROM` 指定基础镜像
> - `WORKDIR` 设置工作目录
> - `COPY/ADD` 拷贝文件
> - `RUN` 执行构建命令
> - `CMD/ENTRYPOINT` 定义容器启动命令
> - `EXPOSE` 声明端口
> - `ENV` 设置环境变量
> - `VOLUME` 定义数据卷
>    这些指令组合起来即可构建完整的应用镜像。

------

### 六、扩展追问

1. `CMD` 和 `ENTRYPOINT` 的区别？在什么场景下使用？
2. `COPY` 和 `ADD` 有什么区别？为什么更推荐 `COPY`？
3. 如何优化 Dockerfile 以减少镜像体积？（多阶段构建）
4. `.dockerignore` 文件的作用是什么？

------

要不要我帮你把 **“Docker 的分层存储原理是什么？为什么要分层？”** 也写成这种八股文答案？