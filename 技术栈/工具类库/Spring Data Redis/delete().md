## delete 方法介绍

### 1. 基本定义
[delete()](file://org\springframework\data\redis\core\RedisTemplate.java#L303-L303) 是 Spring Data Redis 框架中用于删除 Redis 中指定键的方法。

### 2. 所属工具和类
- **框架**：Spring Data Redis
- **类**：`org.springframework.data.redis.core.StringRedisTemplate`（继承自 `RedisTemplate`）
- **方法签名**：`Boolean delete(Object key)`

### 3. 方法功能
从 Redis 中删除指定的键值对，如果键存在则删除并返回 true，如果键不存在则返回 false。

### 4. 在代码中的使用
```java
stringRedisTemplate.delete(CACHE_SHOP_KEY + id);
```


这行代码的作用是：
- 删除 Redis 中对应店铺 ID 的缓存数据
- 在更新店铺信息后，清除旧的缓存以保证数据一致性

### 5. Redis 原生命令对应
该方法对应 Redis 的 `DEL` 命令：
```redis
DEL key
```


### 6. 在业务中的作用

```java
@Override
@Transactional
public Result update(Shop shop) {
    Long id = shop.getId();
    if (id == null) {
        return Result.fail("店铺id不能为空");
    }
    // 1.更新数据库
    updateById(shop);
    // 2.删除缓存（缓存失效策略）
    stringRedisTemplate.delete(CACHE_SHOP_KEY + id);
    return Result.ok();
}
```


执行流程：
1. 更新数据库中的店铺信息
2. 删除 Redis 中对应的缓存数据
3. 下次查询时会重新从数据库加载并缓存

### 7. 相关方法

| 方法           | 功能                     |
| -------------- | ------------------------ |
| `delete(key)`  | 删除单个键               |
| `delete(keys)` | 批量删除多个键           |
| `unlink(key)`  | 非阻塞删除（Redis 4.0+） |
| `hasKey(key)`  | 检查键是否存在           |

### 8. 方法实现原理
```java
// RedisTemplate 中的 delete 方法实现
public Boolean delete(K key) {
    // 1. 序列化键
    byte[] rawKey = rawKey(key);
    
    // 2. 执行 Redis DEL 命令
    Long result = connection.del(rawKey);
    
    // 3. 返回删除结果
    return result > 0;
}
```


### 9. 使用场景示例

#### (1) 缓存更新
```java
// 更新用户信息后删除缓存
public void updateUser(User user) {
    userMapper.update(user);
    redisTemplate.delete("user:" + user.getId());
}
```


#### (2) 缓存失效
```java
// 用户登出时删除会话缓存
public void logout(String token) {
    redisTemplate.delete("session:" + token);
}
```


#### (3) 批量删除
```java
// 批量删除多个缓存键
List<String> keys = Arrays.asList("cache:1", "cache:2", "cache:3");
redisTemplate.delete(keys);
```


### 10. 缓存策略

在当前代码中使用的是**Cache-Aside Pattern**（旁路缓存模式）：

```
更新数据流程：
1. 应用程序更新数据库
2. 应用程序删除缓存
3. 下次读取时重新加载到缓存

优点：
- 实现简单
- 数据一致性好
- 避免了并发更新问题

缺点：
- 删除缓存后首次查询会有延迟
```


### 11. 注意事项

#### (1) 异常处理
```java
try {
    stringRedisTemplate.delete(CACHE_SHOP_KEY + id);
} catch (Exception e) {
    // 记录日志，但不中断业务流程
    log.warn("删除缓存失败，key: {}", CACHE_SHOP_KEY + id, e);
}
```


#### (2) 性能考虑
```java
// 对于批量操作，考虑使用管道
redisTemplate.executePipelined(new SessionCallback<Object>() {
    public Object execute(RedisOperations operations) {
        for (Long id : ids) {
            operations.delete(CACHE_SHOP_KEY + id);
        }
        return null;
    }
});
```


### 12. 优势

1. **数据一致性**：确保缓存与数据库数据一致
2. **简单可靠**：删除操作简单且不容易出错
3. **性能良好**：Redis 的 DEL 操作通常很快
4. **Spring 集成**：与 Spring 框架无缝集成

这是 Spring Data Redis 中最基础也是最重要的缓存管理方法，广泛用于实现缓存失效策略。