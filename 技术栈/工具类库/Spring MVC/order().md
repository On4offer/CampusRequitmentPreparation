## order 方法介绍

### 1. 基本定义
[order()](file://org\springframework\web\servlet\config\annotation\InterceptorRegistration.java#L177-L188) 是 Spring MVC 框架中用于设置拦截器执行顺序的方法。

### 2. 所属工具和类
- **框架**：Spring Web MVC
- **类**：`org.springframework.web.servlet.config.annotation.InterceptorRegistration`
- **方法签名**：`public InterceptorRegistration order(int order)`

### 3. 方法功能
设置当前拦截器在拦截器链中的执行顺序，数字越小优先级越高，越先执行。

### 4. 在代码中的使用
```java
// LoginInterceptor 设置为 order(1)
registry.addInterceptor(new LoginInterceptor())
        .excludePathPatterns(...)
        .order(1);  // 设置执行顺序为1

// RefreshTokenInterceptor 设置为 order(0)
registry.addInterceptor(new RefreshTokenInterceptor(stringRedisTemplate))
        .addPathPatterns("/**")
        .order(0);  // 设置执行顺序为0
```


这段代码的作用是：
- 设置 [RefreshTokenInterceptor](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\RefreshTokenInterceptor.java#L22-L59) 优先执行（order=0）
- 设置 [LoginInterceptor](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\LoginInterceptor.java#L14-L31) 后执行（order=1）

### 5. 方法实现原理
```java
public InterceptorRegistration order(int order) {
    // 1. 设置拦截器的执行顺序
    this.order = order;
    
    // 2. 返回当前对象，支持链式调用
    return this;
}
```


### 6. 执行顺序示例

#### 配置：
```java
registry.addInterceptor(new LoginInterceptor()).order(1);
registry.addInterceptor(new RefreshTokenInterceptor(stringRedisTemplate)).order(0);
registry.addInterceptor(new LoggingInterceptor()).order(2);
```


#### 执行顺序：
```
请求处理流程：
DispatcherServlet 
    → RefreshTokenInterceptor (order=0) ← 最先执行
    → LoginInterceptor (order=1)        ← 第二执行
    → LoggingInterceptor (order=2)      ← 最后执行
    → Controller
```


### 7. 为什么要设置执行顺序

在当前项目中，执行顺序很重要：

```java
// 1. RefreshTokenInterceptor (order=0) - 先执行
//    - 刷新 token 有效期
//    - 从 Redis 获取用户信息并保存到 ThreadLocal
//    - 必须在 LoginInterceptor 之前执行

// 2. LoginInterceptor (order=1) - 后执行
//    - 检查 ThreadLocal 中是否有用户信息
//    - 决定是否需要登录
```


### 8. 相关方法

| 方法                            | 功能               |
| ------------------------------- | ------------------ |
| `order(int order)`              | 设置拦截器执行顺序 |
| `excludePathPatterns(patterns)` | 排除路径模式       |
| `addPathPatterns(patterns)`     | 添加路径模式       |
| `pathMatcher(pathMatcher)`      | 设置路径匹配器     |

### 9. 默认执行顺序

```java
// 如果不设置 order，默认按照添加顺序执行
@Override
public void addInterceptors(InterceptorRegistry registry) {
    // 第一个添加的拦截器，order=0（默认）
    registry.addInterceptor(new FirstInterceptor());
    
    // 第二个添加的拦截器，order=1（默认）
    registry.addInterceptor(new SecondInterceptor());
    
    // 第三个添加的拦截器，order=2（默认）
    registry.addInterceptor(new ThirdInterceptor());
}
```


### 10. 在配置类中的作用

在 [MvcConfig](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\config\MvcConfig.java#L12-L32) 中，[order()](file://org\springframework\web\servlet\config\annotation\InterceptorRegistration.java#L177-L188) 方法用于：
1. **确保执行顺序**：保证 token 刷新在登录检查之前执行
2. **逻辑依赖**：[RefreshTokenInterceptor](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\RefreshTokenInterceptor.java#L22-L59) 为 [LoginInterceptor](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\LoginInterceptor.java#L14-L31) 提供用户信息
3. **系统稳定性**：避免因执行顺序错误导致的功能异常

### 11. 完整执行流程

```java
// HTTP 请求到达
1. RefreshTokenInterceptor.preHandle()  // order=0
   - 验证 token
   - 刷新有效期
   - 保存用户信息到 ThreadLocal

2. LoginInterceptor.preHandle()         // order=1
   - 检查 ThreadLocal 中的用户信息
   - 决定是否放行请求

3. Controller 处理业务逻辑

4. 响应返回后：
   RefreshTokenInterceptor.afterCompletion()
   LoginInterceptor.afterCompletion()
```


### 12. 优势

1. **精确控制**：可以精确控制拦截器的执行顺序
2. **逻辑分离**：不同职责的拦截器可以按依赖关系排序
3. **系统稳定**：避免因执行顺序导致的逻辑错误
4. **链式调用**：支持流畅的 API 配置风格

这是 Spring MVC 中管理拦截器执行顺序的核心方法，对于构建可靠的 Web 应用拦截机制至关重要。