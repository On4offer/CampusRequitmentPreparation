好的 👍 我来帮你把这道题用 **八股文面试模板** 展开整理：

------

# 面试题：Maven 的三大生命周期是什么？常见命令有哪些？

------

## 1. 概念

Maven 是一个 **项目构建与依赖管理工具**，它将项目构建过程划分为三个标准的生命周期：

- **clean**：清理项目，删除之前编译或打包生成的文件。
- **default（build）**：构建核心生命周期，负责编译、测试、打包、安装、部署等。
- **site**：生成项目文档和站点。

------

## 2. 原理剖析

- **生命周期（Lifecycle）**：由一系列有序的 **阶段（phase）** 组成。
- 每个阶段会绑定多个 **插件目标（plugin goal）**，实际执行时 Maven 会从前往后顺序执行。
- **执行某个阶段时，之前的阶段会自动执行**。

例如：
 执行 `mvn package` → 会顺序执行 compile、test、package。

------

## 3. 常见命令

### Clean 生命周期

- `mvn clean` → 删除 target 目录

### Default 生命周期（最常用）

- `mvn compile` → 编译
- `mvn test` → 运行测试
- `mvn package` → 打包（jar/war）
- `mvn install` → 安装到本地仓库
- `mvn deploy` → 部署到远程仓库

### Site 生命周期

- `mvn site` → 生成项目文档
- `mvn site:deploy` → 部署文档

------

## 4. 使用场景

- **开发调试**：`mvn compile` / `mvn test`
- **打包上线**：`mvn clean package`
- **多模块依赖管理**：`mvn install` 安装到本地仓库，供其他模块使用
- **CI/CD 部署**：`mvn deploy` 推送到私服仓库

------

## 5. 面试标准回答（示例）

👉 面试官：Maven 的生命周期有几个？常见命令有哪些？

答：
 Maven 有三大生命周期：**clean、default、site**。
 其中 **default 是核心**，包含编译（compile）、测试（test）、打包（package）、安装（install）、部署（deploy）等阶段。
 常见命令包括：

- `mvn clean` → 清理
- `mvn package` → 打包
- `mvn install` → 安装到本地仓库
- `mvn deploy` → 部署到远程仓库

这样保证了从开发、测试到上线的全流程自动化。

------

## 6. 扩展追问

- 你能说说 **phase 和 goal 的区别** 吗？
- Maven 为什么执行 `mvn package` 时会自动执行 compile 和 test？
- 在实际项目中你是怎么结合 Jenkins/CI 使用 `mvn clean install` 的？
- 多模块项目中，如果只想构建单个子模块该怎么做？

------

要不要我把 **下一题（`dependencies` 和 `dependencyManagement` 的区别？）** 也整理成这种八股文答案？