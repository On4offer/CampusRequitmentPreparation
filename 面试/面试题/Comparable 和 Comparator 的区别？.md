好，这个问题在 **集合与排序** 里非常高频，我来整理一份 **面试答题模板**：

------

# 📌 面试题：Comparable 和 Comparator 的区别？在什么场景下使用？

## 一、核心回答

1. **Comparable 接口**
   - **定义**：对象内部比较规则接口（`java.lang.Comparable`）。
   - **方法**：`int compareTo(T o)`。
   - **特点**：类自身实现，属于 **自然排序**。
   - **示例**：`String`、`Integer` 已经实现 Comparable，支持直接排序。
2. **Comparator 接口**
   - **定义**：外部比较器接口（`java.util.Comparator`）。
   - **方法**：`int compare(T o1, T o2)`。
   - **特点**：类外部实现，属于 **定制排序**，可以定义多种比较规则。
   - **示例**：给 `User` 按年龄或按注册时间排序。
3. **区别总结**
   - Comparable：类 **自身定义排序规则**（一个类只能有一种自然顺序）。
   - Comparator：类 **外部定义排序规则**（可以有多种不同的比较器）。

------

## 二、使用场景

- **Comparable**
  - 当类的排序规则是**固定的、唯一的**，适合在类内部实现。
  - 例如：`Student` 类按学号排序。
- **Comparator**
  - 当类的排序规则是**多样的**，不方便写死在类中，适合用外部比较器。
  - 例如：`Student` 可以按 **成绩**、**年龄**、**姓名** 分别排序。
  - 在 `Collections.sort(list, comparator)` 或 `TreeSet/TreeMap` 构造方法中常用。

------

## 三、项目场景举例

- 在 **黑马点评项目** 中：
  - 如果用户类 User 按 id 排序，可以实现 Comparable。
  - 如果要在“达人榜单”中按 **粉丝数排序**，用 Comparator 更灵活。
- 在 **苍穹外卖项目** 中：
  - 菜品可以默认按 id（Comparable），
  - 但活动页面可能需要按销量、评分、上架时间不同维度排序（Comparator）。

------

## 四、常见追问

1. **一个类能同时用 Comparable 和 Comparator 吗？**

   - 可以，Comparable 定义自然顺序，Comparator 提供额外定制顺序。

2. **Comparator 如何写多个排序条件？**

   - 可以用链式比较，例如：

     ```java
     Comparator<User> cmp = Comparator
         .comparing(User::getAge)
         .thenComparing(User::getName);
     ```

3. **为什么推荐 Comparator？**

   - 避免把排序逻辑写死在实体类中，解耦更好。

------

✅ **一分钟口述版总结**
 Comparable 是对象自身的比较接口，定义自然排序（如 String、Integer）；Comparator 是外部比较器，可以定义多种排序规则。一般情况下，固定唯一的顺序用 Comparable，多样化排序规则用 Comparator。

------

要不要我帮你整理一个 **“Comparable vs Comparator 对照表”**（用表格把区别和应用场景一眼展示），方便你快速记忆？