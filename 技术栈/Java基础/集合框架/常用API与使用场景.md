# 📋 Java 集合框架 - 常用API与使用场景速查

> 日常开发常用集合操作、API速查与代码片段，配合《学习笔记.md》系统学习使用。

---

## 🗺️ 集合选型速查表

| 场景 | 推荐集合 | 特点 |
|------|----------|------|
| 频繁随机访问 | `ArrayList` | 底层数组，O(1)查询 |
| 频繁插入删除 | `LinkedList` | 底层链表，O(1)增删 |
| 去重无序 | `HashSet` | 哈希表，O(1)操作 |
| 去重有序 | `LinkedHashSet` | 保持插入顺序 |
| 去重排序 | `TreeSet` | 红黑树，自动排序 |
| 键值对快速查找 | `HashMap` | 哈希表，最常用 |
| 键值对保持插入顺序 | `LinkedHashMap` | 按插入顺序遍历 |
| 键值对排序 | `TreeMap` | 按键排序 |
| 线程安全List | `CopyOnWriteArrayList` | 读多写少场景 |
| 线程安全Map | `ConcurrentHashMap` | 高并发场景 |
| 队列（FIFO） | `ArrayDeque` / `LinkedList` | 双端队列 |
| 优先队列 | `PriorityQueue` | 堆实现，自动排序 |
| 栈（LIFO） | `ArrayDeque` | 用Deque模拟栈 |

---

## 📚 List 常用操作

### ArrayList

```java
// 创建
List<String> list = new ArrayList<>();
List<String> list2 = new ArrayList<>(100);      // 指定初始容量
List<String> list3 = Arrays.asList("a", "b");   // 固定大小，不能增删
List<String> list4 = new ArrayList<>(Arrays.asList("a", "b")); // 可变

// JDK 9+ 快速创建（不可变）
List<String> list5 = List.of("a", "b", "c");

// 添加元素
list.add("A");
list.add(0, "B");                               // 指定位置插入
list.addAll(anotherList);                       // 添加整个集合

// 获取元素
String first = list.get(0);

// 修改元素
list.set(0, "NewValue");

// 删除元素
list.remove(0);                                 // 按索引删除
list.remove("A");                               // 按对象删除
list.removeIf(s -> s.startsWith("A"));          // 按条件删除（JDK 8+）
list.clear();                                   // 清空

// 查询
int size = list.size();
boolean exists = list.contains("A");
int index = list.indexOf("A");                  // 第一次出现位置
int lastIndex = list.lastIndexOf("A");          // 最后一次出现位置
boolean isEmpty = list.isEmpty();

// 遍历
for (String s : list) { }                       // 增强for
for (int i = 0; i < list.size(); i++) { }       // 索引遍历
list.forEach(System.out::println);              // Lambda
Iterator<String> it = list.iterator();          // 迭代器
while (it.hasNext()) {
    String s = it.next();
    if (s.equals("remove")) it.remove();        // 安全删除
}

// 转换
Object[] arr = list.toArray();
String[] strArr = list.toArray(new String[0]);

// 排序
Collections.sort(list);                         // 自然排序
list.sort(Comparator.naturalOrder());           // 同上
list.sort(Comparator.reverseOrder());           // 倒序
list.sort(Comparator.comparing(String::length)); // 按长度排序

// 子列表（视图，修改会影响原列表）
List<String> sub = list.subList(0, 5);
```

### LinkedList（双端队列特性）

```java
LinkedList<String> linkedList = new LinkedList<>();

// 作为队列使用（FIFO）
linkedList.offer("A");                          // 入队（尾部添加）
linkedList.offerLast("B");                      // 同offer
linkedList.offerFirst("C");                     // 头部添加
String first = linkedList.poll();               // 出队（头部移除）
String peek = linkedList.peek();                // 查看头部不移除

// 作为栈使用（LIFO）
linkedList.push("A");                           // 压栈（头部添加）
String pop = linkedList.pop();                  // 弹栈（头部移除）

// 双端操作
linkedList.addFirst("A");
linkedList.addLast("B");
String first = linkedList.getFirst();
String last = linkedList.getLast();
linkedList.removeFirst();
linkedList.removeLast();
```

---

## 🔗 Set 常用操作

### HashSet（最常用）

```java
// 创建
Set<String> set = new HashSet<>();
Set<String> set2 = new HashSet<>(Arrays.asList("a", "b"));
Set<String> set3 = Set.of("a", "b", "c");       // JDK 9+ 不可变

// 添加（重复元素不会添加，返回false）
set.add("A");
set.addAll(anotherSet);

// 删除
set.remove("A");
set.removeIf(s -> s.length() > 5);
set.clear();

// 查询
boolean exists = set.contains("A");
int size = set.size();
boolean isEmpty = set.isEmpty();

// 遍历
for (String s : set) { }
set.forEach(System.out::println);

// 去重技巧：List转Set再转回List
List<String> uniqueList = new ArrayList<>(new HashSet<>(list));
```

### TreeSet（有序）

```java
// 自然排序
TreeSet<Integer> treeSet = new TreeSet<>();
treeSet.add(3);
treeSet.add(1);
treeSet.add(2);
// 遍历顺序: 1, 2, 3

// 自定义排序
TreeSet<String> lengthSet = new TreeSet<>(Comparator.comparing(String::length));

// 获取首尾
Integer first = treeSet.first();
Integer last = treeSet.last();

// 范围查询
Set<Integer> head = treeSet.headSet(5);         // 小于5的元素
Set<Integer> tail = treeSet.tailSet(5);         // 大于等于5的元素
Set<Integer> sub = treeSet.subSet(2, 5);        // [2, 5) 范围内的元素

// 获取邻近元素
Integer lower = treeSet.lower(5);               // 严格小于5的最大值
Integer floor = treeSet.floor(5);               // 小于等于5的最大值
Integer ceiling = treeSet.ceiling(5);           // 大于等于5的最小值
Integer higher = treeSet.higher(5);             // 严格大于5的最小值
```

### LinkedHashSet（保持插入顺序）

```java
// 适用于需要去重且保持插入顺序的场景
LinkedHashSet<String> linkedSet = new LinkedHashSet<>();
linkedSet.add("C");
linkedSet.add("A");
linkedSet.add("B");
// 遍历顺序: C, A, B（插入顺序）
```

---

## 🗂️ Map 常用操作

### HashMap（最常用）

```java
// 创建
Map<String, Integer> map = new HashMap<>();
Map<String, Integer> map2 = new HashMap<>(100); // 指定初始容量
Map<String, Integer> map3 = Map.of("a", 1, "b", 2); // JDK 9+ 不可变

// 添加/更新
map.put("key", 100);
map.putIfAbsent("key", 200);                    // key不存在时才put
map.putAll(anotherMap);

// 获取
Integer value = map.get("key");
Integer valueOrDefault = map.getOrDefault("key", 0); // 不存在返回默认值

// 删除
map.remove("key");
map.remove("key", 100);                         // key和value都匹配才删除
map.clear();

// 查询
boolean hasKey = map.containsKey("key");
boolean hasValue = map.containsValue(100);
int size = map.size();
boolean isEmpty = map.isEmpty();

// 遍历
// 方式1：遍历key
for (String key : map.keySet()) {
    Integer val = map.get(key);
}

// 方式2：遍历entry（推荐）
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    Integer val = entry.getValue();
}

// 方式3：Lambda（JDK 8+）
map.forEach((k, v) -> System.out.println(k + "=" + v));

// 获取所有key/value
Set<String> keys = map.keySet();
Collection<Integer> values = map.values();
Set<Map.Entry<String, Integer>> entries = map.entrySet();

// 合并（JDK 8+）
map.merge("key", 1, Integer::sum);              // 存在则累加，不存在设为1

// 计算（JDK 8+）
map.compute("key", (k, v) -> v == null ? 1 : v + 1);
map.computeIfAbsent("key", k -> loadValue(k));  // 不存在时计算
map.computeIfPresent("key", (k, v) -> v + 1);   // 存在时计算
```

### TreeMap（有序Map）

```java
// 按键自然排序
TreeMap<String, Integer> treeMap = new TreeMap<>();

// 自定义排序
TreeMap<String, Integer> lengthMap = new TreeMap<>(Comparator.comparing(String::length));

// 范围操作（同TreeSet）
Map<String, Integer> head = treeMap.headMap("key");
Map<String, Integer> tail = treeMap.tailMap("key");
Map<String, Integer> sub = treeMap.subMap("a", "d"); // [a, d)

// 获取首尾键值
String firstKey = treeMap.firstKey();
String lastKey = treeMap.lastKey();
Map.Entry<String, Integer> firstEntry = treeMap.firstEntry();
Map.Entry<String, Integer> lastEntry = treeMap.lastEntry();
```

### LinkedHashMap（保持插入顺序/访问顺序）

```java
// 保持插入顺序（默认）
LinkedHashMap<String, Integer> linkedMap = new LinkedHashMap<>();

// 保持访问顺序（可用于实现LRU缓存）
LinkedHashMap<String, Integer> lruMap = new LinkedHashMap<>(16, 0.75f, true) {
    @Override
    protected boolean removeEldestEntry(Map.Entry<String, Integer> eldest) {
        return size() > 100;                    // 超过100个时删除最老的
    }
};
```

---

## 🔄 集合工具类 Collections

```java
List<String> list = new ArrayList<>();

// 排序
Collections.sort(list);                         // 自然排序
Collections.sort(list, Comparator.reverseOrder()); // 自定义比较器

// 查找
int index = Collections.binarySearch(list, "key"); // 二分查找（需先排序）
String max = Collections.max(list);
String min = Collections.min(list);

// 替换/填充
Collections.replaceAll(list, "old", "new");
Collections.fill(list, "value");                // 全部填充为同一值

// 打乱顺序
Collections.shuffle(list);

// 反转
Collections.reverse(list);

// 旋转
Collections.rotate(list, 3);                    // 向右旋转3位
Collections.rotate(list, -3);                   // 向左旋转3位

// 交换
Collections.swap(list, 0, 1);                   // 交换0和1位置的元素

// 拷贝（目标列表需已有足够容量）
List<String> dest = new ArrayList<>(Collections.nCopies(list.size(), ""));
Collections.copy(dest, list);

// 创建不可变集合
List<String> unmodifiableList = Collections.unmodifiableList(list);
Set<String> unmodifiableSet = Collections.unmodifiableSet(set);
Map<String, Integer> unmodifiableMap = Collections.unmodifiableMap(map);

// 创建同步集合（线程安全）
List<String> syncList = Collections.synchronizedList(list);
Set<String> syncSet = Collections.synchronizedSet(set);
Map<String, Integer> syncMap = Collections.synchronizedMap(map);

// 单例集合
List<String> singletonList = Collections.singletonList("only");
Set<String> singletonSet = Collections.singleton("only");
Map<String, Integer> singletonMap = Collections.singletonMap("key", 1);

// 空集合
List<String> emptyList = Collections.emptyList();
Set<String> emptySet = Collections.emptySet();
Map<String, Integer> emptyMap = Collections.emptyMap();

// 频率统计
int freq = Collections.frequency(list, "A");    // "A"出现的次数

//  disjoint判断（无共同元素返回true）
boolean noCommon = Collections.disjoint(list1, list2);
```

---

## 🧵 线程安全集合

### ConcurrentHashMap

```java
// 创建
ConcurrentHashMap<String, Integer> concurrentMap = new ConcurrentHashMap<>();

// 常用方法（与HashMap类似，但线程安全）
concurrentMap.put("key", 100);
Integer value = concurrentMap.get("key");
concurrentMap.putIfAbsent("key", 200);
concurrentMap.remove("key");

// 原子操作
concurrentMap.compute("key", (k, v) -> v == null ? 1 : v + 1);
concurrentMap.merge("key", 1, Integer::sum);

// 批量操作
concurrentMap.forEach(3, (k, v) -> System.out.println(k + "=" + v)); // 3个线程并行
concurrentMap.forEach(3, (k, v) -> k + "=" + v, System.out::println); // 转换后输出

// 搜索
String result = concurrentMap.search(3, (k, v) -> v > 100 ? k : null);

// 归约
long sum = concurrentMap.reduceValuesToLong(3, v -> v, 0, Long::sum);
```

### CopyOnWriteArrayList

```java
// 适用于读多写少场景
CopyOnWriteArrayList<String> cowList = new CopyOnWriteArrayList<>();

// 读操作（无锁，高性能）
String s = cowList.get(0);
for (String item : cowList) { }

// 写操作（加锁，复制新数组）
cowList.add("A");
cowList.remove("B");

// 迭代器（快照，不会抛出ConcurrentModificationException）
Iterator<String> it = cowList.iterator();
```

---

## 🎯 常用代码场景

### 1. List 去重并保持顺序

```java
// 方法1：LinkedHashSet
List<String> unique = new ArrayList<>(new LinkedHashSet<>(list));

// 方法2：Stream API（JDK 8+）
List<String> unique2 = list.stream()
    .distinct()
    .collect(Collectors.toList());
```

### 2. List 排序

```java
// 自然排序
Collections.sort(list);
list.sort(Comparator.naturalOrder());

// 倒序
list.sort(Comparator.reverseOrder());

// 按字段排序
list.sort(Comparator.comparing(User::getAge));
list.sort(Comparator.comparing(User::getAge).reversed()); // 倒序
list.sort(Comparator.comparing(User::getAge)
                    .thenComparing(User::getName));        // 多字段排序

// null值处理
list.sort(Comparator.nullsFirst(Comparator.naturalOrder()));
list.sort(Comparator.nullsLast(Comparator.naturalOrder()));
```

### 3. List 转 Map

```java
// 按某个字段分组
Map<Integer, List<User>> groupByAge = users.stream()
    .collect(Collectors.groupingBy(User::getAge));

// 转为Map（key不能重复）
Map<Integer, String> idNameMap = users.stream()
    .collect(Collectors.toMap(User::getId, User::getName));

// 处理key冲突
Map<Integer, String> idNameMap2 = users.stream()
    .collect(Collectors.toMap(
        User::getId, 
        User::getName,
        (existing, replacement) -> existing  // 保留已有值
    ));
```

### 4. Map 按Value排序

```java
// 转为List排序后再转回Map
Map<String, Integer> sortedByValue = map.entrySet().stream()
    .sorted(Map.Entry.<String, Integer>comparingByValue().reversed())
    .collect(Collectors.toMap(
        Map.Entry::getKey,
        Map.Entry::getValue,
        (e1, e2) -> e1,
        LinkedHashMap::new  // 保持顺序
    ));
```

### 5. 统计频率

```java
// 统计List中各元素出现次数
Map<String, Long> frequency = list.stream()
    .collect(Collectors.groupingBy(Function.identity(), Collectors.counting()));

// 找出出现次数最多的元素
String mostFrequent = frequency.entrySet().stream()
    .max(Map.Entry.comparingByValue())
    .map(Map.Entry::getKey)
    .orElse(null);
```

### 6. 分页处理

```java
// 手动分页
public <T> List<T> getPage(List<T> list, int pageNum, int pageSize) {
    int fromIndex = (pageNum - 1) * pageSize;
    int toIndex = Math.min(fromIndex + pageSize, list.size());
    if (fromIndex > list.size()) {
        return Collections.emptyList();
    }
    return list.subList(fromIndex, toIndex);
}
```

### 7. 缓存实现（LRU）

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;
    
    public LRUCache(int capacity) {
        super(capacity, 0.75f, true);  // accessOrder = true
        this.capacity = capacity;
    }
    
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}

// 使用
LRUCache<String, Object> cache = new LRUCache<>(100);
cache.put("key", value);
Object value = cache.get("key");
```

---

## ⚠️ 常见坑点速查

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| `Arrays.asList()` | 返回固定大小的List，不能增删 | 需要增删时包一层 `new ArrayList<>(Arrays.asList(...))` |
| `List.of()` | JDK 9+ 返回不可变List | 需要可变时用 `new ArrayList<>(List.of(...))` |
| 遍历时删除 | 普通for/增强for遍历时删除会报错 | 用迭代器的 `remove()` 或 `removeIf()` |
| `subList()` | 返回原List的视图，修改会影响原List | 需要独立副本时用 `new ArrayList<>(list.subList(...))` |
| HashMap的key | 可变对象作为key，修改后可能找不到 | key用不可变对象（String、Integer等） |
| 自定义对象作key | 未重写`equals`和`hashCode` | 必须重写，且保持一致性 |
| TreeMap/TreeSet | 元素未实现Comparable且未传Comparator | 会抛出ClassCastException |
| 空指针 | `get()`返回null时自动拆箱 | 用 `getOrDefault()` 或先判空 |
| 并发修改 | 多线程操作普通集合 | 用Concurrent集合或同步包装 |

---

## 📝 面试代码手写题

### 1. 手写ArrayList核心逻辑

```java
public class MyArrayList<T> {
    private Object[] elementData;
    private int size;
    private static final int DEFAULT_CAPACITY = 10;
    
    public MyArrayList() {
        elementData = new Object[DEFAULT_CAPACITY];
    }
    
    public void add(T element) {
        ensureCapacity();
        elementData[size++] = element;
    }
    
    @SuppressWarnings("unchecked")
    public T get(int index) {
        checkIndex(index);
        return (T) elementData[index];
    }
    
    public T remove(int index) {
        checkIndex(index);
        @SuppressWarnings("unchecked")
        T oldValue = (T) elementData[index];
        int numMoved = size - index - 1;
        if (numMoved > 0) {
            System.arraycopy(elementData, index + 1, elementData, index, numMoved);
        }
        elementData[--size] = null;
        return oldValue;
    }
    
    private void ensureCapacity() {
        if (size == elementData.length) {
            int newCapacity = elementData.length * 2;
            elementData = Arrays.copyOf(elementData, newCapacity);
        }
    }
    
    private void checkIndex(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
    
    public int size() { return size; }
}
```

### 2. 手写LRU缓存

```java
class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;
    
    public LRUCache(int capacity) {
        super(capacity, 0.75f, true);
        this.capacity = capacity;
    }
    
    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}
```

---

> 💡 **提示**：本文档用于日常速查，系统学习请查看《学习笔记.md》
