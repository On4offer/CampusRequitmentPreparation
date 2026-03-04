好的 👍，这是面试/实战里常考的点：除了继承 `Thread`、实现 `Runnable`，我们还可以用 **`Callable` + `FutureTask`** 创建线程，最大的区别是：**能有返回值、能抛异常**。下面我详细介绍：

------

# 🔹 1. Callable 接口

- `java.util.concurrent.Callable<V>`
- 与 `Runnable` 类似，但有两个区别：
  1. `call()` 方法可以有返回值
  2. `call()` 方法可以抛出异常

接口定义：

```java
@FunctionalInterface
public interface Callable<V> {
    V call() throws Exception;
}
```

------

# 🔹 2. FutureTask 类

- `java.util.concurrent.FutureTask<V>`
- 既是一个任务（实现了 `Runnable`），又能获取任务结果（实现了 `Future`）。
- 可以用来包装一个 `Callable`，然后交给 `Thread` 或线程池执行。

构造方法：

```java
FutureTask(Callable<V> callable)
FutureTask(Runnable runnable, V result) // 也可以包装 Runnable
```

------

# 🔹 3. 实现 Callable + FutureTask 创建线程

### 示例代码

```java
import java.util.concurrent.Callable;
import java.util.concurrent.FutureTask;

public class Demo {
    public static void main(String[] args) throws Exception {
        // 1. 创建 Callable 对象
        Callable<Integer> task = () -> {
            System.out.println(Thread.currentThread().getName() + " is running...");
            Thread.sleep(1000);
            return 42;  // 返回结果
        };

        // 2. 用 FutureTask 包装 Callable
        FutureTask<Integer> futureTask = new FutureTask<>(task);

        // 3. 交给 Thread 执行
        Thread t = new Thread(futureTask, "Worker-1");
        t.start();

        // 4. 获取结果（阻塞等待）
        Integer result = futureTask.get();
        System.out.println("Result: " + result);
    }
}
```

运行结果：

```
Worker-1 is running...
Result: 42
```

------

# 🔹 4. FutureTask 的特点

1. **既是 Runnable**：可以被 `Thread` 或线程池执行。
2. **又是 Future**：可以通过 `get()` 拿到结果。
3. **阻塞特性**：调用 `get()` 会阻塞直到任务完成。
4. **可取消**：可以调用 `cancel(true)` 取消任务。

------

# 🔹 5. 与 Runnable 的对比

| 特性         | Runnable           | Callable + FutureTask        |
| ------------ | ------------------ | ---------------------------- |
| 返回值       | 无返回值           | 有返回值（泛型）             |
| 抛出异常     | 不能               | 可以                         |
| 获取执行结果 | 不行               | `Future.get()`               |
| 应用场景     | 简单任务，无需结果 | 需要结果或异常处理的异步任务 |

------

✅ **总结**：

- **Callable**：任务接口，类似 `Runnable`，但能返回结果、能抛异常。
- **FutureTask**：桥梁类，把 `Callable` 包装成 `Runnable`，还能保存执行结果。
- 使用方式：`new Thread(new FutureTask<>(callable)).start();` → `futureTask.get();` 获取结果。

------

要不要我再帮你整理一个 **“Callable + FutureTask 在单线程 vs 在线程池里使用”**的对比代码？这样更贴近实际项目用法。