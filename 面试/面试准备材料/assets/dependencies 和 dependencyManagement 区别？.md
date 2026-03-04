好的 ✅ 我来把这道题也整理成 **八股文面试答案**，方便你面试时背诵和扩展。

------

# 面试题：`dependencies` 和 `dependencyManagement` 的区别？

------

## 1. 概念

- **`dependencies`**：
  - 直接声明项目需要的依赖。
  - 定义在 `<dependencies>` 标签下，项目会实际引入。
- **`dependencyManagement`**：
  - 用于 **统一管理依赖版本**，不直接引入依赖。
  - 定义在 `<dependencyManagement>` 下，子模块在 `<dependencies>` 里声明依赖时可以继承版本号，避免版本不一致问题。

------

## 2. 原理剖析

- `dependencies` = **真正生效**，直接加入项目的 classpath。
- `dependencyManagement` = **约束和声明**，不会自动生效，子项目必须在 `<dependencies>` 中显式声明依赖，才会应用其中的版本信息。
- 使用场景：
  - 多模块项目中，为避免子模块依赖版本不一致，通过父 POM 的 `dependencyManagement` 统一指定版本。

------

## 3. 案例

### 父 POM（dependencyManagement）

```xml
<dependencyManagement>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>3.2.0</version>
        </dependency>
    </dependencies>
</dependencyManagement>
```

### 子 POM（dependencies）

```xml
<dependencies>
    <dependency>
        <groupId>org.springframework.boot</groupId>
        <artifactId>spring-boot-starter-web</artifactId>
        <!-- 这里不写 version，会自动继承父 POM 的版本 -->
    </dependency>
</dependencies>
```

------

## 4. 使用场景

- **单模块项目**：直接用 `<dependencies>` 即可。
- **多模块项目**：父 POM 用 `dependencyManagement` 管控版本，子模块只需声明依赖，不用重复写版本。
- **版本升级**：统一在父 POM 改版本号，所有子模块同步升级，避免冲突。

------

## 5. 面试标准回答（示例）

👉 面试官：`dependencies` 和 `dependencyManagement` 有什么区别？

答：
 `dependencies` 用于 **直接引入依赖**，项目会实际生效；
 而 `dependencyManagement` 主要用于 **统一管理依赖版本**，它本身不会引入依赖，子项目必须在 `dependencies` 中声明依赖时才会生效。
 在 **多模块项目**里，我们一般在父 POM 里写 `dependencyManagement` 统一版本控制，子模块只声明 artifactId 即可，避免版本冲突。

------

## 6. 扩展追问

- 如果在子模块里声明了版本号，会不会覆盖 `dependencyManagement`？
- `dependencyManagement` 和 `pluginManagement` 的区别是什么？
- 在多模块项目中，如何解决 **依赖冲突**？
- 如果同一个依赖被多个父 POM 管理，会采用哪个版本？

------

要不要我再帮你把 **“Maven 如何解决依赖冲突？传递依赖的规则是什么？”** 也整理成这种八股文答案？