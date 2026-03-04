这个问题考察的是你有没有把 **ThreadLocal 从理论落到实战**。我给你一份 **标准项目化回答**，直接套到黑马点评/苍穹外卖里就能用。

------

## ✅ 面试题：在实际项目中用过 ThreadLocal 吗？

### 一、常见使用场景

1. **保存用户信息**

   - 在 Web 项目里，每个请求对应一个线程。
   - 登录后，把用户信息存入 ThreadLocal，这样在后续的业务逻辑（Service/DAO 层）里就可以直接获取用户，而不用层层传参。

   ```java
   public class UserHolder {
       private static final ThreadLocal<UserDTO> tl = new ThreadLocal<>();
       public static void saveUser(UserDTO user){ tl.set(user); }
       public static UserDTO getUser(){ return tl.get(); }
       public static void removeUser(){ tl.remove(); }
   }
   ```

   - 在拦截器里存入，在 `afterCompletion` 里清理：

     ```java
     // 登录校验拦截器
     public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object handler) {
         UserDTO user = getUserFromRedis(req);
         if (user == null) return false;
         UserHolder.saveUser(user);
         return true;
     }
     
     public void afterCompletion(HttpServletRequest req, HttpServletResponse res, Object handler, Exception ex) {
         UserHolder.removeUser(); // 避免内存泄漏
     }
     ```

   ✅ 在黑马点评项目里：

   - 登录成功后把 `UserDTO` 存入 Redis + ThreadLocal；
   - 下游服务（如发布笔记、点赞、下单）直接用 `UserHolder.getUser()` 获取当前用户信息。

2. **事务/数据库连接管理**

   - 在一些老项目（未使用 Spring 事务管理器）里，ThreadLocal 用来绑定当前线程的 `Connection`，保证同一事务中使用同一个连接。
   - 这种方式能避免在方法调用链中反复传递 Connection 参数。

------

### 二、为什么要这样做？

- 避免方法层层传参，简化代码结构。
- 保证一个线程内的数据上下文一致性（如用户信息、事务环境）。
- 性能上比同步开销更小，因为数据隔离不需要加锁。

------

### 三、风险与规避

- **内存泄漏风险**：线程池中线程不销毁，ThreadLocalMap 中的 value 残留。
  - ✅ 解决方案：在请求结束时调用 `remove()`。
- **误用风险**：如果跨线程使用 ThreadLocal，会拿不到数据（因为每个线程独立）。

------

### 四、标准回答（面试模板）

> 在项目中我用过 ThreadLocal，主要是在 Web 系统中保存用户信息。比如在黑马点评项目里，用户登录后我会在拦截器中把用户信息存入 ThreadLocal，这样后续的业务逻辑层可以直接获取用户，不用层层传参。请求结束时我会在 `afterCompletion` 里调用 remove 方法清理，避免线程池环境下内存泄漏。另外在一些没有 Spring 管理事务的项目里，我也用过 ThreadLocal 来绑定数据库连接，保证事务一致性。

------

要不要我帮你再整理一份 **“扩展追问”清单**？比如面试官可能接着问：

- 为什么要在 `afterCompletion` 里 remove，而不是在业务逻辑中？
- 如果不 remove，会发生什么？
- ThreadLocal 和全局静态变量存用户信息有什么区别？