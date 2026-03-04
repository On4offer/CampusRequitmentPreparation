好的 👍 我来给你写一道 **标准面试题答案**，遵循“概念 ➝ 原理 ➝ 案例 ➝ 使用场景 ➝ 扩展追问”的答题模板：

------

# 🎯 面试题

**MyBatis 一级缓存和二级缓存的区别？**

------

## 一、概念

1. **一级缓存（SqlSession 级别缓存）**
   - 默认开启，不能关闭。
   - 作用范围：同一个 `SqlSession` 内，多次执行相同 SQL（相同参数），会直接从缓存中取结果，而不是再次查询数据库。
2. **二级缓存（Mapper/namespace 级别缓存）**
   - 需要手动开启和配置。
   - 作用范围：多个 `SqlSession` 共享，即不同 SqlSession 之间也能复用数据结果。
   - 默认存储实现：`PerpetualCache`（基于 `HashMap`）。也支持整合第三方缓存（如 Redis、Ehcache）。

------

## 二、原理

- **一级缓存**
  - 底层用 `Map<CacheKey, Object>` 存放在 `SqlSession` 的 `Executor` 中。
  - 当 `SqlSession` 执行 `update/insert/delete/commit/rollback/close` 时，缓存会清空，保证数据一致性。
- **二级缓存**
  - 存在于 `Mapper` 的命名空间（namespace）下。
  - 查询时先查二级缓存，没有则查数据库并写入缓存。
  - 二级缓存中的对象需要序列化，默认在 `SqlSession.close()` 或 `commit()` 时写入。

------

## 三、案例

```xml
<!-- 开启二级缓存：在 mybatis-config.xml 中 -->
<settings>
    <setting name="cacheEnabled" value="true"/>
</settings>

<!-- 在某个 Mapper.xml 中启用二级缓存 -->
<cache eviction="LRU" flushInterval="60000" size="512" readOnly="false"/>
```

使用代码：

```java
SqlSession session1 = factory.openSession();
UserMapper mapper1 = session1.getMapper(UserMapper.class);
User u1 = mapper1.selectById(1);
session1.close(); // 关闭后，数据写入二级缓存

SqlSession session2 = factory.openSession();
UserMapper mapper2 = session2.getMapper(UserMapper.class);
User u2 = mapper2.selectById(1); // 命中二级缓存
```

------

## 四、区别总结（面试常用表格）

| 缓存级别 | 默认状态 | 作用范围                                      | 生命周期                            | 是否可关闭 | 存储位置          | 应用场景                       |
| -------- | -------- | --------------------------------------------- | ----------------------------------- | ---------- | ----------------- | ------------------------------ |
| 一级缓存 | 默认开启 | 单个 SqlSession                               | SqlSession 关闭/提交即清空          | 不可关闭   | Executor 内部 Map | 避免同一会话内重复 SQL         |
| 二级缓存 | 默认关闭 | Mapper（namespace）级别，多个 SqlSession 共享 | SqlSession 提交后写入，应用关闭清空 | 可配置关闭 | 内存/第三方缓存   | 跨会话缓存数据，减轻数据库压力 |

------

## 五、使用场景

- **一级缓存**：适合短连接、一次会话内频繁查询同一数据的场景（如同一事务内多次查询同一用户）。
- **二级缓存**：适合读多写少的场景，比如商品分类、热门店铺数据（苍穹外卖、黑马点评中可以缓存商户信息、菜品分类等）。

------

## 六、扩展追问

1. 如果数据库数据变了，二级缓存怎么保证一致性？
   - 答：执行 `update/insert/delete` 时会清空对应 namespace 的缓存。
2. MyBatis 二级缓存如何和 **Redis** 集成？
   - 答：通过自定义 `Cache` 接口实现，将数据存到 Redis 中。
3. 为什么一级缓存是强制开启的？能不能禁用？
   - 答：一级缓存本质就是 SqlSession 内部的 Map，为了减少 JDBC 重复查询，不能关闭。

------

要不要我帮你把 **“一级缓存和二级缓存失效的场景”** 也整理出来？这是面试官特别爱问的追问点。