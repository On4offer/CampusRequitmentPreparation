# 线程执行顺序控制演示

本文件夹包含5个Java文件，每个文件演示一种控制ABCD4个线程执行顺序的方法，以及一个详细的学习文档。

## 学习资源

- **详细学习文档**：[THREAD_ORDER_LEARNING.md](THREAD_ORDER_LEARNING.md) - 包含线程执行顺序控制的原理、方法比较和最佳实践

## 演示文件列表

1. **ThreadOrderUsingJoin.java**
   - 使用`join()`方法控制线程执行顺序
   - 原理：调用线程的`join()`方法会阻塞当前线程，直到被调用线程执行完成
   - 优点：实现简单，代码清晰
   - 缺点：灵活性较差，只能实现严格的顺序执行

2. **ThreadOrderUsingCountDownLatch.java**
   - 使用`CountDownLatch`控制线程执行顺序
   - 原理：CountDownLatch是一个同步辅助类，允许一个或多个线程等待其他线程完成操作
   - 优点：可以实现更复杂的依赖关系，支持多个线程等待
   - 缺点：无法重用，计数到0后不能再使用

3. **ThreadOrderUsingCyclicBarrier.java**
   - 使用`CyclicBarrier`控制线程执行顺序
   - 原理：CyclicBarrier允许一组线程互相等待，直到到达某个公共屏障点
   - 优点：可以重用，支持设置屏障动作
   - 缺点：主要用于线程间的互相等待，不是专门用于顺序控制

4. **ThreadOrderUsingSemaphore.java**
   - 使用`Semaphore`控制线程执行顺序
   - 原理：Semaphore是一个计数信号量，用于控制同时访问特定资源的线程数量
   - 优点：灵活性高，可以实现复杂的线程同步逻辑
   - 缺点：使用不当可能导致死锁

5. **ThreadOrderUsingSyncWaitNotify.java**
   - 使用`synchronized`关键字和`wait/notify`方法控制线程执行顺序
   - 原理：通过对象的监视器锁和线程间的通信机制实现顺序执行
   - 优点：Java最基础的线程同步机制，灵活性高
   - 缺点：代码复杂度较高，需要手动管理锁和线程状态

## 运行方法

1. 编译所有Java文件：
   ```bash
   javac -d . *.java
   ```

2. 运行单个演示文件：
   ```bash
   java thread_order_demo.ThreadOrderUsingJoin
   java thread_order_demo.ThreadOrderUsingCountDownLatch
   java thread_order_demo.ThreadOrderUsingCyclicBarrier
   java thread_order_demo.ThreadOrderUsingSemaphore
   java thread_order_demo.ThreadOrderUsingSyncWaitNotify
   ```

## 结果说明

所有演示文件运行后，都会按照A -> B -> C -> D的顺序输出线程执行信息：

```
Thread A执行
Thread B执行
Thread C执行
Thread D执行
```

不同方法的实现机制不同，但最终都能实现相同的执行顺序控制效果。