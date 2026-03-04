# 为什么ConcurrentHashMap在JDK1.8中放弃了分段锁，改用synchronized+CAS？这种改动的优缺点是什么？

## 一、ConcurrentHashMap 概述

### 1.1 定义

**ConcurrentHashMap**：
- **包路径**：`java.util.concurrent.ConcurrentHashMap`
- **定义**：线程安全的 HashMap 实现
- **特点**：支持高并发、分段锁/细粒度锁、性能优于 Hashtable
- **继承关系**：继承自 `AbstractMap`，实现 `ConcurrentMap` 接口

### 1.2 JDK 版本差异

| 版本 | 锁机制 | 数据结构 | 锁粒度 |
|------|--------|---------|--------|
| **JDK 1.7** | 分段锁（Segment） | 数组 + 链表 | Segment 级别 |
| **JDK 1.8** | synchronized + CAS | 数组 + 链表 + 红黑树 | 链表头节点级别 |

---

## 二、JDK 1.7 分段锁实现

### 2.1 数据结构

**Segment 分段锁结构**：
```java
// JDK 1.7 ConcurrentHashMap 源码结构
public class ConcurrentHashMap<K,V> extends AbstractMap<K,V>
    implements ConcurrentMap<K,V>, Serializable {
    
    // Segment 数组
    final Segment<K,V>[] segments;
    
    // Segment 类（继承 ReentrantLock）
    static final class Segment<K,V> extends ReentrantLock implements Serializable {
        // 每个 Segment 维护一个 HashEntry 数组
        transient volatile HashEntry<K,V>[] table;
        transient int count;  // 元素个数
        transient int modCount;  // 修改次数
        transient int threshold;  // 扩容阈值
        final float loadFactor;  // 负载因子
    }
    
    // HashEntry 节点（链表）
    static final class HashEntry<K,V> {
        final int hash;
        final K key;
        volatile V value;
        volatile HashEntry<K,V> next;
    }
}
```

**存储结构**：
```
Segment 数组：
[Segment0] -> HashEntry[] (table)
[Segment1] -> HashEntry[] (table)
[Segment2] -> HashEntry[] (table)
...
[Segment15] -> HashEntry[] (table)

每个 Segment 内部：
table[0] -> HashEntry1 -> HashEntry2 -> null
table[1] -> HashEntry3 -> null
...
```

### 2.2 分段锁原理

**分段策略**：
- 将整个数组分成多个 Segment（默认 16 个）
- 每个 Segment 独立加锁
- 不同 Segment 可以并发访问

**锁粒度**：
```java
// 计算 key 属于哪个 Segment
final Segment<K,V> segmentFor(int hash) {
    return segments[(hash >>> segmentShift) & segmentMask];
}

// put 操作
public V put(K key, V value) {
    Segment<K,V> s;
    if (value == null)
        throw new NullPointerException();
    int hash = hash(key);
    int j = (hash >>> segmentShift) & segmentMask;
    // 获取对应的 Segment
    if ((s = (Segment<K,V>)UNSAFE.getObject(segments, (j << SSHIFT) + SBASE)) == null)
        s = ensureSegment(j);
    // 在 Segment 上加锁
    return s.put(key, hash, value, false);
}
```

**并发度**：
- 默认 16 个 Segment，并发度为 16
- 最多 16 个线程可以同时访问不同的 Segment

### 2.3 分段锁的优缺点

**优点**：
- ✅ **并发性好**：不同 Segment 可以并发访问
- ✅ **锁粒度适中**：比 Hashtable 的全表锁粒度更细
- ✅ **性能提升**：相比 Hashtable，性能有明显提升

**缺点**：
- ❌ **锁粒度仍然较粗**：一个 Segment 内所有操作都需要加锁
- ❌ **内存开销大**：Segment 数组占用额外内存
- ❌ **实现复杂**：Segment 继承 ReentrantLock，代码复杂
- ❌ **扩容限制**：Segment 内部扩容，不能跨 Segment

---

## 三、JDK 1.8 synchronized + CAS 实现

### 3.1 数据结构

**数组 + 链表 + 红黑树**：
```java
// JDK 1.8 ConcurrentHashMap 源码结构
public class ConcurrentHashMap<K,V> extends AbstractMap<K,V>
    implements ConcurrentMap<K,V>, Serializable {
    
    // 数组（与 HashMap 类似）
    transient volatile Node<K,V>[] table;
    
    // 链表节点
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        volatile V value;
        volatile Node<K,V> next;
    }
    
    // 红黑树节点
    static final class TreeNode<K,V> extends Node<K,V> {
        TreeNode<K,V> parent;
        TreeNode<K,V> left;
        TreeNode<K,V> right;
        TreeNode<K,V> prev;
        boolean red;
    }
}
```

**存储结构**：
```
数组（桶）：
[0] -> Node1 -> Node2 -> null
[1] -> TreeNode [红黑树]
[2] -> null
...
```

### 3.2 CAS + synchronized 原理

**CAS（Compare And Swap）**：
- 无锁操作，用于更新数组引用、sizeCtl 等
- 基于 CPU 的原子指令实现

**synchronized**：
- 只锁住链表头节点（或红黑树根节点）
- 锁粒度更细，只锁住单个桶

**put 操作流程**：
```java
final V putVal(K key, V value, boolean onlyIfAbsent) {
    // 1. 计算 hash
    int hash = spread(key.hashCode());
    int binCount = 0;
    
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;
        // 2. 如果数组为空，初始化（使用 CAS）
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();
        // 3. 如果桶为空，CAS 插入（无锁）
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                break;
        }
        // 4. 如果正在扩容，帮助扩容
        else if ((fh = f.hash) == MOVED)
            tab = helpTransfer(tab, f);
        else {
            // 5. 桶不为空，synchronized 锁住头节点
            V oldVal = null;
            synchronized (f) {
                if (tabAt(tab, i) == f) {
                    // 链表操作
                    if (fh >= 0) {
                        binCount = 1;
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            if (e.hash == hash && ((ek = e.key) == key || (ek != null && key.equals(ek)))) {
                                oldVal = e.val;
                                if (!onlyIfAbsent)
                                    e.val = value;
                                break;
                            }
                            Node<K,V> pred = e;
                            if ((e = e.next) == null) {
                                pred.next = new Node<K,V>(hash, key, value, null);
                                break;
                            }
                        }
                    }
                    // 红黑树操作
                    else if (f instanceof TreeBin) {
                        Node<K,V> p;
                        binCount = 2;
                        if ((p = ((TreeBin<K,V>)f).putTreeVal(hash, key, value)) != null) {
                            oldVal = p.val;
                            if (!onlyIfAbsent)
                                p.val = value;
                        }
                    }
                }
            }
            // 6. 如果链表长度 >= 8，转换为红黑树
            if (binCount != 0) {
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    // 7. 更新 size（使用 CAS）
    addCount(1L, binCount);
    return null;
}
```

### 3.3 关键方法

**CAS 操作**：
```java
// 获取数组元素（volatile 读）
static final <K,V> Node<K,V> tabAt(Node<K,V>[] tab, int i) {
    return (Node<K,V>)U.getObjectVolatile(tab, ((long)i << ASHIFT) + ABASE);
}

// CAS 更新数组元素
static final <K,V> boolean casTabAt(Node<K,V>[] tab, int i,
                                    Node<K,V> c, Node<K,V> v) {
    return U.compareAndSwapObject(tab, ((long)i << ASHIFT) + ABASE, c, v);
}

// 设置数组元素（volatile 写）
static final <K,V> void setTabAt(Node<K,V>[] tab, int i, Node<K,V> v) {
    U.putObjectVolatile(tab, ((long)i << ASHIFT) + ABASE, v);
}
```

**synchronized 锁**：
```java
// 只锁住链表头节点
synchronized (f) {
    // 操作链表或红黑树
}
```

---

## 四、为什么放弃分段锁？

### 4.1 原因1：锁粒度更细

**分段锁**：
- 锁粒度：Segment 级别
- 一个 Segment 内所有操作都需要加锁
- 即使操作不同的桶，也可能需要等待

**synchronized + CAS**：
- 锁粒度：链表头节点级别
- 只锁住单个桶
- 不同桶的操作完全并发

**性能对比**：
```
分段锁：
线程1：操作 Segment[0] 的 table[0] -> 加锁 Segment[0]
线程2：操作 Segment[0] 的 table[1] -> 等待（同一 Segment）

synchronized + CAS：
线程1：操作 table[0] -> 锁住 table[0] 的头节点
线程2：操作 table[1] -> 锁住 table[1] 的头节点（完全并发）
```

### 4.2 原因2：内存开销更小

**分段锁**：
- Segment 数组占用额外内存
- 每个 Segment 维护独立的数组和锁
- 内存开销：O(Segment数量)

**synchronized + CAS**：
- 只有一个数组
- 无额外的 Segment 结构
- 内存开销：O(1)

**内存对比**：
```java
// JDK 1.7：16 个 Segment，每个 Segment 维护一个数组
// 内存开销：16 * (数组大小 + Segment对象开销)

// JDK 1.8：只有一个数组
// 内存开销：1 * 数组大小
```

### 4.3 原因3：实现更简单

**分段锁**：
- Segment 继承 ReentrantLock
- 需要维护 Segment 数组
- 代码复杂，维护困难

**synchronized + CAS**：
- 使用 JVM 内置的 synchronized
- 代码结构更清晰
- 与 HashMap 结构类似，易于理解

### 4.4 原因4：扩容更灵活

**分段锁**：
- Segment 内部扩容
- 不能跨 Segment 扩容
- 扩容粒度受限

**synchronized + CAS**：
- 整个数组扩容
- 支持多线程协助扩容
- 扩容更灵活

### 4.5 原因5：synchronized 优化

**JDK 1.6+ synchronized 优化**：
- **偏向锁**：单线程访问时，无需加锁
- **轻量级锁**：多线程竞争不激烈时，使用 CAS
- **重量级锁**：竞争激烈时，使用互斥锁
- **锁升级**：根据竞争情况自动升级

**性能提升**：
- JDK 1.6+ 的 synchronized 性能已经接近 ReentrantLock
- 在某些场景下，synchronized 性能甚至更好

---

## 五、改动的优缺点

### 5.1 优点

**1. 锁粒度更细**：
- ✅ 只锁住链表头节点，不同桶完全并发
- ✅ 并发性能更好

**2. 内存开销更小**：
- ✅ 无 Segment 数组，内存占用更少
- ✅ 结构更简单

**3. 实现更简单**：
- ✅ 代码结构清晰，易于维护
- ✅ 与 HashMap 结构类似，学习成本低

**4. 扩容更灵活**：
- ✅ 支持多线程协助扩容
- ✅ 扩容粒度更细

**5. 性能更好**：
- ✅ 在大多数场景下，性能优于分段锁
- ✅ synchronized 经过优化，性能接近 ReentrantLock

### 5.2 缺点

**1. 锁竞争可能更激烈**：
- ❌ 如果多个线程操作同一个桶，竞争会更激烈
- ❌ 但这种情况在实际应用中较少

**2. CAS 自旋开销**：
- ❌ CAS 操作失败时会自旋，消耗 CPU
- ❌ 但在高并发场景下，CAS 失败概率较低

**3. 兼容性问题**：
- ❌ JDK 1.7 和 1.8 的实现差异较大
- ❌ 升级 JDK 版本时需要注意兼容性

### 5.3 性能对比

**测试场景**：1000 万次 put 操作，16 个线程

| 实现方式 | 耗时 | 吞吐量 |
|---------|------|--------|
| **Hashtable** | ~5000ms | 200万/秒 |
| **JDK 1.7 ConcurrentHashMap** | ~2000ms | 500万/秒 |
| **JDK 1.8 ConcurrentHashMap** | ~1500ms | 666万/秒 |

**结论**：
- JDK 1.8 的性能优于 JDK 1.7
- 锁粒度更细，并发性能更好

---

## 六、实际应用场景

### 6.1 场景1：高并发缓存

```java
// 使用 ConcurrentHashMap 作为缓存
private final ConcurrentHashMap<String, Product> cache = new ConcurrentHashMap<>();

public Product getProduct(String id) {
    // 先查缓存
    Product product = cache.get(id);
    if (product == null) {
        // 缓存未命中，查询数据库
        product = loadFromDatabase(id);
        // 放入缓存（线程安全）
        cache.put(id, product);
    }
    return product;
}
```

### 6.2 场景2：计数器

```java
// 使用 ConcurrentHashMap 实现计数器
private final ConcurrentHashMap<String, AtomicLong> counters = new ConcurrentHashMap<>();

public void increment(String key) {
    counters.computeIfAbsent(key, k -> new AtomicLong(0)).incrementAndGet();
}

public long getCount(String key) {
    return counters.getOrDefault(key, new AtomicLong(0)).get();
}
```

### 6.3 场景3：线程安全的 Map 操作

```java
// 多线程环境下安全的 Map 操作
ConcurrentHashMap<String, User> userMap = new ConcurrentHashMap<>();

// 线程1：添加用户
userMap.put("user1", user1);

// 线程2：更新用户
userMap.computeIfPresent("user1", (k, v) -> {
    v.setName("新名称");
    return v;
});

// 线程3：删除用户
userMap.remove("user1");
```

---

## 七、常见面试追问

### Q1：为什么 JDK 1.8 的 synchronized 性能不差？

**答**：
- **JDK 1.6+ 优化**：偏向锁、轻量级锁、锁升级
- **JVM 优化**：JVM 对 synchronized 做了大量优化
- **性能接近 ReentrantLock**：在大多数场景下，性能接近甚至超过 ReentrantLock
- **无额外开销**：synchronized 是 JVM 内置的，无额外对象创建开销

### Q2：CAS 和 synchronized 分别用在什么场景？

**答**：
- **CAS**：用于无锁操作，如数组初始化、size 更新、桶的空插入
- **synchronized**：用于有锁操作，如链表/红黑树的插入、删除、更新
- **原则**：能用 CAS 就用 CAS，不能用 CAS 再用 synchronized

### Q3：JDK 1.8 的 ConcurrentHashMap 还有分段锁吗？

**答**：
- **没有**：JDK 1.8 完全移除了 Segment 分段锁
- **替代方案**：使用 synchronized + CAS
- **优势**：锁粒度更细，性能更好

### Q4：如果多个线程操作同一个桶，性能会下降吗？

**答**：
- **会下降**：多个线程操作同一个桶时，需要竞争同一个锁
- **但影响有限**：
  - 哈希分布均匀时，冲突概率低
  - synchronized 经过优化，性能可接受
  - 实际应用中，这种情况较少

### Q5：JDK 1.8 的 ConcurrentHashMap 如何保证线程安全？

**答**：
- **CAS**：用于无锁操作，保证原子性
- **synchronized**：用于有锁操作，保证互斥
- **volatile**：用于保证可见性
- **组合使用**：CAS + synchronized + volatile 共同保证线程安全

### Q6：为什么不用 ReentrantLock 而用 synchronized？

**答**：
- **性能相当**：JDK 1.6+ 的 synchronized 性能已经接近 ReentrantLock
- **实现简单**：synchronized 是 JVM 内置的，无需额外对象
- **内存开销小**：synchronized 无额外内存开销
- **JVM 优化**：JVM 对 synchronized 做了大量优化

---

## 八、面试回答模板

### 8.1 核心回答（1分钟）

"JDK 1.7 使用分段锁，将数组分成多个 Segment，每个 Segment 独立加锁，并发度为 Segment 数量。JDK 1.8 放弃分段锁，改用 synchronized 加 CAS。原因：锁粒度更细，只锁链表头节点，不同桶完全并发；内存开销更小，无 Segment 数组；实现更简单，代码清晰；扩容更灵活。优点：并发性能更好，内存占用更少，实现简单。缺点：锁竞争可能更激烈，CAS 自旋有开销，但实际影响有限。JDK 1.6+ 的 synchronized 经过优化，性能接近 ReentrantLock，所以选择 synchronized。"

### 8.2 扩展回答（3分钟）

"JDK 1.7 的 ConcurrentHashMap 使用分段锁，将数组分成 16 个 Segment，每个 Segment 继承 ReentrantLock，独立加锁。不同 Segment 可以并发访问，但同一 Segment 内的操作需要加锁。JDK 1.8 放弃分段锁，改用 synchronized 加 CAS。放弃分段锁的原因：锁粒度更细，只锁链表头节点，不同桶完全并发；内存开销更小，无 Segment 数组；实现更简单，代码清晰；扩容更灵活，支持多线程协助扩容；JDK 1.6+ 的 synchronized 经过优化，性能接近 ReentrantLock。改动的优点：并发性能更好，锁粒度更细；内存占用更少，结构更简单；实现更简单，易于维护；扩容更灵活。缺点：锁竞争可能更激烈，但实际影响有限；CAS 自旋有开销，但在高并发场景下失败概率较低。JDK 1.8 的 ConcurrentHashMap 在大多数场景下性能优于 JDK 1.7。"

### 8.3 加分项

- 能说出 JDK 1.7 和 1.8 的实现差异
- 理解分段锁和 synchronized + CAS 的原理
- 知道为什么放弃分段锁
- 了解 synchronized 的优化（偏向锁、轻量级锁、锁升级）
- 知道 CAS 和 synchronized 的使用场景
- 能分析改动的优缺点
