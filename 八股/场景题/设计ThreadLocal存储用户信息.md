完全可以 👍，「用 `ThreadLocal` 存储用户信息」是非常好的场景题。

它能考察你对：

- **线程隔离**、**拦截器执行流程** 的理解
- **登录态传递** 的实践能力
- **内存泄漏风险** 与 **清理机制** 的掌握

------

## 🎯 场景题设计

> 在一个电商系统中，很多接口都需要获取当前登录用户的信息。如果每个接口都去 Redis 查询一次，会很麻烦。
>  请你设计一个方案，利用 **ThreadLocal** 在拦截器里保存用户信息，并在业务代码中随时获取。

------

## 📝 面试回答思路

### 1. 为什么用 ThreadLocal？

- **请求与线程绑定**：SpringMVC 默认是“一次请求 = 一个线程”。
- **线程隔离**：ThreadLocal 给每个线程单独存储一份用户信息，不会相互干扰。
- **简化代码**：业务层直接调用 `UserHolder.getUser()` 就能拿到当前用户，无需层层传参。

------

### 2. 设计实现

定义一个 `UserHolder` 工具类：

```java
public class UserHolder {
    private static final ThreadLocal<UserDTO> tl = new ThreadLocal<>();

    // 保存用户
    public static void saveUser(UserDTO user){
        tl.set(user);
    }

    // 获取用户
    public static UserDTO getUser(){
        return tl.get();
    }

    // 移除用户（防止内存泄漏）
    public static void removeUser(){
        tl.remove();
    }
}
```

------

### 3. 拦截器中使用

在 **登录拦截器** 里：

```java
@Override
public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
    String token = request.getHeader("authorization");
    if (token == null) {
        response.setStatus(401);
        return false;
    }
    String userJson = stringRedisTemplate.opsForValue().get("login:token:" + token);
    if (userJson == null) {
        response.setStatus(401);
        return false;
    }
    // 反序列化
    UserDTO user = JSON.parseObject(userJson, UserDTO.class);

    // 存到 ThreadLocal
    UserHolder.saveUser(user);

    return true;
}

@Override
public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
    // 请求结束，必须清理
    UserHolder.removeUser();
}
```

------

### 4. 业务层使用

在 **Controller / Service** 里：

```java
@GetMapping("/me")
public Result me() {
    UserDTO user = UserHolder.getUser(); // 直接取出当前登录用户
    return Result.ok(user);
}
```

------

### 5. 面试扩展追问

1. **如果不 remove 会怎样？**
   - 可能导致内存泄漏，因为 ThreadLocal 使用的是 **线程池复用** 的线程，变量可能残留到下一个请求。
2. **和 Session 的区别？**
   - Session 是跨请求存储，ThreadLocal 是单次请求内存储。
3. **分布式环境下还适用吗？**
   - ThreadLocal 仅在当前服务内有效，分布式环境要结合 **Redis/JWT** 共享用户态。

------

## ✅ 总结标准答法（2 分钟速答）

> 我会设计一个 `UserHolder` 工具类，内部用 `ThreadLocal<UserDTO>` 存储当前请求的用户信息。在登录拦截器里校验 token 后，把用户对象放进 ThreadLocal；请求结束时调用 `remove()` 清理，避免内存泄漏。这样在业务代码中可以直接 `UserHolder.getUser()` 获取用户信息，而不用层层传参。
>  这种方式简单高效，但要注意线程池环境下的内存泄漏问题，必须在 `afterCompletion` 清理。

------

要不要我帮你整理一份 **拦截器 + ThreadLocal 用户存储的全流程图**（从请求 → 拦截器 → ThreadLocal → Controller → 清理），面试时能一图秒杀？

## 追问原理：

这个问题问得非常到位 ✅，也是面试里经常被追问的地方。我们来拆开讲：

------

## 1. **ThreadLocal 存在哪里？**

- **不是存在 ThreadLocal 对象里**，而是存在 **线程对象（Thread）里**。
- 每个 `Thread` 内部都有一个 `ThreadLocalMap`，这是一个类似 `Map<ThreadLocal, Object>` 的结构：

```java
public class Thread {
    ThreadLocal.ThreadLocalMap threadLocals = null; 
}
```

当我们调用：

```java
tl.set(user);
```

实际是把 `(this ThreadLocal → user)` 存进当前线程的 `threadLocals` 里。

因此：

- **同一个线程**可以反复 `get()` 拿到数据。
- **不同线程**之间完全隔离（各自有自己的 `ThreadLocalMap`）。

------

## 2. **为什么要在拦截器里用？**

SpringMVC 请求处理流程：

```
浏览器请求 → DispatcherServlet → Interceptor.preHandle()
          → Controller → Service → Dao
          → Interceptor.afterCompletion() → 返回响应
```

- **拦截器的 preHandle()**：请求刚进来时执行 → 校验 token → 放入 ThreadLocal。
- **Controller/Service**：业务层就可以直接 `UserHolder.getUser()`，不用传参。
- **afterCompletion()**：请求结束时清理 ThreadLocal，避免内存泄漏。

👉 所以用拦截器来做是最自然的，等于在 **请求生命周期的入口存，出口清理**。

------

## 3. **ThreadLocal 的原理是什么？**

- 本质：**为每个线程绑定一份独立变量副本**。
- 实现方式：通过 **Thread → ThreadLocalMap → (ThreadLocal, value)** 的关系来隔离数据。
- 关键点：
  - 每个线程自己管理一份 Map，不共享。
  - `ThreadLocal` 只是提供了一种访问当前线程 Map 的“钥匙”。

### 简化流程

1. `tl.set(value)` → 存储到当前线程的 `ThreadLocalMap`
2. `tl.get()` → 从当前线程的 `ThreadLocalMap` 取数据
3. `tl.remove()` → 删除映射，防止线程复用时脏数据泄漏

------

## 4. **为什么必须 remove？**

- 在 Tomcat/Netty 这种容器里，请求线程通常是 **线程池复用** 的。
- 如果不清理，线程里的 `ThreadLocalMap` 可能把上一个请求的用户信息带到下一个请求，造成 **用户串数据** 或 **内存泄漏**。

所以我们在拦截器的 `afterCompletion()` 必须调用：

```java
UserHolder.removeUser();
```

------

## 5. 面试可扩展回答

- **和 Session 的区别**：
  - Session 是“跨请求存储”，ThreadLocal 是“单次请求内存储”。
- **和参数传递的区别**：
  - ThreadLocal 避免了层层传参，适合做“上下文信息存取”。
- **常见应用场景**：
  - 存储用户信息（UserDTO）
  - 存储事务上下文（DataSource、Transaction）
  - 存储日志链路 ID（traceId）

------

✅ **总结一句话（面试标准答法）：**
 ThreadLocal 的数据其实存在每个线程内部的 `ThreadLocalMap` 中，不同线程互不影响。我们在拦截器里用它，是因为请求和线程一一对应，可以在请求入口存用户信息，在请求出口清理。它的原理就是通过线程作为载体，给每个线程绑定一份独立的数据副本，避免了多线程之间的共享问题。

------

要不要我帮你画一张 **ThreadLocal 原理图（Thread → ThreadLocalMap → value）+ 请求生命周期示意图**？这样你答题时既能讲原理又能形象展示。

