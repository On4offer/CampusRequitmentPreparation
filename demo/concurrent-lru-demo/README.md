# 线程安全 LRU 缓存 Demo（并发版）

在「HashMap + 双向链表」LRU 基础上加锁，支持多线程并发 get/put。大厂可能考「LRU 的并发版本」或「读写锁应用」。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ConcurrentLRUCache.java` | 使用 ConcurrentHashMap + ReentrantReadWriteLock；get 提供「先读锁再写锁移动」与「全程写锁」两种写法；put 全程写锁。 |

## 考点速记

- **为什么用读写锁**：get 多写少时，读锁可并发，写锁独占；避免 synchronized 全互斥。
- **get 中 moveToHead**：移动节点会改链表，必须用写锁；先读锁查是否存在，再升级写锁移动，可减少写锁竞争（本实现已包含；getSimple 为简化版全程写锁）。
- **ConcurrentHashMap**：与读写锁配合，map 本身并发安全，锁只保护链表操作与容量语义。
- **其他思路**：分段锁（按 key 哈希分段）、ConcurrentLinkedHashMap 等库。

## 运行方式

```bash
cd demo/concurrent-lru-demo
javac -d . *.java
java concurrent_lru_demo.ConcurrentLRUCache
```

预期：与普通 LRU 一致，2 被淘汰，输出 null、a、c。
