# LinkedHashMap 的底层原理？如何实现 LRU 缓存？

## 一、LinkedHashMap 概述

### 1.1 定义

**LinkedHashMap**：
- **包路径**：`java.util.LinkedHashMap`
- **定义**：继承自 `HashMap`，在 HashMap 基础上维护双向链表，保证迭代顺序
- **特点**：有序、允许 null key/value、非线程安全
- **继承关系**：继承自 `HashMap`，实现 `Map` 接口

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **底层实现** | HashMap（数组+链表+红黑树）+ 双向链表 |
| **有序性** | ✅ 有序（插入顺序或访问顺序） |
| **null key** | ✅ 允许一个 |
| **null value** | ✅ 允许多个 |
| **性能** | O(1) 平均（与 HashMap 相同） |
| **线程安全** | ❌ 非线程安全 |
| **顺序模式** | 插入顺序（默认）或访问顺序（LRU） |

---

## 二、底层实现原理

### 2.1 数据结构

**LinkedHashMap 继承自 HashMap**：
```java
// LinkedHashMap 源码结构
public class LinkedHashMap<K,V> extends HashMap<K,V> implements Map<K,V> {
    
    // 双向链表的头节点（最老的节点）
    transient LinkedHashMap.Entry<K,V> head;
    
    // 双向链表的尾节点（最新的节点）
    transient LinkedHashMap.Entry<K,V> tail;
    
    // 是否按访问顺序排序（true = LRU，false = 插入顺序）
    final boolean accessOrder;
    
    // LinkedHashMap 的节点（继承自 HashMap.Node，增加了双向链表指针）
    static class Entry<K,V> extends HashMap.Node<K,V> {
        Entry<K,V> before, after;  // 双向链表的前驱和后继指针
        
        Entry(int hash, K key, V value, Node<K,V> next) {
            super(hash, key, value, next);
        }
    }
}
```

**节点结构对比**：
- **HashMap.Node**：`hash, key, value, next`（单链表）
- **LinkedHashMap.Entry**：`hash, key, value, next, before, after`（单链表 + 双向链表）

### 2.2 存储结构

**双重结构**：
```
HashMap 数组（桶）：
[0] -> null
[1] -> Entry(key1, value1) -> Entry(key2, value2) -> null
[2] -> null
[3] -> Entry(key3, value3) -> null
...

双向链表（维护顺序）：
head ←→ Entry(key1) ←→ Entry(key2) ←→ Entry(key3) ←→ tail
         ↑              ↑              ↑
       (插入顺序或访问顺序)
```

**关键点**：
- 每个节点同时存在于 HashMap 的桶结构和双向链表中
- HashMap 负责快速查找（O(1)）
- 双向链表负责维护顺序（O(1)）

### 2.3 插入顺序模式（默认）

**插入流程**：
```java
// LinkedHashMap 重写了 newNode 方法
Node<K,V> newNode(int hash, K key, V value, Node<K,V> e) {
    LinkedHashMap.Entry<K,V> p =
        new LinkedHashMap.Entry<K,V>(hash, key, value, e);
    linkNodeLast(p);  // 将新节点添加到双向链表尾部
    return p;
}

// 将节点添加到双向链表尾部
private void linkNodeLast(LinkedHashMap.Entry<K,V> p) {
    LinkedHashMap.Entry<K,V> last = tail;
    tail = p;
    if (last == null)
        head = p;  // 第一个节点
    else {
        p.before = last;
        last.after = p;  // 连接到链表尾部
    }
}
```

**示例**：
```java
LinkedHashMap<String, Integer> map = new LinkedHashMap<>();
map.put("apple", 1);   // head ←→ apple ←→ tail
map.put("banana", 2); // head ←→ apple ←→ banana ←→ tail
map.put("cherry", 3); // head ←→ apple ←→ banana ←→ cherry ←→ tail

// 遍历结果：apple, banana, cherry（插入顺序）
for (String key : map.keySet()) {
    System.out.println(key);
}
```

### 2.4 访问顺序模式（LRU）

**访问流程**：
```java
// LinkedHashMap 重写了 afterNodeAccess 方法
void afterNodeAccess(Node<K,V> e) {
    LinkedHashMap.Entry<K,V> last;
    if (accessOrder && (last = tail) != e) {
        // 如果开启了访问顺序，且访问的不是尾节点
        LinkedHashMap.Entry<K,V> p =
            (LinkedHashMap.Entry<K,V>)e, b = p.before, a = p.after;
        p.after = null;
        if (b == null)
            head = a;  // p 是头节点
        else
            b.after = a;  // 从原位置移除
        
        if (a != null)
            a.before = b;
        else
            last = b;
        
        if (last == null)
            head = p;
        else {
            p.before = last;
            last.after = p;  // 移动到尾部
        }
        tail = p;
        ++modCount;
    }
}
```

**示例**：
```java
LinkedHashMap<String, Integer> map = new LinkedHashMap<>(16, 0.75f, true);
map.put("apple", 1);   // head ←→ apple ←→ tail
map.put("banana", 2);  // head ←→ apple ←→ banana ←→ tail
map.put("cherry", 3); // head ←→ apple ←→ banana ←→ cherry ←→ tail

map.get("apple");      // 访问 apple，移动到尾部
// head ←→ banana ←→ cherry ←→ apple ←→ tail

map.get("banana");     // 访问 banana，移动到尾部
// head ←→ cherry ←→ apple ←→ banana ←→ tail
```

---

## 三、如何实现 LRU 缓存？

### 3.1 LRU 缓存原理

**LRU（Least Recently Used）**：
- 最近最少使用算法
- 当缓存满时，淘汰最久未访问的元素
- 队头 = 最久未使用，队尾 = 最近使用

**实现步骤**：
1. 开启访问顺序：`accessOrder = true`
2. 重写 `removeEldestEntry`：当超过容量时，自动移除队头元素

### 3.2 标准实现

```java
public class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    /**
     * 构造方法
     * @param capacity 缓存容量
     */
    public LRUCache(int capacity) {
        // 初始容量 = capacity / 0.75 + 1，避免频繁扩容
        // 负载因子 0.75
        // true 表示按访问顺序排序（LRU）
        super((int) Math.ceil(capacity / 0.75f) + 1, 0.75f, true);
        this.capacity = capacity;
    }

    /**
     * 重写 removeEldestEntry，当超过容量时自动移除最久未使用的元素
     * @param eldest 最老的节点（队头）
     * @return true 表示移除，false 表示不移除
     */
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}
```

### 3.3 使用示例

```java
// 创建容量为 3 的 LRU 缓存
LRUCache<String, String> cache = new LRUCache<>(3);

// 插入元素
cache.put("a", "1");  // [a]
cache.put("b", "2");  // [a, b]
cache.put("c", "3");  // [a, b, c]

// 访问元素（会移动到队尾）
cache.get("a");       // [b, c, a]（a 移到尾部）

// 插入新元素（会淘汰最久未使用的 b）
cache.put("d", "4");  // [c, a, d]（b 被淘汰）

System.out.println(cache);  // {c=3, a=1, d=4}
```

### 3.4 淘汰机制详解

**淘汰时机**：
```java
// HashMap 的 putVal 方法（简化版）
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                boolean evict) {
    // ... 插入节点 ...
    
    // 插入后回调
    if (evict)
        afterNodeInsertion(evict);  // LinkedHashMap 重写了这个方法
    return null;
}

// LinkedHashMap 的 afterNodeInsertion 方法
void afterNodeInsertion(boolean evict) {
    LinkedHashMap.Entry<K,V> first;
    if (evict && (first = head) != null && removeEldestEntry(first)) {
        K key = first.key;
        removeNode(hash(key), key, null, false, true);  // 移除队头元素
    }
}
```

**关键点**：
- 淘汰发生在 `put` 之后，不是在 `get` 时
- `removeEldestEntry` 返回 `true` 时才会淘汰
- 淘汰的是 `head`（队头，最久未使用）

---

## 四、详细对比

### 4.1 LinkedHashMap vs HashMap vs TreeMap

| 特性 | HashMap | LinkedHashMap | TreeMap |
|------|---------|---------------|---------|
| **底层实现** | 数组+链表+红黑树 | HashMap + 双向链表 | 红黑树 |
| **有序性** | ❌ 无序 | ✅ 有序（插入/访问顺序） | ✅ 有序（按 key 排序） |
| **性能** | O(1) 平均 | O(1) 平均 | O(log n) |
| **null key** | ✅ 允许 | ✅ 允许 | ❌ 不允许 |
| **内存开销** | 较小 | 较大（双向链表指针） | 中等 |
| **适用场景** | 快速查找 | 需要保持顺序 | 需要排序 |

### 4.2 插入顺序 vs 访问顺序

| 特性 | 插入顺序（默认） | 访问顺序（LRU） |
|------|----------------|----------------|
| **构造参数** | `accessOrder = false` | `accessOrder = true` |
| **顺序规则** | 按插入顺序 | 按访问顺序（最近访问的移到尾部） |
| **适用场景** | 需要保持插入顺序 | LRU 缓存 |
| **get 操作** | 不改变顺序 | 将访问的元素移到尾部 |

---

## 五、实际应用场景

### 5.1 场景1：LRU 缓存实现

```java
// 使用 LinkedHashMap 实现简单的 LRU 缓存
public class SimpleLRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int maxSize;

    public SimpleLRUCache(int maxSize) {
        super(16, 0.75f, true);
        this.maxSize = maxSize;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > maxSize;
    }
}

// 使用示例
SimpleLRUCache<String, User> userCache = new SimpleLRUCache<>(1000);
userCache.put("user1", user1);
User user = userCache.get("user1");  // 访问后移到尾部
```

### 5.2 场景2：保持插入顺序的 Map

```java
// 使用 LinkedHashMap 保持插入顺序
LinkedHashMap<String, Integer> orderMap = new LinkedHashMap<>();
orderMap.put("first", 1);
orderMap.put("second", 2);
orderMap.put("third", 3);

// 遍历结果：first, second, third（插入顺序）
for (Map.Entry<String, Integer> entry : orderMap.entrySet()) {
    System.out.println(entry.getKey() + " = " + entry.getValue());
}
```

### 5.3 场景3：带过期时间的 LRU 缓存

```java
// 扩展 LRU 缓存，支持过期时间
public class ExpiringLRUCache<K, V> extends LinkedHashMap<K, CacheEntry<V>> {
    private final int maxSize;
    private final long expireTime;  // 过期时间（毫秒）

    public ExpiringLRUCache(int maxSize, long expireTime) {
        super(16, 0.75f, true);
        this.maxSize = maxSize;
        this.expireTime = expireTime;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, CacheEntry<V>> eldest) {
        // 超过容量或已过期
        return size() > maxSize || eldest.getValue().isExpired();
    }

    public V get(K key) {
        CacheEntry<V> entry = super.get(key);
        if (entry == null || entry.isExpired()) {
            remove(key);
            return null;
        }
        return entry.getValue();
    }

    // 缓存条目（带时间戳）
    static class CacheEntry<V> {
        private final V value;
        private final long timestamp;

        CacheEntry(V value) {
            this.value = value;
            this.timestamp = System.currentTimeMillis();
        }

        V getValue() {
            return value;
        }

        boolean isExpired() {
            return System.currentTimeMillis() - timestamp > expireTime;
        }
    }
}
```

### 5.4 场景4：最近访问记录

```java
// 使用 LinkedHashMap 记录最近访问的页面
LinkedHashMap<String, PageInfo> recentPages = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, PageInfo> eldest) {
        return size() > 10;  // 只保留最近 10 个页面
    }
};

public void visitPage(String pageId, PageInfo info) {
    recentPages.put(pageId, info);  // 访问后自动移到尾部
}

public List<String> getRecentPages() {
    return new ArrayList<>(recentPages.keySet());  // 按访问顺序返回
}
```

---

## 六、常见面试追问

### Q1：LinkedHashMap 为什么能保持顺序？

**答**：
- **双向链表**：LinkedHashMap 在 HashMap 基础上维护了一条双向链表
- **节点扩展**：`LinkedHashMap.Entry` 继承自 `HashMap.Node`，增加了 `before` 和 `after` 指针
- **插入时维护**：插入新节点时，通过 `linkNodeLast` 将节点添加到链表尾部
- **访问时维护**：当 `accessOrder=true` 时，访问节点会通过 `afterNodeAccess` 将节点移到尾部

### Q2：LinkedHashMap 是线程安全的吗？

**答**：
- ❌ **非线程安全**：LinkedHashMap 不是线程安全的
- **线程安全替代**：
  - `Collections.synchronizedMap(new LinkedHashMap<>())`（外部同步，性能较差）
  - **Caffeine** 或 **Guava Cache**（支持并发、过期、权重等，生产环境推荐）

### Q3：为什么 LRU 要用 `accessOrder=true`？

**答**：
- **访问顺序**：`accessOrder=true` 表示按访问顺序排序，最近访问的节点会移到尾部
- **队头淘汰**：队头（head）是最久未使用的节点，淘汰时移除队头即可
- **自动维护**：每次 `get` 或 `put` 访问节点时，会自动将节点移到尾部，无需手动维护

### Q4：淘汰发生在什么时候？

**答**：
- **淘汰时机**：发生在 `put` 操作之后
- **触发机制**：`put` 完成后调用 `afterNodeInsertion`，检查 `removeEldestEntry` 的返回值
- **不是 get 时**：`get` 操作只会移动节点到尾部，不会触发淘汰

### Q5：LinkedHashMap 和 TreeMap 的区别？

**答**：

| 特性 | LinkedHashMap | TreeMap |
|------|---------------|---------|
| **有序性** | 插入顺序或访问顺序 | 按 key 排序 |
| **底层实现** | HashMap + 双向链表 | 红黑树 |
| **性能** | O(1) 平均 | O(log n) |
| **排序规则** | 插入顺序或 LRU | 自然排序或 Comparator |
| **适用场景** | 保持插入顺序、LRU 缓存 | 需要排序、范围查询 |

**选择建议**：
- **需要保持插入顺序或 LRU**：使用 LinkedHashMap
- **需要按 key 排序**：使用 TreeMap

### Q6：如何实现 LFU（Least Frequently Used）缓存？

**答**：
- **LinkedHashMap 不擅长 LFU**：LinkedHashMap 只记录访问顺序，不记录访问频次
- **实现方式**：
  - 维护访问频次计数器
  - 使用小顶堆或有序结构按频次排序
  - 淘汰频次最低的元素
- **生产推荐**：使用 **Caffeine**，支持 Window TinyLFU 等更先进的淘汰策略

### Q7：LinkedHashMap 的内存开销如何？

**答**：
- **额外开销**：每个节点需要额外的 `before` 和 `after` 指针（各 8 字节，共 16 字节）
- **总开销**：相比 HashMap，每个节点多 16 字节
- **权衡**：用少量内存换取顺序维护，适合需要顺序的场景

### Q8：LinkedHashMap 的初始容量如何设置？

**答**：
- **避免扩容**：初始容量应设置为 `capacity / 0.75 + 1`，避免频繁扩容
- **原因**：当元素数量达到 `容量 * 负载因子` 时会触发扩容
- **示例**：容量为 100 的 LRU 缓存，初始容量应设置为 `(int) Math.ceil(100 / 0.75) + 1 = 134`

---

## 七、面试回答模板

### 7.1 核心回答（1分钟）

"LinkedHashMap 继承自 HashMap，在 HashMap 的基础上维护了一条双向链表来保证迭代顺序。每个节点是 LinkedHashMap.Entry，比 HashMap.Node 多了 before 和 after 指针。LinkedHashMap 支持两种顺序模式：插入顺序（默认）和访问顺序（accessOrder=true）。实现 LRU 缓存需要两步：一是开启访问顺序，二是重写 removeEldestEntry 方法，当 size 超过容量时返回 true，自动移除队头（最久未使用）的元素。LinkedHashMap 不是线程安全的，复杂场景推荐使用 Caffeine 或 Guava Cache。"

### 7.2 扩展回答（3分钟）

"LinkedHashMap 的底层实现是 HashMap 加双向链表。HashMap 负责快速查找，双向链表负责维护顺序。插入时通过 linkNodeLast 将新节点添加到链表尾部。当 accessOrder=true 时，访问节点会通过 afterNodeAccess 将节点移到尾部，实现 LRU。实现 LRU 缓存需要构造时传入 accessOrder=true，并重写 removeEldestEntry，当超过容量时返回 true，触发移除队头元素。淘汰发生在 put 之后，通过 afterNodeInsertion 回调触发。LinkedHashMap 的性能与 HashMap 相同，都是 O(1) 平均，但每个节点需要额外的 16 字节存储双向链表指针。LinkedHashMap 不是线程安全的，生产环境推荐使用 Caffeine 或 Guava Cache，它们支持并发、过期时间、权重等更丰富的功能。"

### 7.3 加分项

- 能说出 LinkedHashMap 继承自 HashMap，增加了双向链表
- 了解插入顺序和访问顺序两种模式
- 知道如何实现 LRU 缓存（accessOrder + removeEldestEntry）
- 理解淘汰机制（put 后触发，移除队头）
- 知道 LinkedHashMap 不是线程安全的
- 了解 Caffeine 或 Guava Cache 作为生产环境替代方案
