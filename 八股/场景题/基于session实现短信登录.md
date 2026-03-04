下面给你一套**“面试+实战”思路**来回答“基于 Session 实现短信登录”的场景题。面试官要的不是你会写两段代码，而是你能**拆需求→定接口→设计状态与风控→落地代码→可测可扩展**。

------

# 一、需求拆解（用户故事）

1. 发送验证码

- 输入：手机号 phone
- 规则：号码合法；单手机号/单 IP 频控；生成 6 位码；把验证码**与生成时间**写入 Session；调用短信通道（面试可用日志代替）。
- 输出：成功/失败。

2. 验证码登录/注册

- 输入：手机号 + 验证码
- 规则：校验手机号；比对 Session 中验证码与未过期；查库是否已有用户，**没有则创建**；登录成功后将**精简的用户视图**写入 Session。
- 输出：登录成功（返回 200）。

3. 登录态校验（网关/拦截器）

- 每次请求读取 Session 中是否有 user，放入 ThreadLocal，放行；没有就拦截返回 401。

> 图里三张流程图正好对应以上三步：**发验证码**、**登录/注册**、**校验登录态**。

------

# 二、接口与状态设计

## 2.1 API 设计

- `POST /user/code?phone=xxx`  发送验证码
- `POST /user/login`  body: `{phone, code}`  短信登录
- 受保护接口例如：`GET /user/me`，需登录

## 2.2 Session 中存什么（Key/Value）

- `SESSION_KEY_CODE_<phone>` → `{code, ts}`  （含时间戳做过期控制）
- `SESSION_KEY_USER` → `UserDTO`（只放必要字段：id、nickName、icon… 不放敏感信息）

> **为什么把 code 和 ts 放 Session？**
>  题目限定“基于 Session”，所以 Session 既承载验证码也承载登录态；在分布式场景换成 Redis 即可（下面有扩展）。

------

# 三、核心逻辑（伪代码+关键点）

## 3.1 发送验证码（防抖+频控+过期）

```java
public Result sendCode(String phone, HttpSession session) {
    // 1) 基础校验
    if (RegexUtils.isPhoneInvalid(phone)) return Result.fail("手机号格式错误");

    // 2) 频率限制：同手机号60s内仅可发送一次（面试表述：防刷）
    String key = "SESSION_KEY_CODE_" + phone;
    CodeBox box = (CodeBox) session.getAttribute(key);
    long now = System.currentTimeMillis();
    if (box != null && now - box.getTs() < 60_000) {
        return Result.fail("发送过于频繁，请稍后再试");
    }

    // 3) 生成 6 位随机码
    String code = RandomUtil.randomNumbers(6);

    // 4) 存入 Session（带时间戳，手动控制 TTL）
    session.setAttribute(key, new CodeBox(code, now));

    // 5) 发短信（演示用日志）
    log.debug("短信验证码已发送：{}", code);
    return Result.ok();
}
```

**要点**

- Session 没有天然 TTL，这里用时间戳自己做过期；真实项目可以**换 Redis + EXPIRE**。
- 面试务必提到**限流**（手机号 + IP 维度）。

## 3.2 短信登录（比对+注册即登录+会话安全）

```java
public Result login(LoginFormDTO form, HttpSession session) {
    String phone = form.getPhone();
    String code  = form.getCode();

    if (RegexUtils.isPhoneInvalid(phone)) return Result.fail("手机号格式错误");

    // 1) 取出验证码并校验
    String key = "SESSION_KEY_CODE_" + phone;
    CodeBox box = (CodeBox) session.getAttribute(key);
    if (box == null || System.currentTimeMillis() - box.getTs() > 5 * 60_000) {
        return Result.fail("验证码已失效");
    }
    if (!box.getCode().equals(code)) return Result.fail("验证码错误");

    // 2) 查询或创建用户（注册即登录）
    User user = query().eq("phone", phone).one();
    if (user == null) user = createUserWithPhone(phone);

    // 3) 会话安全：防 Session 固定（固定攻击）
    // 做法：登录成功前后重置会话ID（某些容器提供 changeSessionId）
    try { request.changeSessionId(); } catch (Throwable ignore) {}

    // 4) 只存 UserDTO，避免大对象 & 敏感字段
    session.setAttribute("SESSION_KEY_USER", toDTO(user));

    // 5) 一次性验证码：用完即删（可选）
    session.removeAttribute(key);
    return Result.ok();
}
```

**要点**

- **验证码有效期**控制（如 5 分钟）；**一次性使用**更安全。
- **Session 固定攻击防御**：登录成功后更换会话 ID。
- **最小化用户信息**放 Session，避免把密码、salt 等敏感字段塞进去。

## 3.3 登录态拦截器（ThreadLocal 传递）

```java
public boolean preHandle(HttpServletRequest req, HttpServletResponse resp, Object handler) {
    UserDTO u = (UserDTO) req.getSession().getAttribute("SESSION_KEY_USER");
    if (u == null) {
        resp.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
        return false;
    }
    UserHolder.set(u); // ThreadLocal
    return true;
}
public void afterCompletion(...) { UserHolder.remove(); } // 防内存泄漏
```

------

# 四、数据库与实体（最小闭环）

- 表：`tb_user(id, phone UNIQUE, nick_name, icon, create_time, update_time)`
- `createUserWithPhone(phone)`：随机生成 nickname（如 “user_3f9a”），插入并返回。

------

# 五、边界与风控（面试加分点）

1. **限流/防刷**：
   - 维度：手机号 + IP；策略：60s 一次、日上限 N 次、滑动窗口。
   - 结果：提升风控意识。
2. **重放/暴力猜码**：
   - 验证失败次数累加，超过阈值临时冻结该手机号的验证（或加图形验证码）。
3. **会话安全**：
   - 登录后 `changeSessionId`；Cookie 设置 `HttpOnly/SameSite=Lax(or Strict)/Secure(HTTPS)`。
   - 退出登录 `session.invalidate()`。
4. **数据一致性**：
   - 并发注册用**唯一索引**保证 `phone` 只有一条。
5. **可观测性**：
   - 记录发码/登录操作日志（phone 脱敏）、错误码设计、审计链路。

------

# 六、可测试性（怎么证明你写对了）

- 单元测试：
  - 合法/非法手机号；首发码成功；60s 内二次发送被拒；验证码正确/错误/过期；首次登录触发注册；二次登录直接读取用户。
- 集成测试：
  - 登录后访问受保护接口 200；登出后 401；多浏览器/多 Session 行为分离。

------

# 七、和 Redis 版的差异（扩展说法）

> 如果面试官追问“生产一般不会用 Session 吧？”——自然切到 Redis 方案：

- **验证码**：`SET code:phone 123456 EX 300 NX` ；频控：`SETNX send:phone 1 EX 60`
- **登录态**：`token -> UserDTO(JSON)`，把 token 写 Cookie/前端存储；无状态横向扩展友好；可做**续期**（滑动过期）。
- **拦截器**：从请求头/Cookie 取 token 去 Redis 换用户，放 ThreadLocal。

------

# 八、标准回答模板（面试版 60–90 秒）

> “这个功能我会分三块做：**发码、登录、校验登录态**。
>  发码接口接收手机号，先做格式校验和频控（手机号+IP 两个维度，60s 一次、日上限），生成 6 位验证码，把验证码和生成时间放到 Session（或 Redis，生产更常用 Redis 并设置 TTL），同时通过短信通道发送。
>  登录接口拿到手机号+验证码，先校验手机号，再从 Session 取验证码并校验有效期与一次性，成功后根据手机号查库，不存在就创建用户（用唯一索引保证幂等）。登录成功后我会把**精简的用户 DTO**放到 Session，并**更换会话 ID**防 Session 固定攻击；同时把一次性验证码删掉。
>  受保护接口我会加一个拦截器：从 Session 取出用户 DTO，没有就返回 401；有的话放到 ThreadLocal，完成后清理避免内存泄漏。
>  安全上我会控制发送频率、失败次数、Cookie 设置 HttpOnly+SameSite+Secure，并记录审计日志。若做分布式，我会把 Session/验证码全部切到 Redis，用 token 方案做登录态和续期。”

------

用这套结构回答，既覆盖了题目的**Session 实现**，也给出了**生产级做法与安全要点**，面试官会非常买账。你上面给的代码已经能跑通闭环了，按我这套再补上**频控/过期/一次性/换会话ID/拦截器**，就从“能跑”升级到“能上线”。