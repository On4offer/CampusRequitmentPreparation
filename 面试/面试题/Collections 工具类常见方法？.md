好，这个问题考察的是 **Java 集合工具类**，常见于中低频面试题，但很好回答，整理成 **面试答题模板**：

------

# 📌 面试题：Collections 工具类常见方法有哪些？线程安全集合如何创建？

## 一、核心回答

1. **Collections 工具类常见方法**
   - **排序类**
     - `Collections.sort(list)`：对 List 排序（可传 Comparator）。
     - `Collections.reverse(list)`：反转顺序。
     - `Collections.shuffle(list)`：随机打乱顺序。
   - **查找/替换类**
     - `Collections.max/min(collection)`：找最大/最小元素。
     - `Collections.binarySearch(list, key)`：二分查找（前提是有序）。
     - `Collections.replaceAll(list, oldVal, newVal)`：批量替换。
   - **填充/复制类**
     - `Collections.copy(dest, src)`：复制集合。
     - `Collections.fill(list, obj)`：用 obj 填充 list。
   - **不可变集合**
     - `Collections.unmodifiableList(list)`：返回只读 List。
   - **线程安全包装**
     - `Collections.synchronizedList(list)`：返回线程安全的 List。

------

## 二、线程安全集合如何创建？

1. **方式一：Collections.synchronizedXXX**

   - 包装现有集合，使其变为同步集合。

   - 例如：

     ```java
     List<String> list = new ArrayList<>();
     List<String> syncList = Collections.synchronizedList(list);
     ```

   - 缺点：所有方法加锁，性能较低。

2. **方式二：并发集合类（推荐）**

   - JUC 包提供的并发集合：
     - `CopyOnWriteArrayList`（读多写少场景）。
     - `ConcurrentHashMap`（高并发 Map）。
     - `ConcurrentLinkedQueue`（高并发队列）。
   - 相比 synchronizedXXX，性能更好。

------

## 三、项目场景举例

- **黑马点评项目**：
  - 如果要统计在线用户列表，且有多线程读写，可以用 `CopyOnWriteArrayList`，保证读写安全。
- **苍穹外卖项目**：
  - 如果要做订单分发队列，用 `ConcurrentLinkedQueue` 比 `Collections.synchronizedList` 更高效。

------

## 四、常见追问

1. **Collections.sort 和 Arrays.sort 区别？**
   - Collections.sort 基于 List；Arrays.sort 基于数组。
2. **unmodifiableList 和 synchronizedList 区别？**
   - unmodifiableList 返回不可修改视图；synchronizedList 返回线程安全包装。
3. **为什么不推荐 synchronizedXXX？**
   - 因为粒度粗，性能差，通常推荐并发集合。

------

✅ **一分钟口述版总结**
 Collections 工具类提供了排序、查找、替换、填充、复制、线程安全包装等方法。线程安全集合可以用 `Collections.synchronizedXXX` 包装普通集合，但推荐使用 JUC 并发集合，如 CopyOnWriteArrayList、ConcurrentHashMap 等，性能更好。

------

要不要我帮你整理一份 **集合工具类方法速查表**（分类表格版），面试时能一眼背下来？