好 👍，这道题非常高频，通常跟 `Future`、线程池返回结果一起考。下面我给你一个标准面试答案。

------

# 🎯 面试题

**线程池中 execute() 和 submit() 的区别？**

------

## ✅ 标准回答

1. **execute() 方法**

- 定义：`void execute(Runnable command)`
- **特点**：
  - 只能提交 `Runnable` 任务。
  - 没有返回值，无法获取任务执行结果，也无法感知异常。

1. **submit() 方法**

- 定义：`<T> Future<T> submit(Callable<T> task)`
- **特点**：
  - 可以提交 `Runnable` 或 `Callable` 任务。
  - 返回一个 `Future` 对象，可以：
    - `get()` 获取返回值。
    - 捕获任务执行中的异常。
    - `cancel()` 取消任务。

------

## 📌 使用场景

- **execute()**：
  - 适合执行不关心结果的任务，如写日志、异步消息投递。
- **submit()**：
  - 适合执行需要结果的任务，如异步计算、下单结果回调。
  - 在黑马点评/苍穹外卖项目中，下单异步扣减库存时，可以用 `submit()` 获取成功/失败结果。

------

## ⚠️ 易错点

- 用 `execute()` 时任务抛出的异常不会被外部捕获，只会在工作线程中打印日志。
- 用 `submit()` 时如果忘记调用 `Future.get()`，异常会被吞掉，看似程序正常，但实际上任务失败了。

------

## 🔍 追问

1. **为什么 submit() 可以接收 Callable？**
    👉 因为内部会把任务封装成 `FutureTask`，它实现了 `RunnableFuture`（同时继承 Runnable 和 Future）。
2. **Future 的缺点是什么？**
    👉 `get()` 方法是阻塞的，不适合复杂异步编排，JDK8 之后推荐用 `CompletableFuture`。
3. **如果要获取异常，为什么 execute() 不行？**
    👉 `execute()` 不返回 `Future`，异常只能在工作线程内部抛出；而 `submit()` 会把异常保存到 `Future` 中，调用 `get()` 时再抛出。

------

要不要我帮你画一个 **`execute()` vs `submit()` 执行流程对比图**，更直观理解？