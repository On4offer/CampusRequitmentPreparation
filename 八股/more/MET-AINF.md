这是个好问题，很多人在学 Java、Spring Boot、SPI 的时候都会遇到 `META-INF`，但不太清楚它到底**是什么、干什么用、为啥都在这目录里**。

------

## ✅ `META-INF` 是什么？

> **`META-INF` 是 Java 应用（尤其是 JAR 包）中的一个特殊目录，用于存放**和应用运行、模块声明、配置等相关的**元信息（Meta Information）**文件。

它在 JAR 包（或 WAR、EAR）中位于根目录，例如：

```
my-library.jar
 ├─ META-INF/
 │   ├─ MANIFEST.MF
 │   ├─ services/
 │   ├─ spring.factories
 │   └─ other config...
```

------

## 📦 `META-INF` 里通常放什么？

| 文件/目录名        | 作用说明                                                |
| ------------------ | ------------------------------------------------------- |
| `MANIFEST.MF`      | JAR 包的“说明书”，包含主类名、版本、依赖等元信息        |
| `services/`        | Java SPI 机制用到的接口声明目录（用于 `ServiceLoader`） |
| `spring.factories` | Spring Boot 的自动配置机制依赖它                        |
| `spring.handlers`  | Spring XML 解析扩展                                     |
| `spring.schemas`   | Spring XML schema 定义                                  |
| `maven/`           | Maven 的构建信息（pom.xml 缓存等）                      |

------

## 🧠 为什么叫“Meta”？

因为它不存放“业务代码”，而是存放“关于这个包的描述信息”——这类信息我们就叫 **元信息（Metadata）**，比如：

- 这个包主类是谁？
- 它声明了哪些服务实现（SPI）？
- 启动时要加载哪些自动配置（Spring Boot）？

➡️ 所以就专门划了一个文件夹叫：`META-INF`（即 "Meta Information"）

------

## 🧪 举个例子：Spring Boot 的自动配置怎么找？

Spring Boot 启动时会扫描这个文件：

```
META-INF/spring.factories
```

内容示例：

```properties
org.springframework.boot.autoconfigure.EnableAutoConfiguration=\
com.example.MyAutoConfig
```

Spring Boot 就会根据这个信息自动加载你的 `@Configuration` 类。

------

## 📌 开发中常见的 `META-INF` 应用场景

| 应用        | 使用的文件/目录              | 用途                     |
| ----------- | ---------------------------- | ------------------------ |
| Java SPI    | `META-INF/services/接口全名` | 声明服务实现类           |
| Spring Boot | `META-INF/spring.factories`  | 自动装配配置类           |
| Maven 插件  | `META-INF/maven/plugin.xml`  | Maven 插件声明           |
| JAR 运行    | `META-INF/MANIFEST.MF`       | 指定主类、版本等运行信息 |

------

## 💬 面试答题模板（简洁专业）

> `META-INF` 是 Java JAR 包中的一个特殊目录，用于存放各种与应用运行和配置相关的元信息，如 MANIFEST.MF（主类信息）、services（SPI 服务发现）、spring.factories（Spring Boot 自动配置）等。Java 和 Spring 框架在运行时会自动读取这些文件，用于动态加载服务、自动装配等功能。

------

## ✅ 总结一句话

> `META-INF` 是 Java 模块的“身份证 + 插件声明中心”，一切“让程序自动知道你是谁”的信息都放这里。

------

是否想让我给你生成一个手写的 SPI 示例项目结构，或解释 `spring.factories` 在启动流程中的具体加载顺序？