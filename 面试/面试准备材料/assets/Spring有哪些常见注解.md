Spring 框架的注解体系是核心知识点，面试中常考察**注解分类、核心作用、使用场景**，以下按功能模块梳理高频注解，附核心说明和使用场景，兼顾基础与高频考点：

### 一、核心容器注解（IoC/DI 核心）

#### 1. 组件注册注解（将 Bean 纳入 Spring 容器管理）

| 注解             | 作用                                                         | 典型场景                           |
| ---------------- | ------------------------------------------------------------ | ---------------------------------- |
| `@Component`     | 通用组件注解，标记类为 Spring 管理的 Bean（基础注解）        | 非分层的通用 Bean                  |
| `@Controller`    | 标注 MVC 的控制器层（特殊 @Component），处理 HTTP 请求       | 控制层（Controller 类）            |
| `@Service`       | 标注业务逻辑层（特殊 @Component）                            | 服务层（Service 类）               |
| `@Repository`    | 标注数据访问层（特殊 @Component），支持持久化异常转换        | 持久层（Dao/Mapper 类）            |
| `@Configuration` | 标注配置类（替代 XML 配置文件），可通过`@Bean`注册 Bean      | 全局配置类（如数据源配置）         |
| `@Bean`          | 配合`@Configuration`，方法级别注册 Bean（返回值为 Bean 实例） | 第三方组件注册（如 RedisTemplate） |

#### 2. 依赖注入注解（给 Bean 注入依赖）

| 注解         | 作用                                                         | 注意点                                          |
| ------------ | ------------------------------------------------------------ | ----------------------------------------------- |
| `@Autowired` | 按类型自动注入依赖（Spring 原生），可用于字段 / 构造器 / 方法 | 默认要求依赖必须存在，可加`required=false`      |
| `@Resource`  | JDK 注解，按**名称**注入（默认），也可指定 type；优先级：name > type | 不支持构造器注入                                |
| `@Qualifier` | 配合`@Autowired`，按名称筛选 Bean（解决同类型多 Bean 冲突）  | `@Autowired @Qualifier("userService")`          |
| `@Value`     | 注入简单值（字面量 / 配置文件属性）                          | `@Value("${server.port}")`、`@Value("default")` |

### 二、Spring MVC 核心注解

| 注解                           | 作用                                                  | 示例                                                     |
| ------------------------------ | ----------------------------------------------------- | -------------------------------------------------------- |
| `@RequestMapping`              | 映射 HTTP 请求（路径、方法、参数等），可用于类 / 方法 | `@RequestMapping("/user")`、`method = RequestMethod.GET` |
| `@GetMapping`                  | 简化`@RequestMapping(method=GET)`                     | `@GetMapping("/user/{id}")`                              |
| `@PostMapping`                 | 简化`@RequestMapping(method=POST)`                    | `@PostMapping("/user")`                                  |
| `@PutMapping`/`@DeleteMapping` | 对应 PUT/DELETE 请求（RESTful 风格）                  |                                                          |
| `@PathVariable`                | 绑定 URL 路径参数到方法参数                           | `getUser(@PathVariable Long id)`                         |
| `@RequestParam`                | 绑定请求参数（Query/String）到方法参数                | `list(@RequestParam(required=false) String name)`        |
| `@RequestBody`                 | 绑定 HTTP 请求体（JSON/XML）到方法参数（通常是 POJO） | `save(@RequestBody User user)`                           |
| `@ResponseBody`                | 将方法返回值直接写入响应体（替代视图解析，返回 JSON） | 控制器方法标注，或用`@RestController`替代                |
| `@RestController`              | 组合`@Controller + @ResponseBody`，返回 JSON 而非视图 | RESTful 接口控制器                                       |
| `@RequestHeader`               | 绑定请求头参数到方法参数                              | `getToken(@RequestHeader("token") String token)`         |
| `@CookieValue`                 | 绑定 Cookie 值到方法参数                              |                                                          |

### 三、切面编程（AOP）注解

| 注解              | 作用                                           | 说明                                          |
| ----------------- | ---------------------------------------------- | --------------------------------------------- |
| `@Aspect`         | 标注类为切面类（配合 @Component 注册）         | 切面类需先纳入 IoC 容器                       |
| `@Before`         | 前置通知：目标方法执行前执行                   | `@Before("execution(* com..*Service.*(..))")` |
| `@After`          | 后置通知：目标方法执行后执行（无论是否异常）   |                                               |
| `@AfterReturning` | 返回通知：目标方法正常返回后执行               | 可获取返回值                                  |
| `@AfterThrowing`  | 异常通知：目标方法抛出异常后执行               | 可捕获异常类型                                |
| `@Around`         | 环绕通知：包裹目标方法，可控制执行时机（最强） | 需手动调用`proceed()`执行目标方法             |
| `@Pointcut`       | 定义切入点（复用切面表达式）                   | `@Pointcut("bean(*Service)")`                 |

### 四、声明式事务注解

| 注解             | 作用                                                         | 关键属性 |
| ---------------- | ------------------------------------------------------------ | -------- |
| `@Transactional` | 标注类 / 方法为事务性（类级别：所有方法生效；方法级别：覆盖类配置） |          |
| 核心属性         | - `propagation`：事务传播行为（如 REQUIRED/REQUIRES_NEW）- `isolation`：隔离级别（如 READ_COMMITTED）- `rollbackFor`：指定回滚的异常类型- `readOnly`：是否只读（优化性能） |          |

### 五、其他高频注解

| 注解                  | 作用                                                         | 使用场景                                                     |
| --------------------- | ------------------------------------------------------------ | ------------------------------------------------------------ |
| `@Scope`              | 指定 Bean 的作用域                                           | `@Scope("singleton")`（默认）、`prototype`（多例）、`request`/`session` |
| `@Lazy`               | 延迟初始化 Bean（单例 Bean 默认启动时初始化，加此注解首次使用时初始化） | 非核心 Bean 优化启动速度                                     |
| `@Primary`            | 同类型多 Bean 时，指定默认注入的 Bean（优先级高于`@Qualifier`） | `@Bean @Primary public UserService userServiceImpl()`        |
| `@Profile`            | 按环境激活 Bean（如 dev/test/prod）                          | 多环境配置（如不同数据源）                                   |
| `@Conditional`        | 条件化注册 Bean（满足条件才注册）                            | 配合自定义 Condition 实现动态配置                            |
| `@CrossOrigin`        | 允许跨域请求（Spring MVC）                                   | 前后端分离项目接口跨域                                       |
| `@Valid`/`@Validated` | 参数校验（配合 JSR-380 注解如 @NotBlank/@NotNull）           | 控制器方法参数校验                                           |

### 面试加分要点

1. **注解优先级**：方法级注解 > 类级注解（如`@Transactional`、`@RequestMapping`）；

2. `@Autowired`与`@Resource`区别

   ：

   - `@Autowired`：Spring 原生，按类型注入，支持`@Qualifier`；
   - `@Resource`：JDK (javax.annotation)，按名称注入，不支持构造器注入；

3. **`@ComponentScan`**：指定扫描包路径（SpringBoot 主类`@SpringBootApplication`已包含）；

4. **SpringBoot 扩展注解**：`@SpringBootApplication`（组合`@SpringBootConfiguration + @EnableAutoConfiguration + @ComponentScan`）、`@EnableAutoConfiguration`（自动配置）、`@ConfigurationProperties`（绑定配置文件属性）等（若面试涉及 SpringBoot 需补充）。

### 总结

回答时建议**按模块分类说明**（如 IoC、MVC、AOP、事务），每个模块挑核心注解讲清「作用 + 使用场景」，再补充 1-2 个高频对比（如`@Autowired` vs `@Resource`），体现对注解的理解而非单纯罗列。