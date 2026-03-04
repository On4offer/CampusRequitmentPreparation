**Answer:**

`ThreadLocal` 的内存泄漏是 Java 并发里一个经典问题，理解它要从 **底层存储结构** 入手。

------

### 1. ThreadLocal 的底层原理

- 每个线程 `Thread` 内部都维护了一个 **ThreadLocalMap**。
- 这个 Map 的 **key** 是 `ThreadLocal` 对象（弱引用 `WeakReference<ThreadLocal<?>>`），**value** 是真正存储的数据。
- 结构大致如下：

```
Thread
 └── ThreadLocalMap (属于线程)
       ├── Entry[0] : (WeakReference<ThreadLocalA>, valueA)
       ├── Entry[1] : (WeakReference<ThreadLocalB>, valueB)
       └── ...
```

------

### 2. 内存泄漏的成因

1. **弱引用的特性**
   - `ThreadLocal` 对象作为 key，是 **弱引用**。
   - 如果外部没有强引用指向这个 `ThreadLocal`，它会被 GC 回收。
2. **value 没有被清理**
   - 即使 key（ThreadLocal）被回收了，`value` 仍然被线程持有（存在于 ThreadLocalMap 的 Entry 中）。
   - 由于这个 `value` 和当前线程绑死，只要线程还活着，`value` 就不能被 GC 回收。
   - 特别是在线程池中，线程会被复用，导致 **value 永久滞留在内存**，这就是泄漏。

------

### 3. 泄漏示意图

```
ThreadLocalMap:
   [ WeakReference<null>, valueX ]
              ↑
     key 已经被 GC 回收
     valueX 仍然存活 → 泄漏
```

------

### 4. 典型场景

- **线程池**：
  - 线程长时间存在，ThreadLocal 的 key 被 GC 掉后，value 却一直留在内存里。
- **Web 容器 (Tomcat)**：
  - 使用 ThreadLocal 存储用户会话或大对象，没有手动清理。
  - 因为线程复用，可能出现数据串用甚至 OOM。

------

### 5. 解决方法 / 最佳实践

1. **手动清理**

   - 用完 ThreadLocal 后，调用 `remove()` 清理当前线程绑定的值。

   ```java
   ThreadLocal<MyObj> local = new ThreadLocal<>();
   try {
       local.set(new MyObj());
       // 使用 local.get()
   } finally {
       local.remove();  // 清理，防止泄漏
   }
   ```

2. **避免存放大对象**

   - 如果必须用 ThreadLocal，尽量存储轻量级对象，降低泄漏风险。

3. **封装 ThreadLocal**

   - 自己写工具类，统一管理 `set/get/remove`，避免忘记清理。

------

### 6. 总结

- **根因**：ThreadLocal 的 key 是弱引用，回收后 value 还被线程持有 → 内存泄漏。
- **风险场景**：线程池、Web 容器。
- **解决办法**：用完 `remove()`，养成良好习惯。

------

💡一句话总结：

> **ThreadLocal 的泄漏不是因为 key 弱引用，而是 value 和线程生命周期绑死，导致 key 被 GC 了但 value 还残留。**

------

要不要我给你画一张 **ThreadLocalMap 的生命周期图**（从 set → key 回收 → value 残留 → remove 清理），直观展示泄漏过程？