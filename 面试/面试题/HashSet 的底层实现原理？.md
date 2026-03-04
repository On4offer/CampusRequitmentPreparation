好 👍
 这道题是 **Set 体系高频面试题**，我帮你整理成 **面试答题模板**：

------

# 📌 面试题：HashSet 的底层实现原理是什么？为什么不允许重复元素？

## 一、核心回答

1. **底层实现**
   - `HashSet` 底层基于 **HashMap** 实现。
   - 每次往 HashSet 添加元素时，实际是把该元素作为 **key** 放入 HashMap，value 是一个固定常量（如 `PRESENT`）。
   - 因此，HashSet 的所有操作（增删改查）都依赖于 HashMap。
2. **为什么不允许重复？**
   - HashMap 的 key 是唯一的，HashSet 元素作为 key 存储，自然保证了唯一性。
   - 添加元素时：
     - 先计算 **hashCode**，找到桶的位置。
     - 再通过 **equals()** 判断是否已有相同元素。
     - 如果存在则覆盖（对 HashSet 来说就是添加失败），否则插入成功。

------

## 二、扩展回答

- **判断重复的依据**
  - 先比较 hashCode() → 再比较 equals()。
  - 所以要保证 **hashCode 和 equals 一致性**，否则可能导致逻辑错误。
- **迭代顺序问题**
  - HashSet 不保证顺序，因为 HashMap 的存储位置由 hash 值决定。
  - 如果要保持插入顺序，可以用 **LinkedHashSet**；
  - 如果要保持排序，可以用 **TreeSet**。
- **线程安全性**
  - HashSet 本身不是线程安全的。
  - 多线程场景可用 `Collections.synchronizedSet()` 或 `ConcurrentHashMap.newKeySet()`。

------

## 三、项目场景举例

- 在 **黑马点评项目** 中，如果要存储某个商户的 **点赞用户 ID 集合**，使用 HashSet 可以保证用户不会重复点赞。
- 在 **苍穹外卖项目** 中，可以用 HashSet 存储 **已支付订单号集合**，避免重复处理订单。

------

## 四、常见追问

1. HashSet 的初始容量和负载因子是多少？
   - 默认容量 16，负载因子 0.75。
2. 如果只重写 equals()，不重写 hashCode() 会怎样？
   - 可能导致两个对象内容相同但存储在不同桶里，Set 中出现重复。
3. HashSet 如何保证扩容时元素还能正确分布？
   - 扩容为原来的 2 倍，节点要么留在原位置，要么迁移到 index+oldCap。

------

✅ **一分钟口述版总结**
 HashSet 底层基于 HashMap，元素作为 key 存储，value 是常量。HashMap 的 key 唯一，所以 HashSet 不允许重复。判断重复时，先比较 hashCode，再比较 equals。如果 equals 相等则判定为重复，不会插入。

------

要不要我帮你整理一份 **HashSet / LinkedHashSet / TreeSet 的对比表**（底层实现、是否有序、是否允许 null、适用场景），方便你面试时一眼回答？