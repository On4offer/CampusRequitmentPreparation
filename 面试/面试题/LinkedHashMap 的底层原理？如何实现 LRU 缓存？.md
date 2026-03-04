好题！这道题常被拿来考察你对 HashMap 演进和缓存设计的理解。我按“面试答题模板（概念→原理→用法→代码→坑点→追问）”给你一套能直接背的答案。

------

# 📌 面试题：LinkedHashMap 的底层原理？如何实现 LRU 缓存？

## 一、结论先行（30 秒版）

- **底层原理**：`LinkedHashMap` = `HashMap`（数组+链表/红黑树） **+ 双向链表**（维护迭代顺序）。每个节点是 `LinkedHashMap.Entry`，在 `HashMap.Node` 基础上增加 `before/after` 指针。
- **顺序模式**：构造时可选
  - `insertion-order`（默认，按插入顺序）
  - `access-order`（`new LinkedHashMap<>(…, true)`，按访问顺序，把最近访问的节点移到队尾）
- **LRU 实现**：开启 `access-order`，并重写 `removeEldestEntry`，当 `size()>capacity` 时自动淘汰队头（最久未使用）。

------

## 二、底层原理（你需要说到的关键词）

1. **结构组成**
   - 继承 `HashMap`，具备哈希桶定位；
   - 额外维护 **全表级的双向链表**（head↔…↔tail）记录顺序；
   - 节点类型：`LinkedHashMap.Entry`（比 `HashMap.Node` 多了 `before/after` 指针）。
2. **顺序维护（O(1））**
   - 插入：新节点追加到链表尾；
   - 访问（当 `accessOrder=true`）：触发 `afterNodeAccess`，把该节点**摘除并移到尾部**；
   - 插入后：`afterNodeInsertion` 可触发淘汰（配合 `removeEldestEntry`）。
3. **复杂度**
   - 查找/插入/删除：与 `HashMap` 一致，均为均摊 O(1)；
   - 维护顺序的链表操作：O(1)。

------

## 三、如何实现 LRU（最少近期使用）缓存

**两步**就够了：

1. 使用访问顺序：`accessOrder = true`；
2. 重写 `removeEldestEntry` 实现**满容即淘汰**。

### ✅ 标准代码（可直接背/用）

```java
public class LruCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LruCache(int capacity) {
        // 初始容量给得稍大些，负载因子 0.75，true 表示按访问顺序
        super((int) Math.ceil(capacity / 0.75f) + 1, 0.75f, true);
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        // 当超过容量时，自动移除最近最少使用的队头元素
        return size() > capacity;
    }
}
```

**使用示例**

```java
LruCache<String, String> cache = new LruCache<>(1000);
cache.put("a","1");
cache.get("a"); // 访问会把 "a" 移到队尾（最近使用）
```

------

## 四、常见坑点 & 最佳实践

- **别忘了 `accessOrder=true`**：默认是插入顺序，不会按访问移动节点，**无法实现 LRU**。
- **线程安全**：`LinkedHashMap` 不是线程安全。并发场景可用：
  - 外部同步：`Collections.synchronizedMap(new LruCache<>(N))`（粒度粗）；
  - 更推荐：**Caffeine** / Guava Cache（支持并发、过期、权重、统计等）。
- **容量与初始大小**：为了减少扩容，构造 `super(initialCapacity, loadFactor, true)` 时，`initialCapacity` 适当放大。
- **访问触发移动**：只有 `get/put/putAll/replace` 等访问会触发移动；**迭代器遍历不会**改变顺序。
- **淘汰时机**：淘汰在 `put` 之后触发（`afterNodeInsertion` 调用 `removeEldestEntry`），不是在 `get` 时。
- **内存压力**：链表指针会带来额外内存开销；大量小对象时注意内存占用。
- **LRU ≠ 过期**：`LinkedHashMap` 不提供 TTL/TTI，到期策略需自行封装时间戳或改用 Caffeine。

------

## 五、和其他实现的对比（两句话带过即可）

- **LinkedHashMap-LRU**：实现简单、无依赖、单机、轻并发可用；
- **Caffeine/Guava**：并发友好，支持 TTL、权重、Window TinyLFU 等更强策略，生产更稳妥。

------

## 六、面试官常见追问

1. **为啥 LRU 要用 `accessOrder=true`？**
    因为需要“访问后移动到队尾”，队头就是最久未使用的元素。
2. **淘汰发生在什么时候？**
    `put` 完成后触发 `afterNodeInsertion`，根据 `removeEldestEntry` 的返回决定是否剔除队头。
3. **如何实现 LFU？**
    `LinkedHashMap` 不擅长 LFU，需要维护访问频次与小顶堆/有序结构；生产建议用 Caffeine。
4. **并发 LRU 怎么做？**
    轻并发可外部同步；高并发建议直接用 Caffeine 的 `Cache`，避免全表锁。

------

## 七、1 分钟口述版

> LinkedHashMap 在 HashMap 之上加了一条双向链表来维护顺序；默认按插入顺序，也可以通过 `accessOrder=true` 改为访问顺序。实现 LRU 的关键是开启访问顺序，并重写 `removeEldestEntry`，在 `size()>capacity` 时淘汰队头（最久未使用）。它不是线程安全、没有 TTL，复杂场景推荐用 Caffeine。

如果你愿意，我可以再给你一版 **支持 TTL 的轻量 LRU** 封装（时间戳+定期清理/惰性删除），或者给你一个 **Caffeine** 的生产化配置示例。