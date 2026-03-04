# HashMap 的底层实现原理？JDK 1.7 和 1.8 有哪些变化？为什么要引入红黑树？

## 一、核心概念

### 1.1 HashMap 概述

**HashMap** 是Java中最常用的集合类之一，基于哈希表实现，提供了O(1)时间复杂度的插入、删除和查找操作（平均情况下）。

**核心特点**：
- 非线程安全
- 允许null键和null值
- 不保证元素顺序
- 初始容量16，负载因子0.75

---

## 二、HashMap 底层结构

### 2.1 JDK 1.7 结构：数组 + 链表

```java
// JDK 1.7 HashMap 核心结构
public class HashMap<K,V> {
    // 底层数组（桶数组）
    transient Entry<K,V>[] table;
    
    // 元素个数
    transient int size;
    
    // 负载因子
    final float loadFactor;
    
    // 扩容阈值 = capacity * loadFactor
    int threshold;
    
    // Entry节点（链表节点）
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

**结构示意图**：
```
数组索引:  0    1    2    3    4    5    ...
          │    │    │    │    │    │
          ▼    ▼    ▼    ▼    ▼    ▼
         null  │   null  │   null
               ▼         ▼
            Entry1    Entry1
               │         │
               ▼         ▼
            Entry2    Entry2
               │         │
               ▼         ▼
            null       null
```

### 2.2 JDK 1.8 结构：数组 + 链表 + 红黑树

```java
// JDK 1.8 HashMap 核心结构
public class HashMap<K,V> {
    // 底层数组（桶数组）
    transient Node<K,V>[] table;
    
    // 元素个数
    transient int size;
    
    // 负载因子
    final float loadFactor;
    
    // 扩容阈值
    int threshold;
    
    // 链表转红黑树的阈值
    static final int TREEIFY_THRESHOLD = 8;
    
    // 红黑树转链表的阈值
    static final int UNTREEIFY_THRESHOLD = 6;
    
    // 最小树化容量
    static final int MIN_TREEIFY_CAPACITY = 64;
    
    // 普通节点（链表节点）
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;
        
        Node(int hash, K key, V value, Node<K,V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }
    
    // 树节点（红黑树节点）
    static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
        TreeNode<K,V> parent;
        TreeNode<K,V> left;
        TreeNode<K,V> right;
        TreeNode<K,V> prev;
        boolean red;
        
        TreeNode(int hash, K key, V val, Node<K,V> next) {
            super(hash, key, val, next);
        }
    }
}
```

**结构示意图**：
```
数组索引:  0    1    2    3    4    5    ...
          │    │    │    │    │    │
          ▼    ▼    ▼    ▼    ▼    ▼
         null  │   null  │   null
               ▼         ▼
            Node1    TreeNode (红黑树)
               │         │
               ▼         │
            Node2        │
               │         │
               ▼         │
            null         │
                      (树结构)
```

---

## 三、JDK 1.7 vs JDK 1.8 详细对比

### 3.1 核心差异对比表

| 对比项 | JDK 1.7 | JDK 1.8 |
|--------|---------|---------|
| **底层结构** | 数组 + 链表 | 数组 + 链表 + 红黑树 |
| **节点类型** | Entry | Node / TreeNode |
| **链表插入方式** | 头插法 | 尾插法 |
| **hash计算** | 4次位运算 + 5次异或 | 1次位运算 + 1次异或 |
| **扩容后rehash** | 所有节点重新hash | 优化：节点位置 = 原位置 或 原位置+oldCap |
| **树化条件** | 无 | 链表长度≥8 且 数组容量≥64 |
| **退化条件** | 无 | 树节点数≤6 |
| **并发问题** | 可能死循环 | 数据丢失（仍非线程安全） |

### 3.2 Hash值计算

**JDK 1.7**：
```java
final int hash(Object k) {
    int h = hashSeed;
    if (0 != h && k instanceof String) {
        return sun.misc.Hashing.stringHash32((String) k);
    }
    
    h ^= k.hashCode();
    // 4次位运算 + 5次异或运算
    h ^= (h >>> 20) ^ (h >>> 12);
    return h ^ (h >>> 7) ^ (h >>> 4);
}
```

**JDK 1.8**（优化后）：
```java
static final int hash(Object key) {
    int h;
    // 1次位运算 + 1次异或运算
    return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
}
```

**优化说明**：
- JDK 1.8的hash计算**更简单高效**
- `h >>> 16`：将高16位右移到低16位
- `h ^ (h >>> 16)`：高16位和低16位异或，**增加hash值的随机性**，减少冲突

### 3.3 数组索引计算

```java
// 计算数组索引
int index = (n - 1) & hash;

// n是数组长度（必须是2的幂）
// hash是key的hash值
// 等价于 hash % n，但位运算更快
```

**为什么数组长度必须是2的幂？**
- 保证 `(n-1) & hash` 能均匀分布
- 例如：n=16，n-1=15(1111)，hash & 1111 能均匀分布0-15
- 如果n不是2的幂，hash分布不均匀，冲突增多

### 3.4 链表插入方式

**JDK 1.7 - 头插法**：
```java
void addEntry(int hash, K key, V value, int bucketIndex) {
    Entry<K,V> e = table[bucketIndex];
    table[bucketIndex] = new Entry<>(hash, key, value, e);  // 头插
    size++;
}
```

**问题**：
- 扩容时可能导致**链表反转**
- 并发环境下可能形成**环形链表**，导致死循环

**JDK 1.8 - 尾插法**：
```java
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    // ...
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = new Node<>(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        // ...
        else {
            // 尾插法：遍历到链表末尾再插入
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    p.next = new Node<>(hash, key, value, null);
                    if (binCount >= TREEIFY_THRESHOLD - 1)
                        treeifyBin(tab, hash);
                    break;
                }
                // ...
            }
        }
    }
}
```

**优势**：
- 避免链表反转
- 减少并发下的问题（但仍非线程安全）

---

## 四、红黑树引入详解

### 4.1 为什么引入红黑树？

**问题背景**：
- HashMap在哈希冲突严重时，链表会变得很长
- 链表查询时间复杂度**O(n)**，性能下降
- 例如：1000个元素，如果hash分布不均匀，某个链表可能有几百个节点

**解决方案**：
- 当链表长度超过阈值时，转换为**红黑树**
- 红黑树查询时间复杂度**O(log n)**，性能大幅提升

### 4.2 红黑树特性

**红黑树（Red-Black Tree）**是一种自平衡二叉查找树，具有以下特性：

1. **节点是红色或黑色**
2. **根节点是黑色**
3. **所有叶子节点（NIL）是黑色**
4. **红色节点的子节点必须是黑色**（不能有连续红色节点）
5. **从任意节点到其每个叶子的所有路径都包含相同数目的黑色节点**

**时间复杂度**：
- 查找：O(log n)
- 插入：O(log n)
- 删除：O(log n)

### 4.3 树化条件

```java
// 树化条件检查
final void treeifyBin(Node<K,V>[] tab, int hash) {
    int n, index; Node<K,V> e;
    // 条件1：数组容量必须 >= 64
    if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
        resize();  // 先扩容，而不是树化
    // 条件2：链表长度 >= 8
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

**树化条件**：
1. **链表长度 ≥ 8**（TREEIFY_THRESHOLD）
2. **数组容量 ≥ 64**（MIN_TREEIFY_CAPACITY）

**为什么需要两个条件？**
- 如果数组容量小，优先**扩容**而不是树化
- 扩容可以减少hash冲突，可能不需要树化
- 只有数组容量足够大时，才考虑树化

### 4.4 退化条件

```java
// 退化条件：树节点数 <= 6
static final int UNTREEIFY_THRESHOLD = 6;

final Node<K,V> untreeify(HashMap<K,V> map) {
    Node<K,V> hd = null, tl = null;
    for (Node<K,V> q = this; q != null; q = q.next) {
        Node<K,V> p = map.replacementNode(q, null);
        if (tl == null)
            hd = p;
        else
            tl.next = p;
        tl = p;
    }
    return hd;
}
```

**退化条件**：树节点数 ≤ 6（UNTREEIFY_THRESHOLD）

**为什么是6而不是8？**
- **避免频繁转换**：如果阈值也是8，删除一个节点就退化，添加一个节点又树化
- **设置6作为缓冲**：避免在8附近频繁转换，提高性能

### 4.5 为什么选择红黑树而不是AVL树？

| 对比项 | 红黑树 | AVL树 |
|--------|--------|-------|
| **平衡性** | 相对宽松 | 严格平衡 |
| **查询性能** | O(log n) | O(log n) |
| **插入性能** | 更快（旋转次数少） | 较慢（旋转次数多） |
| **删除性能** | 更快 | 较慢 |
| **适用场景** | 插入删除频繁 | 查询频繁 |

**HashMap选择红黑树的原因**：
- HashMap**插入删除频繁**，红黑树旋转次数少，性能更好
- 红黑树查询性能也能满足需求（O(log n)）
- **综合性能更优**

---

## 五、扩容机制对比

### 5.1 JDK 1.7 扩容机制

```java
void resize(int newCapacity) {
    Entry[] oldTable = table;
    int oldCapacity = oldTable.length;
    
    Entry[] newTable = new Entry[newCapacity];
    transfer(newTable);  // 重新hash所有节点
    table = newTable;
    threshold = (int)(newCapacity * loadFactor);
}

void transfer(Entry[] newTable) {
    Entry[] src = table;
    int newCapacity = newTable.length;
    for (int j = 0; j < src.length; j++) {
        Entry<K,V> e = src[j];
        if (e != null) {
            src[j] = null;
            do {
                Entry<K,V> next = e.next;
                int i = indexFor(e.hash, newCapacity);  // 重新计算索引
                e.next = newTable[i];  // 头插法
                newTable[i] = e;
                e = next;
            } while (e != null);
        }
    }
}
```

**特点**：
- 扩容时**所有节点重新hash**
- 使用**头插法**插入新数组
- 时间复杂度**O(n)**，性能开销大

### 5.2 JDK 1.8 扩容机制（优化）

```java
final Node<K,V>[] resize() {
    Node<K,V>[] oldTab = table;
    int oldCap = (oldTab == null) ? 0 : oldTab.length;
    int oldThr = threshold;
    int newCap, newThr = 0;
    
    if (oldCap > 0) {
        if (oldCap >= MAXIMUM_CAPACITY) {
            threshold = Integer.MAX_VALUE;
            return oldTab;
        }
        // 容量翻倍
        else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                 oldCap >= DEFAULT_INITIAL_CAPACITY)
            newThr = oldThr << 1; // 阈值翻倍
    }
    
    Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
    table = newTab;
    
    if (oldTab != null) {
        for (int j = 0; j < oldCap; ++j) {
            Node<K,V> e;
            if ((e = oldTab[j]) != null) {
                oldTab[j] = null;
                if (e.next == null)
                    // 只有一个节点，直接移动
                    newTab[e.hash & (newCap - 1)] = e;
                else if (e instanceof TreeNode)
                    // 红黑树节点
                    ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                else {
                    // 链表节点：优化处理
                    Node<K,V> loHead = null, loTail = null;
                    Node<K,V> hiHead = null, hiTail = null;
                    Node<K,V> next;
                    do {
                        next = e.next;
                        // 关键优化：判断节点位置
                        if ((e.hash & oldCap) == 0) {
                            // 位置不变：原索引
                            if (loTail == null)
                                loHead = e;
                            else
                                loTail.next = e;
                            loTail = e;
                        }
                        else {
                            // 位置改变：原索引 + oldCap
                            if (hiTail == null)
                                hiHead = e;
                            else
                                hiTail.next = e;
                            hiTail = e;
                        }
                    } while ((e = next) != null);
                    if (loTail != null) {
                        loTail.next = null;
                        newTab[j] = loHead;  // 原位置
                    }
                    if (hiTail != null) {
                        hiTail.next = null;
                        newTab[j + oldCap] = hiHead;  // 新位置
                    }
                }
            }
        }
    }
    return newTab;
}
```

**优化点**：
1. **不需要重新hash**：通过 `(e.hash & oldCap) == 0` 判断节点位置
2. **节点位置只有两种可能**：
   - 原索引位置（`hash & oldCap == 0`）
   - 原索引 + oldCap（`hash & oldCap != 0`）
3. **性能提升**：避免重新计算hash，时间复杂度仍O(n)，但常数因子更小

**原理说明**：
```
假设 oldCap = 16 (10000)
oldCap - 1 = 15 (01111)
newCap = 32 (100000)
newCap - 1 = 31 (011111)

节点hash值：
- hash = 5  (00101)  -> 5 & 15 = 5,  5 & 16 = 0  -> 位置不变：5
- hash = 21 (10101)  -> 21 & 15 = 5, 21 & 16 != 0 -> 位置改变：5+16=21
```

---

## 六、性能对比

### 6.1 时间复杂度对比

| 操作 | 链表（O(n)） | 红黑树（O(log n)） | 提升 |
|------|--------------|-------------------|------|
| **查找** | O(n) | O(log n) | 显著提升 |
| **插入** | O(1) | O(log n) | 略慢 |
| **删除** | O(n) | O(log n) | 显著提升 |

**实际测试**（链表长度1000）：
- 链表查找：平均500次比较
- 红黑树查找：平均10次比较（log₂1000 ≈ 10）
- **性能提升约50倍**

### 6.2 树化阈值8的选择

**为什么是8？**

根据**泊松分布**统计：
- 链表长度达到8的概率：**0.00000006**（极低）
- 正常情况下，链表长度很少超过8
- 如果超过8，说明hash分布不均匀，需要树化优化

**源码注释**：
```java
* Because TreeNodes are about twice the size of regular nodes, we
* use them only when bins contain enough nodes to warrant use
* (see TREEIFY_THRESHOLD). And when they become too small (due to
* removal or resizing) they are converted back to plain bins.
```

---

## 七、常见面试追问

### Q1：为什么数组长度必须是2的幂？

**答**：
1. **保证hash分布均匀**：`(n-1) & hash` 能均匀分布0到n-1
2. **位运算高效**：`&` 运算比 `%` 运算快
3. **扩容优化**：JDK 1.8的扩容优化依赖2的幂特性

**示例**：
```java
// n = 16 (2的幂)
n - 1 = 15 = 1111
hash & 1111 能均匀分布 0-15

// n = 15 (不是2的幂)
n - 1 = 14 = 1110
hash & 1110 只能得到偶数索引，分布不均匀
```

### Q2：为什么负载因子是0.75？

**答**：
- **平衡时间和空间**：
  - 太小（如0.5）：空间利用率低，频繁扩容
  - 太大（如1.0）：冲突增多，性能下降
- **0.75是经验值**：经过大量测试得出的最优值
- **数学依据**：泊松分布中，0.75时冲突概率和空间利用率达到平衡

### Q3：HashMap为什么线程不安全？

**答**：
1. **数据丢失**：多线程put时，可能覆盖已存在的值
2. **死循环**（JDK 1.7）：扩容时头插法可能导致环形链表
3. **数据不一致**：一个线程在扩容，另一个线程在读取，可能读到null

**解决方案**：使用 `ConcurrentHashMap` 或 `Collections.synchronizedMap()`

### Q4：HashMap的初始容量如何设置？

**答**：
```java
// 预估元素数量
int expectedSize = 100;
// 初始容量 = expectedSize / loadFactor + 1
int initialCapacity = (int)(expectedSize / 0.75f) + 1;
// 向上取整到2的幂
HashMap<String, String> map = new HashMap<>(initialCapacity);
```

**建议**：
- 如果能预估元素数量，设置合适的初始容量
- 避免频繁扩容，提高性能
- 初始容量会自动调整为2的幂

---

## 八、面试回答模板

### 8.1 核心回答（1分钟）

"HashMap底层是数组+链表+红黑树的结构。JDK 1.7使用数组+链表，采用头插法，扩容时所有节点重新hash。JDK 1.8引入了红黑树，当链表长度≥8且数组容量≥64时，链表转为红黑树，查询复杂度从O(n)优化为O(log n)。同时改为尾插法，优化了hash计算和扩容机制。引入红黑树是为了解决hash冲突严重时链表过长导致的性能问题，红黑树能保证查询性能稳定在O(log n)。"

### 8.2 扩展回答（3分钟）

"从底层实现看，HashMap通过key的hash值计算数组索引，使用拉链法解决冲突。JDK 1.7的hash计算复杂，1.8简化为一次位运算和一次异或。扩容机制上，1.7需要重新hash所有节点，1.8通过判断hash值的特定位，节点位置只有两种可能，避免了重新hash。红黑树的选择是因为它在插入删除频繁的场景下性能优于AVL树。树化阈值8是根据泊松分布统计得出的，正常情况下链表长度很少超过8。"

### 8.3 加分项

- 能说出hash计算的优化细节
- 了解扩容机制的优化原理
- 知道为什么选择红黑树而不是AVL树
- 理解树化阈值8的统计学依据
- 能说出JDK 1.7并发死循环的原因
