# Comparable 与 Comparator Demo（口述/集合排序）

技术栈集合框架 + 面试常问：自然排序（Comparable）与比较器（Comparator）区别与用法。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ComparableComparatorDemo.java` | 类实现 Comparable 按年龄排序；用 Comparator 按名字排序。 |

## 考点速记

- **Comparable**：类实现 compareTo，定义“自然顺序”；TreeSet/TreeMap、Collections.sort(list) 会用到。
- **Comparator**：独立比较器，可多种排序方式；Comparator.comparing、thenComparing 常用。
- **区别**：Comparable 内聚在类里一种顺序；Comparator 外部、可多种顺序。

## 运行方式

```bash
cd demo/comparable-comparator-demo
javac -d . *.java
java comparable_comparator_demo.ComparableComparatorDemo
```
