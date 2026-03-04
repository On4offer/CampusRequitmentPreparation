## getHeader 方法介绍

### 1. 基本定义
`getHeader()` 是 Java Servlet API 中 `HttpServletRequest` 接口提供的方法，用于获取 HTTP 请求头信息。

### 2. 所属工具和类
- **工具/框架**：Java Servlet API（Java EE 标准）
- **接口**：`javax.servlet.http.HttpServletRequest`
- **方法签名**：`String getHeader(String name)`

### 3. 方法功能
从 HTTP 请求头中获取指定名称的头部字段值。

### 4. 参数说明
- **name**：请求头字段名称（不区分大小写）
- **返回值**：对应请求头字段的值，如果不存在则返回 `null`

### 5. 在代码中的使用
```java
String token = request.getHeader("authorization");
```


这行代码的作用是：
- 从 HTTP 请求头中获取名为 "authorization" 的字段值
- 通常用于获取认证令牌（Bearer Token）

### 6. HTTP 请求头示例
```
GET /api/user HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
User-Agent: Mozilla/5.0
Accept: application/json
```


执行 `request.getHeader("authorization")` 会返回：
```
"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```


### 7. 相关方法

| 方法                         | 功能                                      |
| ---------------------------- | ----------------------------------------- |
| `getHeader(String name)`     | 获取指定名称的请求头值                    |
| `getHeaders(String name)`    | 获取指定名称的所有请求头值（Enumeration） |
| `getHeaderNames()`           | 获取所有请求头名称（Enumeration）         |
| `getIntHeader(String name)`  | 获取整数类型的请求头值                    |
| `getDateHeader(String name)` | 获取日期类型的请求头值                    |

### 8. 使用场景

#### (1) Token 认证
```java
// 获取 JWT Token
String authHeader = request.getHeader("Authorization");
if (authHeader != null && authHeader.startsWith("Bearer ")) {
    String token = authHeader.substring(7);
}
```


#### (2) 内容协商
```java
// 获取客户端接受的内容类型
String accept = request.getHeader("Accept");
```


#### (3) 客户端信息
```java
// 获取用户代理信息
String userAgent = request.getHeader("User-Agent");
```


### 9. 注意事项

#### (1) 大小写不敏感
```java
// 以下写法效果相同
request.getHeader("Authorization");
request.getHeader("authorization");
request.getHeader("AUTHORIZATION");
```


#### (2) 返回值可能为 null
```java
String token = request.getHeader("authorization");
if (token != null) {
    // 处理 token
}
```


### 10. 在拦截器中的作用
在 [RefreshTokenInterceptor](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\utils\RefreshTokenInterceptor.java#L22-L59) 中，这个方法用于：
1. **身份验证**：获取客户端发送的认证令牌
2. **会话管理**：基于令牌验证用户身份
3. **权限控制**：决定是否允许访问受保护的资源

这是 Web 应用中实现无状态认证的标准做法。