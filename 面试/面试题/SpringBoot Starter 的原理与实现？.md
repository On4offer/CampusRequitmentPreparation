好，这题属于**源码/工程化**常考点。我给你一份可直接背的模板（概念 → 原理 → 步骤 → 代码骨架 → 常见坑 → 追问）。

------

# 📌 面试题

SpringBoot Starter 是什么？自定义 Starter 的实现步骤？

### ✅ 一、概念回答

- **Starter**：一组“**约定好依赖 + 自动配置**”的打包方案。引入一个 starter 依赖后，Spring Boot 会按条件自动创建相关 Bean，让组件**开箱即用**。
- 组成：**`starter`（只管依赖聚合）** + **`autoconfigure`（真正的自动配置与条件装配）**。实际项目也可合并为一个模块，但官方推荐拆分。

------

### ✅ 二、核心原理（自动装配）

- `@EnableAutoConfiguration` → `AutoConfigurationImportSelector` → 扫描自动配置清单
- **Boot 2.x**：读取 `META-INF/spring.factories`
- **Boot 3.x**：读取 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`，并支持 `@AutoConfiguration` 注解
- 是否生效由一系列 `@Conditional*` 决定（如 `@ConditionalOnClass`、`@ConditionalOnMissingBean`、`@ConditionalOnProperty`）。

------

### ✅ 三、自定义 Starter 的标准步骤（Boot 3.x 示范）

> 建议两个模块：`xxx-spring-boot-starter`（依赖聚合） 与 `xxx-spring-boot-autoconfigure`（自动配置）

1. **创建模块**

- `xxx-spring-boot-starter`：`pom` 只 **依赖** `xxx-spring-boot-autoconfigure`、日志等。
- `xxx-spring-boot-autoconfigure`：引入需要的第三方库（如 client SDK）。

1. **编写配置属性类**

```java
@ConfigurationProperties(prefix = "xxx.client")
public class XxxClientProperties {
    private String endpoint;
    private String apiKey;
    private boolean enabled = true;
    // getter/setter
}
```

1. **编写自动配置类**

```java
@AutoConfiguration
@EnableConfigurationProperties(XxxClientProperties.class)
@ConditionalOnClass(XxxClient.class)
@ConditionalOnProperty(prefix="xxx.client", name="enabled", havingValue="true", matchIfMissing=true)
public class XxxClientAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public XxxClient xxxClient(XxxClientProperties props) {
        return new XxxClient(props.getEndpoint(), props.getApiKey());
    }
}
```

1. **注册自动配置清单（Boot 3.x）**

- 在 `xxx-spring-boot-autoconfigure` 的资源文件：
   `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports`

```
com.example.autoconfigure.XxxClientAutoConfiguration
```

1. **（可选）生成配置提示**

- 依赖 `spring-boot-configuration-processor`，编译后为 `application.yml` 提供属性提示。

1. **编写测试**（推荐）

- 使用 `ApplicationContextRunner` 验证条件装配是否生效/失效。

1. **发布与使用**

- 发布到私服/中央仓库；业务项目只需引入 `xxx-spring-boot-starter`，在 `application.yml` 配置 `xxx.client.*` 即可。

------

### ✅ 四、最小文件骨架（Boot 3.x）

```
xxx-spring-boot-starter/
└─ pom.xml  (依赖 xxx-spring-boot-autoconfigure)

xxx-spring-boot-autoconfigure/
├─ src/main/java/com/example/autoconfigure/...
│  ├─ XxxClientProperties.java          (@ConfigurationProperties)
│  └─ XxxClientAutoConfiguration.java   (@AutoConfiguration)
└─ src/main/resources/
   └─ META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports
```

------

### ✅ 五、常见坑（面试加分）

- **3.x 不再使用 `spring.factories`**，改用 `AutoConfiguration.imports`；自动配置类可加 `@AutoConfiguration`。
- 属性绑定别忘了 `@EnableConfigurationProperties`。
- 合理使用 `@ConditionalOnMissingBean`，**允许业务方自定义覆盖**。
- Starter 模块尽量**不直接引重依赖**，把重依赖放到 `autoconfigure`；Starter 只做“门面”。
- 提供**显式关闭开关**（`@ConditionalOnProperty(..., matchIfMissing=true)`），并在文档中标明默认行为。
- 与 Web 环境相关的自动配置，注意区分 Servlet/Reactive 条件（`@ConditionalOnWebApplication`）。

------

### ✅ 六、可能追问

1. **Boot 2.x 与 3.x 的自动装配清单差异？**为什么升级？
2. `@ConditionalOnBean` vs `@ConditionalOnMissingBean` 的取舍场景？
3. 如何**禁用**某个自动配置？（`spring.autoconfigure.exclude` / `@ImportAutoConfiguration(exclude=...)`）
4. 如何为属性生成 IDE 提示？（`spring-boot-configuration-processor`）
5. 如何写**健壮的自动装配测试**？（`ApplicationContextRunner` + 条件断言）

------

⚡ **一段式标准作答**（可直接背）

> Starter 是把依赖与自动配置打包的模块，引入后即可按条件自动装配相关 Bean。自定义 Starter 通常拆为两个模块：starter 只做依赖聚合，autoconfigure 放自动配置。实现步骤是：定义 `@ConfigurationProperties` 属性类；编写带 `@AutoConfiguration` 的自动配置并配合 `@Conditional*` 与 `@ConditionalOnMissingBean`；在 `META-INF/spring/org.springframework.boot.autoconfigure.AutoConfiguration.imports` 注册；可选加上 configuration-processor 生成提示；最后用 `ApplicationContextRunner` 做条件装配测试。Boot 3.x 不再用 `spring.factories`，推荐用 `AutoConfiguration.imports` 并提供可关闭的开关与可覆盖的 Bean，保证可扩展性。