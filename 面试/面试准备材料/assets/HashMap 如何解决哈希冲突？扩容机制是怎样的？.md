# HashMap 如何解决哈希冲突？扩容机制是怎样的？

## 一、哈希冲突概述

### 1.1 什么是哈希冲突？

**哈希冲突**（Hash Collision）是指不同的key经过哈希函数计算后得到相同的数组索引。

```java
// 示例：两个不同的key得到相同的索引
String key1 = "abc";
String key2 = "xyz";
int hash1 = key1.hashCode() & (16 - 1);  // 假设得到索引 5
int hash2 = key2.hashCode() & (16 - 1);  // 假设也得到索引 5
// 这就是哈希冲突
```

**冲突产生的原因**：
- 哈希函数是**多对一**的映射
- 不同的输入可能产生相同的输出
- 数组容量有限，冲突不可避免

### 1.2 解决哈希冲突的方法

常见的哈希冲突解决方法：

| 方法 | 说明 | 优缺点 |
|------|------|--------|
| **链地址法（拉链法）** | 冲突的元素存储在链表中 | ✅ 实现简单<br>✅ 适合动态扩容<br>❌ 需要额外空间存储指针 |
| **开放地址法** | 冲突时寻找下一个空位置 | ✅ 不需要额外空间<br>❌ 删除困难<br>❌ 容易产生聚集 |
| **再哈希法** | 使用多个哈希函数 | ✅ 冲突率低<br>❌ 计算开销大 |
| **建立公共溢出区** | 冲突元素放入溢出区 | ✅ 实现简单<br>❌ 溢出区可能很大 |

**HashMap采用链地址法**，这是最常用且最有效的方法。

---

## 二、HashMap解决哈希冲突：链地址法

### 2.1 链地址法原理

**链地址法（Separate Chaining）**：当发生哈希冲突时，将冲突的元素存储在链表中。

**结构示意图**：
```
数组索引:  0    1    2    3    4    5    ...
          │    │    │    │    │    │
          ▼    ▼    ▼    ▼    ▼    ▼
         null  │   null  │   null
               ▼         ▼
            Node1    Node1
         (key1,val1)  (key3,val3)
               │         │
               ▼         ▼
            Node2    Node2
         (key2,val2)  (key4,val4)
               │         │
               ▼         ▼
            null       null
```

### 2.2 JDK 1.7 实现：数组 + 链表

```java
// JDK 1.7 HashMap 结构
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

// 插入元素（解决冲突）
public V put(K key, V value) {
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
    
    // 不存在，添加新节点（头插法）
    addEntry(hash, key, value, i);
    return null;
}

void addEntry(int hash, K key, V value, int bucketIndex) {
    Entry<K,V> e = table[bucketIndex];
    table[bucketIndex] = new Entry<>(hash, key, value, e);  // 头插
    if (size++ >= threshold)
        resize(2 * table.length);
}
```

**特点**：
- 冲突时，新节点插入到**链表头部**（头插法）
- 查找时，从链表头部开始遍历
- 时间复杂度：**O(n)**（n为链表长度）

### 2.3 JDK 1.8 优化：数组 + 链表 + 红黑树

```java
// JDK 1.8 HashMap 结构
static class Node<K,V> implements Map.Entry<K,V> {
    final int hash;
    final K key;
    V value;
    Node<K,V> next;  // 链表节点
    
    Node(int hash, K key, V value, Node<K,V> next) {
        this.hash = hash;
        this.key = key;
        this.value = value;
        this.next = next;
    }
}

// 插入元素
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = new Node<>(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;
        else if (p instanceof TreeNode)
            // 红黑树节点
            e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
        else {
            // 链表节点：尾插法
            for (int binCount = 0; ; ++binCount) {
                if ((e = p.next) == null) {
                    p.next = new Node<>(hash, key, value, null);
                    // 树化检查
                    if (binCount >= TREEIFY_THRESHOLD - 1)
                        treeifyBin(tab, hash);
                    break;
                }
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    break;
                p = e;
            }
        }
        // ...
    }
    // ...
}
```

**优化点**：
1. **尾插法**：新节点插入到链表尾部（避免链表反转）
2. **红黑树优化**：链表长度≥8且数组容量≥64时，转为红黑树
3. **查询优化**：红黑树查询复杂度**O(log n)**

### 2.4 树化过程

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
            // 将Node转换为TreeNode
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
1. 链表长度 ≥ 8（TREEIFY_THRESHOLD）
2. 数组容量 ≥ 64（MIN_TREEIFY_CAPACITY）

**为什么需要两个条件？**
- 如果数组容量小，优先**扩容**而不是树化
- 扩容可以减少hash冲突，可能不需要树化
- 只有数组容量足够大时，才考虑树化

---

## 三、扩容机制详解

### 3.1 扩容触发条件

```java
// 扩容阈值计算
threshold = capacity * loadFactor;

// 默认值
static final int DEFAULT_INITIAL_CAPACITY = 16;  // 初始容量
static final float DEFAULT_LOAD_FACTOR = 0.75f;   // 负载因子

// 触发扩容
if (size++ >= threshold)
    resize();
```

**扩容时机**：
- 当 `size >= threshold` 时触发扩容
- `threshold = capacity × loadFactor`
- 默认：`threshold = 16 × 0.75 = 12`

### 3.2 JDK 1.7 扩容机制

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

// 计算索引
static int indexFor(int h, int length) {
    return h & (length - 1);
}
```

**特点**：
1. **容量翻倍**：`newCapacity = oldCapacity × 2`
2. **重新hash**：所有节点重新计算索引位置
3. **头插法**：新节点插入到链表头部
4. **时间复杂度**：O(n)，n为元素个数

**问题**：
- 所有节点都需要重新hash，性能开销大
- 头插法可能导致链表反转
- 并发环境下可能形成环形链表

### 3.3 JDK 1.8 扩容机制（优化）

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

1. **不需要重新hash**：
   - 通过 `(e.hash & oldCap) == 0` 判断节点位置
   - 节点位置只有两种可能：
     - **原索引位置**（`hash & oldCap == 0`）
     - **原索引 + oldCap**（`hash & oldCap != 0`）

2. **原理说明**：
   ```
   假设 oldCap = 16 (10000)
   oldCap - 1 = 15 (01111)
   newCap = 32 (100000)
   newCap - 1 = 31 (011111)
   
   节点hash值：
   - hash = 5  (00101)  -> 5 & 15 = 5,  5 & 16 = 0  -> 位置不变：5
   - hash = 21 (10101)  -> 21 & 15 = 5, 21 & 16 != 0 -> 位置改变：5+16=21
   ```

3. **性能提升**：
   - 避免重新计算hash值
   - 时间复杂度仍O(n)，但常数因子更小
   - 实际性能提升约**30-50%**

### 3.4 扩容流程图

```
开始扩容
   │
   ▼
容量翻倍 (newCap = oldCap × 2)
   │
   ▼
遍历旧数组每个位置
   │
   ├─→ 位置为空 → 跳过
   │
   ├─→ 只有一个节点 → 直接移动到新位置
   │
   ├─→ 是红黑树 → 调用split方法拆分
   │
   └─→ 是链表 → 拆分为两个链表
         │
         ├─→ loHead: hash & oldCap == 0 (原位置)
         │
         └─→ hiHead: hash & oldCap != 0 (原位置 + oldCap)
   │
   ▼
更新threshold = newCap × loadFactor
   │
   ▼
结束
```

---

## 四、扩容机制对比

### 4.1 JDK 1.7 vs JDK 1.8

| 对比项 | JDK 1.7 | JDK 1.8 |
|--------|---------|---------|
| **hash计算** | 需要重新hash | 不需要，通过位运算判断 |
| **节点移动** | 所有节点重新计算位置 | 节点位置只有两种可能 |
| **链表插入** | 头插法 | 尾插法 |
| **性能** | 较慢 | 更快（提升30-50%） |
| **并发问题** | 可能死循环 | 数据丢失（仍非线程安全） |

### 4.2 性能测试

```java
public class ResizePerformanceTest {
    public static void main(String[] args) {
        int size = 1000000;
        
        // JDK 1.7 风格（模拟）
        long start = System.currentTimeMillis();
        Map<Integer, String> map1 = new HashMap<>();
        for (int i = 0; i < size; i++) {
            map1.put(i, "value" + i);
        }
        System.out.println("JDK 1.8实际耗时: " + (System.currentTimeMillis() - start) + "ms");
        
        // 扩容次数统计
        System.out.println("扩容次数: " + calculateResizeCount(size));
    }
    
    static int calculateResizeCount(int size) {
        int capacity = 16;
        int count = 0;
        while (capacity * 0.75 < size) {
            capacity *= 2;
            count++;
        }
        return count;
    }
}
```

**扩容次数计算**：
- 初始容量16，阈值12
- 第1次扩容：容量32，阈值24
- 第2次扩容：容量64，阈值48
- 第3次扩容：容量128，阈值96
- ...
- 100万元素大约需要**20次扩容**

---

## 五、负载因子详解

### 5.1 负载因子作用

**负载因子（Load Factor）**：`threshold = capacity × loadFactor`

**作用**：
- 控制HashMap的**填充程度**
- 平衡**时间和空间**的利用率

### 5.2 为什么是0.75？

**0.75是经验值**，经过大量测试得出的最优值：

| 负载因子 | 空间利用率 | 冲突概率 | 性能 |
|---------|-----------|---------|------|
| **0.5** | 低 | 低 | 频繁扩容，性能差 |
| **0.75** | 较高 | 适中 | ✅ 最优平衡 |
| **1.0** | 高 | 高 | 冲突多，性能差 |

**数学依据**（泊松分布）：
- 负载因子0.75时，冲突概率和空间利用率达到最佳平衡
- 链表长度达到8的概率：**0.00000006**（极低）

### 5.3 负载因子调整

```java
// 自定义负载因子
HashMap<String, String> map = new HashMap<>(16, 0.5f);
// 初始容量16，负载因子0.5
// 阈值 = 16 × 0.5 = 8

// 适用场景：
// - 0.5：读多写少，希望减少冲突
// - 0.75：默认值，通用场景
// - 1.0：写多读少，希望充分利用空间
```

---

## 六、常见面试追问

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

### Q2：HashMap扩容有什么缺点？

**答**：
1. **性能开销**：扩容需要重新分配数组和移动节点，时间复杂度O(n)
2. **内存占用**：扩容时新旧数组同时存在，内存占用翻倍
3. **GC压力**：频繁扩容会产生大量临时对象，增加GC压力
4. **并发问题**：多线程环境下扩容可能导致数据丢失或死循环

**优化建议**：
- 如果能预估元素数量，设置合适的初始容量
- 避免频繁扩容，提高性能

### Q3：如何避免频繁扩容？

**答**：
```java
// 预估元素数量
int expectedSize = 1000;
// 初始容量 = expectedSize / loadFactor + 1
int initialCapacity = (int)(expectedSize / 0.75f) + 1;
// 向上取整到2的幂
HashMap<String, String> map = new HashMap<>(initialCapacity);
```

**建议**：
- 如果能预估元素数量，设置合适的初始容量
- 避免频繁扩容，提高性能
- 初始容量会自动调整为2的幂

### Q4：扩容时红黑树如何处理？

**答**：
```java
// 红黑树节点拆分
final void split(HashMap<K,V> map, Node<K,V>[] tab, int index, int bit) {
    TreeNode<K,V> b = this;
    TreeNode<K,V> loHead = null, loTail = null;
    TreeNode<K,V> hiHead = null, hiTail = null;
    int lc = 0, hc = 0;
    for (TreeNode<K,V> e = b, next; e != null; e = next) {
        next = (TreeNode<K,V>)e.next;
        e.next = null;
        // 判断节点位置
        if ((e.hash & bit) == 0) {
            // 原位置
            if ((e.prev = loTail) == null)
                loHead = e;
            else
                loTail.next = e;
            loTail = e;
            ++lc;
        }
        else {
            // 新位置
            if ((e.prev = hiTail) == null)
                hiHead = e;
            else
                hiTail.next = e;
            hiTail = e;
            ++hc;
        }
    }
    // 如果节点数 <= 6，退化为链表
    if (loHead != null) {
        if (lc <= UNTREEIFY_THRESHOLD)
            tab[index] = loHead.untreeify(map);
        else {
            tab[index] = loHead;
            if (hiHead != null)
                loHead.treeify(tab);
        }
    }
    // ...
}
```

**处理流程**：
1. 将红黑树拆分为两个链表（loHead和hiHead）
2. 如果节点数 ≤ 6，退化为链表
3. 否则，重新构建红黑树

---

## 七、面试回答模板

### 7.1 核心回答（1分钟）

"HashMap通过链地址法解决哈希冲突，冲突的元素存储在链表中。JDK 1.8引入了红黑树优化，当链表长度≥8且数组容量≥64时，链表转为红黑树，查询复杂度从O(n)优化为O(log n)。扩容机制方面，当元素数量超过容量×负载因子时触发扩容，容量翻倍。JDK 1.7需要重新hash所有节点，JDK 1.8优化后通过判断hash值的特定位，节点位置只有两种可能：原索引或原索引+oldCap，避免了重新hash，性能提升约30-50%。"

### 7.2 扩展回答（3分钟）

"从冲突解决看，HashMap使用链地址法，数组每个位置存储链表或红黑树的头节点。JDK 1.7使用头插法，1.8改为尾插法避免链表反转。树化条件是根据泊松分布统计得出的，正常情况下链表长度很少超过8。扩容机制上，负载因子0.75是平衡时间和空间的最优值。JDK 1.8的扩容优化利用了数组长度是2的幂的特性，通过位运算快速判断节点位置，避免了重新hash的开销。"

### 7.3 加分项

- 能说出链地址法的原理和优势
- 了解JDK 1.8扩容优化的具体实现
- 知道为什么数组长度必须是2的幂
- 理解负载因子0.75的选择依据
- 能说出如何避免频繁扩容
