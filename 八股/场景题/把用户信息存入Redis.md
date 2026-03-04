当然可以！「把用户信息存进 Redis」非常适合作为 **Java 后端 / Spring Boot** 面试场景题。下面按你喜欢的**面试题模板**给：概念 → 设计 → 代码 → 使用场景 → 扩展追问（附标准回答）。

------

# 场景题描述（可直接复述）

> 设计登录流程：用户登录成功后，将**登录态与必要的用户信息**存入 Redis，用于后续请求的快速鉴权与读取。要求：
>
> - 生成会话 token；
> - 设计合理的 Redis Key、TTL、序列化方式；
> - 支持**滑动过期**；
> - 提供退出登录、单点/多端登录、主动下线的能力；
> - 兼顾安全与性能。

------

# 一、核心概念 & 方案选择

**为什么存 Redis？**

- 访问快（内存），跨实例共享（分布式友好），易做 TTL 和会话控制。

**存什么？（最小必要原则）**

- `UserDTO`（脱敏的必要字段）：`id, nickname, avatar, roles, perms…`
- 不要存：密码哈希、隐私信息、过大的对象。

**数据结构选择**

- `String`（JSON 字符串）：简单直观，适合整体读写。
- `Hash`：字段级更新更方便，节省流量。
- 一般面试中两者都能解释清楚就行，这里给出 **Hash** 与 **JSON** 两版示例。

------

# 二、Key 设计与会话策略

- Key 模板：`login:token:{uuid}` 或 `login:uid:{uid}:{device}`
- TTL：如 `30min`（可按需调整/“记住我”）
- 滑动过期：每次请求续期（例如重置 TTL 为 30min）
- 多端策略：
  - **单端登录**：同 uid 只允许一个 token（用 `SETNX` 或维护 `login:uid:{uid}` → token）
  - **多端登录**：按设备维度 `device` 区分多个 token
- 注销：`DEL key`，并清理辅助索引（如 `uid→token`）

------

# 三、落地代码（Spring Boot）

## 1）生成 token + 存 Redis（JSON版）

```java
@Service
@RequiredArgsConstructor
public class AuthService {
    private final StringRedisTemplate stringRedisTemplate;
    private static final String KEY_PREFIX = "login:token:";
    private static final long TTL_MINUTES = 30L;

    public String login(String username, String password) {
        // 1. 校验用户名密码（略）→ 得到用户实体 user
        User user = userRepository.findByUsername(username);
        if (user == null || !passwordMatches(password, user.getPasswordHash())) {
            throw new BizException("用户名或密码错误");
        }

        // 2. 转 DTO（脱敏）
        UserDTO dto = new UserDTO(user.getId(), user.getNickname(), user.getAvatar(), user.getRoles());

        // 3. 生成 token
        String token = UUID.randomUUID().toString(true); // Hutool 可用；或自己实现

        // 4. 存 Redis（JSON）
        String key = KEY_PREFIX + token;
        String json = JSON.toJSONString(dto);
        stringRedisTemplate.opsForValue().set(key, json, TTL_MINUTES, TimeUnit.MINUTES);

        // 5. 可选：建立 uid→token 映射（用于单端踢下线）
        // stringRedisTemplate.opsForValue().set("login:uid:" + dto.getId(), token, TTL_MINUTES, TimeUnit.MINUTES);

        return token;
    }

    public void logout(String token) {
        stringRedisTemplate.delete(KEY_PREFIX + token);
        // 可选：同时清理 uid→token 映射
    }
}
```

## 2）使用 Hash 存储（字段更新友好）

```java
public void saveLoginToRedisHash(String token, UserDTO dto) {
    String key = "login:token:" + token;
    Map<String, String> map = new HashMap<>();
    map.put("id", String.valueOf(dto.getId()));
    map.put("nickname", dto.getNickname());
    map.put("avatar", dto.getAvatar());
    map.put("roles", String.join(",", dto.getRoles())); // 简单序列化
    stringRedisTemplate.opsForHash().putAll(key, map);
    stringRedisTemplate.expire(key, 30, TimeUnit.MINUTES);
}
```

## 3）拦截器：鉴权 + 滑动续期 + ThreadLocal

```java
@Component
@RequiredArgsConstructor
public class RefreshTokenInterceptor implements HandlerInterceptor {
    private final StringRedisTemplate stringRedisTemplate;
    private static final String KEY_PREFIX = "login:token:";
    private static final long TTL_MINUTES = 30L;

    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) {
        String token = request.getHeader("authorization");
        if (token == null || token.isBlank()) return true; // 无 token 也放行给后续登录拦截器判定

        String key = KEY_PREFIX + token;
        Map<Object, Object> userMap = stringRedisTemplate.opsForHash().entries(key);
        if (userMap == null || userMap.isEmpty()) return true;

        // 反序列化为 UserDTO（Hash 版）
        UserDTO user = new UserDTO();
        user.setId(Long.parseLong((String) userMap.get("id")));
        user.setNickname((String) userMap.get("nickname"));
        user.setAvatar((String) userMap.get("avatar"));
        user.setRoles(Arrays.asList(((String) userMap.get("roles")).split(",")));

        UserHolder.saveUser(user);

        // 滑动续期
        stringRedisTemplate.expire(key, TTL_MINUTES, TimeUnit.MINUTES);
        return true;
    }

    @Override
    public void afterCompletion(HttpServletRequest request, HttpServletResponse response, Object handler, Exception ex) {
        UserHolder.removeUser();
    }
}
```

> 实战里通常用两个拦截器：
>
> - `RefreshTokenInterceptor`：只要带 token 就续期并注入 ThreadLocal（order 先执行）
> - `LoginInterceptor`：**强校验**某些接口必须登录（未登录返回 401）

------

# 四、使用场景（回答点）

- **常用接口**：下单、支付、收藏、签到、个人中心等
- **性能**：Redis QPS 高、延迟低；可用本地缓存（Caffeine）做短期热点加速
- **扩展**：
  - 单点登录（同账号踢下线）
  - 多端并存（PC/APP）
  - 黑名单/注销全局下发（发布订阅或版本号）

------

# 五、安全与工程细节（加分）

1. **最小化存储**：不存密码哈希/隐私；字段可加签名或版本号
2. **TTL 策略**：关键接口才续期，避免刷请求“永不过期”
3. **防窃取**：HTTPS、短 TTL、绑定 UA/设备指纹（适度）、服务端可校验 IP/设备变更
4. **序列化**：
   - JSON 简单直观；注意类演进（DTO 防止反序列化问题）
   - Hash 适合字段级更新与小变更
5. **并发一致性**：登录/下线原子性（Lua 脚本或事务管道）
6. **限流**：登录/刷新频率限制，防暴力尝试
7. **灰度/多环境**：Key 加上环境前缀 `dev:login:token:…`

------

# 六、标准面试回答（≈1 分钟）

> 登录成功后，我会生成一个 `token`，并以 `login:token:{token}` 作为 Key，把**脱敏的 UserDTO** 存进 Redis（JSON 或 Hash），设置 `30min` 的 TTL。
>  在请求入口的拦截器里，读取 `authorization` 头里的 token，查询 Redis 获取用户信息，放进 `ThreadLocal`，并进行**滑动续期**；在强校验拦截器里对必须登录的接口返回 401。
>  退出登录就是 `DEL key`。如果需要单点登录，会同时维护 `login:uid:{uid} → token` 的映射，通过 `SETNX` 或 Lua 脚本保证原子替换。
>  安全方面坚持最小必要字段、HTTPS、合理 TTL 与限流；工程上选择 JSON/Hash 取舍，并保证拦截器 `afterCompletion` 清理 `ThreadLocal`，避免线程复用导致的内存泄漏。

------

# 七、扩展追问（附要点）

1. **为什么选 Redis 而不是本地内存？** —— 分布式共享，会话一致。
2. **和 JWT 的关系？** —— 可二选一或组合：JWT 无状态；Redis 有状态可强制下线与续期。
3. **如何做“记住我”？** —— 发长期 Refresh Token；短期 Access Token + 刷新换新，服务端保存 Refresh 状态。
4. **如何避免频繁续期带来的写放大？** —— 只在关键接口续期，或采用“阈值续期”（如剩余 <10min 才续）。

------

需要的话，我可以把上面的拦截器注册、DTO、`UserHolder`、以及**单点登录的 Lua 原子脚本**一并补齐，形成一套“可拷贝到项目即用”的模块骨架。