好的 👍 这一题是面试官常考的 **源码细节题**，考察你对 ThreadLocalMap 设计的理解。下面给你一份完整的答题模板。

------

## ✅ 面试题：ThreadLocalMap 是怎么解决哈希冲突的？为什么不用链表？

### 一、ThreadLocalMap 的冲突解决方式

1. **底层结构**：

   - ThreadLocalMap 是一个数组（Entry[]），每个元素存储一个键值对：
      `Entry(WeakReference<ThreadLocal<?>> key, Object value)`
   - 它不是标准的 HashMap，而是一个 **定制化的简化版哈希表**。

2. **定位规则**：

   - 通过 ThreadLocal 的 **threadLocalHashCode**（自增的散列值）计算索引：

     ```java
     int i = key.threadLocalHashCode & (table.length - 1);
     ```

3. **冲突解决**：

   - 采用 **开放寻址法（线性探测）**：
     - 如果当前位置已有 Entry，就向后探测下一个位置，直到找到空槽或 key 相等的槽。
     - 删除时采用清理机制（expungeStaleEntry），避免“探测链断裂”。

------

### 二、为什么不用链表？

1. **性能考虑**
   - ThreadLocalMap 每个线程通常只存少量数据（几到几十个 ThreadLocal）。
   - 线性探测比链表查询更快（数组访问 + 局部性好）。
   - 避免了链表节点额外的对象开销（Node 包装），节省内存。
2. **简化实现**
   - ThreadLocalMap 是专用 Map，功能单一，不追求通用性。
   - 不需要像 HashMap 那样考虑大规模扩容、红黑树优化。
3. **垃圾清理机制**
   - ThreadLocalMap 需要及时清理 key=null 的陈旧 Entry。
   - 用链表会导致清理逻辑复杂化，开放寻址更容易在 set/get 时顺带清理。

------

### 三、标准回答（面试模板）

> ThreadLocalMap 解决哈希冲突采用的是 **开放寻址法（线性探测）**，即当一个位置被占用时，会顺序探测下一个空槽来存储。
>  它没有使用 HashMap 的链表结构，是因为 ThreadLocalMap 只为 ThreadLocal 服务，每个线程存的键值对很少，用线性探测能减少对象开销并提高访问的缓存局部性。而且线性探测结合清理机制，更方便及时清除 key 被 GC 回收后的陈旧条目。

------

要不要我帮你把 **开放寻址 + 链表法的对比表格**也整理一下？这样在面试里更容易答得有层次感。