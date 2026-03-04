这道追问在面试里很常见，回答的时候最好从 **项目背景、技术权衡、场景适配** 三个角度来讲，既显得你考虑全面，又能突出“选择 Redis Stream 是有根据的”。

------

## 🎯 标准面试回答

在黑马点评的秒杀优化中，我们没有选择 RabbitMQ/Kafka，而是用 **Redis Stream** 来做消息队列，主要原因有三点：

1. **已有技术栈考虑**
   - 项目已经在用 Redis 做缓存和库存预减，如果再引入 RabbitMQ/Kafka，就需要额外部署、学习、运维。
   - Redis Stream 是原生 Redis 功能，可以直接复用，降低系统复杂度。
2. **场景特点**
   - 我们的消息量级主要集中在秒杀场景，单机 Redis 就能承载高并发写入。
   - Kafka 更适合百万级 TPS、日志采集、流计算等大数据场景，而我们的需求并不需要这么重量级。
3. **功能适配性**
   - Redis Stream 本身支持 **持久化、消费组、消息确认、Pending List**，已经满足“削峰填谷、异步落库、防止丢单”的需求。
   - RabbitMQ 的事务、Kafka 的分区副本机制确实更强大，但对这个秒杀场景来说是“过度设计”。

------

## ✅ 面试扩展追问（你也要准备好）

- **Q1：如果消息量更大，Redis Stream 能扛住吗？**
   → 单机 Redis 有瓶颈，可以扩展 Redis Cluster 或切换到 Kafka 做日志型高吞吐场景。
- **Q2：Redis Stream 和 RabbitMQ 的可靠性有差别吗？**
   → RabbitMQ/Kafka 在消息可靠投递、事务一致性方面更完善，而 Redis Stream 主要靠持久化 + XACK + Pending List 来保证。
- **Q3：如果公司要求引入专业 MQ 怎么办？**
   → 可以替换为 RabbitMQ/Kafka，只需修改订单写入和消费模块，整体架构不变。

------

👉 这样回答就能体现出：**不是你不知道 RabbitMQ/Kafka，而是根据项目场景和性价比选择了 Redis Stream**。

要不要我帮你把这个问题也扩展成一份 **对比表格（Redis Stream vs RabbitMQ vs Kafka）**，方便你面试的时候一目了然？