好的 ✅ 我来帮你把 **“Docker 的常见命令有哪些？”** 按照面试八股文的风格完整展开：

------

# 面试题：Docker 的常见命令有哪些？

### 一、概念解释

Docker 命令行工具是日常操作 Docker 的核心方式，主要分为：

- **镜像管理命令**
- **容器管理命令**
- **数据卷和网络管理命令**
- **其他辅助命令**

------

### 二、常见命令分类与解析

1. **镜像相关**
   - `docker images`：查看本地镜像
   - `docker pull 镜像名:tag`：拉取镜像
   - `docker rmi 镜像ID`：删除镜像
   - `docker build -t 镜像名:tag .`：基于 Dockerfile 构建镜像
2. **容器相关**
   - `docker ps`：查看运行中的容器
   - `docker ps -a`：查看所有容器（包含已停止）
   - `docker run -d --name 容器名 镜像名`：启动容器
   - `docker exec -it 容器ID /bin/bash`：进入容器交互
   - `docker stop/start/restart 容器ID`：停止/启动/重启容器
   - `docker rm 容器ID`：删除容器
3. **数据卷与文件操作**
   - `docker volume ls`：查看数据卷
   - `docker run -v 宿主机目录:容器目录 镜像名`：挂载卷
   - `docker cp 容器ID:路径 宿主机路径`：容器和宿主机之间拷贝文件
4. **日志与监控**
   - `docker logs -f 容器ID`：查看容器日志
   - `docker stats`：实时查看容器资源使用情况
5. **网络相关**
   - `docker network ls`：查看网络
   - `docker network create mynet`：创建自定义网络
   - `docker run --network=mynet 镜像名`：指定网络启动容器

------

### 三、案例说明

在 **苍穹外卖** 项目中：

- 打包镜像：`docker build -t waimai:v1 .`
- 运行容器：`docker run -d -p 8080:8080 --name waimai waimai:v1`
- 查看日志：`docker logs -f waimai`
- 进入容器：`docker exec -it waimai /bin/bash`
   这样可以快速完成部署和调试。

------

### 四、使用场景

- **开发调试**：快速进入容器、查看日志。
- **测试环境**：批量启动和停止容器，模拟微服务环境。
- **生产运维**：通过 `docker stats` 和 `docker logs` 进行监控与排错。

------

### 五、面试标准回答（简洁版）

> Docker 常见命令分为镜像管理（pull、build、rmi）、容器管理（run、ps、exec、stop/start）、数据卷挂载（-v）、日志与监控（logs、stats）、网络管理（network create/ls）等。在实际项目中，常用的就是构建镜像、运行容器、进入容器和查看日志。

------

### 六、扩展追问

1. `docker run` 和 `docker start` 的区别？
2. 如何进入一个正在运行的容器？有哪些方式？
3. `docker logs` 和 `docker exec tail -f` 有什么区别？
4. 删除容器和删除镜像时要注意什么？

------

要不要我帮你把 **“如何在 Docker 中运行一个 SpringBoot 项目？”** 也写成这种面试八股文答案？