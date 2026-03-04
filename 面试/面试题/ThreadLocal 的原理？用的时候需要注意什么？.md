好问题 👍，这题在多线程面试里经常考，尤其是涉及 **用户上下文、数据库连接、线程池复用** 等场景。下面我给你一个标准化答案。

------

# 🎯 面试题

**ThreadLocal 的原理？用的时候需要注意什么？**

------

## ✅ 标准回答

1. **原理**

- 每个 `Thread` 内部维护一个 **ThreadLocalMap**，key 是 `ThreadLocal` 对象，value 是实际存储的值（通常是 **线程特定的上下文信息** 或 **状态数据**，即每个线程独立需要的数据）
- 调用 `threadLocal.set(value)` 时，会把值存到当前线程的 `ThreadLocalMap`。
- 调用 `threadLocal.get()` 时，会从当前线程的 `ThreadLocalMap` 里取值。
- 本质：**为每个线程提供一份独立变量副本**，线程之间互不干扰。

------

## ⚙️ 底层实现

- **Thread 类**里有一个 `ThreadLocalMap` 属性。
- `ThreadLocalMap` 底层是 **数组 + 开放寻址**，key 用的是 **弱引用（WeakReference）**，避免 ThreadLocal 对象本身不被回收。
- 但 **value 没有弱引用**，若不手动 `remove()`，可能导致 **内存泄漏**（ThreadLocal 对象 GC 掉了，但 value 残留在线程中）。

------

## 📌 使用场景（结合项目）

- **用户上下文保存**：
   黑马点评项目里，可以用 `ThreadLocal<UserDTO>` 保存用户信息，避免在每层方法传递参数。
- `ThreadLocal` 的 value 一般存放 **与当前线程强相关、且需要线程隔离的数据**。典型有：
  1. **用户上下文**
     - 例如保存登录用户的 `UserDTO`，避免在每层方法都传参。
     - 在黑马点评/苍穹外卖项目里，请求经过拦截器后，把用户信息放入 `ThreadLocal<UserDTO>`，后续业务层直接取。
  2. **数据库连接 / Session**
     - 每个线程独享一个 `Connection`，保证事务隔离。
     - Spring 的事务管理就是通过 `ThreadLocal` 保存 `ConnectionHolder`。
  3. **事务状态**
     - 保存事务是否开启、回滚标志等。
  4. **格式化工具类**
     - 比如 `SimpleDateFormat` 是线程不安全的，可以用 ThreadLocal 给每个线程一份副本。
  5. **请求级别的上下文数据**
     - TraceId（链路追踪 ID）、Locale（语言环境）、Request Attributes 等。
- **数据库连接管理**：
   每个线程持有自己的 Connection，避免并发冲突。
- **事务隔离**：
   在 Spring 框架中，事务信息（如 Connection、事务状态）就是用 ThreadLocal 保存的。

------

## ⚠️ 注意事项

1. **及时清理**：线程池场景下线程会复用，ThreadLocal 不清理会造成脏数据污染。

   ```java
   try {
       threadLocal.set(user);
       // do something
   } finally {
       threadLocal.remove();
   }
   ```

2. **内存泄漏风险**：

   - key 是弱引用，GC 后 key=null，但 value 仍然存在，可能被遗忘。
   - 必须主动调用 `remove()` 释放。

3. **不适合大对象**：存放大对象容易加重内存占用。

------

## 🔍 追问

1. **ThreadLocal 和 synchronized 的区别？**
    👉 ThreadLocal 是 **空间换时间**，每个线程一份副本；synchronized 是 **时间换空间**，多个线程排队访问同一个资源。
2. **为什么 ThreadLocalMap 的 key 是弱引用？**
    👉 避免 ThreadLocal 对象不再使用时，因强引用导致无法回收。
3. **为什么线程池里 ThreadLocal 更容易出问题？**
    👉 线程池线程复用，如果不清理 ThreadLocal，线程上一次存的值可能“污染”下一次任务。

------

要不要我帮你整理一个 **“10 秒速答版”**，适合面试时快速背诵？