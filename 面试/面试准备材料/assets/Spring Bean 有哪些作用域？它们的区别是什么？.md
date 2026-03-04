👌 你说的应该是 **Spring Bean 的作用域（Scope）**。这个是面试高频考点，确实分为：

- **singleton（单例，Spring 默认）**
- **prototype（原型，每次创建新对象）**
- **request / session / application（Web 环境下的作用域）**
- **websocket（WebSocket 环境下）**

我帮你整理一份答题模板，方便你直接应答。

------

# 📌 面试题

Spring Bean 有哪些作用域？它们的区别是什么？

------

### ✅ 一、概念回答

Spring 为了控制 Bean 的生命周期和共享方式，提供了多种作用域（Scope），可以通过 `@Scope` 注解或 XML 配置指定。

------

### ✅ 二、常见作用域

1. **singleton（默认）**
   - **一个容器中只有一个实例**，所有请求共享。
   - **场景**：Service、Dao、Controller 等无状态 Bean。
2. **prototype**
   - 每次获取 Bean 时都会创建一个新的实例。
   - **场景**：有状态的 Bean，每次调用都需要独立对象（如用户上下文对象）。
3. **request**（Web 环境）
   - 每个 HTTP 请求创建一个 Bean，随请求销毁。
   - **场景**：保存与一次请求绑定的数据（如表单对象）。
4. **session**（Web 环境）
   - 每个 HTTP Session 创建一个 Bean，Session 失效时销毁。
   - **场景**：与用户会话绑定的数据（如购物车对象）。
5. **application**（Web 环境）
   - 整个 Web 应用生命周期共享一个 Bean，相当于 ServletContext 作用域。
   - **场景**：全局配置、应用级缓存。
6. **websocket**（WebSocket 环境）
   - 每个 WebSocket 会话维护一个 Bean。
   - **场景**：即时通讯、长连接数据存储。

------

### ✅ 三、结合项目经验

- 在 **黑马点评** 项目中：
  - Service、Controller 默认是 `singleton`，保证全局复用。
  - 用户信息（登录态）存储在 `ThreadLocal` + Redis，而不是 `session` Bean。
- 在 **苍穹外卖** 项目中：
  - Spring MVC 的请求参数对象用 `request` 作用域，保证线程隔离。

------

### ✅ 四、扩展追问

1. 为什么 Spring 默认作用域是 singleton？
2. prototype Bean 能注入到 singleton Bean 吗？（答：会有问题，需要结合 `ObjectFactory` 或 `Provider` 动态获取）。
3. 如果在多线程环境下使用 singleton Bean，会不会有线程安全问题？
4. SpringBoot 中如何切换作用域？（`@Scope("prototype")` 或者 `@RequestScope` / `@SessionScope`）。
5. 在分布式应用中，`session` scope 会带来什么问题？（答：需要考虑 session 共享，可以用 Redis session）。

------

⚡ **标准回答模板（面试时可直接说）：**

> Spring 提供了多种作用域：singleton（默认，每个容器一个实例）、prototype（每次获取新实例）、request（一次 HTTP 请求）、session（一次会话）、application（整个应用）、websocket（一次 WebSocket 会话）。一般我们在项目中用的最多的是 singleton，比如 Controller 和 Service；如果是一次请求或会话的数据，可以用 request 或 session；prototype 则适合保存有状态的对象。

------

要不要我帮你把 **prototype 注入 singleton 的问题** 也整理成面试答案？这是这道题常见的追问点。