# 生产者-消费者（Lock + Condition / 阻塞队列）Demo

手写有界阻塞队列，使用 **ReentrantLock + Condition** 实现 put/take 的阻塞与唤醒。校招常考手撕。

## 文件说明

| 文件 | 说明 |
|------|------|
| `BlockingQueueDemo.java` | 手写 BlockingQueue：put 满则 await，take 空则 await；使用 while 判断条件。 |

## 考点速记

- **为什么用 while 而不是 if**：虚假唤醒时，被唤醒后条件可能仍不满足，用 while 会再次检查，否则可能越界或空指针。
- **Condition 与 wait/notify**：一个 Lock 可绑多个 Condition（notFull、notEmpty），唤醒更精确；wait/notify 只有一个等待队列。

## 运行方式

```bash
cd demo/producer-consumer-blockingqueue-demo
javac -d . *.java
java producer_consumer_blockingqueue_demo.BlockingQueueDemo
```

预期：生产 0~5 与消费 0~5 交替出现（顺序可能因调度略有不同）。
