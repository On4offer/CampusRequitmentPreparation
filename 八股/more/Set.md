在 Java 中，**`Set`** 是一个接口，属于 Java 集合框架，用于存储**无重复元素**的集合。它的核心特性是：**不允许重复值，且最多包含一个 null（某些实现）**。

------

### 一、Set 的主要特性

- **元素不重复**：集合中不能有重复元素（通过 `equals()` 和 `hashCode()` 判断）。
- **无索引访问**：不像 `List`，不能通过下标访问元素。
- **元素无序/有序**：不同实现类顺序不同（如 [HashSet](HashSet) 无序，[LinkedHashSet](LinkedHashSet) 有序）。

------

### 二、常见实现类及特点

| 实现类                           | 特点                                                         |
| -------------------------------- | ------------------------------------------------------------ |
| [`HashSet`](HashSet)             | 基于[哈希表](哈希表)，**无序**，元素唯一，查询和添加速度快（平均 O(1)） |
| [`LinkedHashSet`](LinkedHashSet) | 基于哈希表 + 双向链表，**保持插入顺序**，性能略低于 HashSet  |
| [`TreeSet`](more/TreeSet)        | 基于红黑树，**自动排序（有序）**，元素必须实现 `Comparable` 或传入 `Comparator` |
| `CopyOnWriteArraySet`            | 线程安全，适合读多写少的并发场景                             |

------

### 三、常用方法（来自 `Collection` 接口）

```java
Set<String> set = new HashSet<>();

set.add("A");        // 添加元素
set.add("B");
set.remove("A");     // 删除元素
set.contains("B");   // 是否包含某元素
set.size();          // 元素数量
set.clear();         // 清空集合
```

------

### 四、遍历 Set 的方式

```java
// for-each 循环
for (String s : set) {
    System.out.println(s);
}

// 迭代器
Iterator<String> it = set.iterator();
while (it.hasNext()) {
    System.out.println(it.next());
}
```

------

### 五、Set 与 List 的区别

| 特性             | Set                         | List                  |
| ---------------- | --------------------------- | --------------------- |
| 是否允许重复     | 否                          | 是                    |
| 是否有顺序       | 实现决定（如 TreeSet 有序） | 有序（插入顺序）      |
| 是否支持索引访问 | 否                          | 是                    |
| 常见实现         | HashSet, TreeSet            | ArrayList, LinkedList |

------

### 六、典型应用场景

- 去重（如过滤重复的用户名、ID）
- 快速查找某元素是否存在
- 保证数据唯一性集合
- 有序去重（使用 TreeSet）

------

是否需要我展示 `HashSet` 和 `TreeSet` 在存储和排序上的代码例子？