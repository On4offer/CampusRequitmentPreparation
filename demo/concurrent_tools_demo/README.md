# 并发工具类详解：CountDownLatch、CyclicBarrier、Semaphore

## 📚 目录

- [概述](#概述)
- [CountDownLatch](#countdownlatch)
- [CyclicBarrier](#cyclicbarrier)
- [Semaphore](#semaphore)
- [三者对比](#三者对比)
- [面试重点](#面试重点)
- [常见面试题](#常见面试题)

---

## 概述

这三个并发工具类都是基于 **AQS（AbstractQueuedSynchronizer）** 实现的，用于协调多个线程之间的同步。

### 共同特点
- 都位于 `java.util.concurrent` 包下
- 都是线程安全的
- 都基于 AQS 实现
- 都用于线程间的协调和同步

---

## CountDownLatch

### 🔍 原理

**CountDownLatch（倒计时门闩）** 是一个同步辅助类，允许一个或多个线程等待其他线程完成操作。

**核心机制：**
- 初始化时设置一个计数器（count）
- 线程调用 `countDown()` 时计数器减1
- 调用 `await()` 的线程会阻塞，直到计数器减为0
- **计数器只能使用一次，不能重置**

**内部实现：**
- 基于 AQS 的共享模式实现
- 使用 `state` 字段表示计数器值
- `countDown()` 调用 `releaseShared(1)` 释放共享锁
- `await()` 调用 `acquireSharedInterruptibly()` 获取共享锁

### 💡 使用场景

1. **等待多个线程完成后再执行主线程**
   ```java
   // 等待所有子任务完成后再汇总结果
   CountDownLatch latch = new CountDownLatch(5);
   // 5个线程执行任务，每个完成后调用 latch.countDown()
   latch.await(); // 主线程等待所有任务完成
   ```

2. **等待多个服务初始化完成**
   ```java
   // 等待数据库、缓存、消息队列等服务启动完成
   CountDownLatch serviceLatch = new CountDownLatch(3);
   // 每个服务启动完成后调用 serviceLatch.countDown()
   serviceLatch.await(); // 等待所有服务启动
   ```

3. **并行计算后汇总结果**
   ```java
   // 多个线程并行计算，主线程等待所有计算完成后汇总
   ```

### 📝 核心方法

| 方法 | 说明 |
|------|------|
| `CountDownLatch(int count)` | 构造方法，初始化计数器 |
| `void await()` | 阻塞当前线程，直到计数器为0 |
| `boolean await(long timeout, TimeUnit unit)` | 带超时的等待 |
| `void countDown()` | 计数器减1 |
| `long getCount()` | 获取当前计数器值 |

### ⚠️ 注意事项

- 计数器只能使用一次，不能重置
- `countDown()` 可以在多个线程中调用
- `await()` 可以被多个线程调用，都会等待计数器为0
- 如果计数器已经为0，`await()` 会立即返回

---

## CyclicBarrier

### 🔍 原理

**CyclicBarrier（循环屏障）** 是一个同步辅助类，允许一组线程互相等待，直到所有线程都到达某个公共屏障点。

**核心机制：**
- 初始化时设置参与线程数（parties）
- 线程调用 `await()` 时会阻塞，直到指定数量的线程都到达屏障点
- 当所有线程到达后，屏障会打开，所有线程继续执行
- **可以重复使用（cyclic）**，可以设置一个回调任务在所有线程到达后执行

**内部实现：**
- 基于 ReentrantLock 和 Condition 实现
- 使用 `count` 记录还未到达屏障的线程数
- 当 `count` 减为0时，执行回调任务（如果有），然后唤醒所有等待的线程
- 重置 `count` 为 `parties`，可以重复使用

### 💡 使用场景

1. **多线程分阶段计算**
   ```java
   // 每个阶段需要等待所有线程完成后再进入下一阶段
   CyclicBarrier barrier = new CyclicBarrier(4);
   // 4个线程执行第一阶段
   barrier.await(); // 等待所有线程完成第一阶段
   // 4个线程执行第二阶段
   barrier.await(); // 等待所有线程完成第二阶段
   ```

2. **多线程数据分片处理**
   ```java
   // 多个线程处理不同的数据分片，需要等待所有分片处理完成后再进行下一步
   ```

3. **模拟多线程赛跑**
   ```java
   // 等待所有选手准备就绪后同时开始
   ```

### 📝 核心方法

| 方法 | 说明 |
|------|------|
| `CyclicBarrier(int parties)` | 构造方法，设置参与线程数 |
| `CyclicBarrier(int parties, Runnable barrierAction)` | 构造方法，设置参与线程数和回调任务 |
| `int await()` | 阻塞当前线程，直到所有线程到达屏障点 |
| `int await(long timeout, TimeUnit unit)` | 带超时的等待 |
| `int getParties()` | 获取参与线程数 |
| `int getNumberWaiting()` | 获取正在等待的线程数 |
| `boolean isBroken()` | 检查屏障是否被破坏 |
| `void reset()` | 重置屏障 |

### ⚠️ 注意事项

- 可以重复使用（cyclic）
- 如果某个线程在等待时被中断，屏障会被破坏（broken）
- 如果某个线程超时，屏障也会被破坏
- 屏障被破坏后，其他等待的线程会抛出 `BrokenBarrierException`

---

## Semaphore

### 🔍 原理

**Semaphore（信号量）** 是一个计数信号量，用于控制同时访问某个资源的线程数量。

**核心机制：**
- 初始化时设置许可证数量（permits）
- 线程调用 `acquire()` 获取许可证，如果没有可用许可证则阻塞
- 线程调用 `release()` 释放许可证，其他等待的线程可以获取
- 可以控制同时访问某个资源的线程数量

**内部实现：**
- 基于 AQS 的共享模式实现
- 使用 `state` 字段表示可用许可证数量
- `acquire()` 调用 `acquireSharedInterruptibly()` 获取共享锁
- `release()` 调用 `releaseShared()` 释放共享锁

### 💡 使用场景

1. **限制同时访问某个资源的线程数量**
   ```java
   // 数据库连接池，限制同时访问数据库的连接数
   Semaphore connectionPool = new Semaphore(10);
   connectionPool.acquire(); // 获取连接
   // 使用连接
   connectionPool.release(); // 释放连接
   ```

2. **控制并发数（限流）**
   ```java
   // 限制同时处理的请求数
   Semaphore rateLimiter = new Semaphore(100);
   rateLimiter.acquire(); // 获取许可
   // 处理请求
   rateLimiter.release(); // 释放许可
   ```

3. **实现生产者-消费者模式**
   ```java
   // 使用信号量控制生产者和消费者的数量
   ```

### 📝 核心方法

| 方法 | 说明 |
|------|------|
| `Semaphore(int permits)` | 构造方法，设置许可证数量 |
| `Semaphore(int permits, boolean fair)` | 构造方法，设置许可证数量和公平性 |
| `void acquire()` | 获取一个许可证，如果没有则阻塞 |
| `void acquire(int permits)` | 获取多个许可证 |
| `boolean tryAcquire()` | 尝试获取许可证，不阻塞 |
| `boolean tryAcquire(long timeout, TimeUnit unit)` | 带超时的尝试获取 |
| `void release()` | 释放一个许可证 |
| `void release(int permits)` | 释放多个许可证 |
| `int availablePermits()` | 获取可用许可证数量 |
| `int drainPermits()` | 获取并清空所有可用许可证 |

### ⚠️ 注意事项

- 可以获取和释放多个许可证
- 支持公平和非公平模式
- `release()` 可以释放比获取时更多的许可证（增加许可证数量）
- 如果线程在等待许可证时被中断，会抛出 `InterruptedException`

---

## 三者对比

| 特性 | CountDownLatch | CyclicBarrier | Semaphore |
|------|----------------|---------------|-----------|
| **用途** | 等待其他线程完成 | 多个线程互相等待 | 控制并发数量 |
| **可重用性** | ❌ 一次性 | ✅ 可重复使用 | ✅ 可重复使用 |
| **计数器方向** | 递减到0 | 递增到parties | 可增可减 |
| **主要方法** | countDown(), await() | await() | acquire(), release() |
| **典型场景** | 等待多个任务完成 | 分阶段任务同步 | 限流、资源池 |
| **基于实现** | AQS共享模式 | ReentrantLock + Condition | AQS共享模式 |

### 选择建议

- **CountDownLatch**：一个或多个线程等待其他线程完成
- **CyclicBarrier**：多个线程需要同步点，分阶段执行
- **Semaphore**：需要控制并发数量或资源访问

---

## 面试重点

### 1. 原理层面

#### CountDownLatch
- **基于 AQS 的共享模式实现**
- 使用 `state` 字段表示计数器值
- `countDown()` 调用 `releaseShared(1)`，`await()` 调用 `acquireSharedInterruptibly()`
- **一次性使用，不能重置**

#### CyclicBarrier
- **基于 ReentrantLock 和 Condition 实现**
- 使用 `count` 记录未到达屏障的线程数
- 当所有线程到达后，执行回调任务，然后重置 `count`
- **可重复使用（cyclic）**

#### Semaphore
- **基于 AQS 的共享模式实现**
- 使用 `state` 字段表示可用许可证数量
- `acquire()` 调用 `acquireSharedInterruptibly()`，`release()` 调用 `releaseShared()`
- **可重复使用，支持公平和非公平模式**

### 2. 使用场景

#### CountDownLatch 场景
- ✅ 等待多个线程完成后再执行主线程
- ✅ 等待多个服务初始化完成
- ✅ 并行计算后汇总结果
- ❌ 不适用于需要重复使用的场景

#### CyclicBarrier 场景
- ✅ 多线程分阶段计算
- ✅ 多线程数据分片处理
- ✅ 需要多个同步点的场景
- ❌ 不适用于只需要等待一次的场景

#### Semaphore 场景
- ✅ 限制同时访问某个资源的线程数量
- ✅ 控制并发数（限流）
- ✅ 实现资源池（如连接池）
- ❌ 不适用于需要等待所有线程完成的场景

### 3. 常见问题

**Q1: CountDownLatch 和 CyclicBarrier 的区别？**
- CountDownLatch 是一次性的，CyclicBarrier 可以重复使用
- CountDownLatch 是一个或多个线程等待其他线程，CyclicBarrier 是多个线程互相等待
- CountDownLatch 计数器递减，CyclicBarrier 计数器递增

**Q2: 如何重置 CountDownLatch？**
- CountDownLatch 不能重置，如果需要重置，需要创建新的实例
- 或者使用 CyclicBarrier 替代

**Q3: Semaphore 如何实现公平性？**
- 构造方法中传入 `true` 表示公平模式：`new Semaphore(permits, true)`
- 公平模式下，等待时间长的线程优先获取许可证

**Q4: CyclicBarrier 的 broken 状态是什么？**
- 当某个线程在等待时被中断或超时，屏障会被破坏
- 破坏后，其他等待的线程会抛出 `BrokenBarrierException`
- 可以使用 `reset()` 方法重置屏障

**Q5: 三个工具类都基于 AQS 吗？**
- CountDownLatch：✅ 基于 AQS
- CyclicBarrier：❌ 基于 ReentrantLock + Condition
- Semaphore：✅ 基于 AQS

---

## 常见面试题

### 1. 基础题

**Q: CountDownLatch 和 join() 方法的区别？**
- `join()` 只能等待一个线程完成，CountDownLatch 可以等待多个线程
- CountDownLatch 更灵活，可以在线程执行过程中调用 `countDown()`

**Q: CyclicBarrier 和 CountDownLatch 的区别？**
- CyclicBarrier 可以重复使用，CountDownLatch 只能使用一次
- CyclicBarrier 是多个线程互相等待，CountDownLatch 是一个或多个线程等待其他线程

**Q: Semaphore 如何实现限流？**
- 初始化时设置许可证数量（如100）
- 每个请求先调用 `acquire()` 获取许可证
- 处理完成后调用 `release()` 释放许可证
- 如果许可证用尽，后续请求会阻塞等待

### 2. 进阶题

**Q: 如何用 CountDownLatch 实现 CyclicBarrier 的功能？**
- 可以创建多个 CountDownLatch，但需要手动管理，不如 CyclicBarrier 方便
- 不推荐，应该直接使用 CyclicBarrier

**Q: Semaphore 的公平模式和非公平模式有什么区别？**
- 公平模式：等待时间长的线程优先获取许可证（FIFO）
- 非公平模式：不保证顺序，可能新来的线程先获取到许可证
- 公平模式性能较低，但更公平

**Q: 如何实现一个可重置的 CountDownLatch？**
- 可以使用 CyclicBarrier 替代
- 或者自己实现一个基于 CyclicBarrier 的包装类

### 3. 实战题

**Q: 设计一个系统，需要等待多个服务启动完成后再启动主服务，如何实现？**
- 使用 CountDownLatch，每个服务启动完成后调用 `countDown()`
- 主服务调用 `await()` 等待所有服务启动完成

**Q: 如何实现一个限流器，限制每秒最多处理100个请求？**
- 使用 Semaphore，初始化许可证数量为100
- 每个请求先获取许可证，处理完成后释放
- 可以结合定时器定期重置许可证数量

**Q: 多个线程需要分阶段处理数据，如何实现？**
- 使用 CyclicBarrier，设置参与线程数
- 每个阶段完成后调用 `await()` 等待所有线程
- 所有线程到达后继续下一阶段

---

## 运行示例

```bash
# 编译
javac concurrent_tools_demo/ConcurrentToolsDemo.java

# 运行
java concurrent_tools_demo.ConcurrentToolsDemo
```

---

## 总结

这三个并发工具类各有特点，适用于不同的场景：

- **CountDownLatch**：等待多个任务完成，一次性使用
- **CyclicBarrier**：多个线程同步点，可重复使用
- **Semaphore**：控制并发数量，可重复使用

理解它们的原理和使用场景，能够帮助我们更好地解决并发编程中的同步问题。

