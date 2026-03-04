好 👍，这题考察的是 **并发编程的核心**，AQS（AbstractQueuedSynchronizer）是 `ReentrantLock`、`CountDownLatch`、`Semaphore` 等的底层核心。下面我给你一个面试模板。

------

# 🎯 面试题

**AQS 是什么？底层如何实现锁和同步器？**

------

## ✅ 标准回答

1. **AQS 是什么**

- AQS 全称 **AbstractQueuedSynchronizer（抽象队列同步器）**，是 **JUC 提供的锁和同步器的框架基类**。
- 通过一个 **volatile int state（整型变量）** 表示同步状态，配合 **FIFO 等待队列（CLH 队列）** 来管理线程竞争。
- 核心思想：**如果获取资源成功 → 执行；获取失败 → 进入队列阻塞，等待唤醒**。

------

## ⚙️ 底层实现

1. **state 表示资源**
   - 0 → 未锁定，1 → 已锁定（独占模式）。
   - 对 state 的操作依赖 CAS（compareAndSwap）。
2. **队列（CLH 双向队列）**
   - 获取锁失败的线程，会被封装为 `Node` 加入等待队列。
   - 队列采用 **自旋 + CAS**，保证并发安全。
3. **阻塞与唤醒**
   - 线程阻塞：`LockSupport.park()`。
   - 线程唤醒：`LockSupport.unpark()`。
   - 避免了传统 `wait/notify` 的易用性问题。
4. **两种模式**
   - **独占模式**（Exclusive）：如 `ReentrantLock`。一个线程占有资源，其他线程必须等待。
   - **共享模式**（Shared）：如 `Semaphore`、`CountDownLatch`。多个线程可以同时访问资源。

------

## 📌 使用场景（常见同步器基于 AQS）

- **ReentrantLock**：独占锁，支持公平/非公平。
- **CountDownLatch**：共享锁，计数减到 0 时释放所有等待线程。
- **Semaphore**：共享锁，限制并发线程数。
- **CyclicBarrier**：基于 `ReentrantLock` + `Condition` 实现的栅栏。

👉 在黑马点评项目里：

- `CountDownLatch` 用于 **缓存预热**（多个线程加载完毕再统一开放）。
- `ReentrantLock` 用于 **防止缓存击穿**。
- `Semaphore` 可以限制 **秒杀接口的并发请求数**。

------

## ⚠️ 易错点

- AQS 本身不是锁，而是 **提供锁的实现框架**。
- 必须继承 AQS 并重写 `tryAcquire/tryRelease` 等方法才能实现自定义同步器。
- 如果唤醒逻辑实现不当，容易出现死锁/线程饥饿。

------

## 🔍 追问

1. **AQS 和 synchronized 的区别？**
    👉 synchronized 由 JVM 实现；AQS 是 JDK 实现的框架，基于 CAS + 队列。
2. **AQS 为什么用 CLH 队列？**
    👉 CLH 是 FIFO 队列，保证公平性，且自旋节点只关注前驱节点，减少竞争。
3. **独占锁和共享锁在 AQS 中如何区分？**
    👉 AQS 提供了两套模板方法：`tryAcquire/tryRelease`（独占）、`tryAcquireShared/tryReleaseShared`（共享）。

------

要不要我帮你写一个 **“10 秒速背版”**，让你面试时可以秒答？