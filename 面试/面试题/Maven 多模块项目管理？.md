好的 ✅ 我来帮你把这题也整理成完整的 **八股文面试答案**：

------

# 面试题：Maven 多模块项目如何管理？

------

## 1. 概念

- **多模块项目（Multi-Module Project）**：
   一个父项目（Parent POM）下面包含多个子模块（Module），每个模块都是独立的 Maven 项目，但共享统一的构建配置和依赖管理。
- 目的：**代码复用、统一依赖、分层架构、便于维护和发布**。

------

## 2. 原理剖析

- **父 POM**：
  - 使用 `<packaging>pom</packaging>`，只做依赖管理和模块聚合，不生成 jar/war。
  - 统一声明依赖版本（`dependencyManagement`）、插件（`pluginManagement`）、公共属性。
- **子模块**：
  - 在 `<modules>` 中声明。
  - 子模块继承父 POM 的配置（依赖版本、插件配置等）。
  - 每个子模块都可以单独构建，也可以通过父 POM 一键构建所有模块。

------

## 3. 案例

### 父 POM（pom.xml）

```xml
<project>
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>parent-project</artifactId>
    <version>1.0.0</version>
    <packaging>pom</packaging>

    <!-- 统一依赖管理 -->
    <dependencyManagement>
        <dependencies>
            <dependency>
                <groupId>org.springframework.boot</groupId>
                <artifactId>spring-boot-starter-web</artifactId>
                <version>3.2.0</version>
            </dependency>
        </dependencies>
    </dependencyManagement>

    <!-- 子模块声明 -->
    <modules>
        <module>service</module>
        <module>dao</module>
        <module>web</module>
    </modules>
</project>
```

### 子模块（例如 service/pom.xml）

```xml
<project>
    <parent>
        <groupId>com.example</groupId>
        <artifactId>parent-project</artifactId>
        <version>1.0.0</version>
    </parent>

    <artifactId>service</artifactId>

    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <!-- 版本号不用写，继承父 POM 的 dependencyManagement -->
        </dependency>
    </dependencies>
</project>
```

------

## 4. 使用场景

- **分层架构**：
  - `common`（工具类模块）
  - `dao`（数据访问层）
  - `service`（业务逻辑层）
  - `web`（接口层）
- **统一依赖管理**：
  - 父 POM 管理依赖版本，子模块只需声明 artifactId。
- **快速构建**：
  - `mvn clean install` → 一次性构建所有子模块。
  - `mvn clean install -pl service -am` → 只构建指定模块及其依赖。

------

## 5. 面试标准回答（示例）

👉 面试官：Maven 多模块项目如何管理？

答：
 Maven 多模块项目通过 **父 POM + 子模块** 管理。
 父 POM 使用 `<packaging>pom</packaging>`，主要负责统一依赖版本管理（`dependencyManagement`）、插件配置（`pluginManagement`），并通过 `<modules>` 声明所有子模块。
 子模块继承父 POM 的配置，只需在 `<dependencies>` 中声明依赖，不需要重复写版本。
 这样既能保证 **版本统一**，又能实现 **分层架构和快速构建**。

------

## 6. 扩展追问

- `dependencyManagement` 和 `dependencies` 在多模块项目中的区别？
- `pluginManagement` 和 `plugins` 的区别？
- 如何只构建单个模块而不是全部模块？
- 如果不同模块需要依赖不同版本的 jar，怎么解决？
- 在多模块项目中，如何避免循环依赖？

------

要不要我接着帮你整理 **“本地仓库、中央仓库、私服仓库的区别？工作流程是什么？”** 这一题？