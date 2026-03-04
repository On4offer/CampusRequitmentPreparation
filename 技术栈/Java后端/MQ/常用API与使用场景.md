# 📌 MQ 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**消息模型、Spring 整合与场景**，便于速查与上手。具体 MQ（Kafka/RabbitMQ/RocketMQ）以各自官方文档与 Starter 为准。

---

## 一、消息模型与概念速查

### 1.1 角色与术语

| 概念 | 说明 |
|------|------|
| **Producer** | 生产者，发送消息 |
| **Consumer** | 消费者，订阅并处理消息 |
| **Broker** | 服务端，存储与转发 |
| **Topic** | 主题（Kafka/RocketMQ），逻辑分类 |
| **Queue** | 队列（RabbitMQ），或 Topic 下的子队列（RocketMQ） |
| **Partition** | 分区（Kafka），并行与顺序单位 |
| **Consumer Group** | 消费组，同组内负载均衡消费 |
| **Offset** | 消费位移，标记消费进度 |

### 1.2 投递语义

| 语义 | 说明 | 常用做法 |
|------|------|----------|
| **At most once** | 最多一次，可能丢 | 一般不采用 |
| **At least once** | 至少一次，可能重复 | 常用 + 消费端幂等 |
| **Exactly once** | 精确一次 | Kafka 事务等，实现复杂 |

---

## 二、Spring Boot 整合要点（通用）

### 2.1 RabbitMQ（Spring AMQP）

- **依赖**：`spring-boot-starter-amqp`
- **配置**：`spring.rabbitmq.host/port/username/password`；可选 virtual-host、publisher-confirm-type
- **发送**：注入 **RabbitTemplate**，`convertAndSend(exchange, routingKey, message)` 或指定 MessageProperties
- **消费**：**@RabbitListener(queues = "队列名")** 标注方法，参数为消息体或 Message；**手动 Ack** 时设置 `ackMode = MANUAL` 并在方法内 channel.basicAck
- **声明队列/交换机**：**@Bean** 声明 **Queue、DirectExchange/TopicExchange、Binding**，或用 **RabbitAdmin** 自动声明

### 2.2 RocketMQ

- **依赖**：`rocketmq-spring-boot-starter`
- **配置**：`rocketmq.name-server`；Producer 组名等
- **发送**：**RocketMQTemplate**，`syncSend(topic, body)`、`asyncSend`、`sendOneWay`；**延时**：`syncSend(topic, body, timeout, delayLevel)`
- **消费**：**@RocketMQMessageListener**(topic, consumerGroup) 标注类，实现 **RocketMQListener&lt;String&gt;** 的 onMessage；**顺序**：consumeMode=ORDERLY

### 2.3 Kafka

- **依赖**：`spring-kafka` 或 `spring-boot-starter-kafka`
- **配置**：`spring.kafka.bootstrap-servers`；producer/consumer 的 key-serializer、value-serializer、acks 等
- **发送**：**KafkaTemplate**，`send(topic, data)` 或 `send(topic, key, data)`
- **消费**：**@KafkaListener(topics = "xxx", groupId = "yyy")** 标注方法，参数为消息体或 ConsumerRecord

---

## 三、可靠性要点速查

| 环节 | 做法 |
|------|------|
| **生产不丢** | 开启 Broker 确认（Confirm/acks）、重试、重要消息可先落库再发 MQ |
| **Broker 不丢** | 持久化、多副本、同步刷盘（按场景权衡） |
| **消费不丢** | 业务处理成功后再 Ack/提交 Offset；异常时 Nack 或重试 |
| **不重复** | 消费端幂等：业务唯一 ID + 去重表或状态机 |
| **顺序** | 同 key 路由同分区/队列；消费端单线程或局部有序 |

---

## 四、使用场景对照

| 场景 | 推荐做法 |
|------|----------|
| **解耦** | 订单服务发 MQ，库存/积分/短信等各自订阅，互不影响 |
| **异步** | 写库成功后发 MQ 再返回，消费者异步发短信/写日志 |
| **削峰** | 秒杀请求先入 MQ，消费者按能力拉取，保护 DB |
| **订单超时关单** | RocketMQ 延时消息或 RabbitMQ TTL+DLQ，到点消费关单 |
| **日志/流处理** | Kafka 高吞吐、持久化、多消费者组复用 |
| **复杂路由** | RabbitMQ 多 Exchange 类型（Direct/Topic/Fanout） |
| **事务最终一致** | RocketMQ 事务消息：半消息 → 本地事务 → 提交/回滚 + 回查 |

---

## 五、常见问题排查

| 现象 | 可能原因 | 处理思路 |
|------|----------|----------|
| 连接失败 | 地址、端口、账号、网络 | 检查配置与防火墙、Broker 状态 |
| 消息堆积 | 消费慢、消费者少、下游阻塞 | 扩容消费者、提高并发、排查慢逻辑与死锁 |
| 重复消费 | 重试、Rebalance、先 Ack 后处理 | 消费端幂等、处理完再 Ack |
| 顺序错乱 | 多分区/多消费者并发 | 同 key 同分区、顺序消费或接受局部有序 |
| 消息丢失 | 未确认、未持久化、先 Ack | 确认机制、持久化、业务成功后再 Ack |

---

## 六、与学习笔记的对应关系

- **概念与选型** → 第 1 章；**模型与机制** → 第 2、3 章；**Kafka/RabbitMQ/RocketMQ** → 第 4～6 章；**可靠性** → 第 7 章；**高可用与优化** → 第 8 章；**实战与面试** → 第 9、10 章及附录。

> 更多原理与面试题见《学习笔记》相应章节。各 MQ 的详细 API 以官方文档与对应 Starter 为准。
