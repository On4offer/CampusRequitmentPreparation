### **LinkedHashMap 介绍**

`LinkedHashMap` 是 Java 集合框架中的一个 `Map` 接口的实现类，它继承自 `HashMap`，并通过 **双向链表** 维护元素的插入顺序或访问顺序。`LinkedHashMap` 提供了比 `HashMap` 更多的特性，特别是在需要保持元素顺序的场景中非常有用。

### **LinkedHashMap 的基本特点**

1. **有序**：与 `HashMap` 不同，`LinkedHashMap` 保证了元素的 **插入顺序** 或 **访问顺序**。这意味着，当你迭代 `LinkedHashMap` 时，元素会按照它们被插入的顺序（或访问顺序）返回。
2. **基于哈希表和双向链表**：`LinkedHashMap` 内部使用一个哈希表来存储键值对，并且通过双向链表来维护元素的插入顺序。每个节点不仅包含键和值，还包含指向前后节点的引用。
3. **允许 `null` 键和值**：`LinkedHashMap` 允许存储一个 `null` 键和多个 `null` 值。
4. **线程不安全**：与 `HashMap` 相同，`LinkedHashMap` 本身也不是线程安全的。如果多个线程同时访问并修改 `LinkedHashMap`，可能会导致数据不一致。可以通过 `Collections.synchronizedMap` 或 `ConcurrentHashMap` 来进行线程安全的处理。
5. **性能**：与 `HashMap` 相比，`LinkedHashMap` 的性能略低，因为它需要额外维护一个双向链表。尤其在插入和删除操作时，双向链表会带来一定的性能开销。

### **LinkedHashMap 的构造函数**

`LinkedHashMap` 提供了多个构造函数，可以定制其行为：

1. **默认构造函数**：

   ```java
   LinkedHashMap<K, V> map = new LinkedHashMap<>();
   ```

   创建一个空的 `LinkedHashMap`，默认容量为 16，负载因子为 0.75。

2. **指定初始容量和负载因子**：

   ```java
   LinkedHashMap<K, V> map = new LinkedHashMap<>(int initialCapacity, float loadFactor);
   ```

   创建一个指定初始容量和负载因子的 `LinkedHashMap`。

3. **指定初始容量、负载因子和顺序模式**：

   ```java
   LinkedHashMap<K, V> map = new LinkedHashMap<>(int initialCapacity, float loadFactor, boolean accessOrder);
   ```

   - `initialCapacity`：指定初始容量。
   - `loadFactor`：指定负载因子。
   - `accessOrder`：指定是否按照访问顺序排序。如果为 `true`，则元素的顺序按照最近访问的顺序排列（用于实现 **LRU 缓存**）；如果为 `false`（默认），则按照元素插入的顺序排列。

### **LinkedHashMap 的常用方法**

`LinkedHashMap` 提供了与 `Map` 接口一致的常用操作方法，并且有一些与顺序相关的额外方法：

1. **添加元素**：
   - `put(K key, V value)`：将指定的键值对插入到 `LinkedHashMap` 中。
   - `putIfAbsent(K key, V value)`：如果指定的键不在 `Map` 中，则插入该键值对。
2. **删除元素**：
   - `remove(Object key)`：删除指定键的键值对。
   - `clear()`：清空所有键值对。
3. **访问元素**：
   - `get(Object key)`：返回指定键的值，如果键不存在返回 `null`。
   - `containsKey(Object key)`：检查 `LinkedHashMap` 中是否包含指定的键。
   - `containsValue(Object value)`：检查 `LinkedHashMap` 中是否包含指定的值。
4. **顺序访问**：
   - `entrySet()`：返回 `LinkedHashMap` 中所有键值对的集合，迭代时按照插入顺序（或访问顺序）返回元素。
   - `keySet()`：返回 `LinkedHashMap` 中所有键的集合，迭代时按照插入顺序（或访问顺序）返回键。
   - `values()`：返回 `LinkedHashMap` 中所有值的集合，迭代时按照插入顺序（或访问顺序）返回值。
5. **访问顺序模式**：
   - 如果构造 `LinkedHashMap` 时设置了 `accessOrder = true`，则可以实现 **LRU 缓存**，使得最近访问的元素排到链表的尾部，而最久未访问的元素会被移到链表的头部。

### **LinkedHashMap 与 HashMap 的对比**

| **特性**            | **LinkedHashMap**                                      | **HashMap**                                            |
| ------------------- | ------------------------------------------------------ | ------------------------------------------------------ |
| **底层数据结构**    | 哈希表 + 双向链表                                      | 哈希表                                                 |
| **是否有序**        | 有序（按插入顺序或访问顺序）                           | 无序                                                   |
| **是否允许 `null`** | 允许一个 `null` 键和多个 `null` 值                     | 允许一个 `null` 键和多个 `null` 值                     |
| **性能**            | 插入和删除操作稍慢于 `HashMap`，因为需要维护双向链表   | 插入和删除操作较快，因为仅依赖于哈希表                 |
| **线程安全**        | 非线程安全                                             | 非线程安全                                             |
| **适用场景**        | 需要保持插入顺序或访问顺序的场景                       | 不需要顺序的场景，适用于性能要求高的操作               |
| **常用方法**        | `put()`, `get()`, `entrySet()`, `keySet()`, `values()` | `put()`, `get()`, `entrySet()`, `keySet()`, `values()` |

### **LinkedHashMap 的访问顺序示例：LRU 缓存**

`LinkedHashMap` 通过设置 `accessOrder = true`，可以实现 **最近最少使用（LRU）缓存** 的功能。在这种模式下，访问过的元素会被移动到链表的尾部，而未访问的元素会停留在链表的头部。

#### **LRU 缓存实现**：

```java
import java.util.*;

public class LRUCache {
    private LinkedHashMap<Integer, Integer> cache;

    public LRUCache(int capacity) {
        cache = new LinkedHashMap<>(capacity, 0.75f, true);  // true 表示按访问顺序排序
    }

    public int get(int key) {
        return cache.getOrDefault(key, -1);
    }

    public void put(int key, int value) {
        cache.put(key, value);
    }

    public static void main(String[] args) {
        LRUCache lru = new LRUCache(3);
        lru.put(1, 1);
        lru.put(2, 2);
        lru.put(3, 3);
        System.out.println(lru.cache);  // 输出 {1=1, 2=2, 3=3}
        lru.get(2);                    // 访问元素 2
        lru.put(4, 4);                 // 插入新的元素，最少使用的元素（1）会被淘汰
        System.out.println(lru.cache);  // 输出 {3=3, 2=2, 4=4}
    }
}
```

在这个例子中：

- **`accessOrder = true`** 使得元素按访问顺序排列。
- 最近访问的元素会被移到尾部，最少访问的元素会被移到头部，最终当缓存满时，最少使用的元素会被删除。

### **总结**

- **`LinkedHashMap`** 是 `HashMap` 的一个有序版本，使用 **双向链表** 来维护元素的插入顺序或访问顺序。
- 它提供了比 `HashMap` 更强的顺序控制能力，适用于需要维护元素顺序的场景。
- `LinkedHashMap` 的性能略低于 `HashMap`，因为它需要维护链表结构，但它支持按插入顺序或访问顺序迭代元素。
- 它还支持通过 **访问顺序** 实现 **LRU 缓存**，非常适合缓存场景。

如果你有更多问题，或者需要进一步的理解，欢迎继续提问！