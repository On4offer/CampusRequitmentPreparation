# Set 接口的常见实现类有哪些？它们的底层原理是什么？

## 一、Set 接口概述

### 1.1 定义

**Set 接口**：
- **包路径**：`java.util.Set`
- **定义**：**不允许重复元素**的集合接口
- **特点**：元素唯一，不保证顺序（除了某些实现类）
- **继承关系**：继承自 `Collection` 接口

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **元素唯一性** | 不允许重复元素 |
| **顺序性** | 大部分实现类不保证顺序 |
| **null 值** | 大部分实现类允许一个 null 值 |

### 1.3 常见实现类

| 实现类 | 底层实现 | 特点 | 线程安全 |
|--------|---------|------|---------|
| **HashSet** | HashMap | 无序、不重复 | ❌ |
| **LinkedHashSet** | LinkedHashMap | 有序（插入顺序）、不重复 | ❌ |
| **TreeSet** | TreeMap（红黑树） | 有序（排序）、不重复 | ❌ |
| **CopyOnWriteArraySet** | CopyOnWriteArrayList | 读多写少、不重复 | ✅ |
| **ConcurrentSkipListSet** | ConcurrentSkipListMap（跳表） | 有序、并发安全 | ✅ |

---

## 二、HashSet 详解

### 2.1 底层实现原理

**HashSet 基于 HashMap 实现**：

```java
// HashSet 源码
public class HashSet<E> extends AbstractSet<E> implements Set<E> {
    private transient HashMap<E,Object> map;  // 底层 HashMap
    
    // 固定的常量对象作为 value
    private static final Object PRESENT = new Object();
    
    // 构造方法
    public HashSet() {
        map = new HashMap<>();
    }
    
    // add 方法：将元素作为 key，PRESENT 作为 value
    public boolean add(E e) {
        return map.put(e, PRESENT) == null;
    }
    
    // contains 方法
    public boolean contains(Object o) {
        return map.containsKey(o);
    }
    
    // remove 方法
    public boolean remove(Object o) {
        return map.remove(o) == PRESENT;
    }
}
```

**核心原理**：
- ✅ **元素作为 key**：Set 中的元素作为 HashMap 的 key 存储
- ✅ **固定 value**：使用常量 `PRESENT` 作为所有元素的 value
- ✅ **去重机制**：利用 HashMap 的 key 唯一性保证元素不重复

### 2.2 去重机制

**HashSet 如何判断元素重复**：

```java
// HashMap 的 put 方法
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}

final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = new Node<>(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        // 1. 先比较 hashCode
        if (p.hash == hash &&
            // 2. 再比较 equals
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;  // 找到相同元素，不插入
        // ...
    }
}
```

**判断流程**：
1. **hashCode 定位**：通过 `hashCode()` 计算哈希值，定位到桶
2. **equals 比较**：在桶内使用 `equals()` 比较元素
3. **如果相同**：不插入，返回 false
4. **如果不同**：插入，返回 true

**示例**：
```java
Set<String> set = new HashSet<>();
set.add("apple");
set.add("banana");
set.add("apple");  // 重复，不会插入

System.out.println(set.size());  // 2
```

### 2.3 特点

| 特点 | 说明 |
|------|------|
| **无序** | 不保证元素的插入顺序 |
| **不重复** | 依赖 hashCode() 和 equals() 保证唯一性 |
| **允许 null** | 允许一个 null 值 |
| **性能** | 添加、删除、查找都是 O(1) 平均时间复杂度 |

### 2.4 使用示例

```java
// HashSet 使用示例
Set<String> set = new HashSet<>();
set.add("apple");
set.add("banana");
set.add("cherry");
set.add("apple");  // 重复，不会添加

System.out.println(set);  // [banana, apple, cherry]（顺序不确定）

// 判断是否包含
boolean contains = set.contains("apple");  // true

// 删除元素
set.remove("banana");
```

---

## 三、LinkedHashSet 详解

### 3.1 底层实现原理

**LinkedHashSet 基于 LinkedHashMap 实现**：

```java
// LinkedHashSet 源码
public class LinkedHashSet<E> extends HashSet<E> implements Set<E> {
    // 构造方法：调用父类构造，传入 LinkedHashMap
    public LinkedHashSet() {
        super(16, .75f, true);  // 调用 HashSet 的构造方法
    }
}

// HashSet 的构造方法
HashSet(int initialCapacity, float loadFactor, boolean dummy) {
    map = new LinkedHashMap<>(initialCapacity, loadFactor);
}
```

**核心原理**：
- ✅ **继承 HashSet**：继承自 HashSet
- ✅ **底层 LinkedHashMap**：使用 LinkedHashMap 替代 HashMap
- ✅ **双向链表**：LinkedHashMap 维护双向链表，记录插入顺序

### 3.2 LinkedHashMap 的双向链表

```java
// LinkedHashMap 的节点结构
static class Entry<K,V> extends HashMap.Node<K,V> {
    Entry<K,V> before, after;  // 双向链表的前后指针
    
    Entry(int hash, K key, V value, Node<K,V> next) {
        super(hash, key, value, next);
    }
}
```

**结构图**：
```
head ←→ [entry1] ←→ [entry2] ←→ [entry3] ←→ tail
         ↑           ↑           ↑
       HashMap     HashMap     HashMap
        桶          桶          桶
```

### 3.3 特点

| 特点 | 说明 |
|------|------|
| **有序** | 保持元素的**插入顺序** |
| **不重复** | 继承 HashSet 的去重机制 |
| **性能** | 比 HashSet 略慢（需要维护链表） |
| **内存** | 比 HashSet 占用更多内存（链表指针） |

### 3.4 使用示例

```java
// LinkedHashSet 使用示例
Set<String> set = new LinkedHashSet<>();
set.add("apple");
set.add("banana");
set.add("cherry");
set.add("apple");  // 重复，不会添加

System.out.println(set);  // [apple, banana, cherry]（保持插入顺序）

// 遍历时保持插入顺序
for (String s : set) {
    System.out.println(s);  // apple, banana, cherry
}
```

---

## 四、TreeSet 详解

### 4.1 底层实现原理

**TreeSet 基于 TreeMap（红黑树）实现**：

```java
// TreeSet 源码
public class TreeSet<E> extends AbstractSet<E> implements NavigableSet<E> {
    private transient NavigableMap<E,Object> m;  // 底层 TreeMap
    
    // 固定的常量对象作为 value
    private static final Object PRESENT = new Object();
    
    // 构造方法
    public TreeSet() {
        this(new TreeMap<E,Object>());
    }
    
    // add 方法：将元素作为 key，PRESENT 作为 value
    public boolean add(E e) {
        return m.put(e, PRESENT) == null;
    }
}
```

**核心原理**：
- ✅ **红黑树**：底层使用 TreeMap，TreeMap 基于红黑树实现
- ✅ **有序**：红黑树保证元素有序
- ✅ **去重**：利用 TreeMap 的 key 唯一性

### 4.2 红黑树结构

**红黑树特点**：
- ✅ **自平衡**：自动保持平衡，避免退化为链表
- ✅ **有序**：中序遍历是有序的
- ✅ **性能**：查找、插入、删除都是 O(log n)

**排序方式**：

**方式1：自然排序（实现 Comparable）**
```java
// 元素实现 Comparable
public class Student implements Comparable<Student> {
    private String name;
    private int age;
    
    @Override
    public int compareTo(Student o) {
        return this.age - o.age;
    }
}

// 使用自然排序
Set<Student> set = new TreeSet<>();
set.add(new Student("张三", 20));
set.add(new Student("李四", 18));
// 自动按年龄排序
```

**方式2：定制排序（传入 Comparator）**
```java
// 使用 Comparator
Set<Student> set = new TreeSet<>(
    Comparator.comparing(Student::getAge).reversed()
);
set.add(new Student("张三", 20));
set.add(new Student("李四", 18));
// 按年龄降序排序
```

### 4.3 特点

| 特点 | 说明 |
|------|------|
| **有序** | 元素自动排序（自然排序或自定义排序） |
| **不重复** | 利用 TreeMap 的 key 唯一性 |
| **性能** | 查找、插入、删除都是 O(log n) |
| **不允许 null** | TreeSet 不允许 null 值（无法比较） |

### 4.4 使用示例

```java
// TreeSet 使用示例（自然排序）
Set<Integer> set = new TreeSet<>();
set.add(3);
set.add(1);
set.add(4);
set.add(1);  // 重复，不会添加

System.out.println(set);  // [1, 3, 4]（自动排序）

// 使用 Comparator
Set<String> set2 = new TreeSet<>(Comparator.reverseOrder());
set2.add("apple");
set2.add("banana");
set2.add("cherry");
System.out.println(set2);  // [cherry, banana, apple]（降序）
```

---

## 五、线程安全 Set 实现

### 5.1 CopyOnWriteArraySet

**底层实现**：
```java
// CopyOnWriteArraySet 源码
public class CopyOnWriteArraySet<E> extends AbstractSet<E> {
    private final CopyOnWriteArrayList<E> al;  // 底层 CopyOnWriteArrayList
    
    public CopyOnWriteArraySet() {
        al = new CopyOnWriteArrayList<E>();
    }
    
    public boolean add(E e) {
        return al.addIfAbsent(e);  // 如果不存在才添加
    }
}
```

**特点**：
- ✅ **线程安全**：基于 CopyOnWriteArrayList
- ✅ **读多写少**：适合读操作频繁的场景
- ✅ **弱一致性**：迭代时可能读不到最新数据
- ❌ **写开销大**：写操作需要复制整个数组

**使用示例**：
```java
import java.util.concurrent.CopyOnWriteArraySet;

Set<String> set = new CopyOnWriteArraySet<>();
set.add("apple");
set.add("banana");

// 多线程安全
for (String s : set) {
    System.out.println(s);
}
```

### 5.2 ConcurrentSkipListSet

**底层实现**：
```java
// ConcurrentSkipListSet 源码
public class ConcurrentSkipListSet<E> extends AbstractSet<E> {
    private final ConcurrentNavigableMap<E,Object> m;  // 底层 ConcurrentSkipListMap
    
    public ConcurrentSkipListSet() {
        m = new ConcurrentSkipListMap<E,Object>();
    }
}
```

**特点**：
- ✅ **线程安全**：基于 ConcurrentSkipListMap（跳表）
- ✅ **有序**：元素自动排序
- ✅ **高性能**：使用无锁算法，性能好
- ✅ **并发安全**：支持高并发场景

**使用示例**：
```java
import java.util.concurrent.ConcurrentSkipListSet;

Set<Integer> set = new ConcurrentSkipListSet<>();
set.add(3);
set.add(1);
set.add(4);

// 多线程安全，自动排序
System.out.println(set);  // [1, 3, 4]
```

---

## 六、详细对比表

### 6.1 功能对比

| 对比项 | HashSet | LinkedHashSet | TreeSet | CopyOnWriteArraySet | ConcurrentSkipListSet |
|--------|---------|--------------|---------|-------------------|---------------------|
| **底层实现** | HashMap | LinkedHashMap | TreeMap（红黑树） | CopyOnWriteArrayList | ConcurrentSkipListMap（跳表） |
| **有序性** | ❌ 无序 | ✅ 插入顺序 | ✅ 排序 | ❌ 无序 | ✅ 排序 |
| **线程安全** | ❌ | ❌ | ❌ | ✅ | ✅ |
| **性能（查找）** | O(1) | O(1) | O(log n) | O(n) | O(log n) |
| **性能（插入）** | O(1) | O(1) | O(log n) | O(n) | O(log n) |
| **允许 null** | ✅ 1个 | ✅ 1个 | ❌ | ✅ 1个 | ❌ |
| **适用场景** | 去重 | 去重+顺序 | 去重+排序 | 读多写少 | 并发+排序 |

### 6.2 选择建议

**选择 HashSet**：
- ✅ 只需要去重，不需要顺序
- ✅ 单线程场景
- ✅ 性能要求高

**选择 LinkedHashSet**：
- ✅ 需要去重 + 保持插入顺序
- ✅ 单线程场景
- ✅ LRU 缓存场景

**选择 TreeSet**：
- ✅ 需要去重 + 自动排序
- ✅ 单线程场景
- ✅ 需要范围查询

**选择 CopyOnWriteArraySet**：
- ✅ 读多写少场景
- ✅ 多线程场景
- ✅ 可以接受弱一致性

**选择 ConcurrentSkipListSet**：
- ✅ 高并发场景
- ✅ 需要排序
- ✅ 需要范围查询

---

## 七、实际应用场景

### 7.1 场景1：用户点赞记录（HashSet）

```java
// 用户点赞过的商户 ID（只需要去重）
Set<Long> likedShopIds = new HashSet<>();

public void likeShop(Long shopId) {
    likedShopIds.add(shopId);
}

public boolean isLiked(Long shopId) {
    return likedShopIds.contains(shopId);
}
```

### 7.2 场景2：访问记录（LinkedHashSet）

```java
// 用户访问记录（需要保持访问顺序，实现 LRU）
Set<String> accessHistory = new LinkedHashSet<>();

public void recordAccess(String url) {
    if (accessHistory.contains(url)) {
        accessHistory.remove(url);  // 移除旧记录
    }
    accessHistory.add(url);  // 添加到末尾
    
    // 限制大小
    if (accessHistory.size() > 100) {
        String first = accessHistory.iterator().next();
        accessHistory.remove(first);
    }
}
```

### 7.3 场景3：排行榜（TreeSet）

```java
// 学生成绩排行榜（需要排序）
Set<Student> ranking = new TreeSet<>(
    Comparator.comparing(Student::getScore).reversed()
);

public void addStudent(Student student) {
    ranking.add(student);
}

public List<Student> getTopN(int n) {
    return ranking.stream()
        .limit(n)
        .collect(Collectors.toList());
}
```

### 7.4 场景4：在线用户集合（CopyOnWriteArraySet）

```java
// 在线用户集合（读多写少）
Set<User> onlineUsers = new CopyOnWriteArraySet<>();

public void userLogin(User user) {
    onlineUsers.add(user);
}

public void userLogout(User user) {
    onlineUsers.remove(user);
}

public int getOnlineCount() {
    return onlineUsers.size();  // 读操作，无锁
}
```

---

## 八、常见面试追问

### Q1：HashSet 为什么不能保证顺序？

**答**：
- **底层 HashMap**：HashSet 基于 HashMap 实现
- **哈希定位**：元素存储位置由 `hashCode()` 决定
- **哈希冲突**：不同元素可能映射到同一桶，顺序不确定
- **扩容影响**：扩容时元素重新分布，顺序改变

**示例**：
```java
Set<String> set = new HashSet<>();
set.add("apple");
set.add("banana");
set.add("cherry");
System.out.println(set);  // 顺序不确定，可能是 [banana, apple, cherry]
```

### Q2：HashSet 和 TreeSet 的选择？

**答**：

| 对比项 | HashSet | TreeSet |
|--------|---------|---------|
| **性能** | O(1) | O(log n) |
| **有序性** | ❌ 无序 | ✅ 有序 |
| **适用场景** | 只需要去重 | 需要去重 + 排序 |
| **null 值** | ✅ 允许 | ❌ 不允许 |

**选择建议**：
- **只需要去重**：使用 HashSet
- **需要排序**：使用 TreeSet

### Q3：如果要线程安全的 Set 怎么办？

**答**：

**方式1：Collections.synchronizedSet()**（不推荐）
```java
Set<String> set = Collections.synchronizedSet(new HashSet<>());
```

**方式2：CopyOnWriteArraySet**（读多写少）
```java
Set<String> set = new CopyOnWriteArraySet<>();
```

**方式3：ConcurrentSkipListSet**（高并发+排序）
```java
Set<String> set = new ConcurrentSkipListSet<>();
```

**推荐**：根据场景选择 CopyOnWriteArraySet 或 ConcurrentSkipListSet

### Q4：HashSet 如何判断元素重复？

**答**：
1. **hashCode 定位**：通过 `hashCode()` 计算哈希值，定位到桶
2. **equals 比较**：在桶内使用 `equals()` 比较元素
3. **如果相同**：不插入，返回 false
4. **如果不同**：插入，返回 true

**重要**：必须同时重写 `hashCode()` 和 `equals()`，使用相同的字段

### Q5：LinkedHashSet 如何保持插入顺序？

**答**：
- **底层 LinkedHashMap**：使用 LinkedHashMap 替代 HashMap
- **双向链表**：LinkedHashMap 维护双向链表，记录插入顺序
- **插入时**：元素插入 HashMap 的同时，也插入双向链表
- **遍历时**：按照双向链表的顺序遍历

---

## 九、面试回答模板

### 9.1 核心回答（1分钟）

"Set 的常见实现类有 HashSet、LinkedHashSet、TreeSet。HashSet 基于 HashMap 实现，元素作为 key 存储，value 使用固定常量，利用 HashMap 的 key 唯一性保证元素不重复，特点是无序、不重复，性能 O(1)。LinkedHashSet 继承 HashSet，底层使用 LinkedHashMap，维护双向链表记录插入顺序，特点是有序、不重复。TreeSet 基于 TreeMap 实现，TreeMap 使用红黑树，特点是有序、不重复，性能 O(log n)。线程安全的有 CopyOnWriteArraySet 和 ConcurrentSkipListSet。"

### 9.2 扩展回答（3分钟）

"从底层实现看，HashSet 将元素作为 HashMap 的 key，PRESENT 作为 value，通过 hashCode 定位桶，equals 比较元素，实现去重。LinkedHashSet 继承 HashSet，但使用 LinkedHashMap，在 HashMap 基础上维护双向链表，保持插入顺序。TreeSet 基于 TreeMap，TreeMap 使用红黑树实现，支持自然排序和自定义排序，通过 compareTo 或 compare 方法判断元素是否重复。线程安全方面，CopyOnWriteArraySet 基于 CopyOnWriteArrayList，适合读多写少；ConcurrentSkipListSet 基于跳表，支持高并发和排序。选择上，只需要去重用 HashSet，需要顺序用 LinkedHashSet，需要排序用 TreeSet。"

### 9.3 加分项

- 能说出 HashSet 基于 HashMap 的实现原理
- 了解 LinkedHashSet 如何保持插入顺序
- 知道 TreeSet 基于红黑树的实现
- 理解 HashSet 的去重机制（hashCode + equals）
- 能说出不同 Set 实现类的适用场景