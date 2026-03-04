# ConcurrentHashMap 的实现原理？为什么是线程安全的？

## 一、ConcurrentHashMap 概述

### 1.1 为什么需要 ConcurrentHashMap？

**HashMap的问题**：
- **非线程安全**：多线程环境下可能出现数据丢失、死循环等问题
- **Hashtable的问题**：使用`synchronized`锁整个表，性能差

**ConcurrentHashMap的优势**：
- **线程安全**：保证并发安全
- **高性能**：锁粒度更细，支持高并发
- **分段锁/节点锁**：只锁部分数据，提高并发度

### 1.2 版本演进

| 版本 | 实现方式 | 特点 |
|------|---------|------|
| **JDK 1.7** | 分段锁（Segment） | 锁粒度：Segment级别 |
| **JDK 1.8** | CAS + synchronized | 锁粒度：节点级别（更细） |

---

## 二、JDK 1.7 实现：分段锁机制

### 2.1 分段锁结构

```java
// JDK 1.7 ConcurrentHashMap 结构
public class ConcurrentHashMap<K, V> {
    // Segment数组
    final Segment<K,V>[] segments;
    
    // Segment内部类（类似小的HashMap）
    static final class Segment<K,V> extends ReentrantLock implements Serializable {
        // HashEntry数组（每个Segment内部是一个HashMap）
        transient volatile HashEntry<K,V>[] table;
        
        // 元素个数
        transient int count;
        
        // 修改次数
        transient int modCount;
        
        // 扩容阈值
        transient int threshold;
        
        // 负载因子
        final float loadFactor;
    }
    
    // HashEntry节点
    static final class HashEntry<K,V> {
        final int hash;
        final K key;
        volatile V value;
        volatile HashEntry<K,V> next;
    }
}
```

**结构示意图**：
```
ConcurrentHashMap
    │
    ├─→ Segment[0] (ReentrantLock)
    │     └─→ HashEntry[] table
    │           ├─→ HashEntry1 -> HashEntry2 -> null
    │           └─→ HashEntry3 -> null
    │
    ├─→ Segment[1] (ReentrantLock)
    │     └─→ HashEntry[] table
    │
    └─→ Segment[15] (ReentrantLock)
          └─→ HashEntry[] table
```

### 2.2 分段锁原理

**核心思想**：
- 将整个HashMap分为**16个Segment**（默认）
- 每个Segment内部是一个小的HashMap
- 每个Segment有一把**ReentrantLock**
- 不同Segment的操作可以**并行执行**

**锁粒度**：Segment级别（比Hashtable的表级锁细）

### 2.3 定位Segment

```java
// 计算Segment索引
final Segment<K,V> segmentFor(int hash) {
    return segments[(hash >>> segmentShift) & segmentMask];
}

// segmentShift和segmentMask的计算
int sshift = 0;
int ssize = 1;
while (ssize < concurrencyLevel) {
    ++sshift;
    ssize <<= 1;  // ssize必须是2的幂
}
segmentShift = 32 - sshift;
segmentMask = ssize - 1;
```

**示例**：
```java
// 假设concurrencyLevel = 16
// ssize = 16, sshift = 4
// segmentShift = 32 - 4 = 28
// segmentMask = 15 (1111)

// hash = 1234567890
// segmentIndex = (1234567890 >>> 28) & 15
```

### 2.4 Put操作实现

```java
public V put(K key, V value) {
    Segment<K,V> s;
    if (value == null)
        throw new NullPointerException();
    int hash = hash(key);
    // 定位Segment
    int j = (hash >>> segmentShift) & segmentMask;
    if ((s = (Segment<K,V>)UNSAFE.getObject(segments, (j << SSHIFT) + SBASE)) == null)
        s = ensureSegment(j);
    // 调用Segment的put方法
    return s.put(key, hash, value, false);
}

// Segment的put方法
final V put(K key, int hash, V value, boolean onlyIfAbsent) {
    HashEntry<K,V> node = tryLock() ? null : scanAndLockForPut(key, hash, value);
    V oldValue;
    try {
        HashEntry<K,V>[] tab = table;
        int index = (tab.length - 1) & hash;
        HashEntry<K,V> first = tab[index];
        for (HashEntry<K,V> e = first;;) {
            if (e != null) {
                K k;
                if ((k = e.key) == key || (e.hash == hash && key.equals(k))) {
                    oldValue = e.value;
                    if (!onlyIfAbsent) {
                        e.value = value;
                        ++modCount;
                    }
                    break;
                }
                e = e.next;
            }
            else {
                if (node != null)
                    node.setNext(first);
                else
                    node = new HashEntry<K,V>(hash, key, value, first);
                int c = count + 1;
                if (c > threshold && tab.length < MAXIMUM_CAPACITY)
                    rehash(node);
                else
                    tab[index] = node;
                ++modCount;
                count = c;
                oldValue = null;
                break;
            }
        }
    } finally {
        unlock();
    }
    return oldValue;
}
```

**特点**：
1. **先定位Segment**：通过hash值计算Segment索引
2. **获取锁**：调用`tryLock()`或`scanAndLockForPut()`
3. **操作数据**：在Segment内部进行put操作
4. **释放锁**：在finally块中释放锁

### 2.5 Get操作实现

```java
public V get(Object key) {
    Segment<K,V> s;
    HashEntry<K,V>[] tab;
    int h = hash(key);
    long u = (((h >>> segmentShift) & segmentMask) << SSHIFT) + SBASE;
    if ((s = (Segment<K,V>)UNSAFE.getObject(segments, (int)(u >>> SSHIFT))) != null &&
        (tab = s.table) != null) {
        for (HashEntry<K,V> e = (HashEntry<K,V>) UNSAFE.getObjectVolatile
                 (tab, ((long)(((tab.length - 1) & h)) << TSHIFT) + TBASE);
             e != null; e = e.next) {
            K k;
            if ((k = e.key) == key || (e.hash == h && key.equals(k)))
                return e.value;
        }
    }
    return null;
}
```

**特点**：
- **无锁读取**：使用`UNSAFE.getObjectVolatile`保证可见性
- **volatile保证**：HashEntry的value是volatile的，保证可见性
- **性能高**：读操作不需要加锁

### 2.6 JDK 1.7的优缺点

**优点**：
- ✅ 锁粒度比Hashtable细（Segment级别）
- ✅ 不同Segment的操作可以并行
- ✅ 读操作无锁，性能好

**缺点**：
- ❌ Segment数量固定（默认16），扩展性受限
- ❌ 锁粒度仍然较大（Segment级别）
- ❌ 实现复杂，代码维护困难

---

## 三、JDK 1.8 实现：CAS + synchronized

### 3.1 核心结构

```java
// JDK 1.8 ConcurrentHashMap 结构
public class ConcurrentHashMap<K,V> {
    // 底层数组（类似HashMap）
    transient volatile Node<K,V>[] table;
    
    // 扩容时的临时数组
    private transient volatile Node<K,V>[] nextTable;
    
    // 控制标识符（负数表示正在初始化或扩容）
    private transient volatile int sizeCtl;
    
    // 普通节点
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        volatile V val;
        volatile Node<K,V> next;
    }
    
    // 树节点
    static final class TreeNode<K,V> extends Node<K,V> {
        TreeNode<K,V> parent;
        TreeNode<K,V> left;
        TreeNode<K,V> right;
        TreeNode<K,V> prev;
        boolean red;
    }
    
    // ForwardingNode（扩容时使用）
    static final class ForwardingNode<K,V> extends Node<K,V> {
        final Node<K,V>[] nextTable;
        ForwardingNode(Node<K,V>[] tab) {
            super(MOVED, null, null, null);
            this.nextTable = tab;
        }
    }
}
```

**结构示意图**：
```
ConcurrentHashMap
    │
    └─→ Node[] table
          │
          ├─→ Node1 -> Node2 -> null
          │
          ├─→ TreeNode (红黑树)
          │
          └─→ ForwardingNode (扩容标记)
```

### 3.2 并发控制机制

**核心策略**：
1. **CAS**：用于无锁操作（插入新节点）
2. **synchronized**：用于有冲突的操作（链表/树操作）
3. **volatile**：保证可见性

### 3.3 Put操作实现

```java
public V put(K key, V value) {
    return putVal(key, value, false);
}

final V putVal(K key, V value, boolean onlyIfAbsent) {
    if (key == null || value == null) throw new NullPointerException();
    int hash = spread(key.hashCode());
    int binCount = 0;
    for (Node<K,V>[] tab = table;;) {
        Node<K,V> f; int n, i, fh;
        if (tab == null || (n = tab.length) == 0)
            tab = initTable();  // 初始化
        else if ((f = tabAt(tab, i = (n - 1) & hash)) == null) {
            // 情况1：桶为空，使用CAS插入
            if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
                break;
        }
        else if ((fh = f.hash) == MOVED)
            // 情况2：正在扩容，帮助扩容
            tab = helpTransfer(tab, f);
        else {
            // 情况3：桶不为空，synchronized锁定头节点
            V oldVal = null;
            synchronized (f) {
                if (tabAt(tab, i) == f) {
                    if (fh >= 0) {
                        // 链表节点
                        binCount = 1;
                        for (Node<K,V> e = f;; ++binCount) {
                            K ek;
                            if (e.hash == hash &&
                                ((ek = e.key) == key ||
                                 (ek != null && key.equals(ek)))) {
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
                    else if (f instanceof TreeBin) {
                        // 红黑树节点
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
            if (binCount != 0) {
                if (binCount >= TREEIFY_THRESHOLD)
                    treeifyBin(tab, i);
                if (oldVal != null)
                    return oldVal;
                break;
            }
        }
    }
    addCount(1L, binCount);
    return null;
}
```

**关键步骤**：

1. **桶为空**：使用**CAS**无锁插入
   ```java
   if (casTabAt(tab, i, null, new Node<K,V>(hash, key, value, null)))
   ```

2. **桶不为空**：使用**synchronized**锁定头节点
   ```java
   synchronized (f) {
       // 操作链表或树
   }
   ```

3. **正在扩容**：帮助扩容
   ```java
   if ((fh = f.hash) == MOVED)
       tab = helpTransfer(tab, f);
   ```

### 3.4 CAS操作

```java
// CAS插入节点
static final <K,V> boolean casTabAt(Node<K,V>[] tab, int i,
                                     Node<K,V> c, Node<K,V> v) {
    return U.compareAndSwapObject(tab, ((long)i << ASHIFT) + ABASE, c, v);
}

// 获取节点（volatile读）
static final <K,V> Node<K,V> tabAt(Node<K,V>[] tab, int i) {
    return (Node<K,V>)U.getObjectVolatile(tab, ((long)i << ASHIFT) + ABASE);
}

// 设置节点（volatile写）
static final <K,V> void setTabAt(Node<K,V>[] tab, int i, Node<K,V> v) {
    U.putObjectVolatile(tab, ((long)i << ASHIFT) + ABASE, v);
}
```

**CAS优势**：
- **无锁操作**：不需要加锁，性能高
- **原子性**：保证操作的原子性
- **适用场景**：桶为空时的插入操作

### 3.5 Get操作实现

```java
public V get(Object key) {
    Node<K,V>[] tab; Node<K,V> e, p; int n, eh; K ek;
    int h = spread(key.hashCode());
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (e = tabAt(tab, (n - 1) & h)) != null) {
        if ((eh = e.hash) == h) {
            if ((ek = e.key) == key || (ek != null && key.equals(ek)))
                return e.val;
        }
        else if (eh < 0)
            // 红黑树或ForwardingNode
            return (p = e.find(h, key)) != null ? p.val : null;
        while ((e = e.next) != null) {
            if (e.hash == h &&
                ((ek = e.key) == key || (ek != null && key.equals(ek))))
                return e.val;
        }
    }
    return null;
}
```

**特点**：
- **无锁读取**：使用`tabAt`（volatile读）保证可见性
- **volatile保证**：Node的val是volatile的
- **性能高**：读操作不需要加锁

### 3.6 扩容机制（多线程协作）

```java
private final void transfer(Node<K,V>[] tab, Node<K,V>[] nextTab) {
    int n = tab.length, stride;
    // 计算每个线程处理的桶数量
    if ((stride = (NCPU > 1) ? (n >>> 3) / NCPU : n) < MIN_TRANSFER_STRIDE)
        stride = MIN_TRANSFER_STRIDE;
    
    if (nextTab == null) {
        // 初始化新数组
        nextTab = new Node<K,V>[n << 1];
    }
    
    ForwardingNode<K,V> fwd = new ForwardingNode<K,V>(nextTab);
    boolean advance = true;
    boolean finishing = false;
    
    for (int i = 0, bound = 0;;) {
        Node<K,V> f; int fh;
        while (advance) {
            int nextIndex, nextBound;
            if (--i >= bound || finishing)
                advance = false;
            else if ((nextIndex = transferIndex) <= 0) {
                i = -1;
                advance = false;
            }
            else if (U.compareAndSwapInt(this, TRANSFERINDEX, nextIndex,
                      nextBound = (nextIndex > stride ?
                                   nextIndex - stride : 0))) {
                bound = nextBound;
                i = nextIndex - 1;
                advance = false;
            }
        }
        
        if (i < 0 || i >= n || i + n >= nextn) {
            // 扩容完成
            // ...
        }
        else if ((f = tabAt(tab, i)) == null)
            // 空桶，标记为ForwardingNode
            advance = casTabAt(tab, i, null, fwd);
        else if ((fh = f.hash) == MOVED)
            // 已迁移，跳过
            advance = true;
        else {
            // 迁移节点
            synchronized (f) {
                // 迁移逻辑
            }
        }
    }
}
```

**特点**：
- **多线程协作**：多个线程可以同时参与扩容
- **分段迁移**：每个线程处理一部分桶
- **ForwardingNode**：标记已迁移的桶
- **性能优化**：减少扩容时间

---

## 四、线程安全性分析

### 4.1 JDK 1.7 线程安全保证

**保证机制**：
1. **Segment锁**：每个Segment有独立的ReentrantLock
2. **锁分段**：不同Segment的操作互不影响
3. **volatile保证**：HashEntry的value是volatile的

**示例**：
```java
// 线程1操作Segment[0]
Segment[0].lock();  // 获取锁
// 操作Segment[0]的数据
Segment[0].unlock();  // 释放锁

// 线程2操作Segment[1]
Segment[1].lock();  // 可以并行执行
// 操作Segment[1]的数据
Segment[1].unlock();
```

### 4.2 JDK 1.8 线程安全保证

**保证机制**：
1. **CAS保证原子性**：桶为空时的插入操作
2. **synchronized保证互斥**：桶不为空时的操作
3. **volatile保证可见性**：Node的val和next是volatile的
4. **sizeCtl控制**：控制初始化和扩容的并发

**示例**：
```java
// 情况1：桶为空，CAS插入
if (casTabAt(tab, i, null, new Node<>())) {
    // CAS成功，插入完成
}

// 情况2：桶不为空，synchronized锁定
synchronized (f) {
    // 操作链表或树
}
```

### 4.3 为什么线程安全？

**JDK 1.7**：
- ✅ **锁分段**：不同Segment的操作互不影响
- ✅ **ReentrantLock**：保证同一Segment的互斥访问
- ✅ **volatile**：保证可见性

**JDK 1.8**：
- ✅ **CAS**：保证无锁操作的原子性
- ✅ **synchronized**：保证有冲突操作的互斥性
- ✅ **volatile**：保证可见性
- ✅ **锁粒度更细**：只锁单个节点，不是整个Segment

---

## 五、JDK 1.7 vs JDK 1.8 对比

### 5.1 实现方式对比

| 对比项 | JDK 1.7 | JDK 1.8 |
|--------|---------|---------|
| **底层结构** | Segment数组 + HashEntry数组 | Node数组 + 链表 + 红黑树 |
| **锁机制** | ReentrantLock（Segment级别） | synchronized（节点级别） |
| **锁粒度** | Segment级别（较粗） | 节点级别（更细） |
| **并发度** | Segment数量（默认16） | 节点数量（更高） |
| **CAS使用** | 较少 | 较多（无锁操作） |
| **扩容机制** | Segment内部扩容 | 多线程协作扩容 |

### 5.2 性能对比

**JDK 1.8的优势**：
- ✅ **锁粒度更细**：只锁单个节点，不是整个Segment
- ✅ **CAS优化**：无锁操作更多，性能更好
- ✅ **并发度更高**：可以支持更高的并发
- ✅ **代码更简洁**：实现更简单，维护更容易

**性能测试**（仅供参考）：
- JDK 1.8的并发性能比JDK 1.7提升约**30-50%**

---

## 六、常见面试追问

### Q1：为什么JDK 1.8使用synchronized而不是ReentrantLock？

**答**：
1. **synchronized优化**：JDK 1.6后synchronized进行了大量优化（偏向锁、轻量级锁）
2. **性能相当**：在低竞争情况下，synchronized性能已经和ReentrantLock相当
3. **代码简洁**：synchronized代码更简洁，不需要手动释放锁
4. **JVM优化**：JVM对synchronized有更好的优化支持

### Q2：ConcurrentHashMap允许null值吗？

**答**：
- **不允许null key和null value**
- **原因**：
  - null值在并发环境下会产生歧义
  - 无法区分"key不存在"和"key存在但value为null"
  - 避免并发问题

### Q3：ConcurrentHashMap和Hashtable的区别？

**答**：

| 对比项 | Hashtable | ConcurrentHashMap |
|--------|-----------|-------------------|
| **锁机制** | synchronized锁整个表 | 分段锁/节点锁 |
| **锁粒度** | 表级别（粗） | Segment/节点级别（细） |
| **并发度** | 低（全表锁） | 高（分段/节点锁） |
| **性能** | 低 | 高 |
| **null值** | 不允许 | 不允许 |

### Q4：ConcurrentHashMap的size()方法如何实现？

**答**：
```java
// JDK 1.8的size()实现
public int size() {
    long n = sumCount();
    return ((n < 0L) ? 0 :
            (n > (long)Integer.MAX_VALUE) ? Integer.MAX_VALUE :
            (int)n);
}

final long sumCount() {
    CounterCell[] as = counterCells; CounterCell a;
    long sum = baseCount;
    if (as != null) {
        for (int i = 0; i < as.length; ++i) {
            if ((a = as[i]) != null)
                sum += a.value;
        }
    }
    return sum;
}
```

**特点**：
- 使用**CounterCell数组**分段计数
- 避免锁竞争，提高性能
- 最终结果是所有CounterCell的累加

---

## 七、面试回答模板

### 7.1 核心回答（1分钟）

"ConcurrentHashMap是线程安全的HashMap实现。JDK 1.7采用分段锁机制，将整个表分为16个Segment，每个Segment有独立的ReentrantLock，不同Segment的操作可以并行。JDK 1.8取消了Segment，采用CAS + synchronized，锁粒度缩小到节点级别。桶为空时使用CAS无锁插入，桶不为空时使用synchronized锁定头节点。读操作使用volatile保证可见性，无需加锁。这样既保证了线程安全，又兼顾了性能。"

### 7.2 扩展回答（3分钟）

"从实现细节看，JDK 1.7的分段锁虽然比Hashtable的表级锁细，但Segment数量固定，扩展性受限。JDK 1.8的优化利用了CAS和synchronized，CAS用于无锁操作，synchronized用于有冲突的操作，锁粒度更细，并发度更高。扩容时采用多线程协作机制，多个线程可以同时参与扩容，减少扩容时间。volatile保证了可见性，读操作无需加锁，性能更好。"

### 7.3 加分项

- 能说出JDK 1.7和1.8的具体实现差异
- 了解CAS和synchronized的使用场景
- 知道为什么JDK 1.8使用synchronized而不是ReentrantLock
- 理解多线程协作扩容的机制
- 能说出volatile在ConcurrentHashMap中的作用
