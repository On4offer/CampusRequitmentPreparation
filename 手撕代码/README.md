# 手撕代码（面试向）

本文件夹整理 **校招/社招面试** 中常见的 **Java 手撕代码** 和 **SQL 手写题**，便于集中练习和复习。  
**算法题**（链表、二叉树、DP、二分等）请到项目内其他文件夹单独学习。

---

## 文件说明

| 文件 | 内容 |
|------|------|
| [Java手撕代码题.md](./Java手撕代码题.md) | 单例、LRU、生产者-消费者、交替/顺序打印、手写 ArrayList/HashMap、死锁、wait/notify、**手写线程池、限流器（令牌桶/滑动窗口）、带过期缓存、公平/非公平锁** 等 |
| [Java手撕知识点.md](./Java手撕知识点.md) | 对应 Java 手撕题的**原理与考点**：volatile、DCL、Condition、LRU 原理、HashMap/ArrayList、死锁、线程池、限流算法、公平锁等 |
| [SQL手撕题.md](./SQL手撕题.md) | **基础题**（SELECT/WHERE/ORDER BY/LIMIT/DISTINCT/聚合/IN/LIKE/NULL/JOIN/CASE/子查询）、建表、排名/TopN、多表关联、行转列、连续登录、留存、中位数、累计求和、同环比 |
| [SQL手撕知识点.md](./SQL手撕知识点.md) | 对应 SQL 手撕题的**原理与考点**：SQL 执行顺序、JOIN、窗口函数、GROUP BY/HAVING、子查询、连续/留存、同环比等 |

---

## 最近几年常考方向（简要）

### Java 手撕
- **单例**：懒汉 DCL、静态内部类（必会）
- **并发**：生产者-消费者（阻塞队列 / wait-notify）、两线程交替打印、三线程顺序打印 ABC
- **数据结构**：手写 LRU（LinkedHashMap 或 链表+HashMap）、手写简单 ArrayList/HashMap
- **其他**：死锁示例、深拷贝、线程池核心逻辑

### SQL
- **排名**：第二高薪水、部门最高工资、row_number / rank / dense_rank、每科前 N 名
- **多表**：学生-课程-成绩-教师 四表关联、NOT IN / EXISTS
- **聚合**：GROUP BY、HAVING、COUNT/SUM/AVG
- **进阶**：行转列（CASE WHEN）、连续登录 N 天、次日留存、窗口函数
- **补充**：中位数、累计求和（如每月 GMV 累计）、同环比（LAG 环比/同比）

---

## 使用建议

1. **Java**：单例、LRU、生产者-消费者、交替打印 建议能闭卷写；ArrayList/HashMap 能讲清扩容与流程。
2. **SQL**：先练熟四表模型下的多表 JOIN 和分组聚合，再练窗口排名和连续/留存。
3. 算法题（链表、树、DP、二分、滑动窗口等）放在 **算法题** 专用文件夹，本目录不重复收录。
4. **可运行 demo**：本目录题目对应的可运行代码与更多题型（手写 Future、并发 LRU、Redis 锁、工厂/责任链等）见仓库 **demo/** 目录及 [demo/README.md](../demo/README.md)、[demo/DEMO覆盖审阅.md](../demo/DEMO覆盖审阅.md)。
