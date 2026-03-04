好 👍
 这道题是 **Java 基础高频面试题**，我给你整理成 **面试答题模板**。

------

# 📌 面试题：Java 中 equals() 和 == 的区别？hashCode() 有什么作用？

## 一、核心回答

1. **== 的作用**
   - 对于基本数据类型：比较的是 **值** 是否相等。
   - 对于引用数据类型：比较的是 **内存地址** 是否相同（是否指向同一个对象）。
2. **equals() 的作用**
   - 默认继承自 `Object` 类，底层实现还是 `==`，比较的是地址。
   - 一般会被类重写，用来比较 **对象的内容是否相等**（如 String、Integer、集合类）。
3. **hashCode() 的作用**
   - 返回对象的哈希值（int 类型）。
   - 在集合框架（如 `HashMap`、`HashSet`）中，`hashCode()` 用来确定对象存放的位置，提升查找效率。
   - **约定**：如果两个对象 `equals()` 相等，那么它们的 `hashCode()` 必须相等；但 hashCode 相等，不一定 equals 相等（哈希冲突）。

------

## 二、扩展回答

- **为什么要同时重写 equals() 和 hashCode()?**
  - 只重写 equals()：可能导致两个相等的对象存储在 HashSet 中却重复存在。
  - 只重写 hashCode()：可能导致两个对象 hash 相同但 equals 不同，出现逻辑错误。
  - 正确做法：同时重写，保证一致性。
- **典型案例：String**
  - `String` 类重写了 equals() 和 hashCode()：
    - equals() 比较字符串内容。
    - hashCode() 通过内容计算。
  - 所以 `"abc".equals(new String("abc")) == true`，并且它们的 hashCode() 相同。

------

## 三、项目场景举例

- 在 **黑马点评项目** 中：
  - 商户缓存的 key 通常是 `Long id`，如果用对象作为 key（比如 Shop 对象），必须重写 equals 和 hashCode，否则可能出现查不到缓存的情况。
- 在 **苍穹外卖项目** 中：
  - 如果用 `Set<Order>` 去重订单，需要保证 `Order` 类正确重写 equals 和 hashCode，否则相同订单可能被当作不同对象存两份。

------

## 四、常见追问

1. 为什么 hashCode() 相等，equals() 不一定相等？
   - 因为可能发生哈希冲突。
2. HashMap 在 put 时如何用 equals 和 hashCode？
   - 先用 hashCode 定位桶，再用 equals 判断是否为同一对象。
3. String 为什么适合作为 HashMap 的 key？
   - 因为 String 重写了 equals 和 hashCode，且是不可变类。

------

✅ **一分钟口述版总结**
 在 Java 中，`==` 比较基本类型值或对象地址，`equals()` 一般用来比较对象内容。`hashCode()` 决定对象在哈希结构中的位置。必须同时重写 equals 和 hashCode，才能保证在集合中行为正确。

------

要不要我帮你把 **equals() 和 hashCode() 在 HashMap 中的执行流程图**画出来？这样更直观地展示 put/get 的过程。