好的，我们把这道题完整展开，按照面试常用模板来回答：

------

# 🎯 面试题

**Java 中创建线程的方式有哪些？Runnable 和 Callable 的区别？**

------

## ✅ 标准回答

### 1. 创建线程的方式

1. **继承 Thread 类**

   ```java
   class MyThread extends Thread {
       @Override
       public void run() {
           System.out.println("Thread running...");
       }
   }
   new MyThread().start();
   ```

   👉 不推荐：Java 只能单继承，扩展性差。

2. **实现 Runnable 接口**

   ```java
   Runnable task = () -> System.out.println("Runnable running...");
   new Thread(task).start();
   ```

   👉 常用：任务与线程分离，可复用任务逻辑。

3. **实现 Callable 接口 + FutureTask**

   ```java
   Callable<Integer> task = () -> 123;
   FutureTask<Integer> future = new FutureTask<>(task);
   new Thread(future).start();
   System.out.println(future.get()); // 123
   ```

   👉 支持**返回值**、**异常抛出**。

4. **线程池（推荐）**

   ```java
   ExecutorService pool = Executors.newFixedThreadPool(5);
   pool.submit(() -> System.out.println("thread pool running..."));
   ```

   👉 企业级开发推荐：避免频繁创建销毁线程，提升性能。

5. **其他方式**

   - `ScheduledExecutorService`：定时/周期性任务
   - `CompletableFuture`：异步编排（JDK8）
   - `ForkJoinPool`：分治并行计算

------

### 2. Runnable vs Callable

| 特性     | Runnable                        | Callable                           |
| -------- | ------------------------------- | ---------------------------------- |
| 方法     | `void run()`                    | `V call() throws Exception`        |
| 返回值   | 无                              | 有返回值                           |
| 异常处理 | 不能抛出受检异常                | 可以抛出受检异常                   |
| 配合类   | `Thread` / `Executor.execute()` | `FutureTask` / `Executor.submit()` |
| 典型场景 | 简单任务、无需结果              | 需要结果/异常捕获                  |

------

## 📌 使用场景（结合黑马点评/苍穹外卖）

- **Runnable**：如在黑马点评项目里，异步记录用户浏览足迹/写日志，不关心结果。
- **Callable**：如在苍穹外卖里，提交订单后异步扣减库存，需要返回结果是否成功。
- **线程池**：短信验证码发送、优惠券秒杀处理，必须用线程池控制并发。

------

## ⚠️ 注意点

- 别直接用 `new Thread()`，要用线程池统一管理。
- `FutureTask` 的 `get()` 是阻塞的，要小心性能。
- `Callable` 任务执行异常会包装在 `ExecutionException` 中。

------

## 🔍 追问

1. 如果一个线程既想要返回值又想捕获异常，用 Runnable 行吗？
    👉 不行，必须用 Callable 或者在 Runnable 中手动 try/catch + 回调。
2. 为什么推荐线程池而不是直接 new Thread？
    👉 线程池避免频繁创建/销毁线程（昂贵），支持任务排队、并发数控制、复用线程。

------

要不要我帮你整理一个 **“一句话速背版”**，比如在面试时 20 秒内直接说清楚的那种？