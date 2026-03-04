## addInterceptor 方法介绍

### 1. 基本定义
[addInterceptor()](file://org\springframework\web\servlet\config\annotation\InterceptorRegistry.java#L58-L69) 是 Spring MVC 框架中用于注册拦截器的核心方法。

### 2. 所属工具和类
- **框架**：Spring Web MVC
- **类**：`org.springframework.web.servlet.config.annotation.InterceptorRegistry`
- **方法签名**：`public InterceptorRegistration addInterceptor(HandlerInterceptor interceptor)`

### 3. 方法功能
将指定的拦截器添加到 Spring MVC 的拦截器注册中心，并返回一个 [InterceptorRegistration](file://org\springframework\web\servlet\config\annotation\InterceptorRegistration.java#L38-L292) 对象用于进一步配置该拦截器。

### 4. 在代码中的使用
```java
registry.addInterceptor(new LoginInterceptor())
```


这行代码的作用是：
- 将新建的 [LoginInterceptor](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\LoginInterceptor.java#L14-L31) 实例注册到 Spring MVC 拦截器链中
- 返回 [InterceptorRegistration](file://org\springframework\web\servlet\config\annotation\InterceptorRegistration.java#L38-L292) 对象用于链式配置

### 5. 方法实现原理
```java
public InterceptorRegistration addInterceptor(HandlerInterceptor interceptor) {
    // 1. 创建拦截器注册配置对象
    InterceptorRegistration registration = new InterceptorRegistration(interceptor);
    
    // 2. 将注册对象添加到内部列表中
    this.registrations.add(registration);
    
    // 3. 返回注册对象，支持链式调用
    return registration;
}
```


### 6. 拦截器注册流程

#### 步骤1：创建拦截器实例
```java
new LoginInterceptor()  // 创建拦截器对象
```


#### 步骤2：注册到拦截器中心
```java
registry.addInterceptor(new LoginInterceptor())
```


#### 步骤3：返回配置对象
```java
// 返回 InterceptorRegistration 对象，用于进一步配置
InterceptorRegistration registration = registry.addInterceptor(new LoginInterceptor());
```


### 7. 链式配置示例
```java
registry.addInterceptor(new LoginInterceptor())
        .excludePathPatterns("/user/login", "/user/code")  // 排除路径
        .addPathPatterns("/api/**")                        // 指定拦截路径
        .order(1);                                         // 设置执行顺序
```


### 8. 相关类

#### InterceptorRegistry
- **作用**：拦截器注册中心
- **职责**：管理所有注册的拦截器

#### InterceptorRegistration
- **作用**：单个拦截器的配置注册器
- **职责**：提供拦截器的详细配置方法

#### HandlerInterceptor
- **作用**：拦截器接口
- **职责**：定义拦截器的行为规范

### 9. 在配置类中的作用

在 [MvcConfig](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\config\MvcConfig.java#L12-L32) 中，这个方法用于：
1. **注册业务拦截器**：将自定义的登录拦截器和 token 刷新拦截器注册到 Spring MVC
2. **构建拦截器链**：形成请求处理前的拦截器调用链
3. **统一配置管理**：集中管理所有拦截器的配置

### 10. 完整调用链
```java
// 1. Spring MVC 启动时调用 WebMvcConfigurer
@Override
public void addInterceptors(InterceptorRegistry registry) {
    
    // 2. 添加 LoginInterceptor 拦截器
    registry.addInterceptor(new LoginInterceptor())
            .excludePathPatterns(
                "/shop/**",
                "/user/code",
                "/user/login"
            )
            .order(1);
            
    // 3. 添加 RefreshTokenInterceptor 拦截器
    registry.addInterceptor(new RefreshTokenInterceptor(stringRedisTemplate))
            .addPathPatterns("/**")
            .order(0);
}
```


### 11. Spring MVC 拦截器工作机制

```
HTTP请求 → DispatcherServlet → HandlerExecutionChain → 按顺序执行拦截器
                                           ↑
                                   通过 addInterceptor 注册的拦截器列表
```


### 12. 优势

1. **统一管理**：所有拦截器在一处配置和管理
2. **灵活配置**：支持详细的路径匹配和排除规则
3. **顺序控制**：可以精确控制拦截器执行顺序
4. **类型安全**：编译时检查拦截器类型

这是 Spring MVC 中配置拦截器的核心方法，是实现 Web 层横切关注点（如权限控制、日志记录等）的重要机制。