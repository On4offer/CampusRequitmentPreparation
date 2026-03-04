# HashMap的JDK1.7和1.8底层实现差异（数组+链表/红黑树），负载因子0.75的设计原因，以及并发场景下的线程安全问题如何解决？

## 一、HashMap 概述

### 1.1 定义

**HashMap**：
- **包路径**：`java.util.HashMap`
- **定义**：基于哈希表实现的 Map，key-value 键值对存储
- **特点**：无序、允许 null key/value、非线程安全
- **继承关系**：继承自 `AbstractMap`，实现 `Map` 接口

### 1.2 JDK 版本差异

| 版本 | 底层结构 | 哈希冲突解决 | 插入方式 |
|------|---------|-------------|---------|
| **JDK 1.7** | 数组 + 链表 | 链表 | 头插法 |
| **JDK 1.8** | 数组 + 链表 + 红黑树 | 链表 + 红黑树 | 尾插法 |

---

## 二、JDK 1.7 底层实现

### 2.1 数据结构

**数组 + 链表**：
```java
// JDK 1.7 HashMap 源码结构
public class HashMap<K,V> extends AbstractMap<K,V> {
    // 数组（桶）
    transient Entry<K,V>[] table;
    
    // Entry 节点（链表）
    static class Entry<K,V> implements Map.Entry<K,V> {
        final K key;
        V value;
        Entry<K,V> next;  // 指向下一个节点
        int hash;
        
        Entry(int h, K k, V v, Entry<K,V> n) {
            value = v;
            next = n;
            key = k;
            hash = h;
        }
    }
}
```

**存储结构**：
```
数组（桶）：
[0] -> null
[1] -> Entry(key1, value1) -> Entry(key2, value2) -> null
[2] -> null
[3] -> Entry(key3, value3) -> null
...
```

### 2.2 插入方式：头插法

**头插法实现**：
```java
// JDK 1.7 的 put 方法（简化版）
public V put(K key, V value) {
    if (table == EMPTY_TABLE) {
        inflateTable(threshold);
    }
    if (key == null)
        return putForNullKey(value);
    int hash = hash(key);
    int i = indexFor(hash, table.length);
    
    // 遍历链表，查找是否已存在
    for (Entry<K,V> e = table[i]; e != null; e = e.next) {
        Object k;
        if (e.hash == hash && ((k = e.key) == key || key.equals(k))) {
            V oldValue = e.value;
            e.value = value;
            return oldValue;
        }
    }
    
    modCount++;
    // 头插法：新节点插入到链表头部
    addEntry(hash, key, value, i);
    return null;
}

void addEntry(int hash, K key, V value, int bucketIndex) {
    Entry<K,V> e = table[bucketIndex];
    // 新节点作为头节点，原头节点作为 next
    table[bucketIndex] = new Entry<>(hash, key, value, e);
    if (size++ >= threshold)
        resize(2 * table.length);
}
```

**头插法图示**：
```
插入前：
table[i] -> Entry1 -> Entry2 -> null

插入 Entry3（头插法）：
table[i] -> Entry3 -> Entry1 -> Entry2 -> null
```

### 2.3 特点

- ✅ **简单**：只使用链表解决哈希冲突
- ❌ **性能问题**：链表过长时，查找性能退化到 O(n)
- ❌ **头插法问题**：多线程下可能导致死循环（扩容时）

---

## 三、JDK 1.8 底层实现

### 3.1 数据结构

**数组 + 链表 + 红黑树**：
```java
// JDK 1.8 HashMap 源码结构
public class HashMap<K,V> extends AbstractMap<K,V> {
    // 数组（桶）
    transient Node<K,V>[] table;
    
    // 链表节点
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;
    }
    
    // 红黑树节点
    static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
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
[0] -> null
[1] -> Node(key1, value1) -> Node(key2, value2) -> null
[2] -> TreeNode(key3, value3) [红黑树]
[3] -> null
...
```

### 3.2 树化条件

**树化阈值**：
- 链表长度 >= 8 且数组长度 >= 64 时，转换为红黑树
- 如果数组长度 < 64，优先扩容而不是树化

**源码实现**：
```java
final void treeifyBin(Node<K,V>[] tab, int hash) {
    int n, index; Node<K,V> e;
    if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
        resize();  // 如果数组长度 < 64，优先扩容
    else if ((e = tab[index = (n - 1) & hash]) != null) {
        TreeNode<K,V> hd = null, tl = null;
        do {
            TreeNode<K,V> p = new TreeNode<>(e.hash, e.key, e.value, null);
            if (tl == null)
                hd = p;
            else {
                p.prev = tl;
                tl.next = p;
            }
            tl = p;
        } while ((e = e.next) != null);
        if ((tab[index] = hd) != null)
            hd.treeify(tab);  // 转换为红黑树
    }
}
```

### 3.3 插入方式：尾插法

**尾插法实现**：
```java
// JDK 1.8 的 putVal 方法（简化版）
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = new Node<>(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        if (p.hash == hash && ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        else if (p instanceof TreeNode)
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        else {
            // 遍历链表
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    // 尾插法：新节点插入到链表尾部
                    p.next = new Node<>(hash, key, value, null);
                    if (binCount >= TREEIFY_THRESHOLD - 1)
                        treeifyBin(tab, hash);
                    break;
                }
                if (e.hash == hash && ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;
            }
        }
        // ...
    }
    return null;
}
```

**尾插法图示**：
```
插入前：
table[i] -> Node1 -> Node2 -> null

插入 Node3（尾插法）：
table[i] -> Node1 -> Node2 -> Node3 -> null
```

### 3.4 特点

- ✅ **性能优化**：链表过长时转换为红黑树，查找性能 O(log n)
- ✅ **尾插法**：避免多线程下的死循环问题
- ✅ **树化阈值**：链表长度 >= 8 且数组长度 >= 64 才树化

---

## 四、JDK 1.7 和 1.8 主要差异

### 4.1 数据结构差异

| 特性 | JDK 1.7 | JDK 1.8 |
|------|---------|---------|
| **底层结构** | 数组 + 链表 | 数组 + 链表 + 红黑树 |
| **节点类型** | Entry | Node / TreeNode |
| **哈希冲突** | 只用链表 | 链表 + 红黑树 |
| **树化条件** | 无 | 链表长度 >= 8 且数组长度 >= 64 |
| **插入方式** | 头插法 | 尾插法 |

### 4.2 性能差异

**查找性能**：
- **JDK 1.7**：链表查找 O(n)，最坏情况性能差
- **JDK 1.8**：链表查找 O(n)，红黑树查找 O(log n)，性能更好

**插入性能**：
- **JDK 1.7**：头插法 O(1)，但可能导致死循环
- **JDK 1.8**：尾插法 O(1)，避免死循环

### 4.3 扩容机制差异

**JDK 1.7**：
```java
// 扩容时，元素重新计算位置
void transfer(Entry[] newTable, boolean rehash) {
    int newCapacity = newTable.length;
    for (Entry<K,V> e : table) {
        while(null != e) {
            Entry<K,V> next = e.next;
            if (rehash) {
                e.hash = null == e.key ? 0 : hash(e.key);
            }
            int i = indexFor(e.hash, newCapacity);
            e.next = newTable[i];  // 头插法
            newTable[i] = e;
            e = next;
        }
    }
}
```

**JDK 1.8**：
```java
// 扩容时，元素要么留在原位置，要么迁移到 index + oldCap 位置
final Node<K,V>[] resize() {
    // ...
    // 通过 (hash & oldCap) == 0 判断元素位置
    // 如果为 0，留在原位置
    // 如果不为 0，迁移到 index + oldCap 位置
}
```

---

## 五、负载因子 0.75 的设计原因

### 5.1 负载因子定义

**负载因子（Load Factor）**：
- **定义**：`负载因子 = 元素个数 / 数组容量`
- **作用**：决定何时触发扩容
- **默认值**：0.75

**扩容阈值**：
```java
threshold = capacity * loadFactor
// 例如：capacity = 16, loadFactor = 0.75
// threshold = 16 * 0.75 = 12
// 当元素个数 > 12 时，触发扩容
```

### 5.2 为什么是 0.75？

**数学分析**：

**泊松分布**：
- HashMap 使用泊松分布来统计哈希冲突的概率
- 当负载因子为 0.75 时，哈希冲突的概率相对较低

**空间和时间权衡**：
- **负载因子太小**（如 0.5）：
  - ✅ 哈希冲突少
  - ❌ 空间浪费大（频繁扩容）
  - ❌ 扩容开销大
- **负载因子太大**（如 1.0）：
  - ✅ 空间利用率高
  - ❌ 哈希冲突多
  - ❌ 查找性能差
- **负载因子 0.75**：
  - ✅ 平衡空间和时间
  - ✅ 哈希冲突概率适中
  - ✅ 空间利用率合理

### 5.3 实验数据

**不同负载因子的性能对比**：

| 负载因子 | 空间利用率 | 哈希冲突概率 | 查找性能 | 扩容频率 |
|---------|-----------|------------|---------|---------|
| **0.5** | 低 | 很低 | 很好 | 高 |
| **0.75** | 中 | 低 | 好 | 中 |
| **1.0** | 高 | 高 | 差 | 低 |

**0.75 的优势**：
- 空间利用率：75%，比较合理
- 哈希冲突：概率较低，性能好
- 扩容频率：适中，不会频繁扩容

### 5.4 源码注释

```java
/**
 * The load factor used when none specified in constructor.
 * 默认负载因子 0.75 在时间和空间成本之间提供了良好的权衡。
 * 较高的值减少了空间开销，但增加了查找成本（反映在 HashMap 类的大多数操作中，
 * 包括 get 和 put）。在设置初始容量时，应考虑映射中的预期条目数及其负载因子，
 * 以最小化重新哈希操作的数量。如果初始容量大于最大条目数除以负载因子，
 * 则不会发生任何重新哈希操作。
 */
static final float DEFAULT_LOAD_FACTOR = 0.75f;
```

---

## 六、并发场景下的线程安全问题

### 6.1 HashMap 为什么不是线程安全的？

**问题1：数据丢失**：
```java
// 线程1和线程2同时执行 put 操作
// 线程1：put("key1", "value1")
// 线程2：put("key2", "value2")
// 可能结果：只有一个值被保存，另一个丢失
```

**问题2：死循环（JDK 1.7）**：
```java
// JDK 1.7 扩容时使用头插法，多线程下可能导致死循环
// 线程1和线程2同时扩容，可能导致链表形成环
```

**问题3：数据不一致**：
```java
// 线程1：get("key")
// 线程2：put("key", "newValue")
// 可能结果：线程1读取到不一致的数据
```

### 6.2 JDK 1.7 的死循环问题

**死循环产生原因**：
```java
// JDK 1.7 的 transfer 方法（扩容时）
void transfer(Entry[] newTable, boolean rehash) {
    int newCapacity = newTable.length;
    for (Entry<K,V> e : table) {
        while(null != e) {
            Entry<K,V> next = e.next;  // 线程1执行到这里
            // 线程2此时可能已经修改了链表结构
            int i = indexFor(e.hash, newCapacity);
            e.next = newTable[i];  // 头插法
            newTable[i] = e;
            e = next;  // 可能导致死循环
        }
    }
}
```

**死循环场景**：
```
线程1执行到 e.next = newTable[i] 时暂停
线程2完成扩容，链表结构改变
线程1继续执行，可能导致链表形成环
```

### 6.3 JDK 1.8 的改进

**尾插法避免死循环**：
- JDK 1.8 使用尾插法，避免多线程下的死循环
- 但 HashMap 仍然不是线程安全的（数据丢失、数据不一致等问题依然存在）

---

## 七、并发场景下的解决方案

### 7.1 方案1：使用 Collections.synchronizedMap

**实现方式**：
```java
Map<String, String> map = Collections.synchronizedMap(new HashMap<>());

// 使用方式
synchronized (map) {
    map.put("key", "value");
    String value = map.get("key");
}
```

**特点**：
- ✅ 线程安全
- ❌ 性能差（全表锁）
- ❌ 需要手动同步

### 7.2 方案2：使用 ConcurrentHashMap（推荐）

**实现方式**：
```java
Map<String, String> map = new ConcurrentHashMap<>();

// 使用方式（无需手动同步）
map.put("key", "value");
String value = map.get("key");
```

**特点**：
- ✅ 线程安全
- ✅ 性能好（分段锁/CAS + synchronized）
- ✅ 无需手动同步

### 7.3 方案3：使用 Hashtable（不推荐）

**实现方式**：
```java
Map<String, String> map = new Hashtable<>();
```

**特点**：
- ✅ 线程安全
- ❌ 性能差（全表锁）
- ❌ 已过时，不推荐使用

### 7.4 方案4：使用读写锁

**实现方式**：
```java
import java.util.concurrent.locks.ReadWriteLock;
import java.util.concurrent.locks.ReentrantReadWriteLock;

public class ThreadSafeHashMap<K, V> {
    private final Map<K, V> map = new HashMap<>();
    private final ReadWriteLock lock = new ReentrantReadWriteLock();
    
    public V put(K key, V value) {
        lock.writeLock().lock();
        try {
            return map.put(key, value);
        } finally {
            lock.writeLock().unlock();
        }
    }
    
    public V get(K key) {
        lock.readLock().lock();
        try {
            return map.get(key);
        } finally {
            lock.readLock().unlock();
        }
    }
}
```

**特点**：
- ✅ 线程安全
- ✅ 读写分离，读操作并发性好
- ⚠️ 实现复杂

---

## 八、ConcurrentHashMap 简介

### 8.1 JDK 1.7 实现（分段锁）

**Segment 分段锁**：
```java
// JDK 1.7 ConcurrentHashMap 结构
public class ConcurrentHashMap<K,V> {
    // Segment 数组
    final Segment<K,V>[] segments;
    
    static final class Segment<K,V> extends ReentrantLock {
        // 每个 Segment 维护一个 HashEntry 数组
        transient volatile HashEntry<K,V>[] table;
    }
}
```

**特点**：
- 将数组分成多个 Segment
- 每个 Segment 独立加锁
- 不同 Segment 可以并发访问

### 8.2 JDK 1.8 实现（CAS + synchronized）

**CAS + synchronized**：
```java
// JDK 1.8 ConcurrentHashMap 结构
public class ConcurrentHashMap<K,V> {
    // 数组（与 HashMap 类似）
    transient volatile Node<K,V>[] table;
    
    // 使用 CAS 和 synchronized 保证线程安全
    final V putVal(K key, V value, boolean onlyIfAbsent) {
        // ...
        synchronized (f) {  // 只锁住链表头节点
            // ...
        }
    }
}
```

**特点**：
- 取消分段锁
- 使用 CAS + synchronized
- 只锁住链表头节点，粒度更细

---

## 九、实际应用场景

### 9.1 场景1：单线程环境（HashMap）

```java
// 单线程环境，使用 HashMap
Map<String, User> userMap = new HashMap<>();
userMap.put("user1", user1);
User user = userMap.get("user1");
```

### 9.2 场景2：多线程环境（ConcurrentHashMap）

```java
// 多线程环境，使用 ConcurrentHashMap
Map<String, Product> productCache = new ConcurrentHashMap<>();

// 线程1
productCache.put("product1", product1);

// 线程2
Product product = productCache.get("product1");  // 线程安全
```

### 9.3 场景3：读多写少（读写锁）

```java
// 读多写少场景，使用读写锁优化
ThreadSafeHashMap<String, Config> configMap = new ThreadSafeHashMap<>();

// 多个线程并发读
Config config = configMap.get("config1");  // 读锁，并发性好

// 偶尔写
configMap.put("config1", newConfig);  // 写锁，互斥
```

---

## 十、常见面试追问

### Q1：为什么 JDK 1.8 要引入红黑树？

**答**：
- **性能优化**：链表过长时，查找性能退化到 O(n)
- **红黑树优势**：查找性能 O(log n)，比链表快
- **树化条件**：链表长度 >= 8 且数组长度 >= 64
- **权衡**：红黑树节点占用空间更大，所以只在必要时树化

### Q2：为什么树化条件是链表长度 >= 8？

**答**：
- **泊松分布**：根据泊松分布，链表长度达到 8 的概率非常低（约 0.00000006）
- **性能权衡**：链表长度 < 8 时，链表性能可接受；>= 8 时，红黑树性能更好
- **经验值**：8 是经过大量测试得出的最佳阈值

### Q3：为什么 JDK 1.8 改用尾插法？

**答**：
- **避免死循环**：JDK 1.7 的头插法在多线程扩容时可能导致死循环
- **保持顺序**：尾插法可以保持元素的插入顺序（在某些场景下有用）
- **简化逻辑**：尾插法逻辑更简单，易于维护

### Q4：负载因子可以修改吗？

**答**：
- **可以修改**：可以通过构造方法设置负载因子
- **不推荐**：除非有特殊需求，否则不推荐修改
- **影响**：修改负载因子会影响性能和空间利用率

```java
// 自定义负载因子
HashMap<String, String> map = new HashMap<>(16, 0.5f);  // 负载因子 0.5
```

### Q5：HashMap 在并发场景下会出现哪些问题？

**答**：
- **数据丢失**：多线程 put 操作可能导致数据丢失
- **死循环**：JDK 1.7 扩容时可能导致死循环（JDK 1.8 已修复）
- **数据不一致**：多线程读写可能导致数据不一致
- **解决方案**：使用 ConcurrentHashMap 或 Collections.synchronizedMap

### Q6：为什么负载因子是 0.75 而不是 0.5 或 1.0？

**答**：
- **0.5**：空间浪费大，扩容频繁
- **1.0**：哈希冲突多，查找性能差
- **0.75**：平衡空间和时间，是经过数学分析和实验验证的最优值

---

## 十一、面试回答模板

### 11.1 核心回答（1分钟）

"JDK 1.7 使用数组加链表，哈希冲突只用链表解决，插入使用头插法。JDK 1.8 引入红黑树，当链表长度 >= 8 且数组长度 >= 64 时转换为红黑树，插入改用尾插法，避免多线程死循环。负载因子 0.75 是平衡空间和时间的最优值，空间利用率 75%，哈希冲突概率低。HashMap 不是线程安全的，并发场景下会出现数据丢失、死循环等问题。解决方案是使用 ConcurrentHashMap，JDK 1.8 使用 CAS 加 synchronized，只锁链表头节点，性能好。"

### 11.2 扩展回答（3分钟）

"JDK 1.7 和 1.8 的主要差异：数据结构从数组加链表变为数组加链表加红黑树，插入方式从头插法改为尾插法。JDK 1.8 引入红黑树是为了优化性能，当链表长度 >= 8 且数组长度 >= 64 时树化，查找性能从 O(n) 提升到 O(log n)。尾插法避免了 JDK 1.7 多线程扩容时的死循环问题。负载因子 0.75 是经过数学分析和实验验证的最优值，平衡了空间利用率和哈希冲突概率。HashMap 不是线程安全的，并发场景下会出现数据丢失、死循环、数据不一致等问题。解决方案是使用 ConcurrentHashMap，JDK 1.8 的 ConcurrentHashMap 取消了分段锁，改用 CAS 加 synchronized，只锁链表头节点，粒度更细，性能更好。"

### 11.3 加分项

- 能说出 JDK 1.7 和 1.8 的主要差异
- 了解红黑树引入的原因和树化条件
- 知道头插法和尾插法的区别
- 理解负载因子 0.75 的设计原因
- 了解 HashMap 的线程安全问题
- 知道并发场景下的解决方案
