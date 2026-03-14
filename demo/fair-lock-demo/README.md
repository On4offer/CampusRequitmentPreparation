# 公平锁 vs 非公平锁 Demo

理解 ReentrantLock(true/false) 的区别，校招口述即可。

## 文件说明

| 文件 | 说明 |
|------|------|
| `FairLockDemo.java` | 演示非公平锁与公平锁的创建与使用方式。 |

## 考点速记

- **非公平**：lock() 时先 CAS 抢一次，抢到直接执行，吞吐高，可能饥饿。
- **公平**：严格 FIFO，新线程直接入队，避免饥饿，吞吐一般更低。
- **AQS**：ReentrantLock 内部用 AQS，state 表示重入次数，等待队列 FIFO。

## 运行方式

```bash
cd demo/fair-lock-demo
javac -d . *.java
java fair_lock_demo.FairLockDemo
```
