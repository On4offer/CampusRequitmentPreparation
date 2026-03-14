# 手写简易 Future Demo（阻塞队列存结果）

大厂手撕题：「用阻塞队列存结果，get() 时 take」实现带返回值的异步任务。与 `callable-future-demo` 区别：本 demo **手写** Future 与提交逻辑，不直接用 `ExecutorService.submit(Callable)`。

## 文件说明

| 文件 | 说明 |
|------|------|
| `SimpleFuture.java` | 内部 BlockingQueue 存一个结果；submit 时起线程执行 Callable，结果 put 入队；get() 时 take 阻塞取；支持 get(timeout)、cancel、isDone。 |

## 考点速记

- **思路**：Callable 在 worker 线程执行 → 结果 put 到 BlockingQueue → 调用方 get() 时 take() 阻塞直到有结果。
- **与 JDK Future 对比**：JDK 的 FutureTask 用 state + WaitNode 链表等待，这里用单元素队列简化实现。
- **注意**：本实现 cancel 只设标志位，不真正中断线程；若要支持中断需在 worker 里检查 Thread.interrupted()。

## 运行方式

```bash
cd demo/simple-future-demo
javac -d . *.java
java simple_future_demo.SimpleFuture
```

预期：先打印「主线程可先做别的事」，约 300ms 后打印 `get() = 42`。
