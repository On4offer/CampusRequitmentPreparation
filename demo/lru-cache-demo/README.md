# LRU 缓存 Demo（校招手撕高频）

两种实现：**LinkedHashMap 版**（面试可先说思路）与 **HashMap + 双向链表**（常要求手写）。

## 文件说明

| 文件 | 说明 |
|------|------|
| `LRUCacheLinkedHashMap.java` | 继承 LinkedHashMap，accessOrder=true，重写 removeEldestEntry。 |
| `LRUCacheHandWritten.java` | 手写：HashMap 存 key→Node，双向链表维护访问顺序，头插、删尾。 |

## 考点速记

- **为什么 HashMap**：O(1) 按 key 查找节点。
- **为什么双向链表**：O(1) 删除、移动节点（已知前驱后继）；单链表无法 O(1) 删当前节点。
- **LinkedHashMap accessOrder=true**：get 时会把节点移到队尾，再配合 removeEldestEntry 实现 LRU。

## 运行方式

```bash
cd demo/lru-cache-demo
javac -d . *.java
java lru_cache_demo.LRUCacheLinkedHashMap
java lru_cache_demo.LRUCacheHandWritten
```
