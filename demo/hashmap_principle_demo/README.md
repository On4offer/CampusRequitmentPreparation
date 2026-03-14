# HashMap 原理 Demo

HashMap 结构、hash 计算、下标、put 流程、扩容与树化阈值。校招常考“讲一下 put 过程”“为什么用 (n-1)&hash”“什么时候转红黑树”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `HashMapPrincipleDemo.java` | 演示 hash 计算、下标计算、容量 2 的幂、扩容后位置规律；不实现完整 HashMap，仅原理演示。 |

## 考点速记

- **结构**：数组 + 链表；链表长度 ≥ 8 且 table 长度 ≥ 64 时转红黑树。
- **下标**：index = (n - 1) & hash，n 为 2 的幂时等价于 hash % n，位运算更快。
- **hash**：h ^ (h >>> 16) 高 16 位参与运算，减少碰撞。
- **扩容**：负载因子 0.75，扩为 2 倍；节点要么留在原下标，要么移到原下标 + oldCap。

## 运行方式

```bash
cd demo/hashmap_principle_demo
javac -d . *.java
java hashmap_principle_demo.HashMapPrincipleDemo
```
