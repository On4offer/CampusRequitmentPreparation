# HashMap 在高并发下会发生什么问题？

## 一、核心问题概述

### 1.1 HashMap 线程不安全的原因

**HashMap 不是线程安全的**，在高并发环境下会出现多种问题：

1. **数据丢失/覆盖**
2. **扩容死循环**（JDK 1.7特有）
3. **元素丢失**
4. **读取脏数据**
5. **ConcurrentModificationException**

---

## 二、问题1：数据丢失/覆盖

### 2.1 问题描述

**场景**：多个线程同时执行put操作时，可能互相覆盖，导致数据丢失。

### 2.2 问题原因

**源码分析**：
```java
// HashMap 的 put 方法（JDK 1.8）
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}

final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    if ((p = tab[i = (n - 1) & hash]) == null)
        // ❌ 问题：多线程同时执行到这里，可能都判断为null
        tab[i] = new Node<>(hash, key, value, null);  // 覆盖
    else {
        // 处理冲突
    }
    // ...
}
```

**并发场景**：
```
线程A：检查 tab[i] == null  → true
线程B：检查 tab[i] == null  → true（A还没插入）
线程A：tab[i] = new Node(...)  → 插入节点A
线程B：tab[i] = new Node(...)  → 覆盖节点A ❌
结果：节点A丢失
```

### 2.3 代码示例

```java
// 演示数据覆盖问题
public class HashMapConcurrencyTest {
    public static void main(String[] args) throws InterruptedException {
        Map<Integer, String> map = new HashMap<>();
        
        // 10个线程同时put
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(10);
        
        for (int i = 0; i < 10; i++) {
            final int threadId = i;
            executor.submit(() -> {
                for (int j = 0; j < 1000; j++) {
                    map.put(threadId * 1000 + j, "value" + j);
                }
                latch.countDown();
            });
        }
        
        latch.await();
        executor.shutdown();
        
        // 期望：10000个元素
        // 实际：可能少于10000（数据丢失）
        System.out.println("实际元素数量: " + map.size());
    }
}
```

**运行结果**：
```
期望：10000个元素
实际：可能只有8000-9000个（数据丢失）
```

---

## 三、问题2：扩容死循环（JDK 1.7特有）

### 3.1 问题描述

**场景**：JDK 1.7中，多线程同时扩容时可能形成**环形链表**，导致get操作死循环，CPU占用100%。

### 3.2 问题原因

**JDK 1.7 扩容源码**：
```java
// JDK 1.7 扩容方法
void transfer(Entry[] newTable) {
    Entry[] src = table;
    int newCapacity = newTable.length;
    for (int j = 0; j < src.length; j++) {
        Entry<K,V> e = src[j];
        if (e != null) {
            src[j] = null;
            do {
                Entry<K,V> next = e.next;  // 保存next引用
                int i = indexFor(e.hash, newCapacity);
                e.next = newTable[i];  // 头插法
                newTable[i] = e;
                e = next;
            } while (e != null);
        }
    }
}
```

**死循环形成过程**：

**初始状态**：
```
旧数组索引3：A -> B -> null
```

**线程A执行到一半**：
```
线程A：
1. e = A, next = B
2. newTable[3] = A
3. A.next = null
4. 此时被挂起

新数组状态：A -> null
```

**线程B完成扩容**：
```
线程B：
1. e = A, next = B
2. newTable[3] = A, A.next = null
3. e = B, next = null
4. newTable[3] = B, B.next = A

新数组状态：B -> A -> null
```

**线程A继续执行**：
```
线程A：
1. e = B（之前保存的next）
2. newTable[3] = B, B.next = A
3. e = A（B.next）
4. newTable[3] = A, A.next = B（之前B.next = A）

结果：A -> B -> A（环形链表）❌
```

### 3.3 死循环演示

```java
// 演示死循环问题（JDK 1.7）
public class HashMapDeadLoopTest {
    public static void main(String[] args) {
        final Map<Integer, String> map = new HashMap<>(2);
        map.put(1, "A");
        
        // 线程1：扩容
        new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                map.put(i, "value" + i);
            }
        }).start();
        
        // 线程2：扩容
        new Thread(() -> {
            for (int i = 1000; i < 2000; i++) {
                map.put(i, "value" + i);
            }
        }).start();
        
        // 线程3：读取（可能死循环）
        new Thread(() -> {
            while (true) {
                map.get(1);  // 可能进入环形链表，死循环
            }
        }).start();
    }
}
```

**现象**：
- CPU占用100%
- 程序无响应
- 需要强制终止

### 3.4 JDK 1.8 的改进

**JDK 1.8 改为尾插法**：
```java
// JDK 1.8 扩容方法（尾插法）
do {
    next = e.next;
    if ((e.hash & bit) == 0) {
        if (loTail == null)
            loHead = e;
        else
            loTail.next = e;  // 尾插法
        loTail = e;
    }
    // ...
} while ((e = next) != null);
```

**改进效果**：
- ✅ **解决了死循环问题**：尾插法不会形成环形链表
- ❌ **但仍存在数据丢失**：没有加锁，仍非线程安全

---

## 四、问题3：元素丢失

### 4.1 问题描述

**场景**：扩容迁移过程中，多个线程同时操作可能导致节点丢失。

### 4.2 问题原因

**并发场景**：
```
线程A：正在迁移节点1
线程B：同时迁移节点2（覆盖节点1）
结果：节点1丢失
```

**代码示例**：
```java
// 演示元素丢失问题
public class HashMapDataLossTest {
    public static void main(String[] args) throws InterruptedException {
        Map<Integer, Integer> map = new HashMap<>();
        
        // 多个线程同时put，触发扩容
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(100);
        
        for (int i = 0; i < 100; i++) {
            final int key = i;
            executor.submit(() -> {
                map.put(key, key);
                latch.countDown();
            });
        }
        
        latch.await();
        executor.shutdown();
        
        // 检查是否有元素丢失
        for (int i = 0; i < 100; i++) {
            if (map.get(i) == null) {
                System.out.println("元素丢失: " + i);
            }
        }
    }
}
```

---

## 五、问题4：读取脏数据

### 5.1 问题描述

**场景**：一个线程在读取，另一个线程在修改，可能读取到不一致的数据。

### 5.2 问题原因

**并发场景**：
```
线程A：读取 key1 的值
线程B：同时修改 key1 的值
结果：线程A可能读取到旧值或中间状态
```

**代码示例**：
```java
// 演示脏数据问题
public class HashMapDirtyReadTest {
    public static void main(String[] args) {
        Map<String, Integer> map = new HashMap<>();
        map.put("count", 0);
        
        // 线程1：读取
        new Thread(() -> {
            while (true) {
                Integer count = map.get("count");
                System.out.println("读取到: " + count);
                // 可能读取到不一致的值
            }
        }).start();
        
        // 线程2：修改
        new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                map.put("count", i);
            }
        }).start();
    }
}
```

---

## 六、问题5：ConcurrentModificationException

### 6.1 问题描述

**场景**：一个线程在遍历，另一个线程在修改，会抛出`ConcurrentModificationException`。

### 6.2 问题原因

**fail-fast机制**：HashMap的迭代器使用fail-fast机制，检测到modCount变化就抛异常。

**代码示例**：
```java
// 演示ConcurrentModificationException
public class HashMapCMETest {
    public static void main(String[] args) {
        Map<Integer, String> map = new HashMap<>();
        map.put(1, "A");
        map.put(2, "B");
        map.put(3, "C");
        
        // 线程1：遍历
        new Thread(() -> {
            for (Map.Entry<Integer, String> entry : map.entrySet()) {
                System.out.println(entry);
                try { Thread.sleep(100); } catch (Exception e) {}
            }
        }).start();
        
        // 线程2：修改
        new Thread(() -> {
            try { Thread.sleep(50); } catch (Exception e) {}
            map.put(4, "D");  // ❌ 抛出ConcurrentModificationException
        }).start();
    }
}
```

---

## 七、JDK 1.7 vs JDK 1.8 对比

### 7.1 问题对比表

| 问题 | JDK 1.7 | JDK 1.8 |
|------|---------|---------|
| **数据丢失/覆盖** | ✅ 存在 | ✅ 存在 |
| **扩容死循环** | ❌ 存在（严重） | ✅ 已解决 |
| **元素丢失** | ✅ 存在 | ✅ 存在 |
| **读取脏数据** | ✅ 存在 | ✅ 存在 |
| **ConcurrentModificationException** | ✅ 存在 | ✅ 存在 |

### 7.2 JDK 1.8 的改进

**改进点**：
1. ✅ **解决死循环**：改为尾插法，避免环形链表
2. ✅ **优化扩容**：不需要重新hash，性能提升
3. ❌ **仍非线程安全**：没有加锁，仍存在数据丢失等问题

---

## 八、解决方案

### 8.1 方案1：使用ConcurrentHashMap（推荐）

```java
// 使用ConcurrentHashMap
Map<String, String> map = new ConcurrentHashMap<>();
// 线程安全，性能高
```

**优势**：
- ✅ **线程安全**：保证并发安全
- ✅ **高性能**：锁粒度细，支持高并发
- ✅ **无死循环**：JDK 1.8实现避免了死循环

### 8.2 方案2：使用Collections.synchronizedMap()

```java
// 使用synchronizedMap
Map<String, String> map = Collections.synchronizedMap(new HashMap<>());
// 线程安全，但性能较低
```

**特点**：
- ✅ **线程安全**：所有操作都加锁
- ❌ **性能低**：锁整个表，并发度低
- ❌ **不推荐**：性能不如ConcurrentHashMap

### 8.3 方案3：使用Hashtable（不推荐）

```java
// 使用Hashtable
Map<String, String> map = new Hashtable<>();
// 线程安全，但性能很差
```

**特点**：
- ✅ **线程安全**：所有方法都加synchronized
- ❌ **性能很差**：锁整个表，并发度极低
- ❌ **已过时**：不推荐使用

### 8.4 方案对比

| 方案 | 线程安全 | 性能 | 推荐度 |
|------|---------|------|--------|
| **ConcurrentHashMap** | ✅ | 高 | ⭐⭐⭐⭐⭐ |
| **synchronizedMap** | ✅ | 中 | ⭐⭐⭐ |
| **Hashtable** | ✅ | 低 | ⭐ |
| **HashMap** | ❌ | 高 | ❌（并发场景） |

---

## 九、最佳实践

### 9.1 单线程场景

```java
// 单线程场景：使用HashMap
Map<String, String> map = new HashMap<>();
// 性能最高，无锁开销
```

### 9.2 多线程读多写少

```java
// 读多写少：使用ConcurrentHashMap
Map<String, String> map = new ConcurrentHashMap<>();
// 读操作无锁，性能好
```

### 9.3 多线程高并发

```java
// 高并发场景：使用ConcurrentHashMap
Map<String, String> map = new ConcurrentHashMap<>();
// 锁粒度细，支持高并发
```

### 9.4 需要强一致性

```java
// 需要强一致性：使用synchronizedMap或加锁
Map<String, String> map = Collections.synchronizedMap(new HashMap<>());
// 或使用ConcurrentHashMap + 外部同步
```

---

## 十、常见面试追问

### Q1：为什么JDK 1.7会出现死循环，而JDK 1.8不会？

**答**：
- **JDK 1.7**：使用**头插法**，多线程扩容时可能形成环形链表
- **JDK 1.8**：使用**尾插法**，避免了环形链表的形成
- **但JDK 1.8仍非线程安全**：仍存在数据丢失等问题

### Q2：HashMap在什么情况下会出现数据丢失？

**答**：
1. **多线程put**：同时put到同一位置，可能互相覆盖
2. **扩容时**：多线程同时扩容，节点可能丢失
3. **删除时**：多线程同时删除，可能删除失败

### Q3：如何避免HashMap的并发问题？

**答**：
1. **使用ConcurrentHashMap**（推荐）：线程安全，性能高
2. **使用synchronizedMap**：线程安全，但性能较低
3. **外部加锁**：使用synchronized或ReentrantLock
4. **单线程使用**：如果确定是单线程，使用HashMap即可

### Q4：ConcurrentHashMap为什么不会出现死循环？

**答**：
- **JDK 1.8**：使用CAS + synchronized，锁粒度细
- **多线程协作扩容**：多个线程协作迁移，避免环形链表
- **ForwardingNode**：标记已迁移的节点，避免重复迁移

---

## 十一、面试回答模板

### 11.1 核心回答（1分钟）

"HashMap在高并发下会出现多个问题：数据丢失和覆盖，多个线程同时put可能互相覆盖；JDK 1.7中扩容时可能形成环形链表导致死循环，CPU占用100%；元素可能在扩容迁移过程中丢失；可能读取到脏数据；遍历时修改会抛出ConcurrentModificationException。JDK 1.8解决了死循环问题，但仍非线程安全。解决方案是使用ConcurrentHashMap，它通过CAS和synchronized保证线程安全，锁粒度细，性能高。"

### 11.2 扩展回答（3分钟）

"从具体问题看，数据丢失是因为put操作不是原子的，多线程同时判断桶为空时都会插入，导致覆盖。JDK 1.7的死循环是因为头插法在多线程扩容时可能形成环形链表，JDK 1.8改为尾插法解决了这个问题。元素丢失发生在扩容迁移过程中，多线程同时操作可能导致节点丢失。读取脏数据是因为没有同步机制，可能读到中间状态。解决方案中，ConcurrentHashMap是最佳选择，它使用CAS实现无锁操作，synchronized锁定节点，锁粒度细，性能好。"

### 11.3 加分项

- 能说出JDK 1.7死循环的具体形成过程
- 了解JDK 1.8的改进和仍存在的问题
- 知道各种解决方案的优缺点
- 理解ConcurrentHashMap为什么能避免这些问题
- 能说出不同场景下的最佳实践
