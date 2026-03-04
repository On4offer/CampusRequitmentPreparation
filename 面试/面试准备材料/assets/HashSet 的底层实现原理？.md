# HashSet 的底层实现原理是什么？为什么不允许重复元素？

## 一、HashSet 概述

### 1.1 定义

**HashSet**：
- **包路径**：`java.util.HashSet`
- **定义**：基于 **HashMap** 实现的 Set，不允许重复元素
- **特点**：无序、不重复、允许 null 值
- **继承关系**：继承自 `AbstractSet`，实现 `Set` 接口

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **底层实现** | 基于 HashMap |
| **元素存储** | 元素作为 HashMap 的 key |
| **去重机制** | 利用 HashMap 的 key 唯一性 |
| **有序性** | ❌ 不保证顺序 |
| **线程安全** | ❌ 非线程安全 |
| **性能** | O(1) 平均时间复杂度 |

---

## 二、底层实现原理

### 2.1 源码结构

```java
// HashSet 源码
public class HashSet<E> extends AbstractSet<E> implements Set<E> {
    // 底层 HashMap
    private transient HashMap<E,Object> map;
    
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
    
    // size 方法
    public int size() {
        return map.size();
    }
}
```

**核心原理**：
- ✅ **元素作为 key**：Set 中的元素作为 HashMap 的 key 存储
- ✅ **固定 value**：使用常量 `PRESENT` 作为所有元素的 value
- ✅ **所有操作委托给 HashMap**：add、remove、contains 都调用 HashMap 的方法

### 2.2 存储结构

**HashMap 的存储结构**：
```
HashMap 数组（桶）：
[0] -> null
[1] -> Node(key1, PRESENT) -> Node(key2, PRESENT) -> null
[2] -> null
[3] -> Node(key3, PRESENT) -> null
...
```

**HashSet 的存储**：
- 元素作为 HashMap 的 key
- value 统一使用 `PRESENT` 常量
- 通过 HashMap 的 key 唯一性保证元素不重复

---

## 三、为什么不允许重复元素？

### 3.1 去重机制

**HashSet 的去重依赖于 HashMap 的 key 唯一性**：

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
            e = p;  // 找到相同 key，覆盖 value
        else {
            // 处理哈希冲突（链表或红黑树）
            // ...
        }
        if (e != null) {
            V oldValue = e.value;
            if (!onlyIfAbsent || oldValue == null)
                e.value = value;  // 覆盖 value
            return oldValue;  // 返回旧值（对 HashSet 来说就是添加失败）
        }
    }
    // ...
    return null;  // 返回 null（表示添加成功）
}
```

**去重流程**：
1. **hashCode 定位**：通过 `hashCode()` 计算哈希值，定位到桶
2. **equals 比较**：在桶内使用 `equals()` 比较元素
3. **如果相同**：覆盖 value，返回旧值（HashSet 的 add 返回 false）
4. **如果不同**：插入新节点，返回 null（HashSet 的 add 返回 true）

### 3.2 判断重复的依据

**两个条件**：
1. **hashCode 相同**：元素必须映射到同一个桶
2. **equals 返回 true**：元素内容相同

**重要约定**：
- ✅ **equals 相等，hashCode 必须相等**
- ✅ **hashCode 相等，equals 不一定相等**（哈希冲突）
- ⚠️ **必须同时重写 hashCode() 和 equals()**，使用相同的字段

### 3.3 示例说明

```java
// 示例1：正常去重
Set<String> set = new HashSet<>();
set.add("apple");
set.add("banana");
set.add("apple");  // 重复，不会添加

System.out.println(set.size());  // 2
System.out.println(set);  // [banana, apple]（顺序不确定）

// 示例2：自定义类去重
public class Person {
    private String name;
    private int age;
    
    // 必须重写 hashCode 和 equals
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }
}

Set<Person> personSet = new HashSet<>();
personSet.add(new Person("张三", 20));
personSet.add(new Person("李四", 18));
personSet.add(new Person("张三", 20));  // 重复，不会添加

System.out.println(personSet.size());  // 2
```

---

## 四、添加元素流程

### 4.1 add() 方法详解

```java
// HashSet 的 add 方法
public boolean add(E e) {
    return map.put(e, PRESENT) == null;
}
```

**流程分析**：
1. **调用 HashMap.put()**：将元素作为 key，PRESENT 作为 value
2. **HashMap 处理**：
   - 计算 hashCode，定位桶
   - 如果桶为空，直接插入
   - 如果桶不为空，比较 equals
   - 如果相同，覆盖 value，返回旧值
   - 如果不同，插入新节点，返回 null
3. **HashSet 判断**：
   - 如果返回 null，表示添加成功（返回 true）
   - 如果返回非 null，表示元素已存在（返回 false）

### 4.2 完整流程图

```
add(element)
   │
   ▼
HashMap.put(element, PRESENT)
   │
   ▼
计算 hashCode：hash = element.hashCode()
   │
   ▼
定位桶：index = (n - 1) & hash
   │
   ▼
桶为空？
   ├─→ 是 → 直接插入 → 返回 null → HashSet.add() 返回 true
   │
   └─→ 否 → 遍历链表/树
         │
         ├─→ hashCode 相同 && equals 相同 → 覆盖 value → 返回旧值 → HashSet.add() 返回 false
         │
         └─→ 都不相同 → 插入新节点 → 返回 null → HashSet.add() 返回 true
```

---

## 五、查找元素流程

### 5.1 contains() 方法详解

```java
// HashSet 的 contains 方法
public boolean contains(Object o) {
    return map.containsKey(o);
}
```

**HashMap.containsKey() 流程**：
```java
public boolean containsKey(Object key) {
    return getNode(hash(key), key) != null;
}

final Node<K,V> getNode(int hash, Object key) {
    Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (first = tab[(n - 1) & hash]) != null) {
        // 先比较第一个节点
        if (first.hash == hash &&
            ((k = first.key) == key || (key != null && key.equals(k))))
            return first;
        // 遍历链表/树
        if ((e = first.next) != null) {
            do {
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    return e;
            } while ((e = e.next) != null);
        }
    }
    return null;
}
```

**查找流程**：
1. **hashCode 定位**：计算 hashCode，定位到桶
2. **equals 比较**：在桶内使用 equals 比较
3. **找到返回 true**：如果找到相同元素，返回 true
4. **未找到返回 false**：如果未找到，返回 false

---

## 六、删除元素流程

### 6.1 remove() 方法详解

```java
// HashSet 的 remove 方法
public boolean remove(Object o) {
    return map.remove(o) == PRESENT;
}
```

**HashMap.remove() 流程**：
```java
public V remove(Object key) {
    Node<K,V> e;
    return (e = removeNode(hash(key), key, null, false, true)) == null ?
        null : e.value;
}
```

**删除流程**：
1. **hashCode 定位**：计算 hashCode，定位到桶
2. **equals 比较**：在桶内使用 equals 比较
3. **找到删除**：如果找到相同元素，删除节点，返回 value（PRESENT）
4. **未找到返回 null**：如果未找到，返回 null

---

## 七、为什么不允许重复？

### 7.1 根本原因

**HashMap 的 key 唯一性**：
- HashMap 的 key 必须是唯一的
- HashSet 将元素作为 HashMap 的 key 存储
- 因此 HashSet 的元素自然唯一

### 7.2 技术实现

**去重机制**：
1. **hashCode 定位**：快速定位到可能的桶
2. **equals 确认**：精确判断是否重复
3. **覆盖策略**：如果重复，覆盖 value（对 HashSet 来说就是添加失败）

### 7.3 设计优势

**优势**：
- ✅ **复用 HashMap**：不需要重新实现哈希表
- ✅ **性能高效**：O(1) 平均时间复杂度
- ✅ **代码简洁**：所有操作委托给 HashMap

---

## 八、常见问题

### 8.1 只重写 equals()，不重写 hashCode() 会怎样？

**问题**：
```java
public class Person {
    private String name;
    private int age;
    
    @Override
    public boolean equals(Object obj) {
        // 重写了 equals
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }
    
    // ❌ 没有重写 hashCode()
}
```

**后果**：
```java
Set<Person> set = new HashSet<>();
Person p1 = new Person("张三", 20);
Person p2 = new Person("张三", 20);

set.add(p1);
set.add(p2);

System.out.println(set.size());  // 2（应该是 1）❌
System.out.println(p1.equals(p2));  // true
System.out.println(p1.hashCode() == p2.hashCode());  // false（默认 hashCode 不同）
```

**原因**：
- equals 相等但 hashCode 不同
- 两个对象映射到不同的桶
- HashSet 认为它们是不同的元素
- 导致重复存储

### 8.2 只重写 hashCode()，不重写 equals() 会怎样？

**问题**：
```java
public class Person {
    private String name;
    private int age;
    
    @Override
    public int hashCode() {
        // 重写了 hashCode
        return Objects.hash(name, age);
    }
    
    // ❌ 没有重写 equals()
}
```

**后果**：
```java
Set<Person> set = new HashSet<>();
Person p1 = new Person("张三", 20);
Person p2 = new Person("张三", 20);

set.add(p1);
set.add(p2);

System.out.println(set.size());  // 2（应该是 1）❌
System.out.println(p1.hashCode() == p2.hashCode());  // true
System.out.println(p1.equals(p2));  // false（默认 equals 比较地址）
```

**原因**：
- hashCode 相同但 equals 不同
- 两个对象映射到同一个桶
- 但在桶内 equals 比较返回 false
- HashSet 认为它们是不同的元素
- 导致重复存储

### 8.3 正确实现

```java
public class Person {
    private String name;
    private int age;
    
    // ✅ 同时重写 hashCode 和 equals
    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }
}

// 正确使用
Set<Person> set = new HashSet<>();
Person p1 = new Person("张三", 20);
Person p2 = new Person("张三", 20);

set.add(p1);
set.add(p2);

System.out.println(set.size());  // 1 ✅
```

---

## 九、初始容量和负载因子

### 9.1 默认参数

**HashSet 的默认参数**（继承自 HashMap）：
- **初始容量**：16
- **负载因子**：0.75
- **扩容阈值**：16 * 0.75 = 12

### 9.2 扩容机制

**扩容时机**：
- 当元素个数超过 `容量 * 负载因子` 时触发扩容
- 扩容为原来的 2 倍

**扩容过程**：
```java
// HashMap 的扩容
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
        // 扩容为 2 倍
        else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                 oldCap >= DEFAULT_INITIAL_CAPACITY)
            newThr = oldThr << 1;  // 阈值也翻倍
    }
    // ...
}
```

**扩容后元素分布**：
- 节点要么留在原位置
- 要么迁移到 `index + oldCap` 位置
- 通过 `(hash & oldCap) == 0` 判断

---

## 十、实际应用场景

### 10.1 场景1：用户点赞记录

```java
// 用户点赞过的商户 ID（去重）
Set<Long> likedShopIds = new HashSet<>();

public void likeShop(Long shopId) {
    likedShopIds.add(shopId);  // 重复点赞不会添加
}

public boolean isLiked(Long shopId) {
    return likedShopIds.contains(shopId);
}
```

### 10.2 场景2：已处理订单号

```java
// 已支付订单号集合（避免重复处理）
Set<String> processedOrderIds = new HashSet<>();

public void processOrder(String orderId) {
    if (processedOrderIds.contains(orderId)) {
        return;  // 已处理，跳过
    }
    // 处理订单
    doProcessOrder(orderId);
    processedOrderIds.add(orderId);
}
```

### 10.3 场景3：去重操作

```java
// 列表去重
List<String> list = Arrays.asList("apple", "banana", "apple", "cherry");
Set<String> set = new HashSet<>(list);
List<String> uniqueList = new ArrayList<>(set);
// 结果：["banana", "apple", "cherry"]（顺序不确定）
```

---

## 十一、常见面试追问

### Q1：HashSet 的初始容量和负载因子是多少？

**答**：
- **初始容量**：16
- **负载因子**：0.75
- **扩容阈值**：12（16 * 0.75）
- **扩容倍数**：2 倍

### Q2：如果只重写 equals()，不重写 hashCode() 会怎样？

**答**：
- ❌ **会导致重复存储**
- **原因**：equals 相等但 hashCode 不同，两个对象映射到不同的桶
- **示例**：两个内容相同的对象会被认为是不同的元素
- **解决**：必须同时重写 hashCode() 和 equals()，使用相同的字段

### Q3：HashSet 如何保证扩容时元素还能正确分布？

**答**：
- **扩容为 2 倍**：新容量 = 旧容量 * 2
- **元素重新分布**：
  - 通过 `(hash & oldCap) == 0` 判断
  - 如果为 0，留在原位置
  - 如果不为 0，迁移到 `index + oldCap` 位置
- **原因**：容量是 2 的幂，扩容后只需要判断 hash 值的一位

### Q4：HashSet 为什么不能保证顺序？

**答**：
- **底层 HashMap**：HashSet 基于 HashMap 实现
- **哈希定位**：元素存储位置由 `hashCode()` 决定
- **哈希冲突**：不同元素可能映射到同一桶，顺序不确定
- **扩容影响**：扩容时元素重新分布，顺序改变

**解决方案**：
- **保持插入顺序**：使用 `LinkedHashSet`
- **保持排序**：使用 `TreeSet`

### Q5：HashSet 是线程安全的吗？

**答**：
- ❌ **非线程安全**：HashSet 不是线程安全的
- **线程安全替代**：
  - `Collections.synchronizedSet(new HashSet<>())`
  - `ConcurrentHashMap.newKeySet()`
  - `CopyOnWriteArraySet`（读多写少场景）

---

## 十二、面试回答模板

### 12.1 核心回答（1分钟）

"HashSet 底层基于 HashMap 实现，元素作为 HashMap 的 key 存储，value 使用固定常量 PRESENT。所有操作都委托给 HashMap，包括 add、remove、contains。HashSet 不允许重复元素，是因为 HashMap 的 key 必须是唯一的。判断重复时，先通过 hashCode 定位到桶，再通过 equals 比较元素内容。如果 hashCode 相同且 equals 返回 true，则判定为重复，不会插入。必须同时重写 hashCode 和 equals，使用相同的字段，否则可能导致逻辑错误。"

### 12.2 扩展回答（3分钟）

"从源码看，HashSet 内部维护一个 HashMap，元素作为 key，PRESENT 作为 value。add 方法调用 HashMap.put，如果返回 null 表示添加成功，返回非 null 表示元素已存在。去重机制依赖 HashMap 的 key 唯一性，通过 hashCode 定位桶，equals 比较内容。如果只重写 equals 不重写 hashCode，会导致 equals 相等但 hashCode 不同，两个对象映射到不同桶，重复存储。如果只重写 hashCode 不重写 equals，会导致 hashCode 相同但 equals 不同，在桶内比较失败，也重复存储。必须同时重写，使用相同字段。HashSet 不保证顺序，因为存储位置由 hashCode 决定。初始容量 16，负载因子 0.75，扩容为 2 倍。"

### 12.3 加分项

- 能说出 HashSet 基于 HashMap 的实现原理
- 了解去重机制（hashCode + equals）
- 知道必须同时重写 hashCode 和 equals
- 理解为什么 HashSet 不保证顺序
- 能说出 HashSet 的初始容量和负载因子