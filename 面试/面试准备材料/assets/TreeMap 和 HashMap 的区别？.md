# TreeMap 和 HashMap 的区别？TreeMap 如何保证有序？

## 一、TreeMap 和 HashMap 概述

### 1.1 定义

**HashMap**：
- **包路径**：`java.util.HashMap`
- **定义**：基于哈希表实现的 Map，key-value 键值对存储
- **特点**：无序、允许 null key/value、非线程安全
- **继承关系**：继承自 `AbstractMap`，实现 `Map` 接口

**TreeMap**：
- **包路径**：`java.util.TreeMap`
- **定义**：基于红黑树（Red-Black Tree）实现的 Map，key 有序
- **特点**：有序、不允许 null key、非线程安全
- **继承关系**：继承自 `AbstractMap`，实现 `NavigableMap` 接口

### 1.2 核心对比

| 特性 | HashMap | TreeMap |
|------|---------|---------|
| **底层实现** | 数组 + 链表 + 红黑树 | 红黑树 |
| **有序性** | ❌ 无序 | ✅ 有序（按 key 排序） |
| **null key** | ✅ 允许一个 | ❌ 不允许 |
| **null value** | ✅ 允许多个 | ✅ 允许多个 |
| **性能** | O(1) 平均 | O(log n) |
| **线程安全** | ❌ 非线程安全 | ❌ 非线程安全 |
| **排序方式** | 无 | 自然排序或自定义 Comparator |

---

## 二、底层实现原理对比

### 2.1 HashMap 的底层实现

**数据结构**：
```java
// HashMap 源码结构
public class HashMap<K,V> extends AbstractMap<K,V> {
    // 数组（桶）
    transient Node<K,V>[] table;
    
    // 节点结构（链表）
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;
    }
    
    // 红黑树节点（JDK 1.8+）
    static final class TreeNode<K,V> extends LinkedHashMap.Entry<K,V> {
        TreeNode<K,V> parent;
        TreeNode<K,V> left;
        TreeNode<K,V> right;
        TreeNode<K,V> prev;
        boolean red;
    }
}
```

**存储机制**：
- 通过 `hashCode()` 计算哈希值，定位到数组索引
- 如果发生哈希冲突，使用链表或红黑树存储
- 当链表长度 >= 8 且数组长度 >= 64 时，转换为红黑树

### 2.2 TreeMap 的底层实现

**数据结构**：
```java
// TreeMap 源码结构
public class TreeMap<K,V> extends AbstractMap<K,V> 
    implements NavigableMap<K,V> {
    
    // 比较器
    private final Comparator<? super K> comparator;
    
    // 红黑树根节点
    private transient Entry<K,V> root;
    
    // 红黑树节点
    static final class Entry<K,V> implements Map.Entry<K,V> {
        K key;
        V value;
        Entry<K,V> left;
        Entry<K,V> right;
        Entry<K,V> parent;
        boolean color = BLACK;  // 红色或黑色
    }
}
```

**存储机制**：
- 所有元素存储在红黑树中
- 插入时根据 key 的大小关系找到合适位置
- 通过旋转和变色保持红黑树平衡

---

## 三、TreeMap 如何保证有序？

### 3.1 红黑树的有序性

**红黑树特性**：
- 红黑树是自平衡二叉查找树
- 中序遍历（左-根-右）的结果是有序的
- 通过比较 key 的大小决定插入位置

**插入流程**：
```java
// TreeMap 的 put 方法（简化版）
public V put(K key, V value) {
    Entry<K,V> t = root;
    if (t == null) {
        // 第一个节点作为根节点
        root = new Entry<>(key, value, null);
        size = 1;
        return null;
    }
    
    int cmp;
    Entry<K,V> parent;
    Comparator<? super K> cpr = comparator;
    
    if (cpr != null) {
        // 使用自定义比较器
        do {
            parent = t;
            cmp = cpr.compare(key, t.key);
            if (cmp < 0)
                t = t.left;   // 小于当前节点，往左
            else if (cmp > 0)
                t = t.right;   // 大于当前节点，往右
            else
                return t.setValue(value);  // 相等，覆盖
        } while (t != null);
    } else {
        // 使用自然排序（key 必须实现 Comparable）
        if (key == null)
            throw new NullPointerException();
        Comparable<? super K> k = (Comparable<? super K>) key;
        do {
            parent = t;
            cmp = k.compareTo(t.key);
            if (cmp < 0)
                t = t.left;
            else if (cmp > 0)
                t = t.right;
            else
                return t.setValue(value);
        } while (t != null);
    }
    
    // 创建新节点并插入
    Entry<K,V> e = new Entry<>(key, value, parent);
    if (cmp < 0)
        parent.left = e;
    else
        parent.right = e;
    
    // 修复红黑树平衡（旋转和变色）
    fixAfterInsertion(e);
    size++;
    return null;
}
```

### 3.2 排序规则

**两种排序方式**：

1. **自然排序**（Natural Ordering）：
   - key 必须实现 `Comparable` 接口
   - 使用 `key.compareTo(otherKey)` 比较

```java
// 示例：使用自然排序
TreeMap<String, Integer> map = new TreeMap<>();
map.put("apple", 1);
map.put("banana", 2);
map.put("cherry", 3);

// 遍历结果：apple, banana, cherry（按字母顺序）
for (String key : map.keySet()) {
    System.out.println(key);
}
```

2. **自定义排序**（Custom Comparator）：
   - 创建 TreeMap 时传入 `Comparator`
   - 使用 `comparator.compare(key1, key2)` 比较

```java
// 示例：使用自定义比较器（降序）
TreeMap<Integer, String> map = new TreeMap<>(Comparator.reverseOrder());
map.put(3, "three");
map.put(1, "one");
map.put(2, "two");

// 遍历结果：3, 2, 1（降序）
for (Integer key : map.keySet()) {
    System.out.println(key);
}

// 示例：自定义比较器（按学生年龄排序）
TreeMap<Student, String> studentMap = new TreeMap<>(
    Comparator.comparing(Student::getAge).thenComparing(Student::getName)
);
```

### 3.3 红黑树平衡机制

**红黑树的 5 条规则**：
1. 每个节点要么是红色，要么是黑色
2. 根节点是黑色
3. 每个叶子节点（NIL）是黑色
4. 如果一个节点是红色，那么它的两个子节点都是黑色
5. 从任意节点到其每个叶子的所有路径都包含相同数目的黑色节点

**平衡操作**：
- **左旋**（Left Rotation）：将右子节点提升为父节点
- **右旋**（Right Rotation）：将左子节点提升为父节点
- **变色**（Color Flip）：改变节点颜色

**插入后的修复**：
```java
// TreeMap 的 fixAfterInsertion 方法（简化版）
private void fixAfterInsertion(Entry<K,V> x) {
    x.color = RED;  // 新插入的节点设为红色
    
    while (x != null && x != root && x.parent.color == RED) {
        if (parentOf(x) == leftOf(parentOf(parentOf(x)))) {
            Entry<K,V> y = rightOf(parentOf(parentOf(x)));
            if (colorOf(y) == RED) {
                // 情况1：叔叔节点是红色，变色
                setColor(parentOf(x), BLACK);
                setColor(y, BLACK);
                setColor(parentOf(parentOf(x)), RED);
                x = parentOf(parentOf(x));
            } else {
                // 情况2/3：叔叔节点是黑色，旋转
                if (x == rightOf(parentOf(x))) {
                    x = parentOf(x);
                    rotateLeft(x);
                }
                setColor(parentOf(x), BLACK);
                setColor(parentOf(parentOf(x)), RED);
                rotateRight(parentOf(parentOf(x)));
            }
        } else {
            // 对称情况（右子树）
            // ...
        }
    }
    root.color = BLACK;  // 根节点始终是黑色
}
```

---

## 四、详细对比

### 4.1 性能对比

| 操作 | HashMap | TreeMap |
|------|---------|---------|
| **put** | O(1) 平均，O(n) 最坏 | O(log n) |
| **get** | O(1) 平均，O(n) 最坏 | O(log n) |
| **remove** | O(1) 平均，O(n) 最坏 | O(log n) |
| **containsKey** | O(1) 平均，O(n) 最坏 | O(log n) |
| **遍历** | O(n) | O(n) |

**性能分析**：
- **HashMap**：哈希定位快，但最坏情况下（所有元素哈希冲突）退化为链表，性能 O(n)
- **TreeMap**：所有操作都是 O(log n)，性能稳定，但比 HashMap 慢

### 4.2 使用场景对比

**HashMap 适用场景**：
- ✅ 需要快速查找、插入、删除
- ✅ 不需要保持 key 的顺序
- ✅ 允许 null key/value
- ✅ 数据量大，追求性能

**TreeMap 适用场景**：
- ✅ 需要保持 key 有序
- ✅ 需要范围查询（如 `subMap`、`headMap`、`tailMap`）
- ✅ 需要按顺序遍历
- ✅ key 需要实现 Comparable 或提供 Comparator

### 4.3 null 值处理

**HashMap**：
```java
HashMap<String, Integer> map = new HashMap<>();
map.put(null, 1);        // ✅ 允许
map.put("key", null);    // ✅ 允许
map.put(null, null);     // ✅ 允许（覆盖之前的 null key）
```

**TreeMap**：
```java
TreeMap<String, Integer> map = new TreeMap<>();
map.put(null, 1);        // ❌ NullPointerException
map.put("key", null);    // ✅ 允许
```

**原因**：
- TreeMap 需要比较 key 的大小，null 无法比较
- HashMap 使用 `hashCode()`，null 的 hashCode 为 0

---

## 五、实际应用场景

### 5.1 场景1：排行榜系统

```java
// 使用 TreeMap 实现按分数排序的排行榜
TreeMap<Integer, List<String>> leaderboard = new TreeMap<>(Comparator.reverseOrder());

public void addScore(String player, int score) {
    leaderboard.computeIfAbsent(score, k -> new ArrayList<>()).add(player);
}

public List<String> getTopPlayers(int topN) {
    return leaderboard.entrySet().stream()
        .limit(topN)
        .flatMap(entry -> entry.getValue().stream())
        .collect(Collectors.toList());
}
```

### 5.2 场景2：区间查询

```java
// 使用 TreeMap 实现时间范围查询
TreeMap<LocalDateTime, Order> orderMap = new TreeMap<>();

// 查询某个时间段的订单
public List<Order> getOrdersBetween(LocalDateTime start, LocalDateTime end) {
    return new ArrayList<>(orderMap.subMap(start, true, end, true).values());
}

// 查询某个时间点之前的订单
public List<Order> getOrdersBefore(LocalDateTime time) {
    return new ArrayList<>(orderMap.headMap(time, true).values());
}
```

### 5.3 场景3：缓存最近访问的数据（LRU）

```java
// 使用 TreeMap 实现按访问时间排序的缓存
TreeMap<Long, String> accessTimeCache = new TreeMap<>();

public void access(String data) {
    long currentTime = System.currentTimeMillis();
    accessTimeCache.put(currentTime, data);
    
    // 清理超过 1 小时的旧数据
    long oneHourAgo = currentTime - 3600000;
    accessTimeCache.headMap(oneHourAgo).clear();
}
```

### 5.4 场景4：HashMap 快速查找

```java
// 使用 HashMap 存储用户信息，快速查找
HashMap<Long, User> userMap = new HashMap<>();

public User getUserById(Long userId) {
    return userMap.get(userId);  // O(1) 快速查找
}

public void updateUser(Long userId, User user) {
    userMap.put(userId, user);  // O(1) 快速更新
}
```

---

## 六、常见面试追问

### Q1：TreeMap 为什么不用 HashMap？

**答**：
- **需要有序性**：TreeMap 保证 key 有序，HashMap 无序
- **范围查询**：TreeMap 提供 `subMap`、`headMap`、`tailMap` 等方法，HashMap 不支持
- **性能权衡**：虽然 TreeMap 的 O(log n) 比 HashMap 的 O(1) 慢，但有序性更重要

### Q2：TreeMap 是线程安全的吗？

**答**：
- ❌ **非线程安全**：TreeMap 不是线程安全的
- **线程安全替代**：
  - `Collections.synchronizedMap(new TreeMap<>())`
  - `ConcurrentSkipListMap`（基于跳表，支持并发，性能更好）

### Q3：ConcurrentSkipListMap 和 TreeMap 的区别？

**答**：

| 特性 | TreeMap | ConcurrentSkipListMap |
|------|---------|----------------------|
| **底层实现** | 红黑树 | 跳表（Skip List） |
| **线程安全** | ❌ 非线程安全 | ✅ 线程安全 |
| **性能** | O(log n) | O(log n) |
| **并发性能** | 不支持并发 | 支持高并发 |
| **有序性** | ✅ 有序 | ✅ 有序 |

**选择建议**：
- **单线程场景**：使用 TreeMap
- **多线程场景**：使用 ConcurrentSkipListMap

### Q4：TreeMap 的 key 为什么不能为 null？

**答**：
- **需要比较**：TreeMap 需要比较 key 的大小来决定插入位置
- **null 无法比较**：`null.compareTo(other)` 或 `comparator.compare(null, other)` 会抛出 `NullPointerException`
- **HashMap 可以**：HashMap 使用 `hashCode()`，null 的 hashCode 为 0，可以处理

### Q5：TreeMap 和 LinkedHashMap 的区别？

**答**：

| 特性 | TreeMap | LinkedHashMap |
|------|---------|---------------|
| **有序性** | 按 key 排序 | 按插入顺序或访问顺序 |
| **底层实现** | 红黑树 | 数组 + 链表 + 双向链表 |
| **性能** | O(log n) | O(1) 平均 |
| **排序规则** | 自然排序或 Comparator | 插入顺序或 LRU |

**选择建议**：
- **需要按 key 排序**：使用 TreeMap
- **需要保持插入顺序或 LRU**：使用 LinkedHashMap

### Q6：TreeMap 如何实现范围查询？

**答**：
- **subMap(K fromKey, K toKey)**：返回指定范围的子 Map
- **headMap(K toKey)**：返回小于 toKey 的所有键值对
- **tailMap(K fromKey)**：返回大于等于 fromKey 的所有键值对
- **firstKey() / lastKey()**：返回最小/最大 key
- **lowerKey(K key) / higherKey(K key)**：返回小于/大于指定 key 的最大/最小 key

```java
TreeMap<Integer, String> map = new TreeMap<>();
map.put(1, "one");
map.put(3, "three");
map.put(5, "five");
map.put(7, "seven");
map.put(9, "nine");

// 范围查询
SortedMap<Integer, String> subMap = map.subMap(3, 7);  // {3=three, 5=five}
SortedMap<Integer, String> headMap = map.headMap(5);     // {1=one, 3=three}
SortedMap<Integer, String> tailMap = map.tailMap(5);     // {5=five, 7=seven, 9=nine}
```

---

## 七、面试回答模板

### 7.1 核心回答（1分钟）

"HashMap 基于哈希表实现，通过 hashCode 定位，平均时间复杂度 O(1)，但无序。TreeMap 基于红黑树实现，所有操作 O(log n)，但保证 key 有序。TreeMap 的有序性来自红黑树的中序遍历特性，插入时根据 key 的大小关系找到合适位置，通过旋转和变色保持平衡。TreeMap 支持自然排序（key 实现 Comparable）或自定义排序（传入 Comparator）。HashMap 允许 null key，TreeMap 不允许，因为需要比较 key 的大小。"

### 7.2 扩展回答（3分钟）

"从底层实现看，HashMap 使用数组加链表或红黑树，通过哈希值定位桶，平均 O(1) 但最坏 O(n)。TreeMap 完全基于红黑树，所有操作都是 O(log n)，性能稳定但比 HashMap 慢。TreeMap 的有序性通过红黑树的中序遍历保证，插入时根据比较结果决定左右子树，插入后通过旋转和变色修复平衡。TreeMap 支持两种排序：自然排序要求 key 实现 Comparable，自定义排序可以传入 Comparator。TreeMap 还提供范围查询方法如 subMap、headMap、tailMap，适合排行榜、区间查询等场景。HashMap 适合快速查找，TreeMap 适合需要有序的场景。"

### 7.3 加分项

- 能说出 TreeMap 基于红黑树实现
- 了解红黑树的平衡机制（旋转和变色）
- 知道 TreeMap 支持自然排序和自定义排序
- 理解 TreeMap 为什么不允许 null key
- 知道 TreeMap 提供范围查询方法
- 了解 ConcurrentSkipListMap 作为线程安全替代
