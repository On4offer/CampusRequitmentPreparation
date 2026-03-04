基于 Recis 设计缓存层存储店铺信息，采用 Cache-Aside 策略，通过逻辑过期解决缓存击穿问题，缓存空值解决缓存穿透问题，动态TTL解决缓存雪崩问题。


基于你的代码，整理一套面试问答，模拟真实面试场景：

---

## 面试问答（模拟真实面试）

### 第一轮：项目介绍与基础理解

**面试官**：你好，我看到你简历上写了“基于 Redis 设计缓存层存储店铺信息，采用 Cache-Aside 策略，通过逻辑过期解决缓存击穿问题，缓存空值解决缓存穿透问题，动态TTL解决缓存雪崩问题”。能先介绍一下这个项目的背景和你的职责吗？

**你（建议回答）**：
- 项目背景：点评类应用，店铺信息查询频繁，需要降低数据库压力
- 职责：设计并实现缓存层，解决缓存三大问题
- 技术选型：Redis + Cache-Aside + 逻辑过期

---

**面试官**：好，先说说什么是 Cache-Aside 策略？为什么选择它而不是 Write-Through 或 Write-Behind？

**你（建议回答）**：
- Cache-Aside：读时先查缓存，miss 查库并回写；写时先写库再删缓存
- 优点：实现简单、灵活、缓存命中率高
- 缺点：首次访问延迟、可能出现不一致窗口
- 为什么不选 Write-Through：写操作频繁时性能差，需要同步写缓存
- 为什么不选 Write-Behind：需要异步队列，复杂度高，一致性更难保证

---

**面试官追问**：你说写时先写库再删缓存，那如果删除缓存失败怎么办？会不会导致数据不一致？

**你（建议回答）**：
- 删除失败会存在不一致窗口，但影响有限：下次读会 miss，查库后回写新值
- 优化：1）重试机制；2）延迟双删（写库后删除，延迟再删一次）；3）消息队列异步删除；4）Binlog 订阅同步删除
- 代码中 `ShopServiceImpl.update()` 先更新 DB，再删除缓存，配合 `@Transactional` 保证 DB 成功后再删缓存

---

### 第二轮：缓存三大问题深入

**面试官**：你提到用缓存空值解决缓存穿透，能详细说说吗？

**你（建议回答）**：
- 问题：恶意请求不存在的 key，每次都穿透到 DB
- 方案：DB 查不到时，写入空值（如空字符串），设置短 TTL（如 2 分钟）
- 代码实现：
```60:88:src/main/java/com/hmdp/utils/CacheClient.java
public <R,ID> R queryWithPassThrough(...){
    // 判断命中的是否是空值
    if (json != null) {
        return null; // 空值直接返回
    }
    // DB查询为空时，写入空值缓存
    if (r == null) {
        stringRedisTemplate.opsForValue().set(key, "", CACHE_NULL_TTL, TimeUnit.MINUTES);
        return null;
    }
}
```

---

**面试官追问**：空值缓存 TTL 设置为 2 分钟，如果 2 分钟内这个店铺真的被创建了，用户查询会不会一直返回空？

**你（建议回答）**：
- 会存在短暂不一致，但可接受：2 分钟后自动过期，新请求会查库
- 优化：1）新增店铺时主动删除对应的空值 key；2）使用布隆过滤器预判存在性；3）空值 TTL 更短（如 30 秒）
- 实际场景：店铺创建频率低，2 分钟窗口影响小

---

**面试官**：逻辑过期解决缓存击穿，具体是怎么实现的？

**你（建议回答）**：
- 问题：热点 key 过期瞬间，大量并发同时访问 DB
- 方案：逻辑过期 + 异步重建
- 实现：
  1. 写入时用 `RedisData` 包装数据和逻辑过期时间，不设置物理 TTL
  2. 读取时判断逻辑过期，过期则获取互斥锁，异步重建，主线程返回旧值
  3. 代码：
```91:137:src/main/java/com/hmdp/utils/CacheClient.java
public <R, ID> R queryWithLogicalExpire(...){
    // 判断是否过期
    if(expireTime.isAfter(LocalDateTime.now())) {
        return r; // 未过期直接返回
    }
    // 已过期，获取锁异步重建
    if (isLock){
        CACHE_REBUILD_EXECUTOR.submit(() -> {
            // 异步重建缓存
        });
    }
    return r; // 返回过期数据
}
```

---

**面试官追问**：如果异步重建过程中，数据库查询很慢，或者失败了怎么办？

**你（建议回答）**：
- 数据库慢：主线程已返回旧值，不影响用户体验；但旧数据可能过期较久
- 失败处理：
  1. try-catch 捕获异常，记录日志
  2. 释放锁，避免死锁
  3. 可增加重试机制（最多 3 次）
  4. 监控告警，及时发现 DB 问题
- 代码中已有 finally 释放锁：
```129:131:src/main/java/com/hmdp/utils/CacheClient.java
finally {
    unlock(lockKey);
}
```

---

**面试官追问**：为什么逻辑过期能解决击穿，而物理过期不行？

**你（建议回答）**：
- 物理过期：key 过期后立即消失，大量请求同时 miss，都去查 DB
- 逻辑过期：key 不过期，即使逻辑过期也返回旧值，只有一个线程重建，其他线程读旧值，避免并发穿透
- 代价：可能读到过期数据，需要容忍最终一致性

---

**面试官**：动态 TTL 解决缓存雪崩，你是怎么实现的？

**你（建议回答）**：
- 问题：大量 key 同时过期，导致请求洪峰打到 DB
- 方案：动态 TTL，避免同时过期
- 实现：
  1. `CacheClient.set()` 接受 `time` 和 `unit` 参数，调用方自定义 TTL
  2. 可结合业务设置不同 TTL：热点数据长 TTL + 逻辑过期，冷数据短 TTL
  3. 可加入随机抖动：`ttl = baseTTL + Random(0, jitter)`
- 代码：
```33:35:src/main/java/com/hmdp/utils/CacheClient.java
public void set(String key, Object value, Long time, TimeUnit unit) {
    stringRedisTemplate.opsForValue().set(key, JSONUtil.toJsonStr(value), time, unit);
}
```

---

**面试官追问**：你的代码里 `CACHE_SHOP_TTL = 30L` 是固定的，怎么体现“动态”？

**你（建议回答）**：
- 当前实现：`RedisConstants` 是默认值，实际调用可传不同 TTL
- 更动态的做法：
  1. 根据数据热度分级：热点 1 小时 + 逻辑过期，普通 30 分钟，冷数据 5 分钟
  2. 加入随机抖动：`ttl = 30 + Random(0, 10)` 分钟
  3. 根据访问频率动态调整：访问次数多的延长 TTL
- 改进建议：在 `CacheClient` 中封装 `setWithRandomTTL()` 方法

---

### 第三轮：实现细节与代码追问

**面试官**：你的互斥锁是怎么实现的？有什么问题吗？

**你（建议回答）**：
- 实现：使用 Redis `SETNX`（`setIfAbsent`）实现分布式锁
- 代码：
```195:198:src/main/java/com/hmdp/utils/CacheClient.java
private boolean tryLock(String key) {
    Boolean flag = stringRedisTemplate.opsForValue().setIfAbsent(key, "1", 10, TimeUnit.SECONDS);
    return BooleanUtil.isTrue(flag);
}
```

---

**面试官追问**：这个锁实现有什么问题？如果获取锁的线程挂了，锁会一直存在吗？

**你（建议回答）**：
- 已设置 TTL（10 秒），避免死锁
- 问题：
  1. 锁的 value 是固定 "1"，无法识别持有者，可能误删其他线程的锁
  2. 锁 TTL 固定 10 秒，如果缓存重建超过 10 秒，锁会提前释放
  3. 没有锁续期机制
- 改进：
  1. value 使用 UUID + 线程ID
  2. 使用 Redisson 的看门狗机制自动续期
  3. 释放锁时先判断 value 是否匹配

---

**面试官**：`queryWithMutex` 方法中，如果获取锁失败，为什么要 sleep 50ms 然后递归重试？

**你（建议回答）**：
- 避免忙等待，降低 CPU 占用
- 50ms 是经验值，平衡响应速度和系统负载
- 递归重试可能导致栈溢出，可改为循环 + 最大重试次数
- 代码：
```169:172:src/main/java/com/hmdp/utils/CacheClient.java
if (!isLock) {
    Thread.sleep(50);
    return queryWithMutex(keyPrefix, id, type, dbFallback, time, unit);
}
```

---

**面试官追问**：如果一直获取不到锁怎么办？会不会无限递归？

**你（建议回答）**：
- 当前实现会无限递归，存在风险
- 改进：
  1. 增加最大重试次数（如 3 次）
  2. 超过次数后直接返回 null 或抛出异常
  3. 记录日志，监控锁竞争情况
  4. 可考虑降级策略：直接查库或返回默认值

---

**面试官**：`CACHE_REBUILD_EXECUTOR` 线程池大小是 10，这个是怎么确定的？

**你（建议回答）**：
- 10 是经验值，需要根据实际业务调整
- 考虑因素：
  1. 并发重建请求数
  2. DB 查询耗时
  3. 服务器 CPU 核心数
- 计算公式：`线程数 = CPU核心数 * 2 + 1`（IO 密集型）
- 改进：可配置化，根据监控数据动态调整

---

### 第四轮：性能与一致性

**面试官**：逻辑过期方案下，用户可能读到过期数据，你们能接受吗？

**你（建议回答）**：
- 店铺信息变化不频繁，短暂过期可接受
- 如果对一致性要求高：
  1. 关键字段（如价格）单独缓存，使用物理过期
  2. 使用版本号机制，读取时对比版本
  3. 写操作时主动刷新缓存
- 业务场景：店铺信息主要是展示，不是实时交易，最终一致性可接受

---

**面试官**：如何保证缓存和数据库的一致性？

**你（建议回答）**：
- 当前方案：写库后删除缓存（Cache-Aside）
- 问题：删除失败或并发读写可能导致不一致
- 优化：
  1. 延迟双删：写库后删除，延迟再删一次
  2. 消息队列：写库后发送消息，异步删除缓存
  3. Binlog 订阅：Canal 监听 MySQL Binlog，自动删除缓存
  4. 版本号：缓存中存储版本号，读取时对比

---

**面试官追问**：如果更新店铺信息时，先删除缓存再写库，会有什么问题？

**你（建议回答）**：
- 问题：删除缓存后、写库完成前，如果有读请求，会查库并回写旧值到缓存
- 时序：
  1. 线程 A 删除缓存
  2. 线程 B 读请求，缓存 miss，查库（旧值），写缓存
  3. 线程 A 写库（新值）
  4. 结果：缓存是旧值，DB 是新值
- 所以先写库再删缓存更合理

---

### 第五轮：扩展与优化

**面试官**：如果 Redis 挂了，整个缓存层不可用，你们怎么处理？

**你（建议回答）**：
- 降级策略：
  1. 熔断器：Redis 不可用时，直接查库，避免等待超时
  2. 多级缓存：本地缓存（Caffeine）+ Redis，Redis 挂掉时使用本地缓存
  3. 限流：Redis 不可用时，限制请求量，保护数据库
- 高可用：
  1. Redis 主从 + 哨兵，自动故障转移
  2. Redis Cluster 集群模式
  3. 多机房部署，就近访问

---

**面试官**：如何监控缓存的效果？比如命中率、穿透率？

**你（建议回答）**：
- 监控指标：
  1. 缓存命中率：`命中次数 / 总请求数`
  2. 缓存穿透率：空值命中次数
  3. 缓存重建次数：逻辑过期触发重建的次数
  4. 锁竞争情况：获取锁失败的次数
- 实现：
  1. AOP 切面统计缓存操作
  2. 使用 Micrometer + Prometheus 暴露指标
  3. Grafana 可视化展示
  4. 设置告警阈值

---

**面试官**：如果店铺信息更新很频繁，你的方案还适用吗？

**你（建议回答）**：
- 频繁更新时，Cache-Aside 删除缓存会导致命中率下降
- 优化：
  1. 写操作时更新缓存而非删除（Write-Through）
  2. 使用消息队列异步更新缓存
  3. 只缓存热点数据，冷数据不缓存
  4. 使用本地缓存 + Redis 多级缓存
- 需要根据业务特点选择策略

---

### 第六轮：场景题

**面试官**：假设现在有一个热点店铺，QPS 达到 10000，你的方案能扛住吗？

**你（建议回答）**：
- 分析：
  1. Redis 单机 QPS 可达 10 万+，10000 QPS 可承受
  2. 逻辑过期方案：大部分请求命中缓存，只有过期时才会重建
  3. 如果逻辑过期时间设置合理（如 1 小时），重建频率低
- 优化：
  1. 使用本地缓存（Caffeine）作为一级缓存，Redis 作为二级缓存
  2. 逻辑过期时间设置更长（如 2 小时）
  3. 提前预热：在过期前 10 分钟异步重建
  4. Redis 集群分片，避免单点压力

---

**面试官**：如果现在要你优化这个缓存方案，你会从哪些方面入手？

**你（建议回答）**：
- 代码层面：
  1. 锁实现改用 Redisson，支持可重入、自动续期
  2. 增加最大重试次数，避免无限递归
  3. 空值缓存 TTL 可配置化
  4. 增加缓存预热机制
- 架构层面：
  1. 多级缓存：本地缓存 + Redis
  2. 布隆过滤器：预判 key 是否存在，减少穿透
  3. 缓存预热：系统启动时加载热点数据
  4. 监控告警：完善的监控体系
- 性能优化：
  1. 序列化优化：使用 Kryo 替代 JSON
  2. 批量查询：支持批量获取缓存
  3. 异步化：非关键路径异步处理

---

## 总结：核心要点

1. Cache-Aside 策略：先查缓存，miss 查库写缓存；写库后删缓存
2. 缓存穿透：空值缓存 + 短 TTL
3. 缓存击穿：逻辑过期 + 异步重建 + 互斥锁
4. 缓存雪崩：动态 TTL + 随机抖动
5. 一致性：写库后删缓存，可配合延迟双删、消息队列
6. 高可用：Redis 主从、集群、多级缓存、降级策略

---

## 建议准备

1. 画流程图：Cache-Aside 读写流程、逻辑过期重建流程
2. 准备数据：缓存命中率、QPS 提升、DB 压力下降
3. 思考边界：Redis 故障、锁竞争、数据一致性
4. 代码细节：能解释每一行代码的作用和设计意图

需要我补充其他场景或深入某个问题吗？

------

实现基于 Redis 的 Token 校验与滑动过期机制，结合 ThreadLocal 管理用户上下文，提升用户登录体验。


基于代码，整理面试问答，模拟真实面试场景：

---

## 面试问答（模拟真实面试）

### 第一轮：项目介绍与基础理解

**面试官**：你好，我看到你简历上写了"实现基于 Redis 的 Token 校验与滑动过期机制，结合 ThreadLocal 管理用户上下文"。能先介绍一下这个功能的背景和实现思路吗？

**你（建议回答）**：
- 背景：无状态登录，支持多端登录，提升用户体验
- 核心思路：
  1. 登录时生成 UUID 作为 token，将用户信息存入 Redis Hash
  2. 每次请求通过拦截器校验 token，刷新过期时间（滑动过期）
  3. 使用 ThreadLocal 存储当前请求的用户信息，避免重复查询
- 技术选型：Redis Hash + Spring MVC 拦截器 + ThreadLocal

---

**面试官**：为什么选择 Redis 存储 token，而不是 JWT？

**你（建议回答）**：
- Redis 存储的优势：
  1. 服务端可控：可主动失效 token（如登出、封禁）
  2. 存储用户完整信息：无需每次解析 JWT
  3. 支持滑动过期：每次请求刷新过期时间
  4. 可统计在线用户数
- JWT 的劣势：
  1. 无法主动失效（除非维护黑名单）
  2. 信息泄露后无法立即撤销
  3. 滑动过期需要额外机制
- 业务场景：需要支持强制下线、封禁等，Redis 更合适

---

**面试官追问**：Redis 存储 token 有什么缺点？

**你（建议回答）**：
- 缺点：
  1. 需要 Redis 可用性，Redis 故障会影响登录
  2. 内存占用：每个 token 占用内存
  3. 跨服务需要共享 Redis
- 优化：
  1. Redis 高可用（主从、哨兵、集群）
  2. 多级缓存：本地缓存 + Redis
  3. 定期清理过期 token

---

### 第二轮：Token 生成与存储

**面试官**：登录时 token 是怎么生成的？为什么用 UUID？

**你（建议回答）**：
- 生成方式：使用 Hutool 的 `UUID.randomUUID().toString(true)` 生成
- 代码：
```108:110:src/main/java/com/hmdp/service/impl/UserServiceImpl.java
// 7.1.随机生成token，作为登录令牌
String token = UUID.randomUUID().toString(true);
```
- 为什么用 UUID：
  1. 唯一性：避免碰撞
  2. 不可预测：安全性好
  3. 无业务含义：不暴露用户信息
- 为什么不直接用用户ID：
  1. 容易被猜测
  2. 无法支持多端登录
  3. 安全性差

---

**面试官追问**：UUID 的长度是多少？会不会太长？

**你（建议回答）**：
- UUID 标准格式：32 位十六进制（去掉连字符）
- `toString(true)` 会去掉连字符，长度 32
- 如果觉得长，可以：
  1. Base64 编码缩短
  2. 使用雪花算法生成 ID
  3. 使用 Redis 自增 ID + 时间戳
- 实际场景：32 字符可接受，前端存储无压力

---

**面试官**：用户信息为什么用 Redis Hash 存储，而不是 String？

**你（建议回答）**：
- Hash 的优势：
  1. 部分更新：只更新单个字段，无需序列化整个对象
  2. 内存效率：Hash 压缩存储，比 JSON 字符串更省内存
  3. 原子操作：支持 HINCRBY 等原子操作
- 代码：
```131:135:src/main/java/com/hmdp/service/impl/UserServiceImpl.java
// 7.3.存入 Redis 的 Hash 类型
String tokenKey = LOGIN_USER_KEY + token;
stringRedisTemplate.opsForHash().putAll(tokenKey, userMap);
// 7.4.设置token有效期
stringRedisTemplate.expire(tokenKey, LOGIN_USER_TTL, TimeUnit.MINUTES);
```
- String 的劣势：
  1. 更新需要序列化整个对象
  2. 内存占用更大
  3. 无法部分更新

---

**面试官追问**：Hash 存储的 key 和 field 分别是什么？

**你（建议回答）**：
- Key：`login:token:{token}`，如 `login:token:abc123def456`
- Field：用户信息字段，如 `id`、`nickName`、`icon`
- Value：字段对应的字符串值
- 结构示例：
```
login:token:abc123def456
  ├─ id: "1"
  ├─ nickName: "user123"
  └─ icon: "http://..."
```

---

### 第三轮：Token 校验与拦截器

**面试官**：Token 校验是怎么实现的？拦截器的执行顺序是什么？

**你（建议回答）**：
- 实现：使用两个拦截器
  1. `RefreshTokenInterceptor`（order=0）：刷新 token，将用户信息存入 ThreadLocal
  2. `LoginInterceptor`（order=1）：校验 ThreadLocal 中是否有用户
- 代码：
```19:32:src/main/java/com/hmdp/config/MvcConfig.java
// token刷新的拦截器
registry.addInterceptor(new RefreshTokenInterceptor(stringRedisTemplate))
    .addPathPatterns("/**").order(0);
// 登录拦截器
registry.addInterceptor(new LoginInterceptor())
    .excludePathPatterns(...).order(1);
```
- 执行顺序：先执行 RefreshTokenInterceptor，再执行 LoginInterceptor

---

**面试官追问**：为什么需要两个拦截器？一个不行吗？

**你（建议回答）**：
- 职责分离：
  1. `RefreshTokenInterceptor`：所有请求都执行，刷新 token，填充 ThreadLocal
  2. `LoginInterceptor`：只拦截需要登录的接口，校验 ThreadLocal
- 好处：
  1. 代码清晰：职责单一
  2. 灵活配置：不同接口可配置不同拦截规则
  3. 性能优化：RefreshTokenInterceptor 即使 token 无效也放行，不阻塞
- 如果合并：
  1. 逻辑复杂
  2. 难以区分哪些接口需要登录
  3. 不符合单一职责原则

---

**面试官**：`RefreshTokenInterceptor` 的具体实现逻辑是什么？

**你（建议回答）**：
- 流程：
  1. 从请求头获取 token（`authorization`）
  2. 如果 token 为空，直接放行
  3. 从 Redis 查询用户信息（Hash 结构）
  4. 如果用户不存在，放行（可能是未登录）
  5. 将用户信息存入 ThreadLocal
  6. 刷新 token 过期时间（滑动过期）
  7. 请求结束后清理 ThreadLocal
- 代码：
```32:53:src/main/java/com/hmdp/utils/RefreshTokenInterceptor.java
@Override
public boolean preHandle(...) {
    // 1.获取请求头中的token
    String token = request.getHeader("authorization");
    // 2.基于TOKEN获取redis中的用户
    String key = LOGIN_USER_KEY + token;
    Map<Object, Object> userMap = stringRedisTemplate.opsForHash().entries(key);
    // 3.判断用户是否存在
    if (userMap.isEmpty()) {
        return true; // 放行，让LoginInterceptor处理
    }
    // 5.将查询到的hash数据转为UserDTO
    UserDTO userDTO = BeanUtil.fillBeanWithMap(userMap, new UserDTO(), false);
    // 6.存在，保存用户信息到 ThreadLocal
    UserHolder.saveUser(userDTO);
    // 7.刷新token有效期
    stringRedisTemplate.expire(key, LOGIN_USER_TTL, TimeUnit.MINUTES);
    return true;
}
```

---

**面试官追问**：为什么 `RefreshTokenInterceptor` 中用户不存在也放行？

**你（建议回答）**：
- 原因：
  1. 有些接口不需要登录（如商品列表、店铺详情）
  2. 让 `LoginInterceptor` 决定是否需要登录
  3. 避免重复校验逻辑
- 如果在这里拦截：
  1. 无法区分哪些接口需要登录
  2. 需要维护白名单，代码复杂
  3. 不符合职责分离原则

---

**面试官**：`LoginInterceptor` 是怎么判断用户是否登录的？

**你（建议回答）**：
- 判断方式：检查 ThreadLocal 中是否有用户信息
- 代码：
```14:24:src/main/java/com/hmdp/utils/LoginInterceptor.java
@Override
public boolean preHandle(...) {
    // 1.判断是否需要拦截（ThreadLocal中是否有用户）
    if (UserHolder.getUser() == null) {
        // 没有，需要拦截，设置状态码
        response.setStatus(401);
        // 拦截
        return false;
    }
    // 有用户，则放行
    return true;
}
```
- 为什么用 ThreadLocal：
  1. 避免重复查询 Redis
  2. 线程隔离，线程安全
  3. 请求结束后自动清理

---

### 第四轮：滑动过期机制

**面试官**：什么是滑动过期？你是怎么实现的？

**你（建议回答）**：
- 滑动过期：每次请求时刷新 token 过期时间，用户活跃则 token 不过期
- 实现：在 `RefreshTokenInterceptor` 中调用 `expire` 刷新过期时间
- 代码：
```50:50:src/main/java/com/hmdp/utils/RefreshTokenInterceptor.java
stringRedisTemplate.expire(key, LOGIN_USER_TTL, TimeUnit.MINUTES);
```
- 过期时间：`LOGIN_USER_TTL = 36000` 分钟（25 天）

---

**面试官追问**：滑动过期和固定过期有什么区别？

**你（建议回答）**：
- 固定过期：
  1. Token 在固定时间后过期，无论是否活跃
  2. 用户需要重新登录
  3. 体验差
- 滑动过期：
  1. 用户活跃时自动刷新过期时间
  2. 长期不活跃才过期
  3. 体验好，减少登录次数
- 对比：
  - 固定过期：登录后 7 天过期，即使每天使用
  - 滑动过期：每天使用则不过期，30 天不活跃才过期

---

**面试官追问**：滑动过期有什么安全问题？

**你（建议回答）**：
- 安全问题：
  1. Token 泄露后，攻击者持续使用会一直有效
  2. 无法强制用户下线（除非删除 token）
- 优化：
  1. 设置最大过期时间：即使滑动，超过 30 天强制重新登录
  2. 记录最后活跃时间：超过阈值要求重新验证
  3. 支持强制下线：管理员删除 token
  4. 多端登录管理：支持查看和踢出其他设备

---

**面试官**：如果用户一直不活跃，token 什么时候过期？

**你（建议回答）**：
- 当前实现：25 天后过期（`LOGIN_USER_TTL = 36000` 分钟）
- 问题：如果用户在第 25 天访问，token 会再延长 25 天，可能永远不过期
- 改进：
  1. 设置最大过期时间：如 30 天，超过后强制重新登录
  2. 记录首次登录时间：超过最大时间后不再刷新
  3. 代码示例：
```java
// 获取token创建时间
Long createTime = stringRedisTemplate.opsForHash().get(key, "createTime");
if (System.currentTimeMillis() - createTime > MAX_EXPIRE_TIME) {
    // 超过最大时间，不刷新，要求重新登录
    return;
}
```

---

### 第五轮：ThreadLocal 管理用户上下文

**面试官**：为什么用 ThreadLocal 存储用户信息？有什么好处？

**你（建议回答）**：
- 原因：
  1. 避免重复查询 Redis：一次请求只查一次
  2. 线程隔离：每个请求独立，线程安全
  3. 代码简洁：业务代码直接 `UserHolder.getUser()`，无需传参
- 代码：
```5:19:src/main/java/com/hmdp/utils/UserHolder.java
public class UserHolder {
    private static final ThreadLocal<UserDTO> tl = new ThreadLocal<>();
    
    public static void saveUser(UserDTO user){
        tl.set(user);
    }
    
    public static UserDTO getUser(){
        return tl.get();
    }
    
    public static void removeUser(){
        tl.remove();
    }
}
```

---

**面试官追问**：ThreadLocal 有什么内存泄漏风险？你是怎么避免的？

**你（建议回答）**：
- 内存泄漏风险：
  1. ThreadLocal 的 key 是弱引用，value 是强引用
  2. 如果线程是线程池复用的，ThreadLocal 可能一直存在
  3. 导致 value 无法回收
- 避免方式：
  1. 在 `afterCompletion` 中主动清理
  2. 代码：
```55:59:src/main/java/com/hmdp/utils/RefreshTokenInterceptor.java
@Override
public void afterCompletion(...) {
    // 移除用户
    UserHolder.removeUser();
}
```
- 为什么在 `afterCompletion`：
  1. 请求处理完成后清理
  2. 即使异常也会执行
  3. 避免线程池复用导致的内存泄漏

---

**面试官追问**：如果忘记调用 `removeUser()` 会怎样？

**你（建议回答）**：
- 问题：
  1. 线程池复用线程时，ThreadLocal 中的值会残留
  2. 下一个请求可能拿到上一个请求的用户信息
  3. 导致安全问题（用户 A 的请求拿到用户 B 的信息）
- 解决方案：
  1. 使用 `try-finally` 确保清理
  2. 使用 `@Cleanup` 注解（Lombok）
  3. 使用过滤器统一清理
- 改进代码：
```java
@Override
public boolean preHandle(...) {
    try {
        // ... 业务逻辑
        return true;
    } finally {
        // 确保清理
        UserHolder.removeUser();
    }
}
```

---

**面试官**：ThreadLocal 在异步场景下会有什么问题？

**你（建议回答）**：
- 问题：
  1. 异步线程无法获取主线程的 ThreadLocal 值
  2. 导致用户信息丢失
- 场景：
```java
// 主线程
UserHolder.saveUser(userDTO);
// 异步线程
CompletableFuture.runAsync(() -> {
    UserDTO user = UserHolder.getUser(); // null，获取不到
});
```
- 解决方案：
  1. 传递用户信息：将 `userDTO` 作为参数传递
  2. 使用 `InheritableThreadLocal`：子线程可继承父线程的值（但线程池不适用）
  3. 使用 `TransmittableThreadLocal`（阿里开源）：支持线程池传递
  4. 使用上下文对象：封装用户信息，显式传递

---

### 第六轮：性能与安全

**面试官**：每次请求都要查询 Redis，会不会有性能问题？

**你（建议回答）**：
- 性能分析：
  1. Redis 查询很快（通常 < 1ms）
  2. 但高并发下可能成为瓶颈
- 优化：
  1. 本地缓存：热点用户信息缓存到本地（Caffeine），减少 Redis 查询
  2. 连接池：合理配置 Redis 连接池大小
  3. 批量查询：支持批量获取用户信息
  4. 异步刷新：token 刷新可以异步执行
- 代码示例：
```java
// 本地缓存 + Redis
UserDTO user = localCache.get(token);
if (user == null) {
    user = getFromRedis(token);
    localCache.put(token, user, 5, TimeUnit.MINUTES);
}
```

---

**面试官**：Token 放在请求头中，如果被中间人攻击怎么办？

**你（建议回答）**：
- 风险：
  1. HTTP 传输可能被窃听
  2. Token 泄露后可能被冒用
- 防护：
  1. 使用 HTTPS：加密传输
  2. Token 设置合理过期时间：减少泄露影响
  3. 绑定设备/IP：记录登录设备，异常登录要求验证
  4. 刷新 Token 机制：AccessToken + RefreshToken
  5. 记录登录日志：异常登录告警
- 改进：
  1. 使用 JWT + Redis：JWT 存储基本信息，Redis 存储完整信息
  2. 双 Token：AccessToken（短过期）+ RefreshToken（长过期）

---

**面试官追问**：如果用户 token 泄露了，怎么处理？

**你（建议回答）**：
- 处理：
  1. 用户修改密码：删除所有 token，强制重新登录
  2. 管理员封禁：删除用户所有 token
  3. 支持单点登出：删除当前 token
  4. 记录异常行为：异常 IP/设备登录告警
- 代码实现：
```java
// 删除用户所有token
public void logoutAll(Long userId) {
    // 方案1：遍历所有token（不推荐，性能差）
    // 方案2：维护用户token列表（推荐）
    Set<String> tokens = getUserTokens(userId);
    tokens.forEach(token -> {
        stringRedisTemplate.delete(LOGIN_USER_KEY + token);
    });
}
```

---

### 第七轮：扩展与优化

**面试官**：如果现在要支持多端登录（手机、PC、平板），你的方案需要怎么改？

**你（建议回答）**：
- 当前问题：
  1. 一个用户只能有一个 token
  2. 新登录会覆盖旧 token
- 改进：
  1. Token 结构：`login:token:{userId}:{deviceType}:{token}`
  2. 维护用户 token 列表：`login:user:{userId}` -> Set<token>
  3. 支持查看在线设备：返回所有活跃 token
  4. 支持踢出设备：删除指定 token
- 代码示例：
```java
// 登录时
String token = UUID.randomUUID().toString(true);
String deviceType = request.getHeader("device-type"); // mobile/pc/tablet
String tokenKey = LOGIN_USER_KEY + userId + ":" + deviceType + ":" + token;
// 保存到用户token列表
stringRedisTemplate.opsForSet().add("login:user:" + userId, tokenKey);
```

---

**面试官**：如果现在要你优化这个方案，你会从哪些方面入手？

**你（建议回答）**：
- 性能：
  1. 本地缓存：热点用户信息缓存到本地
  2. 异步刷新：token 刷新异步执行
  3. 批量查询：支持批量获取用户信息
- 安全：
  1. 双 Token：AccessToken + RefreshToken
  2. 绑定设备/IP：异常登录检测
  3. 登录日志：记录登录历史
- 功能：
  1. 多端登录：支持多设备同时在线
  2. 强制下线：支持踢出指定设备
  3. 单点登录：支持 SSO
- 监控：
  1. Token 使用统计：统计 token 使用频率
  2. 异常检测：异常登录告警
  3. 性能监控：Redis 查询耗时统计

---

**面试官**：如果 Redis 挂了，整个登录系统就不可用了，有什么降级方案？

**你（建议回答）**：
- 降级：
  1. 本地缓存：Redis 不可用时使用本地缓存（Caffeine）
  2. 数据库降级：Redis 不可用时查询数据库（性能差，但可用）
  3. 熔断器：Redis 不可用时快速失败，避免等待超时
- 高可用：
  1. Redis 主从：自动故障转移
  2. Redis 集群：多节点部署
  3. 多机房：就近访问
- 代码示例：
```java
try {
    UserDTO user = getFromRedis(token);
} catch (Exception e) {
    // Redis不可用，降级到本地缓存
    UserDTO user = localCache.get(token);
    if (user == null) {
        // 本地缓存也没有，查询数据库（性能差）
        user = getFromDatabase(token);
    }
}
```

---

## 总结：核心要点

1. Token 生成：UUID 随机生成，不可预测
2. Token 存储：Redis Hash 结构，支持部分更新
3. Token 校验：拦截器链，RefreshTokenInterceptor + LoginInterceptor
4. 滑动过期：每次请求刷新过期时间，提升用户体验
5. ThreadLocal：管理用户上下文，避免重复查询，注意内存泄漏
6. 安全性：HTTPS 传输，支持强制下线，异常检测
7. 性能优化：本地缓存、异步刷新、连接池优化
8. 扩展性：支持多端登录、单点登录、SSO

---

## 建议准备

1. 画流程图：登录流程、Token 校验流程、拦截器执行顺序
2. 准备数据：QPS、Redis 查询耗时、内存占用
3. 思考边界：Redis 故障、Token 泄露、异步场景
4. 代码细节：能解释每一行代码的作用和设计意图

需要我补充其他场景或深入某个问题吗？