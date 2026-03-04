在 Java 中，**`List`** 是一个接口，属于 Java 集合框架（Java Collection Framework）的一部分。它表示一个**有序、可重复元素的集合**，可以通过索引访问元素。

------

### 一、`List` 的主要特性

- **有序**：元素按插入顺序排列。
- **可重复**：允许存在重复元素。
- **支持索引**：可通过下标访问元素，支持随机访问（如 `get(int index)`）。
- **动态大小**：不像数组固定长度，`List` 可以动态增加或删除元素。

------

### 二、常用实现类

| 实现类                 | 特点                                             |
| ---------------------- | ------------------------------------------------ |
| `ArrayList`            | 基于数组，查询快、插入删除慢，线程不安全，最常用 |
| `LinkedList`           | 基于双向链表，插入删除快，查询慢                 |
| `Vector`               | 与 `ArrayList` 类似，但线程安全（已较少使用）    |
| `Stack`                | 继承自 `Vector`，表示栈结构（后进先出）          |
| `CopyOnWriteArrayList` | 线程安全，适合读多写少的并发场景                 |

------

### 三、常用方法（接口定义）

```java
List<String> list = new ArrayList<>();

list.add("A");        // 添加元素
list.add(1, "B");     // 在指定位置添加元素
list.get(0);          // 获取索引处的元素
list.set(1, "C");     // 替换指定位置的元素
list.remove(0);       // 删除指定索引的元素
list.contains("C");   // 是否包含元素
list.size();          // 获取元素个数
list.clear();         // 清空所有元素
```

------

### 四、遍历方式

```java
// for-each 循环
for (String s : list) {
    System.out.println(s);
}

// 使用索引
for (int i = 0; i < list.size(); i++) {
    System.out.println(list.get(i));
}

// 使用迭代器
Iterator<String> it = list.iterator();
while (it.hasNext()) {
    System.out.println(it.next());
}
```

------

### 五、`List` 使用场景

- 有顺序要求的数据集合
- 需要通过下标快速访问元素
- 需要处理重复数据的集合
- 频繁查找时优先使用 `ArrayList`；频繁插入/删除用 `LinkedList`

------

需要我具体演示一下 `ArrayList` 和 `LinkedList` 的性能差异或者代码示例吗？