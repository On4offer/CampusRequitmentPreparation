好 👍
 这道题属于 **Map 体系常见对比题**，我来给你整理一份 **面试答题模板**：

------

# 📌 面试题：TreeMap 和 HashMap 的区别？TreeMap 如何保证有序？

## 一、核心回答

1. **底层结构**
   - **HashMap**：基于 **数组 + 链表 + 红黑树**（JDK1.8 后），通过哈希定位，存取速度快。
   - **TreeMap**：基于 **红黑树**（自平衡二叉查找树）实现，按 key 的大小顺序存储元素。
2. **有序性**
   - **HashMap**：无序，key 的顺序依赖 hash 值。
   - **TreeMap**：有序，可以是 **自然顺序**（key 实现 Comparable）或 **自定义顺序**（传入 Comparator）。
3. **性能**
   - HashMap：插入、删除、查找平均 O(1)，最坏 O(n)。
   - TreeMap：所有操作复杂度 O(log n)。
4. **null 键和值**
   - HashMap：允许一个 null key 和多个 null value。
   - TreeMap：key 不允许为 null（比较时会报 NPE），value 可以为 null。

------

## 二、TreeMap 如何保证有序？

1. **底层红黑树**
   - 插入时，会根据 key 的大小关系插入到合适的位置。
   - 插入后如果破坏了红黑树的平衡，会通过 **旋转和变色** 来保持平衡。
   - 红黑树保证了中序遍历时 key 是有序的。
2. **排序规则**
   - 默认：key 必须实现 `Comparable` 接口（自然排序）。
   - 自定义：创建 TreeMap 时传入 `Comparator`，可以按自定义规则排序。

------

## 三、项目场景举例

- 在 **黑马点评项目** 中：
  - 用 HashMap 存储商户信息，按 id 查找，性能高。
  - 如果要实现“按评分排序的排行榜”，用 TreeMap 维护评分到商户的映射，更合适。
- 在 **苍穹外卖项目** 中：
  - HashMap 适合存储订单号 → 订单信息。
  - 如果要做“订单按时间顺序展示”，可以用 TreeMap（key = 下单时间）。

------

## 四、常见追问

1. TreeMap 为什么不用 HashMap？
   - 当需要 **有序性** 时才用 TreeMap，比如排行榜、区间查询。
2. TreeMap 是线程安全的吗？
   - 不是，线程安全需要 `Collections.synchronizedMap(new TreeMap<>())` 或 `ConcurrentSkipListMap`。
3. ConcurrentSkipListMap 和 TreeMap 的区别？
   - ConcurrentSkipListMap 基于 **跳表**，支持并发，性能更好；TreeMap 基于红黑树，不支持并发。

------

✅ **一分钟口述版总结**
 HashMap 基于哈希表实现，存取快但无序；TreeMap 基于红黑树实现，能保证 key 有序。TreeMap 的有序性来自红黑树的插入、旋转和变色机制，key 需要实现 Comparable 或传入 Comparator。

------

要不要我帮你再整理一个 **HashMap vs TreeMap vs LinkedHashMap 对比表**，面试时能一口气把三者说清楚？