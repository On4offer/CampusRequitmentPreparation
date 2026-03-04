好 👍
 这道题是考察 **集合类的历史演进**，我帮你整理成 **面试答题模板**。

------

# 📌 面试题：ArrayList 与 Vector 的区别？为什么 Vector 已经被淘汰？

## 一、核心回答

1. **底层结构**
   - 两者底层都是 **动态数组**，支持随机访问，扩容时都是按 **1.5 倍或 2 倍** 增长。
2. **线程安全**
   - **ArrayList**：线程不安全，性能高。
   - **Vector**：线程安全（方法都用 `synchronized` 修饰），性能差。
3. **扩容机制**
   - ArrayList：默认扩容 1.5 倍（JDK1.8）。
   - Vector：默认扩容为 2 倍。
4. **历史原因**
   - Vector 出现较早（JDK1.0），那时并发方案不成熟。
   - JDK1.2 引入 `ArrayList`，并在 JUC 包里提供了 `CopyOnWriteArrayList` 等更优方案。

------

## 二、为什么 Vector 被淘汰？

1. **同步方式粗糙**
   - Vector 直接在方法级别加锁（synchronized），即使是读操作也要加锁，开销大。
2. **扩展性差**
   - 无法灵活应对高并发场景。
   - JUC 包提供了更高效的并发容器（如 `CopyOnWriteArrayList`）。
3. **逐渐被替代**
   - 单线程/读多写少场景 → 用 ArrayList。
   - 多线程并发场景 → 用 CopyOnWriteArrayList。
   - 因此 Vector 几乎不再使用，只是出于兼容性仍保留在 JDK 中。

------

## 三、项目场景举例

- 在 **黑马点评项目** 中，如果需要存储商户评论列表：
  - 单线程场景用 ArrayList（性能更好）。
  - 多线程场景用 CopyOnWriteArrayList。
  - 不会使用 Vector。
- 在 **苍穹外卖项目** 中，如果维护用户登录会话列表：
  - 多线程环境下也会用并发集合，而不是 Vector。

------

## 四、常见追问

1. **Vector 为什么线程安全但性能差？**
   - 因为方法级锁，锁粒度太大，频繁竞争。
2. **Vector 和 CopyOnWriteArrayList 的区别？**
   - Vector 用 synchronized 锁整个方法；CopyOnWriteArrayList 采用写时复制，读无锁，适合读多写少场景。
3. **现在项目中什么时候还会用 Vector？**
   - 基本不会用，只存在于遗留代码或需要兼容老版本 API 的场景。

------

✅ **一分钟口述版总结**
 ArrayList 和 Vector 底层都是动态数组，但 ArrayList 线程不安全，性能更好；Vector 线程安全但性能差，因为方法全加 synchronized。随着 JUC 包提供更优的并发集合，Vector 已被淘汰，实际开发几乎不用。

------

要不要我帮你把 **ArrayList / Vector / CopyOnWriteArrayList 的区别**做成一个对比表格？这样一眼就能看出进化路径。