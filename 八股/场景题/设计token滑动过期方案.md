完全可以！“**基于 Java+Redis 的 Token 滑动过期（Sliding Expiration）方案**”是非常典型、很考察工程落地与权衡取舍的**场景题**。下面我按“面试题模板”来给你一份可直接背/可直接落地的答案。

------

# 一、题目描述（给面试官的场景）

公司后端为多端（Web/小程序/APP）提供 REST API。登录后发放 Token。要求：

1. 用户**活跃就不掉线**，长期不活跃自动下线；
2. 支持**多端多设备**并行；
3. **可强制下线/注销**；
4. **安全可控**，兼顾性能与成本。
    请设计一个**Token 滑动过期**方案，并说明关键实现、时序流程、数据结构、并发与安全处理、以及与传统 JWT/Session 的对比。

------

# 二、核心概念速记

- **滑动过期（Sliding Expiration）**：会话有一个**不活跃超时**（idle timeout）。只要在超时时间内有访问，就**自动续期**；若超过超时无人访问，会话失效。
- **访问令牌（AT, Access Token）**：短期凭证，用来访问业务接口；到期需要用 RT 刷新。
- **刷新令牌（RT, Refresh Token）**：较长寿命，用于获取新 AT；通常**只在刷新接口使用**，不直连业务。
- **会话状态存储**：用 **Redis** 存储用户会话（含设备信息、权限快照、最近活跃时间等），利用 **key 的 TTL 实现滑动过期**。

------

# 三、架构与数据设计

## 3.1 令牌策略（推荐）

- **AT（短期，5~30 分钟）**：JWT 或随机串均可。
- **RT（长期，7~30 天）**：**只在 /auth/refresh 使用**，并做**令牌轮换（Rotation）**，被使用一次就作废旧 RT。

> 为什么 AT 要短？——降低泄露风险；为什么要 RT？——避免频繁登录，又能安全地续期。

## 3.2 Redis Key 设计

- `login:session:{tenant}:{uid}:{deviceId}` → Hash
  - 字段：`uid, deviceId, roles, permsHash, issuedAt, lastActiveAt, atId (可选), rtId (可选), ip, ua, ...`
  - **TTL=idleTimeout**（如 30min），每次访问**延长 TTL**（滑动）
- `login:rt:{rtId}` → String（或 Hash）
  - 值：`{uid, deviceId, sessionKey, expireAt, rotated=false}`
  - TTL=RT 期限（如 7d）
- `blacklist:at:{jti}`（可选）→ 用于提前吊销 AT（JWT 黑名单）

> 多设备并行：不同 deviceId 即不同 session key，各自独立滑动。

------

# 四、时序流程（文字版时序图）

## 4.1 登录

1. 用户提交账号密码/验证码
2. 服务器鉴权通过 → 生成 **sessionKey** 与 **RT**（rtId），写入：
   - `login:session:*`（TTL=30min）
   - `login:rt:rtId`（TTL=7d）
3. 生成 **AT（5~30min）**并返回：`{AT, RT片段/标识, deviceId, 过期秒数}`

## 4.2 访问业务接口（携带 AT）

1. 解析 AT（或查 Redis 校验）
2. 校验通过 → **滑动续期**：`expire(login:session:*)` 重置 TTL=30min
3. 更新 `lastActiveAt`（可在滑动阈值内再写，减少写压）
4. 继续执行业务

> **写放大优化**：只在距离过期阈值（如 < 1/3 TTL）时才续期，避免每次都写。

## 4.3 刷新令牌（AT 过期或将过期）

1. 客户端调用 `/auth/refresh`，带 RT
2. 校验 `login:rt:rtId`：存在、未过期、未旋转、与 `sessionKey` 对上
3. **令牌轮换**：
   - 置旧 RT `rotated=true`（或直接删除）
   - 生成新 RT（新 rtId）与新 AT
   - 更新 `login:session:*`（如延长 TTL）
4. 返回新 AT 与新 RT 标识

> **防重放**：旧 RT 一旦被使用即失效；若遭窃取，第二次使用会失败。

## 4.4 注销/踢下线

- 删除 `login:session:*`
- 删除/作废 `login:rt:*`
- 可选：将当前 AT 的 `jti` 放入黑名单，给一个短 TTL（剩余有效期）

------

# 五、关键实现（Java/Spring 伪代码）

## 5.1 业务拦截器（滑动续期）

```java
public boolean preHandle(HttpServletRequest req, HttpServletResponse res, Object h) {
    String at = req.getHeader("Authorization");
    if (StrUtil.isBlank(at)) return true; // 放行到匿名接口或让后续鉴权处理

    // 1) 解析/校验 AT（签名、过期、jti 黑名单）
    Claims claims = jwt.verify(at);
    String sessionKey = claims.get("sk", String.class); // 会话键
    String jti = claims.getId();

    // 2) 会话存在才算登录态
    BoundHashOperations<String, Object, Object> ops = redis.boundHashOps(sessionKey);
    Map<Object,Object> session = ops.entries();
    if (session == null || session.isEmpty()) {
        throw new UnauthException("session expired");
    }

    // 3) 滑动续期（阈值触发，减少写）
    Long ttl = redis.getExpire(sessionKey, TimeUnit.SECONDS);
    if (ttl != null && ttl < 10 * 60) { // 距离过期 < 10min 再续 30min
        redis.expire(sessionKey, 30, TimeUnit.MINUTES);
        ops.put("lastActiveAt", String.valueOf(System.currentTimeMillis()));
    }

    return true;
}
```

## 5.2 刷新接口（RT 轮换）

```java
public RefreshResp refresh(String rt) {
    String rtKey = "login:rt:" + parseRtId(rt);
    RtRecord record = redis.get(rtKey);
    if (record == null || record.isRotated() || record.isExpired()) {
        throw new UnauthException("invalid refresh token");
    }

    String sessionKey = record.getSessionKey();
    if (!redis.hasKey(sessionKey)) {
        throw new UnauthException("session expired");
    }

    // 令牌轮换
    record.setRotated(true);
    redis.set(rtKey, record, Duration.ofHours(1)); // 给短点时间窗口或直接DEL

    String newRtId = genId();
    redis.set("login:rt:" + newRtId,
            new RtRecord(uid, deviceId, sessionKey, now+7d, false),
            Duration.ofDays(7));

    // 生成新 AT
    String at = jwt.issue(uid, Map.of("sk", sessionKey), 15 * 60);

    // 适度延长 session TTL
    redis.expire(sessionKey, 30, TimeUnit.MINUTES);

    return new RefreshResp(at, newRtId);
}
```

------

# 六、参数建议（可背诵）

- **AT 有效期**：15 分钟
- **会话 idle TTL（滑动）**：30 分钟
- **RT 有效期**：7 天
- **续期阈值**：TTL < 10 分钟时才续期
- **多设备**：`sessionKey` 维度包含 `deviceId`
- **权限快照**：`permsHash` 写入会话；权限变更时刷新/强制踢出

------

# 七、并发与安全要点

1. **幂等与竞态**：刷新接口要防止**并发双发**（可用 Lua 对 `rotated` 位做 CAS）。
2. **RT 轮换窗口**：旧 RT 用一次即失效；为处理网络抖动可给旧 RT 一个极短“宽限 TTL”（如 30s），同时标记 `rotated=true`，第二次使用必失败。
3. **AT 黑名单（可选）**：需要“立即失效”时（风控、主动登出）可对当前 AT 的 `jti` 入黑名单。
4. **重放防护**：AT 短期、HTTPS 传输、RT 仅用于刷新接口；可绑定 `ip/ua` 指纹（权衡误杀）。
5. **封禁/强退**：统一走 `sessionKey` 删除 + 黑名单。
6. **监控审计**：记录登录/刷新/续期/注销日志；加入告警（异常刷新频率、跨地区登录等）。

------

# 八、与其它方案对比（面试必问）

| 方案                         | 特点                                      | 优点                          | 缺点/适用                                |
| ---------------------------- | ----------------------------------------- | ----------------------------- | ---------------------------------------- |
| 纯 Session（Redis）          | 仅服务端状态，Cookie/Token 携带 sessionId | 简单、可滑动 TTL、易强退      | 需要集中存储，跨域需处理                 |
| 纯 JWT（无服务端状态）       | 无状态                                    | 简化存储、CDN 友好            | **无法滑动过期**、无法即时强退，需黑名单 |
| **JWT + Redis 会话（推荐）** | JWT 当 AT，Redis 记录会话并滑动           | 既能滑动/强退，又减少查库负担 | 实现稍复杂，需维护 RT 与会话一致性       |

------

# 九、典型使用场景

- **ToC 高并发登录**：活跃用户不断续期，不活跃用户自然回收。
- **多端登录**：手机/平板/PC 各自 session 滑动。
- **风控/强退**：命中风险策略立即让指定 session 失效。

------

# 十、测试与演示点（面试中主动提）

- **时间旅行测试**：模拟 N 分钟无访问，验证过期；模拟频繁访问，验证 TTL 续期。
- **并发刷新**：10 并发同时刷新，只允许 1 成功。
- **多设备**：A、B 设备互不影响；可单独踢 A。
- **安全用例**：复用旧 RT、盗用 AT、黑名单即时生效。

------

# 十一、可复述的标准回答（30–60 秒版）

> 我采用 **“AT 短期 + RT 长期 + Redis 会话滑动”** 的混合方案。用户登录后创建 `login:session:{uid}:{deviceId}`，设定 **30 分钟 TTL**；发放 **15 分钟 AT** 和 **7 天 RT**。每次业务请求在拦截器中校验 AT 后，**仅在 TTL 低于阈值**时对 session 执行 **expire 重置**（滑动续期），并更新 `lastActiveAt`。AT 过期由 `/auth/refresh` 用 RT 换新，RT 采用 **令牌轮换** 防重放。注销或风控强退时，直接删除对应 session，并可将当前 AT 的 `jti` 放入黑名单以**立刻**失效。这样既保证了活跃用户不断线，也能对不活跃会话自动回收，同时具备多设备管理与安全可控能力。

------

# 十二、可扩展追问（准备答案要点）

1. **如何降低续期写放大？**——阈值续期、批量管道、异步刷新。
2. **如何做单点登录（SSO）与跨域？**——网关统一签发/校验，域名/跨域 Cookie 配置或前端持 Header。
3. **如何立即生效权限变更？**——会话存 `permsHash`，权限变更时对该用户所有 `sessionKey` 置失效。
4. **如何处理时钟漂移与多集群？**——统一 NTP，同步签名密钥，Redis Cluster + Key HashTag。
5. **为什么不用纯 JWT 滑动？**——JWT 自身不可续期，只能发新 Token；若无服务端状态就无法判定会话“活跃”与“强退”。

------

如果你需要，我可以把上面的**拦截器、刷新接口**按你项目的 Spring Boot 代码风格（比如你正在写的 `RefreshTokenInterceptor`）直接改成**可运行的模板代码**，连同 Redis key 常量与 Lua 脚本一起给到你。