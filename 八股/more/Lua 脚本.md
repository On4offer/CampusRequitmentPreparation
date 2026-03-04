当然！Lua 脚本在 Redis 中非常重要，特别是在**需要多个操作原子执行**、**实现安全可靠的分布式锁**时，Lua 是神器级的存在。

------

## 一、什么是 Lua 脚本？

- **Lua** 是一种轻量、嵌入式的脚本语言。
- Redis 从 **2.6 版本起**，支持在服务器端执行 Lua 脚本。
- 通过 `EVAL` 或 `EVALSHA` 命令将 Lua 脚本发送到 Redis 执行。

------

## 二、为什么在 Redis 中使用 Lua？

> **因为 Redis 单线程 + Lua 原子执行**，所以：

- 多个命令在 Lua 中一次性执行，**避免 race condition（竞争条件）**
- 保证原子性、不被打断
- 减少网络往返开销

------

## 三、Lua 脚本在 Redis 中的语法格式

```bash
EVAL script numkeys key1 key2 ... arg1 arg2 ...
```

- `script`：Lua 脚本代码
- `numkeys`：后面多少参数是“键”
- `key1...`：传入的 key（通过 `KEYS[]` 访问）
- `arg1...`：传入的参数（通过 `ARGV[]` 访问）

------

### 示例一：判断锁是否属于自己再释放（用于分布式锁）

```lua
-- 如果key的值等于客户端传入的标识，则删除key
if redis.call("get", KEYS[1]) == ARGV[1] then
  return redis.call("del", KEYS[1])
else
  return 0
end
```

对应 Redis 命令：

```bash
EVAL "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" \
1 lock_key unique_id
```

------

### 示例二：原子加减库存

```lua
-- 原子减少库存
local stock = tonumber(redis.call("get", KEYS[1]))
if stock > 0 then
  return redis.call("decr", KEYS[1])
else
  return -1
end
```

------

## 四、Lua 脚本的执行特点

| 特性         | 说明                                           |
| ------------ | ---------------------------------------------- |
| **原子性强** | 脚本整体是一个原子操作，期间不会被其他命令插入 |
| **高性能**   | 运行在 Redis 进程中，速度极快                  |
| **安全**     | 不支持访问本地文件、系统命令等                 |
| **可缓存**   | 可以用 `EVALSHA` 复用已加载脚本                |

------

## 五、常见应用场景

- 实现**安全的分布式锁释放**（避免删掉别人的锁）
- **库存扣减、余额修改**等原子事务
- **限流（令牌桶/漏斗）**
- **排行榜更新**等复合操作

------

## 六、总结一句话：

> **Lua 脚本是 Redis 中实现原子、多步骤操作的利器，具备原子性、高性能、安全性，是分布式锁、限流、事务控制等场景的首选。**

------

如果你想，我可以帮你写一个 Lua 分布式锁的完整 Java 示例（Redisson 不用，纯原生 Redis + Lua），或者一个秒杀系统用 Lua 扣库存，要不要？