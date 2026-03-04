好问题 👍，我们来系统梳理一下 **`Thread` 类常用方法**，并结合示例说明在实际使用中怎么用。

------

# 🔹 一、常用构造方法

```java
Thread()                     // 创建一个线程对象
Thread(Runnable target)      // 通过 Runnable 对象创建线程
Thread(String name)          // 指定线程名字
Thread(Runnable target, String name)
```

👉 一般推荐 **实现 Runnable 接口**，再用 Thread 包装：

```java
Runnable task = () -> {
    System.out.println(Thread.currentThread().getName() + " is running...");
};
Thread t = new Thread(task, "Worker-1");
t.start();
```

------

# 🔹 二、启动与控制

| 方法              | 作用                                                        | 使用示例                                               |
| ----------------- | ----------------------------------------------------------- | ------------------------------------------------------ |
| `start()`         | 启动线程，进入 **就绪态**，等待 CPU 调度                    | `t.start();`                                           |
| `run()`           | 线程执行的入口点（一般不用手动调用，否则就是普通方法调用）  | `t.run(); // 不会启动新线程`                           |
| `sleep(ms)`       | 让当前线程睡眠指定毫秒数，释放 CPU，不释放锁                | `Thread.sleep(1000);`                                  |
| `yield()`         | 让出 CPU 执行权，让调度器切换到其他线程（不保证一定会切换） | `Thread.yield();`                                      |
| `join()`          | 等待某个线程执行完成                                        | `t.join();`                                            |
| `interrupt()`     | 中断线程（只是设置中断标志，不会强制停掉线程）              | `t.interrupt();`                                       |
| `isInterrupted()` | 判断线程是否被中断                                          | `while(!Thread.currentThread().isInterrupted()) {...}` |

------

# 🔹 三、线程状态相关

- `getState()`：获取线程当前状态（NEW、RUNNABLE、BLOCKED、WAITING、TIMED_WAITING、TERMINATED）
- `isAlive()`：线程是否存活（start 之后且未结束）

------

# 🔹 四、线程属性相关

- `setName(String name)` / `getName()`：设置或获取线程名字
- `setPriority(int newPriority)` / `getPriority()`：设置/获取优先级（1~10，默认 5）
- `setDaemon(boolean on)`：设置为守护线程（随主线程结束而结束），必须在 `start()` 前调用

------

# 🔹 五、实际使用示例

### 1. **创建并启动线程**

```java
class MyTask implements Runnable {
    public void run() {
        System.out.println(Thread.currentThread().getName() + " is running...");
    }
}

public class Demo {
    public static void main(String[] args) {
        Thread t1 = new Thread(new MyTask(), "Worker-1");
        t1.start();
    }
}
```

------

### 2. **join() 等待线程完成**

```java
public class Demo {
    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            try {
                Thread.sleep(2000);
                System.out.println("Worker-1 finished");
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        t1.start();
        
        t1.join(); // 等待 t1 完成
        System.out.println("Main thread continues...");
    }
}
```

------

### 3. **interrupt() 中断线程**

```java
public class Demo {
    public static void main(String[] args) {
        Thread t1 = new Thread(() -> {
            while (!Thread.currentThread().isInterrupted()) {
                System.out.println("Working...");
                try {
                    Thread.sleep(500);
                } catch (InterruptedException e) {
                    System.out.println("Interrupted while sleeping");
                    Thread.currentThread().interrupt(); // 重新设置中断状态
                }
            }
            System.out.println("Thread exiting...");
        });

        t1.start();
        try { Thread.sleep(2000); } catch (InterruptedException e) {}
        t1.interrupt(); // 请求中断
    }
}
```

------

# 🔹 六、总结（面试答法）

- **常用方法**：`start()`、`run()`、`sleep()`、`yield()`、`join()`、`interrupt()`、`isInterrupted()`、`getState()`、`setDaemon()` 等。
- **实际使用**：`start()` 用来启动线程；`join()` 等待线程完成；`sleep()` 让线程暂停；`interrupt()` 协作式中断线程；守护线程可用于后台任务。
- **注意**：不要直接调用 `run()`，那只是普通方法，不会启动新线程。

------

要不要我帮你整理一张 **“Thread 方法 → 功能 → 示例代码” 的对照表**，方便你快速复习和背诵？