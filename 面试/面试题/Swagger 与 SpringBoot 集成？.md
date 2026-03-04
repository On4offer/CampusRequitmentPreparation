好的 ✅ 我来帮你写一道完整的 **Swagger 与 SpringBoot 集成**面试题答案，依旧保持「概念 → 原理 → 使用步骤 → 项目实践 → 面试模板 → 扩展追问」结构：

------

## 面试题：Swagger 如何与 SpringBoot 集成？

### 1. 概念

**Swagger** 是基于 **OpenAPI 规范** 的接口文档生成工具。与 SpringBoot 集成后，可以通过注解自动生成 REST API 文档，并提供交互式 UI 页面（如 Swagger UI、Knife4j），方便前后端联调和测试。

------

### 2. 原理

Swagger 通过 **扫描 SpringBoot 项目中的注解（Controller、Model）**，自动解析接口信息（URL、请求方式、参数、返回值），并生成 OpenAPI 格式的 JSON，再由 Swagger UI 渲染成可视化文档。

------

### 3. 集成步骤

1. **引入依赖**（Maven 示例，Springfox 或 Knife4j）

```xml
<!-- Springfox 3.x -->
<dependency>
    <groupId>io.springfox</groupId>
    <artifactId>springfox-boot-starter</artifactId>
    <version>3.0.0</version>
</dependency>
```

或

```xml
<!-- Knife4j，更美观的 UI -->
<dependency>
    <groupId>com.github.xiaoymin</groupId>
    <artifactId>knife4j-spring-boot-starter</artifactId>
    <version>3.0.3</version>
</dependency>
```

1. **编写配置类**

```java
@Configuration
@EnableOpenApi  // Knife4j 用 @EnableKnife4j
public class SwaggerConfig {

    @Bean
    public Docket api() {
        return new Docket(DocumentationType.OAS_30) // OpenAPI 3.0
                .select()
                .apis(RequestHandlerSelectors.basePackage("com.example.controller"))
                .paths(PathSelectors.any())
                .build()
                .apiInfo(apiInfo());
    }

    private ApiInfo apiInfo() {
        return new ApiInfoBuilder()
                .title("苍穹外卖 API 文档")
                .description("接口文档示例")
                .version("1.0")
                .build();
    }
}
```

1. **Controller 中添加注解**

```java
@RestController
@RequestMapping("/user")
@Api(tags = "用户接口")
public class UserController {

    @ApiOperation("用户登录接口")
    @PostMapping("/login")
    public Result login(@ApiParam("手机号") String phone,
                        @ApiParam("验证码") String code) {
        return Result.success("登录成功");
    }
}
```

1. **启动项目，访问文档地址**

- Springfox 默认：`http://localhost:8080/swagger-ui/`
- Knife4j 默认：`http://localhost:8080/doc.html`

------

### 4. 项目实践（苍穹外卖 / 黑马点评 示例）

- **苍穹外卖**：使用 Knife4j 集成 Swagger，生成用户登录、下单、菜品管理等接口文档，前端直接在 `doc.html` 页面调试接口。
- **黑马点评**：集成 Swagger 后，生成店铺查询、签到、优惠券领取接口文档，测试人员直接用 Swagger UI 验证返回结果。

------

### 5. 面试模板回答

> Swagger 与 SpringBoot 集成主要分三步：
>
> 1. **引入依赖**（Springfox 或 Knife4j）；
> 2. **配置 Docket Bean**，指定扫描包和文档信息；
> 3. **在 Controller 上添加注解**（如 `@Api`, `@ApiOperation`, `@ApiParam`）；
>     启动后即可通过 `/swagger-ui/` 或 `/doc.html` 访问接口文档。
>     在实际项目中，比如苍穹外卖，我就通过 Knife4j 生成 API 文档，方便前后端联调和测试。

------

### 6. 扩展追问

- Swagger 常见注解有哪些？作用分别是什么？
- 为什么生产环境一般不直接暴露 Swagger？如何做权限控制？
- Swagger 与 Postman、Apifox 相比，各自的优势是什么？
- OpenAPI 2.0 和 OpenAPI 3.0 有什么区别？

------

要不要我帮你把 **Swagger 常见注解对照表**（`@Api`, `@ApiOperation`, `@ApiParam`, `@ApiModel`, `@ApiModelProperty`）也整理一份，方便面试时速记？