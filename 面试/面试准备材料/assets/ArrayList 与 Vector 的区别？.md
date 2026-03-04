# ArrayList 与 Vector 的区别？为什么 Vector 已经被淘汰？

## 一、核心概念

### 1.1 ArrayList

**ArrayList**：
- **包路径**：`java.util.ArrayList`
- **定义**：基于**动态数组**实现的 List，支持随机访问
- **线程安全**：❌ **线程不安全**
- **性能**：✅ **性能高**（无锁开销）
- **出现版本**：JDK 1.2

### 1.2 Vector

**Vector**：
- **包路径**：`java.util.Vector`
- **定义**：基于**动态数组**实现的 List，支持随机访问
- **线程安全**：✅ **线程安全**（方法级 synchronized）
- **性能**：❌ **性能差**（锁开销大）
- **出现版本**：JDK 1.0（遗留类）

### 1.3 核心区别

| 对比项 | ArrayList | Vector |
|--------|-----------|--------|
| **线程安全** | ❌ 不安全 | ✅ 安全 |
| **性能** | ✅ 高 | ❌ 低 |
| **锁机制** | 无锁 | synchronized（方法级） |
| **扩容倍数** | 1.5 倍 | 2 倍 |
| **出现版本** | JDK 1.2 | JDK 1.0 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ❌ 已淘汰 |

---

## 二、底层实现对比

### 2.1 数据结构

**两者底层都是动态数组**：

```java
// ArrayList 底层
public class ArrayList<E> {
    transient Object[] elementData;  // 底层数组
    private int size;                 // 元素个数
}

// Vector 底层
public class Vector<E> {
    protected Object[] elementData;  // 底层数组
    protected int elementCount;       // 元素个数
    protected int capacityIncrement;  // 扩容增量
}
```

**相同点**：
- ✅ 都使用**数组**存储元素
- ✅ 都支持**随机访问**（通过索引）
- ✅ 都支持**动态扩容**

### 2.2 扩容机制对比

#### ArrayList 扩容（JDK 1.8）

```java
// ArrayList 扩容方法
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + (oldCapacity >> 1);  // 1.5 倍
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

**扩容规则**：
- **默认容量**：10
- **扩容倍数**：**1.5 倍**（`oldCapacity + oldCapacity >> 1`）
- **扩容时机**：元素个数超过当前容量时

#### Vector 扩容

```java
// Vector 扩容方法
private void grow(int minCapacity) {
    int oldCapacity = elementData.length;
    int newCapacity = oldCapacity + ((capacityIncrement > 0) ?
                                     capacityIncrement : oldCapacity);  // 2 倍
    if (newCapacity - minCapacity < 0)
        newCapacity = minCapacity;
    elementData = Arrays.copyOf(elementData, newCapacity);
}
```

**扩容规则**：
- **默认容量**：10
- **扩容倍数**：**2 倍**（如果 capacityIncrement <= 0）
- **扩容时机**：元素个数超过当前容量时

**对比**：
| 对比项 | ArrayList | Vector |
|--------|-----------|--------|
| **默认容量** | 10 | 10 |
| **扩容倍数** | 1.5 倍 | 2 倍 |
| **扩容策略** | 更节省内存 | 扩容更快但浪费内存 |

---

## 三、线程安全对比

### 3.1 ArrayList - 线程不安全

**ArrayList 的方法没有加锁**：

```java
// ArrayList 的 add 方法（无锁）
public boolean add(E e) {
    modCount++;
    add(e, elementData, size);
    return true;
}

private void add(E e, Object[] elementData, int s) {
    if (s == elementData.length)
        elementData = grow();
    elementData[s] = e;
    size = s + 1;
}
```

**问题**：
- ❌ **多线程不安全**：多线程同时 add 可能导致数据丢失
- ❌ **并发修改异常**：遍历时修改会抛出 `ConcurrentModificationException`

**示例**：
```java
// 多线程不安全示例
List<Integer> list = new ArrayList<>();
ExecutorService executor = Executors.newFixedThreadPool(10);

for (int i = 0; i < 1000; i++) {
    executor.submit(() -> list.add(1));
}

// 结果：可能少于 1000（数据丢失）
System.out.println(list.size());  // 可能输出 800-900
```

### 3.2 Vector - 线程安全

**Vector 的方法都加 synchronized**：

```java
// Vector 的 add 方法（加锁）
public synchronized boolean add(E e) {
    modCount++;
    add(e, elementData, elementCount);
    return true;
}

private void add(E e, Object[] elementData, int s) {
    if (s == elementData.length)
        elementData = grow();
    elementData[s] = e;
    elementCount = s + 1;
}
```

**特点**：
- ✅ **线程安全**：所有方法都加 `synchronized`
- ❌ **性能差**：即使是读操作也要加锁
- ❌ **锁粒度粗**：锁整个方法，并发度低

**示例**：
```java
// Vector 线程安全示例
Vector<Integer> vector = new Vector<>();
ExecutorService executor = Executors.newFixedThreadPool(10);

for (int i = 0; i < 1000; i++) {
    executor.submit(() -> vector.add(1));
}

// 结果：一定是 1000（线程安全）
System.out.println(vector.size());  // 1000
```

### 3.3 性能对比

**测试代码**：
```java
public class PerformanceTest {
    public static void main(String[] args) {
        int size = 1000000;
        int threadCount = 10;
        
        // ArrayList 测试
        List<Integer> arrayList = new ArrayList<>();
        long start = System.currentTimeMillis();
        ExecutorService executor1 = Executors.newFixedThreadPool(threadCount);
        for (int i = 0; i < size; i++) {
            executor1.submit(() -> arrayList.add(1));
        }
        executor1.shutdown();
        while (!executor1.isTerminated()) {}
        System.out.println("ArrayList: " + (System.currentTimeMillis() - start) + "ms");
        
        // Vector 测试
        Vector<Integer> vector = new Vector<>();
        start = System.currentTimeMillis();
        ExecutorService executor2 = Executors.newFixedThreadPool(threadCount);
        for (int i = 0; i < size; i++) {
            executor2.submit(() -> vector.add(1));
        }
        executor2.shutdown();
        while (!executor2.isTerminated()) {}
        System.out.println("Vector: " + (System.currentTimeMillis() - start) + "ms");
    }
}
```

**测试结果**（仅供参考）：
- **ArrayList**：性能高，但可能数据丢失
- **Vector**：性能低，但线程安全

---

## 四、为什么 Vector 已经被淘汰？

### 4.1 原因1：同步方式粗糙

**问题**：
- **方法级锁**：所有方法都加 `synchronized`，锁粒度粗
- **读操作也加锁**：即使是读操作也要加锁，性能差
- **并发度低**：多线程竞争激烈，性能下降

**示例**：
```java
// Vector 的 get 方法（读操作也加锁）
public synchronized E get(int index) {
    if (index >= elementCount)
        throw new ArrayIndexOutOfBoundsException(index);
    return elementData(index);
}
```

**对比**：
- **Vector**：读操作加锁，性能差
- **CopyOnWriteArrayList**：读操作无锁，性能高

### 4.2 原因2：有更好的替代方案

**JDK 1.2 引入 ArrayList**：
- ✅ **单线程场景**：使用 ArrayList，性能高
- ✅ **多线程场景**：使用 JUC 并发集合

**JUC 并发集合**：
- **CopyOnWriteArrayList**：读多写少场景
- **ConcurrentHashMap**：高并发 Map
- **ConcurrentLinkedQueue**：高并发队列

**对比表**：
| 场景 | 推荐方案 | 不推荐 |
|------|---------|--------|
| **单线程** | ArrayList | Vector |
| **多线程读多写少** | CopyOnWriteArrayList | Vector |
| **多线程高并发** | ConcurrentHashMap | synchronizedMap |

### 4.3 原因3：历史遗留问题

**Vector 的历史**：
- **JDK 1.0**：Vector 出现，那时并发方案不成熟
- **JDK 1.2**：引入 ArrayList，提供更好的单线程方案
- **JDK 1.5**：引入 JUC 包，提供更好的并发方案
- **现在**：Vector 已过时，只保留用于兼容性

**现状**：
- ❌ **不推荐使用**：实际开发中几乎不用
- ⚠️ **保留原因**：为了兼容老版本 API
- ✅ **替代方案**：ArrayList + JUC 并发集合

---

## 五、实际应用场景

### 5.1 单线程场景 - 使用 ArrayList

```java
// 单线程场景：使用 ArrayList
List<Product> products = new ArrayList<>();
products.add(new Product("商品1", 100));
products.add(new Product("商品2", 200));

// 性能高，无锁开销
for (Product product : products) {
    System.out.println(product);
}
```

### 5.2 多线程读多写少 - 使用 CopyOnWriteArrayList

```java
// 多线程读多写少：使用 CopyOnWriteArrayList
List<User> onlineUsers = new CopyOnWriteArrayList<>();

// 用户上线（写操作少）
public void userLogin(User user) {
    onlineUsers.add(user);
}

// 获取在线用户（读操作多，无锁）
public List<User> getOnlineUsers() {
    return onlineUsers;  // 读操作无锁，性能高
}
```

### 5.3 多线程高并发 - 使用 ConcurrentHashMap

```java
// 多线程高并发：使用 ConcurrentHashMap
Map<String, String> cache = new ConcurrentHashMap<>();

// 多线程安全，性能高
public String get(String key) {
    return cache.get(key);
}

public void put(String key, String value) {
    cache.put(key, value);
}
```

### 5.4 不推荐使用 Vector

```java
// ❌ 不推荐：使用 Vector
Vector<String> vector = new Vector<>();
vector.add("元素1");
vector.add("元素2");

// 问题：
// 1. 性能差（所有操作加锁）
// 2. 有更好的替代方案（CopyOnWriteArrayList）
```

---

## 六、详细对比表

### 6.1 功能对比

| 对比项 | ArrayList | Vector |
|--------|-----------|--------|
| **线程安全** | ❌ | ✅ |
| **性能** | ✅ 高 | ❌ 低 |
| **锁机制** | 无锁 | synchronized（方法级） |
| **扩容倍数** | 1.5 倍 | 2 倍 |
| **默认容量** | 10 | 10 |
| **出现版本** | JDK 1.2 | JDK 1.0 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ❌ 已淘汰 |

### 6.2 方法对比

| 方法 | ArrayList | Vector |
|------|-----------|--------|
| `add(E e)` | 无锁 | `synchronized` |
| `get(int index)` | 无锁 | `synchronized` |
| `remove(int index)` | 无锁 | `synchronized` |
| `size()` | 无锁 | `synchronized` |

### 6.3 性能对比

| 操作 | ArrayList | Vector | 说明 |
|------|-----------|--------|------|
| **单线程 add** | 快 | 慢 | Vector 有锁开销 |
| **多线程 add** | 快但不安全 | 慢但安全 | ArrayList 可能数据丢失 |
| **单线程 get** | 快 | 慢 | Vector 读操作也加锁 |
| **多线程 get** | 快但不安全 | 慢但安全 | ArrayList 可能读到脏数据 |

---

## 七、替代方案

### 7.1 ArrayList vs Vector vs CopyOnWriteArrayList

| 对比项 | ArrayList | Vector | CopyOnWriteArrayList |
|--------|-----------|--------|---------------------|
| **线程安全** | ❌ | ✅ | ✅ |
| **性能（读）** | ✅ 高 | ❌ 低 | ✅ 高（无锁） |
| **性能（写）** | ✅ 高 | ❌ 低 | ❌ 低（需要复制） |
| **适用场景** | 单线程 | ❌ 已淘汰 | 读多写少 |
| **推荐度** | ⭐⭐⭐⭐⭐ | ❌ | ⭐⭐⭐⭐ |

### 7.2 选择建议

**单线程场景**：
```java
// ✅ 推荐：ArrayList
List<String> list = new ArrayList<>();
```

**多线程读多写少**：
```java
// ✅ 推荐：CopyOnWriteArrayList
List<String> list = new CopyOnWriteArrayList<>();
```

**多线程高并发**：
```java
// ✅ 推荐：ConcurrentHashMap
Map<String, String> map = new ConcurrentHashMap<>();
```

**不推荐**：
```java
// ❌ 不推荐：Vector
Vector<String> vector = new Vector<>();
```

---

## 八、常见面试追问

### Q1：Vector 为什么线程安全但性能差？

**答**：
1. **方法级锁**：所有方法都加 `synchronized`，锁粒度粗
2. **读操作也加锁**：即使是读操作也要加锁，性能差
3. **并发度低**：多线程竞争激烈，性能下降
4. **锁开销大**：频繁加锁解锁，CPU 开销大

**对比**：
- **Vector**：读操作加锁，性能差
- **CopyOnWriteArrayList**：读操作无锁，性能高

### Q2：Vector 和 CopyOnWriteArrayList 的区别？

**答**：

| 对比项 | Vector | CopyOnWriteArrayList |
|--------|--------|---------------------|
| **锁机制** | synchronized（方法级） | ReentrantLock（写操作） |
| **读操作** | 加锁 | 无锁 |
| **写操作** | 加锁 | 加锁 + 复制 |
| **性能（读）** | 低 | 高 |
| **性能（写）** | 低 | 低（需要复制） |
| **适用场景** | ❌ 已淘汰 | 读多写少 |

### Q3：现在项目中什么时候还会用 Vector？

**答**：
- ❌ **基本不会用**：实际开发中几乎不用
- ⚠️ **遗留代码**：只存在于老项目中
- ⚠️ **兼容性**：需要兼容老版本 API 的场景
- ✅ **推荐替代**：使用 ArrayList + JUC 并发集合

### Q4：ArrayList 和 Vector 的扩容机制有什么区别？

**答**：

| 对比项 | ArrayList | Vector |
|--------|-----------|--------|
| **扩容倍数** | 1.5 倍 | 2 倍 |
| **扩容公式** | `oldCapacity + (oldCapacity >> 1)` | `oldCapacity * 2` |
| **内存效率** | 更节省 | 更浪费 |
| **扩容次数** | 更多 | 更少 |

**示例**：
```java
// ArrayList：10 → 15 → 22 → 33 → 49 → ...
// Vector：10 → 20 → 40 → 80 → 160 → ...
```

### Q5：如何保证 ArrayList 的线程安全？

**答**：

**方式1：外部同步**（不推荐）
```java
List<String> list = new ArrayList<>();
synchronized (list) {
    list.add("元素");
}
```

**方式2：Collections.synchronizedList()**（不推荐）
```java
List<String> list = Collections.synchronizedList(new ArrayList<>());
```

**方式3：使用并发集合**（推荐）
```java
// 读多写少
List<String> list = new CopyOnWriteArrayList<>();

// 高并发
Map<String, String> map = new ConcurrentHashMap<>();
```

---

## 九、面试回答模板

### 9.1 核心回答（1分钟）

"ArrayList 和 Vector 底层都是动态数组，但 ArrayList 线程不安全，性能高；Vector 线程安全但性能差，因为所有方法都加 synchronized 锁，锁粒度粗，即使是读操作也要加锁。扩容机制上，ArrayList 扩容 1.5 倍，Vector 扩容 2 倍。Vector 是 JDK 1.0 的遗留类，随着 JDK 1.2 引入 ArrayList 和 JDK 1.5 引入 JUC 并发集合，Vector 已被淘汰。现在单线程用 ArrayList，多线程用 CopyOnWriteArrayList 或 ConcurrentHashMap，不再使用 Vector。"

### 9.2 扩展回答（3分钟）

"从实现细节看，ArrayList 和 Vector 都使用数组存储，支持随机访问。区别在于线程安全：ArrayList 无锁，性能高但线程不安全；Vector 所有方法加 synchronized，线程安全但性能差。扩容上，ArrayList 按 1.5 倍扩容，更节省内存；Vector 按 2 倍扩容，扩容更快但浪费内存。Vector 被淘汰的原因：一是同步方式粗糙，方法级锁导致性能差；二是有更好的替代方案，单线程用 ArrayList，多线程用 CopyOnWriteArrayList；三是历史遗留，JDK 1.0 的设计已过时。实际开发中，几乎不再使用 Vector，推荐使用 ArrayList + JUC 并发集合。"

### 9.3 加分项

- 能说出 ArrayList 和 Vector 的底层实现和扩容机制
- 了解 Vector 被淘汰的原因
- 知道如何选择合适的集合类
- 理解 synchronized 锁的性能影响
- 能说出 Vector 和 CopyOnWriteArrayList 的区别