好的 ✅ 我来帮你把这个问题整理成 **面试题八股文风格答案**，包括 **概念 → 原理 → 使用场景 → 项目实践 → 标准回答模板 → 扩展追问**。

------

# 面试题

**Redis 常见的数据结构有哪些？底层原理是什么？**

------

## 1️⃣ 概念

Redis 提供了 **五大核心数据结构** 和一些 **高级扩展结构**：

- **String**（字符串）
- **Hash**（哈希表/字典）
- **List**（列表）
- **Set**（集合）
- **Sorted Set（ZSet）**（有序集合）
   扩展：Bitmap、HyperLogLog、Geo、Stream。

------

## 2️⃣ 底层原理

- **String**：底层是 **SDS（Simple Dynamic String）**，记录字符串长度，避免 C 风格字符串的 `\0` 遍历开销。
- **Hash**：小数据量时用 **压缩列表 ziplist**，大数据量时用 **哈希表 hashtable**。
- **List**：Redis 3.2 起用 **quicklist**（双向链表 + 压缩列表），既支持快速插入删除，又节省内存。
- **Set**：底层用 **整数数组 intset** 或 **哈希表 hashtable**，根据元素类型和数量动态切换。
- **Sorted Set (ZSet)**：底层由 **跳表 skiplist + 哈希表** 共同实现，保证范围查询和按分数排序的高效性。
- **Bitmap**：基于 **String 位运算** 实现。
- **HyperLogLog**：基于 **概率统计算法**，用极小空间近似统计基数。
- **Geo**：基于 ZSet 存储地理位置，经纬度编码为 geohash。
- **Stream**：类似消息队列，底层基于日志追加文件。

------

## 3️⃣ 使用场景

- **String**：缓存对象、计数器、分布式锁。
- **Hash**：存储对象（如用户信息）。
- **List**：消息队列、关注列表、最新消息。
- **Set**：去重、标签系统、共同好友。
- **ZSet**：排行榜、推荐系统（按分数排序）。
- **Bitmap**：用户签到、布隆过滤器底层。
- **HyperLogLog**：统计 UV（百万用户去重）。
- **Geo**：附近商户、打车距离计算。
- **Stream**：日志存储、消息队列。

------

## 4️⃣ 项目实践（黑马点评 / 苍穹外卖）

- **黑马点评**：
  - 用户签到 → Bitmap
  - UV 统计 → HyperLogLog
  - 附近商户 → Geo
  - 缓存店铺数据 → String/Hash
- **苍穹外卖**：
  - 秒杀库存预减 → String（原子操作）
  - 订单消息队列 → List / Stream

------

## 5️⃣ 面试标准回答模板

> Redis 提供了五大核心数据结构：String、Hash、List、Set 和 Sorted Set。
>
> - **String** 底层是 SDS，适合做缓存、计数器；
> - **Hash** 底层是 ziplist 或 hashtable，适合存储对象；
> - **List** 底层是 quicklist，常用于消息队列；
> - **Set** 基于 hashtable 或 intset，适合去重和集合运算；
> - **ZSet** 基于跳表和哈希表，适合排行榜和范围查询。
>    此外还有 Bitmap、HyperLogLog、Geo、Stream 等扩展结构，分别用于签到、UV 统计、附近商户和消息队列。
>    在项目中我用过 Bitmap 做用户签到、用 HyperLogLog 统计 UV、用 Geo 实现附近商户功能。

------

## 6️⃣ 扩展追问

- Redis 为什么用 **跳表** 而不是红黑树？
- HyperLogLog 为什么能用 12KB 统计上亿 UV？
- List 改成 quicklist 的优势是什么？
- Hash 在小数据量时为什么不用 hashtable 而用 ziplist？
- 如果让你设计一个“排行榜+分页”，ZSet 怎么实现？

------

要不要我帮你把这个问题写成 **简历面试自述版（2-3分钟口述答案）**，你在面试时可以直接背？