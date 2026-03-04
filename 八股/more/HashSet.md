### `HashSet`

`HashSet` 是 Java 中的一个集合类，它实现了 **Set 接口**，并且基于 **哈希表** 实现。`HashSet` 主要用于存储不重复的元素。它不保证集合中的元素顺序，因此它不是一个有序的集合。

### 1. **`HashSet` 的特点**

- **不允许重复元素**：`HashSet` 保证集合中的每个元素都是唯一的。如果尝试插入一个已经存在的元素，插入操作会失败，不会抛出异常。
- **无序**：`HashSet` 中的元素没有固定的顺序，元素的顺序与插入顺序无关。它是基于哈希表的，元素在集合中的位置取决于其哈希值。
- **允许 `null` 值**：`HashSet` 允许一个 `null` 元素。如果插入多个 `null`，只有一个会被存储，因为集合不允许重复元素。
- **基于哈希表实现**：`HashSet` 底层使用 `HashMap` 来存储元素。它通过元素的哈希值来确定元素的位置，从而提供常数时间复杂度（O(1)）的元素插入、删除和查找操作。

### 2. **`HashSet` 的常用方法**

`HashSet` 继承自 `AbstractSet` 类，并实现了 `Set` 接口。以下是一些常用方法：

- **`add(E e)`**：将指定的元素添加到集合中。如果集合中已经包含该元素，则返回 `false`；否则，添加成功并返回 `true`。
- **`remove(Object o)`**：从集合中移除指定的元素。如果元素存在，移除成功并返回 `true`，否则返回 `false`。
- **`contains(Object o)`**：检查集合中是否包含指定的元素，返回 `true` 如果集合中包含该元素，反之返回 `false`。
- **`size()`**：返回集合中元素的数量。
- **`clear()`**：移除集合中的所有元素。
- **`isEmpty()`**：检查集合是否为空，返回 `true` 如果集合中没有元素，反之返回 `false`。
- **`iterator()`**：返回一个迭代器，用于遍历集合中的元素。
- **`toArray()`**：返回一个包含集合所有元素的数组。

### 3. **`HashSet` 示例**

以下是一个 `HashSet` 的使用示例：

```java
import java.util.HashSet;

public class HashSetExample {
    public static void main(String[] args) {
        // 创建一个 HashSet 实例
        HashSet<String> set = new HashSet<>();

        // 添加元素
        set.add("apple");
        set.add("banana");
        set.add("cherry");

        // 添加重复元素，add 返回 false
        boolean added = set.add("apple");  // false，因为 apple 已经存在
        System.out.println("Element added: " + added);  // 输出 false

        // 打印集合
        System.out.println("HashSet: " + set);  // 输出 HashSet: [banana, apple, cherry]

        // 检查集合是否包含某个元素
        boolean contains = set.contains("banana");
        System.out.println("Contains banana: " + contains);  // 输出 true

        // 移除元素
        set.remove("banana");
        System.out.println("After removing banana: " + set);  // 输出 After removing banana: [apple, cherry]

        // 获取集合大小
        System.out.println("Size of set: " + set.size());  // 输出 2

        // 清空集合
        set.clear();
        System.out.println("Is set empty? " + set.isEmpty());  // 输出 true
    }
}
```

### 4. **`HashSet` 和 `HashMap` 的关系**

`HashSet` 底层是基于 `HashMap` 实现的。`HashSet` 中存储的每个元素实际上是 `HashMap` 的一个键，而值则是固定的 `PRESENT` 常量。`HashSet` 利用 `HashMap` 的键的唯一性来保证集合中元素的唯一性。

- `HashSet` 允许插入一个 `null` 元素，而 `HashMap` 也允许 `null` 作为键或值。
- `HashSet` 的插入、删除和查找操作的时间复杂度为 O(1)，这是因为它基于哈希表结构。

### 简洁总结：

- **`HashSet` 并没有继承 `HashMap`**，也没有实现它。
- 它是 **“组合”（调用）了一个 `HashMap` 对象**作为内部结构。
- 这意味着：
  - `HashSet` 的元素，其实被作为 `HashMap` 的 key 存进去；
  - 值（value）用一个固定的对象 `PRESENT` 占位，不关心。

------

### 举个例子来说明：

你执行：

```java
HashSet<String> set = new HashSet<>();
set.add("apple");
set.add("banana");
```

底层其实等同于做了：

```java
HashMap<String, Object> map = new HashMap<>();
map.put("apple", PRESENT);
map.put("banana", PRESENT);
```

- 所以 `HashSet` 利用 `HashMap` 的特性（键唯一、查找快）来实现自己的功能。
- 但它对外**不暴露 `HashMap` 的方法**，只暴露 `Set` 接口规定的行为。

------

这就是 **“[组合优于继承](组合优于继承)”** 的经典应用。

### 5. **`HashSet` 的性能**

由于 `HashSet` 底层使用哈希表，它提供了常数时间复杂度的插入、删除和查找操作，具体性能取决于哈希函数和哈希冲突的处理方式。当哈希表的负载因子（即元素个数与容量的比例）过大时，`HashSet` 会进行扩容，这会导致性能下降。

### 6. **`HashSet` 的使用场景**

`HashSet` 非常适合以下场景：

- **去重**：当你需要去除重复元素时，`HashSet` 非常有用。例如，存储一个列表中的唯一元素。

  ```java
  List<String> list = Arrays.asList("apple", "banana", "apple", "cherry");
  Set<String> set = new HashSet<>(list);
  System.out.println(set);  // 输出 [banana, apple, cherry]
  ```

- **集合操作**：`HashSet` 可以用于集合之间的并集、交集和差集操作。例如，检查两个集合是否有共同元素，或获取两个集合的并集。

- **高效查找**：当需要频繁检查某个元素是否存在于集合中时，`HashSet` 提供了高效的查找性能。

### 7. **总结**

- **`HashSet`** 是基于哈希表实现的集合类，保证集合中的元素唯一。
- 它提供了常数时间复杂度（O(1)）的插入、删除和查找操作。
- `HashSet` 不保证元素的顺序，也允许 `null` 元素。
- 它非常适合用于去重、集合操作以及高效查找等场景。

通过 `HashSet`，开发者可以更加高效地处理不需要重复元素的集合操作，从而提高代码的性能和简洁性。