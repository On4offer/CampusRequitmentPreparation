# Collections 工具类常见方法有哪些？线程安全集合如何创建？

## 一、Collections 工具类概述

### 1.1 定义

**Collections 工具类**：
- **包路径**：`java.util.Collections`
- **定义**：Java 集合框架提供的**静态工具类**，提供对集合的常用操作
- **特点**：所有方法都是**静态方法**，可以直接通过类名调用
- **作用**：提供排序、查找、替换、填充、同步等集合操作

### 1.2 核心功能分类

| 功能分类 | 主要方法 | 说明 |
|---------|---------|------|
| **排序操作** | `sort()`、`reverse()`、`shuffle()` | 对集合进行排序、反转、打乱 |
| **查找操作** | `max()`、`min()`、`binarySearch()` | 查找最大/最小元素、二分查找 |
| **替换操作** | `replaceAll()`、`fill()` | 批量替换、填充元素 |
| **复制操作** | `copy()` | 复制集合 |
| **同步包装** | `synchronizedXXX()` | 创建线程安全集合 |
| **不可变集合** | `unmodifiableXXX()` | 创建只读集合 |
| **其他操作** | `frequency()`、`disjoint()` | 统计频率、判断是否不相交 |

---

## 二、排序操作

### 2.1 sort() - 排序

**方法签名**：
```java
// 使用自然排序（需要元素实现 Comparable）
public static <T extends Comparable<? super T>> void sort(List<T> list)

// 使用自定义比较器
public static <T> void sort(List<T> list, Comparator<? super T> c)
```

**使用示例**：
```java
// 示例1：自然排序（String 实现了 Comparable）
List<String> list = new ArrayList<>();
list.add("张三");
list.add("李四");
list.add("王五");
Collections.sort(list);  // 按字典序排序
// 结果：[李四, 王五, 张三]

// 示例2：自定义排序（按长度排序）
Collections.sort(list, (s1, s2) -> s1.length() - s2.length());

// 示例3：对象排序
List<Student> students = new ArrayList<>();
students.add(new Student("张三", 20));
students.add(new Student("李四", 18));
Collections.sort(students, Comparator.comparing(Student::getAge));
```

### 2.2 reverse() - 反转

**方法签名**：
```java
public static void reverse(List<?> list)
```

**使用示例**：
```java
List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
Collections.reverse(list);  // 反转顺序
// 结果：[5, 4, 3, 2, 1]
```

### 2.3 shuffle() - 随机打乱

**方法签名**：
```java
// 使用默认随机源
public static void shuffle(List<?> list)

// 使用指定随机源
public static void shuffle(List<?> list, Random rnd)
```

**使用示例**：
```java
List<Integer> list = new ArrayList<>(Arrays.asList(1, 2, 3, 4, 5));
Collections.shuffle(list);  // 随机打乱
// 结果：随机顺序，如 [3, 1, 5, 2, 4]

// 使用指定随机源（可重现）
Random random = new Random(123);
Collections.shuffle(list, random);
```

---

## 三、查找操作

### 3.1 max() / min() - 查找最大/最小元素

**方法签名**：
```java
// 使用自然排序
public static <T extends Object & Comparable<? super T>> T max(Collection<? extends T> coll)
public static <T extends Object & Comparable<? super T>> T min(Collection<? extends T> coll)

// 使用自定义比较器
public static <T> T max(Collection<? extends T> coll, Comparator<? super T> comp)
public static <T> T min(Collection<? extends T> coll, Comparator<? super T> comp)
```

**使用示例**：
```java
// 示例1：自然排序
List<Integer> numbers = Arrays.asList(3, 1, 4, 1, 5);
Integer max = Collections.max(numbers);  // 5
Integer min = Collections.min(numbers);  // 1

// 示例2：自定义比较器
List<String> words = Arrays.asList("apple", "banana", "cherry");
String longest = Collections.max(words, Comparator.comparing(String::length));  // "banana"
String shortest = Collections.min(words, Comparator.comparing(String::length));  // "apple"
```

### 3.2 binarySearch() - 二分查找

**方法签名**：
```java
// 使用自然排序（前提：列表必须有序）
public static <T> int binarySearch(List<? extends Comparable<? super T>> list, T key)

// 使用自定义比较器
public static <T> int binarySearch(List<? extends T> list, T key, Comparator<? super T> c)
```

**返回值**：
- **找到**：返回元素索引（>= 0）
- **未找到**：返回 `-(插入点) - 1`（< 0）

**使用示例**：
```java
// 示例1：有序列表查找
List<Integer> list = new ArrayList<>(Arrays.asList(1, 3, 5, 7, 9));
int index = Collections.binarySearch(list, 5);  // 2（找到）
int notFound = Collections.binarySearch(list, 4);  // -3（未找到，插入点为2）

// 示例2：自定义比较器
List<Student> students = new ArrayList<>();
students.add(new Student("张三", 18));
students.add(new Student("李四", 20));
students.add(new Student("王五", 22));
Collections.sort(students, Comparator.comparing(Student::getAge));
int idx = Collections.binarySearch(students, new Student("", 20), 
    Comparator.comparing(Student::getAge));  // 1
```

**注意事项**：
- ⚠️ **列表必须有序**：使用前必须先排序，否则结果不确定
- ⚠️ **时间复杂度**：O(log n)，比线性查找 O(n) 快

---

## 四、替换和填充操作

### 4.1 replaceAll() - 批量替换

**方法签名**：
```java
public static <T> boolean replaceAll(List<T> list, T oldVal, T newVal)
```

**使用示例**：
```java
List<String> list = new ArrayList<>(Arrays.asList("apple", "banana", "apple", "cherry"));
boolean replaced = Collections.replaceAll(list, "apple", "orange");
// 结果：["orange", "banana", "orange", "cherry"]
// 返回值：true（至少替换了一个）
```

### 4.2 fill() - 填充

**方法签名**：
```java
public static <T> void fill(List<? super T> list, T obj)
```

**使用示例**：
```java
List<String> list = new ArrayList<>(Arrays.asList("a", "b", "c", "d"));
Collections.fill(list, "x");
// 结果：["x", "x", "x", "x"]
```

**注意事项**：
- ⚠️ **替换所有元素**：会将列表中所有元素替换为指定值
- ⚠️ **列表大小不变**：只替换现有元素，不改变列表大小

---

## 五、复制操作

### 5.1 copy() - 复制集合

**方法签名**：
```java
public static <T> void copy(List<? super T> dest, List<? extends T> src)
```

**使用示例**：
```java
List<String> src = Arrays.asList("a", "b", "c");
List<String> dest = new ArrayList<>(Arrays.asList("x", "x", "x", "x", "x"));
Collections.copy(dest, src);
// 结果：dest = ["a", "b", "c", "x", "x"]
```

**注意事项**：
- ⚠️ **目标列表大小**：目标列表大小必须 >= 源列表大小
- ⚠️ **索引复制**：从索引 0 开始复制，覆盖目标列表的前 N 个元素
- ⚠️ **异常**：如果目标列表太小，会抛出 `IndexOutOfBoundsException`

---

## 六、同步包装（线程安全集合）

### 6.1 synchronizedList() - 线程安全 List

**方法签名**：
```java
public static <T> List<T> synchronizedList(List<T> list)
```

**实现原理**：
- 返回一个**同步包装器**，所有方法都加 `synchronized` 锁
- 锁的是**整个集合对象**，锁粒度粗

**使用示例**：
```java
// 创建线程安全的 List
List<String> list = new ArrayList<>();
List<String> syncList = Collections.synchronizedList(list);

// 多线程安全使用
syncList.add("元素1");
syncList.add("元素2");

// 遍历时需要手动同步
synchronized (syncList) {
    for (String item : syncList) {
        System.out.println(item);
    }
}
```

**注意事项**：
- ⚠️ **遍历需要同步**：使用迭代器遍历时，需要手动加锁
- ⚠️ **性能较低**：所有操作都加锁，并发度低
- ⚠️ **不推荐**：性能不如 `CopyOnWriteArrayList` 或 `ConcurrentHashMap`

### 6.2 synchronizedSet() - 线程安全 Set

**方法签名**：
```java
public static <T> Set<T> synchronizedSet(Set<T> s)
```

**使用示例**：
```java
Set<String> set = new HashSet<>();
Set<String> syncSet = Collections.synchronizedSet(set);
```

### 6.3 synchronizedMap() - 线程安全 Map

**方法签名**：
```java
public static <K,V> Map<K,V> synchronizedMap(Map<K,V> m)
```

**使用示例**：
```java
Map<String, String> map = new HashMap<>();
Map<String, String> syncMap = Collections.synchronizedMap(map);
```

**对比 ConcurrentHashMap**：
```java
// 方式1：synchronizedMap（不推荐）
Map<String, String> map1 = Collections.synchronizedMap(new HashMap<>());

// 方式2：ConcurrentHashMap（推荐）
Map<String, String> map2 = new ConcurrentHashMap<>();
```

---

## 七、不可变集合

### 7.1 unmodifiableList() - 只读 List

**方法签名**：
```java
public static <T> List<T> unmodifiableList(List<? extends T> list)
```

**使用示例**：
```java
List<String> list = new ArrayList<>(Arrays.asList("a", "b", "c"));
List<String> unmodifiable = Collections.unmodifiableList(list);

// 可以读取
String first = unmodifiable.get(0);  // "a"

// 不能修改（会抛出 UnsupportedOperationException）
// unmodifiable.add("d");  // ❌ 抛出异常
// unmodifiable.set(0, "x");  // ❌ 抛出异常
```

**注意事项**：
- ⚠️ **只读视图**：返回的是原列表的只读视图，不是副本
- ⚠️ **原列表修改**：如果原列表被修改，只读视图也会反映变化
- ⚠️ **防御性编程**：适合返回给外部调用者，防止意外修改

### 7.2 unmodifiableSet() / unmodifiableMap()

**使用示例**：
```java
// 只读 Set
Set<String> set = new HashSet<>(Arrays.asList("a", "b", "c"));
Set<String> unmodifiableSet = Collections.unmodifiableSet(set);

// 只读 Map
Map<String, String> map = new HashMap<>();
map.put("key1", "value1");
Map<String, String> unmodifiableMap = Collections.unmodifiableMap(map);
```

---

## 八、其他常用方法

### 8.1 frequency() - 统计频率

**方法签名**：
```java
public static int frequency(Collection<?> c, Object o)
```

**使用示例**：
```java
List<String> list = Arrays.asList("apple", "banana", "apple", "cherry", "apple");
int count = Collections.frequency(list, "apple");  // 3
```

### 8.2 disjoint() - 判断是否不相交

**方法签名**：
```java
public static boolean disjoint(Collection<?> c1, Collection<?> c2)
```

**使用示例**：
```java
List<Integer> list1 = Arrays.asList(1, 2, 3);
List<Integer> list2 = Arrays.asList(4, 5, 6);
boolean disjoint = Collections.disjoint(list1, list2);  // true（没有共同元素）

List<Integer> list3 = Arrays.asList(1, 2, 3);
List<Integer> list4 = Arrays.asList(3, 4, 5);
boolean notDisjoint = Collections.disjoint(list3, list4);  // false（有共同元素3）
```

### 8.3 emptyList() / emptySet() / emptyMap() - 空集合

**使用示例**：
```java
// 返回不可变的空集合
List<String> emptyList = Collections.emptyList();
Set<String> emptySet = Collections.emptySet();
Map<String, String> emptyMap = Collections.emptyMap();

// 避免返回 null，推荐返回空集合
public List<String> getItems() {
    if (items == null || items.isEmpty()) {
        return Collections.emptyList();  // 而不是返回 null
    }
    return items;
}
```

---

## 九、线程安全集合创建方式

### 9.1 方式一：Collections.synchronizedXXX（不推荐）

**特点**：
- ✅ **简单**：直接包装现有集合
- ❌ **性能低**：所有方法加锁，锁粒度粗
- ❌ **并发度低**：高并发场景性能差

**示例**：
```java
// List
List<String> syncList = Collections.synchronizedList(new ArrayList<>());

// Set
Set<String> syncSet = Collections.synchronizedSet(new HashSet<>());

// Map
Map<String, String> syncMap = Collections.synchronizedMap(new HashMap<>());
```

**遍历时需要手动同步**：
```java
List<String> syncList = Collections.synchronizedList(new ArrayList<>());

// ❌ 错误：可能抛出 ConcurrentModificationException
for (String item : syncList) {
    System.out.println(item);
}

// ✅ 正确：手动加锁
synchronized (syncList) {
    for (String item : syncList) {
        System.out.println(item);
    }
}
```

### 9.2 方式二：JUC 并发集合（推荐）

#### CopyOnWriteArrayList - 读多写少场景

**特点**：
- ✅ **读无锁**：读操作性能高
- ✅ **线程安全**：写操作加锁
- ❌ **写开销大**：写操作需要复制整个数组
- ✅ **适合场景**：读多写少

**示例**：
```java
import java.util.concurrent.CopyOnWriteArrayList;

List<String> list = new CopyOnWriteArrayList<>();
list.add("元素1");
list.add("元素2");

// 多线程安全，读操作无锁
for (String item : list) {
    System.out.println(item);
}
```

#### ConcurrentHashMap - 高并发 Map

**特点**：
- ✅ **高性能**：锁粒度细，支持高并发
- ✅ **线程安全**：保证并发安全
- ✅ **推荐使用**：替代 synchronizedMap

**示例**：
```java
import java.util.concurrent.ConcurrentHashMap;

Map<String, String> map = new ConcurrentHashMap<>();
map.put("key1", "value1");
map.put("key2", "value2");

// 多线程安全，性能高
String value = map.get("key1");
```

#### ConcurrentLinkedQueue - 高并发队列

**特点**：
- ✅ **无锁算法**：使用 CAS 实现
- ✅ **高性能**：适合高并发场景
- ✅ **线程安全**：保证并发安全

**示例**：
```java
import java.util.concurrent.ConcurrentLinkedQueue;

Queue<String> queue = new ConcurrentLinkedQueue<>();
queue.offer("元素1");
queue.offer("元素2");

String element = queue.poll();
```

### 9.3 方式对比

| 方式 | 性能 | 并发度 | 推荐度 | 适用场景 |
|------|------|--------|--------|----------|
| **synchronizedXXX** | 低 | 低 | ⭐⭐ | 低并发场景 |
| **CopyOnWriteArrayList** | 中（读高） | 中 | ⭐⭐⭐⭐ | 读多写少 |
| **ConcurrentHashMap** | 高 | 高 | ⭐⭐⭐⭐⭐ | 高并发 Map |
| **ConcurrentLinkedQueue** | 高 | 高 | ⭐⭐⭐⭐⭐ | 高并发队列 |

---

## 十、实际应用场景

### 10.1 场景1：商品列表排序

```java
// 商品列表按价格排序
List<Product> products = productService.getAllProducts();
Collections.sort(products, Comparator.comparing(Product::getPrice));

// 按销量降序
Collections.sort(products, Comparator.comparing(Product::getSales).reversed());
```

### 10.2 场景2：在线用户列表（线程安全）

```java
// 使用 CopyOnWriteArrayList（读多写少）
List<User> onlineUsers = new CopyOnWriteArrayList<>();

// 用户上线（写操作少）
public void userLogin(User user) {
    onlineUsers.add(user);
}

// 获取在线用户（读操作多）
public List<User> getOnlineUsers() {
    return Collections.unmodifiableList(onlineUsers);  // 返回只读视图
}
```

### 10.3 场景3：配置信息缓存（线程安全）

```java
// 使用 ConcurrentHashMap
Map<String, Config> configCache = new ConcurrentHashMap<>();

// 多线程安全读写
public Config getConfig(String key) {
    return configCache.get(key);
}

public void updateConfig(String key, Config config) {
    configCache.put(key, config);
}
```

### 10.4 场景4：返回不可变集合

```java
// 服务层返回给控制器
public List<Product> getProducts() {
    List<Product> products = productService.getAllProducts();
    // 返回只读视图，防止外部修改
    return Collections.unmodifiableList(products);
}
```

---

## 十一、常见面试追问

### Q1：Collections.sort() 和 Arrays.sort() 的区别？

**答**：

| 对比项 | Collections.sort() | Arrays.sort() |
|--------|-------------------|---------------|
| **操作对象** | List 集合 | 数组 |
| **底层实现** | 转换为数组后调用 Arrays.sort() | 直接对数组排序 |
| **时间复杂度** | O(n log n) | O(n log n) |
| **稳定性** | 稳定排序 | 稳定排序（对象数组） |

**示例**：
```java
// Collections.sort() - 操作 List
List<Integer> list = new ArrayList<>(Arrays.asList(3, 1, 4, 1, 5));
Collections.sort(list);

// Arrays.sort() - 操作数组
int[] array = {3, 1, 4, 1, 5};
Arrays.sort(array);
```

### Q2：unmodifiableList() 和 synchronizedList() 的区别？

**答**：

| 对比项 | unmodifiableList() | synchronizedList() |
|--------|-------------------|-------------------|
| **作用** | 创建只读视图 | 创建线程安全包装 |
| **修改** | 不能修改（抛出异常） | 可以修改（线程安全） |
| **性能** | 无额外开销 | 有锁开销 |
| **使用场景** | 防止外部修改 | 多线程安全访问 |

### Q3：为什么不推荐使用 synchronizedXXX？

**答**：
1. **性能低**：所有方法加锁，锁粒度粗
2. **并发度低**：高并发场景性能差
3. **遍历需要同步**：使用迭代器需要手动加锁
4. **有更好的替代**：JUC 并发集合性能更好

**推荐**：
- List → `CopyOnWriteArrayList`（读多写少）
- Map → `ConcurrentHashMap`（高并发）
- Queue → `ConcurrentLinkedQueue`（高并发队列）

### Q4：binarySearch() 为什么要求列表有序？

**答**：
- **二分查找原理**：通过比较中间元素，缩小查找范围
- **前提条件**：列表必须有序，才能判断目标在哪一半
- **如果无序**：无法判断，结果不确定
- **时间复杂度**：O(log n)，比线性查找 O(n) 快

### Q5：如何选择线程安全集合？

**答**：

**选择 CopyOnWriteArrayList**：
- ✅ 读多写少场景
- ✅ 数据量不大
- ✅ 可以接受弱一致性

**选择 ConcurrentHashMap**：
- ✅ 高并发 Map 场景
- ✅ 需要高性能
- ✅ 替代 synchronizedMap

**选择 Collections.synchronizedXXX**：
- ✅ 低并发场景
- ✅ 简单快速实现
- ❌ 不推荐用于高并发

---

## 十二、面试回答模板

### 12.1 核心回答（1分钟）

"Collections 工具类提供了丰富的静态方法，主要包括：排序操作如 sort、reverse、shuffle；查找操作如 max、min、binarySearch；替换填充如 replaceAll、fill；复制操作如 copy；同步包装如 synchronizedList、synchronizedMap；不可变集合如 unmodifiableList。线程安全集合创建有两种方式：一是使用 Collections.synchronizedXXX 包装普通集合，但性能较低，不推荐；二是使用 JUC 并发集合，如 CopyOnWriteArrayList、ConcurrentHashMap、ConcurrentLinkedQueue，性能更好，推荐使用。"

### 12.2 扩展回答（3分钟）

"从具体方法看，sort 方法可以对 List 进行排序，支持自然排序和自定义比较器；binarySearch 实现二分查找，但要求列表有序；max 和 min 可以查找最大最小元素。线程安全方面，synchronizedXXX 方法返回同步包装器，所有方法加锁，锁粒度粗，性能低，遍历时还需要手动同步。更好的选择是 JUC 并发集合：CopyOnWriteArrayList 适合读多写少，读操作无锁性能高；ConcurrentHashMap 使用分段锁或 CAS，锁粒度细，性能高；ConcurrentLinkedQueue 使用无锁算法，适合高并发队列场景。实际项目中，推荐使用 JUC 并发集合，而不是 synchronizedXXX。"

### 12.3 加分项

- 能说出 Collections 工具类的主要方法分类
- 了解 binarySearch 的前提条件和返回值含义
- 知道 synchronizedXXX 的遍历需要手动同步
- 理解为什么推荐 JUC 并发集合
- 能说出不同线程安全集合的适用场景