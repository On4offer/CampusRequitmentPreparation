# Java 集合框架 Demo

List / Set / Map 常用用法与选型。校招常考“ArrayList 和 LinkedList 区别”“HashMap 和 TreeMap 区别”“Set 如何去重”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `CollectionFrameworkDemo.java` | List（ArrayList/LinkedList）、Set（HashSet/TreeSet）、Map（HashMap）基本用法与选型示例。 |

## 考点速记

- **ArrayList vs LinkedList**：ArrayList 数组实现，随机访问 O(1)、尾插 O(1) 均摊；LinkedList 链表，头插/删 O(1)，随机访问 O(n)。
- **HashSet**：基于 HashMap，元素为 key，value 为 PRESENT；去重依赖 equals/hashCode。
- **HashMap vs TreeMap**：HashMap 无序 O(1) 查找；TreeMap 红黑树有序，O(log n) 查找，可传入 Comparator。

## 运行方式

```bash
cd demo/collection_framework_demo
javac -d . *.java
java collection_framework_demo.CollectionFrameworkDemo
```
