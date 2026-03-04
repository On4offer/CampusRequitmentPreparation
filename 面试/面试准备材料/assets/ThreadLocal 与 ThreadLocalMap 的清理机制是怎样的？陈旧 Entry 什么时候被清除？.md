好的，这题考的是你对 **弱引用 + 懒清理策略**是否吃透。给你一份能在面试里直接复述的标准答案。

------

## ✅ 面试题：ThreadLocal 与 ThreadLocalMap 的清理机制是怎样的？陈旧 Entry 什么时候被清除？

### 一、先说定义

- **Entry 结构**：`Entry = (WeakReference<ThreadLocal<?>> key, Object value)`
- **陈旧 Entry（stale entry）**：当 `ThreadLocal` 被 GC 回收后，`key == null`、但 `value` 仍被强引用挂在表里，这个槽就是陈旧 Entry。

------

### 二、清理触发点（都是“懒清理”）

1. **get(tl)**
   - 查找过程中若遇到 `key == null` 的槽，**立即触发清理**（`expungeStaleEntry`），顺带修复线性探测链。
   - 命中后返回 `value`；未命中走 `getEntryAfterMiss`，这一步也可能清理。
2. **set(tl, value)**
   - 寻址时若遇到陈旧槽位，会调用 **`replaceStaleEntry`**：把当前 `tl` 写入并**向前/向后清一次“脏链”**。
   - 插入新 Entry 后会尝试 **`cleanSomeSlots`**（按探测步数做部分清洁），如果仍然“脏”，并且达到阈值，会 **rehash**，rehash 前后都会清理一批陈旧条目。
3. **remove(tl)**
   - 定位到 `tl` 对应槽位，置空并 **立即 `expungeStaleEntry`** 连带清理后续探测链上的陈旧条目。
   - 这是业务侧**最快、最可靠**的清理方式（强烈推荐 `try/finally` 调用）。
4. **线程结束**
   - `ThreadLocalMap` 挂在 `Thread` 身上；**线程终止**时，整张表随线程一起被 GC 回收，残留 value 也会被释放。

------

### 三、为什么是“懒清理”？

- `ThreadLocalMap` 不是全局结构，只服务单个线程，且条目通常很少。
- 为减少额外开销，不做周期性扫描；而是**在 get/set/remove 时顺路清**，用开放寻址的局部遍历完成清理。

------

### 四、陈旧 Entry 具体“什么时候被清除”？

- **GC 把 key 回收** ➜ 并不会立刻清 value；
- **下一次对该 Map 的任何访问**（`get/set/remove`）命中或经过该槽位时：
  - 命中或探测到 **`key == null`** ➜ 立刻调用 `expungeStaleEntry / replaceStaleEntry / cleanSomeSlots` 清掉它；
  - 插入后触发的 **`cleanSomeSlots`** 会按步数做**局部清理**；
  - **`rehash`**（触发于 size ≥ 阈值）会**成批清理**。
- **若线程长期不再访问该 Map 且线程长寿（线程池线程）** ➜ 可能长期残留，形成内存占用风险。

------

### 五、面试“标准作答”一句话版

> ThreadLocal 的 key 是弱引用，key 被 GC 回收后会形成 **stale entry**。ThreadLocalMap 采用**懒清理**：在 `get/set/remove` 时，遇到 `key == null` 的槽会通过 `expungeStaleEntry/replaceStaleEntry/cleanSomeSlots` 立即清理；插入达到阈值时还会 `rehash` 批量清。业务侧应在使用完毕后 **显式 `remove()`**，尤其在线程池中，避免 value 残留造成内存泄漏；线程结束也会整体释放。