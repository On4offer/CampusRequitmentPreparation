## expire 方法介绍

### 1. 基本定义
`expire` 方法是 `StringRedisTemplate` 提供的用于设置 Redis 键过期时间的方法。

### 2. 所属框架和类
- **框架**：Spring Data Redis
- **类**：`StringRedisTemplate` (继承自 `RedisTemplate`)
- **包路径**：`org.springframework.data.redis.core.StringRedisTemplate`

### 3. 方法签名
```java
Boolean expire(String key, long timeout, TimeUnit unit)
```


### 4. 参数说明
- **key**：要设置过期时间的 Redis 键
- **timeout**：过期时间数值
- **unit**：时间单位（如 `TimeUnit.MINUTES`、`TimeUnit.SECONDS` 等）

### 5. 功能作用
为指定的 Redis 键设置生存时间（TTL），当到达指定时间后，键会自动从 Redis 中删除。

### 6. 在代码中的使用
```java
// 设置token的过期时间
stringRedisTemplate.expire(tokenKey, LOGIN_USER_TTL, TimeUnit.MINUTES);
```


这行代码的作用是：
- 为用户登录令牌（tokenKey）设置过期时间
- 过期时长为 `LOGIN_USER_TTL` 分钟
- 过期后 Redis 会自动删除该用户的登录信息

### 7. Redis 原生命令对应
该方法对应 Redis 的 `EXPIRE` 命令：
```
EXPIRE key seconds
```


### 8. 返回值
- **true**：设置成功
- **false**：设置失败（如键不存在）

### 9. 常见使用场景

#### (1) 会话管理
```java
// 设置会话过期时间
stringRedisTemplate.expire("session:user:123", 30, TimeUnit.MINUTES);
```


#### (2) 缓存过期
```java
// 设置缓存过期时间
stringRedisTemplate.expire("cache:product:1001", 1, TimeUnit.HOURS);
```


#### (3) 验证码过期
```java
// 设置验证码过期时间
stringRedisTemplate.expire("code:13812345678", 5, TimeUnit.MINUTES);
```


### 10. 相关方法

| 方法                         | 功能                               |
| ---------------------------- | ---------------------------------- |
| `expire(key, timeout, unit)` | 设置相对过期时间                   |
| `expireAt(key, date)`        | 设置绝对过期时间（指定具体时间点） |
| `getExpire(key)`             | 获取剩余过期时间                   |
| `persist(key)`               | 移除过期时间，使键永久存在         |

### 11. 实际意义
在用户登录场景中，`expire` 方法确保了：
- 用户登录状态不会永久保存
- 提高系统安全性（防止token被盗用）
- 节省Redis内存资源
- 实现自动登出功能

这是实现安全会话管理的重要机制。