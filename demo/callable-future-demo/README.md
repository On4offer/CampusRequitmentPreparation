# Callable + Future 取结果 Demo

校招手撕题「其他高频考点」：实现 Callable + Future 取结果；常用方式为线程池 `submit(Callable)` 返回 `Future`，`get()` 阻塞取结果。

## 文件说明

| 文件 | 说明 |
|------|------|
| `CallableFutureDemo.java` | 线程池提交 Callable，主线程通过 Future.get() 取返回值。 |

## 考点速记

- **Callable**：相对 Runnable 可有返回值、可抛受检异常。
- **Future**：表示异步结果，get() 阻塞直到完成；可配合超时 get(timeout, unit)。
- 手写「用阻塞队列存结果」：worker 执行完把结果 put 到队列，调用方 get() 时 take。

## 运行方式

```bash
cd demo/callable-future-demo
javac -d . *.java
java callable_future_demo.CallableFutureDemo
```
