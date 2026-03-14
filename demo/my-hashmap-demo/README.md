# 手写简易 HashMap Demo

数组+链表实现 put/get、hash、扩容。校招常考“讲清 put 流程与扩容”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `MyHashMap.java` | hash = key.hashCode() ^ (hashCode>>>16)；index = (n-1)&hash；负载因子 0.75 扩容 2 倍。 |

## 考点速记

- **容量 2 的幂**：(n-1)&hash 等价于 hash%n，位运算更快；扩容时节点要么原位置要么原位置+oldCap。
- **高 16 位异或**：减少碰撞。
- **负载因子 0.75**：空间与时间折中。

## 运行方式

```bash
cd demo/my-hashmap-demo
javac -d . *.java
java my_hashmap_demo.MyHashMap
```
