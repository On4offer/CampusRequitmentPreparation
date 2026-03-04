好问题 👍
 我来给你整理成面试题标准回答（结合黑马点评项目场景）。

------

# 面试题：为什么 `RefreshTokenInterceptor` 要优先执行？

## 1. 背景

- 在黑马点评项目中，我们有两个拦截器：
  1. **RefreshTokenInterceptor**：负责校验 Redis 中的 Token、刷新 TTL（滑动过期）、注入用户信息到 `ThreadLocal`。
  2. **LoginInterceptor**：负责鉴权，判断哪些接口必须登录。
- 两者都要处理 Token，但职责不同，**执行顺序很关键**。

------

## 2. 为什么要优先执行？

### （1）**刷新 TTL 要在鉴权之前**

- 如果先执行 `LoginInterceptor`，会发现 `ThreadLocal` 里还没有用户信息，会直接返回 401。
- 而 `RefreshTokenInterceptor` 执行后，会：
  - 从 Redis 取出用户信息
  - 注入到 `ThreadLocal`
  - 顺便刷新 TTL（保证滑动过期）
- 这样后续的 `LoginInterceptor` 就能顺利拿到用户，完成鉴权。

### （2）**保持用户活跃状态**

- 优先执行保证了**只要有合法 Token，就会先刷新 Redis 里的 TTL**。
- 如果 `LoginInterceptor` 拦截了请求，刷新逻辑根本不会执行 → 导致 Token 提前过期，用户体验差。

### （3）**职责分离，解耦鉴权与续期**

- `RefreshTokenInterceptor` 只负责**会话管理**（读取 & 续命 & ThreadLocal 注入）。
- `LoginInterceptor` 只负责**权限控制**（是否允许访问）。
- 顺序保证了两者解耦，各司其职。

------

## 3. 标准回答

> 在黑马点评项目中，`RefreshTokenInterceptor` 必须优先执行，因为它负责从 Redis 校验 Token、刷新 TTL，并将用户信息写入 `ThreadLocal`。只有它先完成，后续的 `LoginInterceptor` 才能正确判断用户是否已登录，否则会直接返回 401。同时，优先刷新 TTL 可以保证活跃用户的会话不会因为未续期而意外过期，提升用户体验。

------

## 4. 扩展追问

- 如果把两个拦截器顺序反了，会发生什么？
- 如果请求是静态资源、验证码接口这种无需登录的路径，两个拦截器如何配置？
- `RefreshTokenInterceptor` 中为什么要在 `afterCompletion` 移除 `ThreadLocal`？
- 如果并发下大量请求同时续期，如何避免 Redis 写放大？

------

要不要我帮你画一个 **执行时序图**（请求到来 → RefreshTokenInterceptor → LoginInterceptor → Controller）？面试时能直观解释为什么要优先执行。