好 👍 我来把这题也整理成标准的 **八股文面试答案**，方便你背诵：

------

# 面试题：Maven 的依赖范围（scope）有哪些？在什么场景下使用？

------

## 1. 概念

Maven 的 **依赖范围（scope）** 决定了依赖在 **编译、测试、运行、打包** 等阶段是否可用，以及是否会传递给下游依赖。

------

## 2. 原理剖析

### 常见的 6 种依赖范围

1. **compile（默认）**
   - 编译、测试、运行都有效。
   - 会传递给下游依赖。
   - 适合大多数业务依赖。
2. **provided（已提供）**
   - 编译、测试有效；运行时由容器提供。
   - 不会打进最终包。
   - 典型：`servlet-api`，由 Tomcat 提供。
3. **runtime**
   - 编译时不需要，运行/测试需要。
   - 常用于 JDBC 驱动。
4. **test**
   - 仅测试阶段有效。
   - 不会打包，也不会传递。
   - 典型：`junit`、`mockito`。
5. **system**
   - 和 provided 类似，但依赖必须显式指定本地 jar 路径。
   - 基本淘汰，移植性差。
6. **import（仅 dependencyManagement 可用）**
   - 用于引入 BOM（Bill of Materials），统一版本控制。
   - 典型：Spring Boot 的 `spring-boot-dependencies`。

------

## 3. 案例

```xml
<dependencies>
    <!-- 默认 compile -->
    <dependency>
        <groupId>org.projectlombok</groupId>
        <artifactId>lombok</artifactId>
        <version>1.18.30</version>
        <scope>provided</scope>
    </dependency>

    <!-- 测试依赖 -->
    <dependency>
        <groupId>junit</groupId>
        <artifactId>junit</artifactId>
        <version>4.13.2</version>
        <scope>test</scope>
    </dependency>
</dependencies>
```

------

## 4. 使用场景

- **compile** → 业务代码依赖，如 `spring-context`
- **provided** → 容器已提供的库，如 `servlet-api`
- **runtime** → 运行时需要的库，如 `mysql-connector-java`
- **test** → 单元测试库，如 `junit`
- **system** → 特殊场景下引入本地 jar（不推荐）
- **import** → 引入 BOM，统一依赖版本，如 Spring Boot

------

## 5. 面试标准回答（示例）

👉 面试官：Maven 的依赖范围有哪些？你能举例说明吗？

答：
 Maven 常见的依赖范围有 6 种：

- **compile（默认）**：编译、运行、测试都有效，会传递，比如 `spring-core`；
- **provided**：编译和测试有效，运行由容器提供，比如 `servlet-api`；
- **runtime**：只在运行时需要，比如 JDBC 驱动；
- **test**：仅测试有效，比如 `junit`；
- **system**：类似 provided，但需要本地 jar 路径，不推荐；
- **import**：仅在 dependencyManagement 中使用，用于引入 BOM，比如 `spring-boot-dependencies`。

------

## 6. 扩展追问

- provided 和 runtime 的区别是什么？
- 为什么不推荐使用 system scope？
- Spring Boot 为什么推荐用 import scope 引入 BOM？
- 如果不写 `<scope>`，默认是什么？

------

要不要我接着帮你整理 **“Maven 常见的插件有哪些？分别解决什么问题？”** 这一题？