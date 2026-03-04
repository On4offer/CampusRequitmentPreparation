## excludePathPatterns 方法介绍

### 1. 基本定义
[excludePathPatterns()](file://org\springframework\web\servlet\config\annotation\InterceptorRegistration.java#L124-L136) 是 Spring MVC 框架中用于配置拦截器排除路径模式的方法。

### 2. 所属工具和类
- **框架**：Spring Web MVC
- **类**：`org.springframework.web.servlet.config.annotation.InterceptorRegistration`
- **方法签名**：`public InterceptorRegistration excludePathPatterns(String... patterns)`

### 3. 方法功能
指定哪些 URL 路径模式不应该被当前拦截器拦截，即排除特定路径的拦截处理。

### 4. 在代码中的使用
```java
registry.addInterceptor(new LoginInterceptor())
        .excludePathPatterns(
                "/shop/**",
                "/voucher/**",
                "/shop-type/**",
                "/upload/**",
                "/blog/hot",
                "/user/code",
                "/user/login"
        )
```


这段代码的作用是：
- 为 [LoginInterceptor](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\LoginInterceptor.java#L14-L31) 配置排除路径
- 这些路径将不会触发登录拦截器的处理逻辑

### 5. 方法实现原理
```java
public InterceptorRegistration excludePathPatterns(String... patterns) {
    // 1. 将排除路径模式添加到内部集合中
    this.excludePatterns.addAll(Arrays.asList(patterns));
    
    // 2. 返回当前对象，支持链式调用
    return this;
}
```


### 6. 路径匹配规则

#### Ant 风格路径匹配
```java
// 1. 精确匹配
"/user/login"         // 只匹配完全相同的路径

// 2. 路径通配符
"/shop/**"            // 匹配 /shop/ 及其所有子路径
                      // 例如: /shop/list, /shop/detail/123, /shop/category/electronics

// 3. 单字符通配符
"/user/?"             // 匹配 /user/ 后跟单个字符
                      // 例如: /user/a, /user/1  但不匹配 /user/admin

// 4. 单层路径匹配
"/shop/*"             // 匹配 /shop/ 后跟一层路径
                      // 例如: /shop/list  但不匹配 /shop/category/list
```


### 7. 排除路径示例

```java
// 配置的排除路径
.excludePathPatterns(
    "/shop/**",        // 商店相关接口
    "/user/code",      // 获取验证码接口
    "/user/login"      // 用户登录接口
)

// 以下请求不会被 LoginInterceptor 拦截：
GET /shop/list              ✓
GET /shop/detail/123        ✓
POST /user/code             ✓
POST /user/login            ✓

// 以下请求会被 LoginInterceptor 拦截：
GET /api/user/profile       ✗
POST /order/create          ✗
GET /blog/my-posts          ✗
```


### 8. 相关方法

| 方法                            | 功能               |
| ------------------------------- | ------------------ |
| `excludePathPatterns(patterns)` | 排除指定路径模式   |
| `addPathPatterns(patterns)`     | 指定拦截路径模式   |
| `order(order)`                  | 设置拦截器执行顺序 |
| `pathMatcher(pathMatcher)`      | 设置路径匹配器     |

### 9. 在配置类中的作用

在 [MvcConfig](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\config\MvcConfig.java#L12-L32) 中，这个方法用于：
1. **权限控制**：允许匿名访问某些公共资源接口
2. **用户体验**：让用户能够访问登录、注册等基础功能
3. **系统设计**：区分需要认证和不需要认证的接口

### 10. 完整配置流程

```java
@Override
public void addInterceptors(InterceptorRegistry registry) {
    // 1. 添加拦截器
    InterceptorRegistration registration = registry.addInterceptor(new LoginInterceptor());
    
    // 2. 配置排除路径（这些路径不拦截）
    registration.excludePathPatterns(
        "/user/code",     // 获取验证码
        "/user/login",    // 用户登录
        "/shop/**"        // 商店信息（公开）
    );
    
    // 3. 设置执行顺序
    registration.order(1);
}
```


### 11. 与 addPathPatterns 的关系

```java
// 方式1：默认拦截所有，排除特定路径
registry.addInterceptor(new LoginInterceptor())
        .excludePathPatterns("/user/login", "/user/code");  // 排除登录相关

// 方式2：只拦截特定路径
registry.addInterceptor(new LoginInterceptor())
        .addPathPatterns("/api/**", "/user/**")             // 只拦截API和用户相关
        .excludePathPatterns("/user/login", "/user/code");  // 但排除登录相关
```


### 12. 优势

1. **灵活控制**：精确控制哪些路径需要/不需要拦截
2. **用户体验**：允许用户访问必要的公开接口
3. **安全性**：确保敏感接口得到保护
4. **链式调用**：支持流畅的 API 配置风格

这是 Spring MVC 中实现精细化权限控制的重要方法，通过合理配置排除路径，可以在保证安全性的同时提供良好的用户体验。