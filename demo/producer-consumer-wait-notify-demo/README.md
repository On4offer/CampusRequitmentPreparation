# 生产者-消费者（wait/notify）Demo

使用 **synchronized + wait/notify** 实现有界队列的生产者-消费者。校招口述或手撕都可能考。

## 文件说明

| 文件 | 说明 |
|------|------|
| `WaitNotifyProducerConsumer.java` | 共享队列 + lock.wait() / lock.notifyAll()，条件判断用 while。 |

## 考点速记

- **wait/notify 必须在 synchronized 块内**：wait 会释放锁，被唤醒后需重新竞争锁；没有“当前持有锁”的前提无法正确释放与唤醒。
- **wait 与 sleep**：wait 是 Object 方法、释放锁；sleep 是 Thread 方法、不释放锁。

## 运行方式

```bash
cd demo/producer-consumer-wait-notify-demo
javac -d . *.java
java producer_consumer_wait_notify_demo.WaitNotifyProducerConsumer
```

运行约 2 秒后按 Ctrl+C 或自动结束（示例中 2 秒后 interrupt）。
