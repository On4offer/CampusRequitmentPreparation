# 📋 Java 多线程与并发 - 常用API与使用场景速查

> 日常开发常用多线程API、代码模板与场景速查，配合《学习笔记.md》系统学习使用。

---

## 🚀 快速开始

### 创建线程的3种方式

```java
// 方式1：继承 Thread 类
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("Thread running: " + Thread.currentThread().getName());
    }
}
MyThread t1 = new MyThread();
t1.start();

// 方式2：实现 Runnable 接口（推荐）
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("Runnable running: " + Thread.currentThread().getName());
    }
}
Thread t2 = new Thread(new MyRunnable());
t2.start();

// 方式3：实现 Callable 接口（有返回值）
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        return "Result from " + Thread.currentThread().getName();
    }
}
FutureTask<String> futureTask = new FutureTask<>(new MyCallable());
new Thread(futureTask).start();
String result = futureTask.get();  // 阻塞获取结果

// Lambda 简化（JDK 8+）
new Thread(() -> System.out.println("Lambda thread")).start();
```

---

## 🔧 Thread 类常用API

### 线程属性

```java
Thread t = new Thread();

// 获取/设置线程名
t.setName("Worker-1");
String name = t.getName();          // "Worker-1"

// 获取线程ID
long id = t.getId();

// 获取线程状态
Thread.State state = t.getState();  // NEW, RUNNABLE, BLOCKED, WAITING, TIMED_WAITING, TERMINATED

// 优先级（1-10，默认5）
t.setPriority(Thread.MAX_PRIORITY); // 10
t.setPriority(Thread.MIN_PRIORITY); // 1
t.setPriority(Thread.NORM_PRIORITY); // 5

// 是否守护线程
t.setDaemon(true);                  // 守护线程，主线程结束自动终止
boolean isDaemon = t.isDaemon();

// 是否存活
boolean alive = t.isAlive();

// 当前线程
Thread current = Thread.currentThread();
```

### 线程控制

```java
// 启动线程
t.start();                          // 只能调用一次

// 休眠（不释放锁）
Thread.sleep(1000);                 // 休眠1秒
Thread.sleep(1000, 500000);         // 休眠1秒+500000纳秒

// 让出CPU
Thread.yield();                     // 提示调度器当前线程愿意让出CPU

// 等待线程结束
t.join();                           // 无限等待
t.join(5000);                       // 最多等待5秒

// 中断线程
t.interrupt();                      // 发送中断信号
Thread.interrupted();               // 清除中断状态并返回之前的状态
t.isInterrupted();                  // 查询中断状态（不清除）

// 停止线程（已废弃，勿用）
// t.stop();  // ✗ 不安全，已废弃
// t.suspend(); // ✗ 已废弃
// t.resume();  // ✗ 已废弃
```

---

## 🔄 线程同步

### synchronized 关键字

```java
public class Counter {
    private int count = 0;
    private final Object lock = new Object();
    
    // 同步实例方法（锁当前对象）
    public synchronized void increment() {
        count++;
    }
    
    // 同步静态方法（锁类对象）
    public static synchronized void staticMethod() {
        // ...
    }
    
    // 同步代码块（更灵活，推荐）
    public void incrementWithBlock() {
        synchronized (lock) {           // 可以指定任意对象作为锁
            count++;
        }
    }
    
    // 锁类对象（用于静态上下文）
    public void classLevelLock() {
        synchronized (Counter.class) {
            // ...
        }
    }
}
```

### volatile 关键字

```java
// 保证可见性，禁止指令重排序
// 适用于：一写多读的场景，如状态标志
public class VolatileExample {
    private volatile boolean running = true;
    
    public void stop() {
        running = false;                // 对所有线程立即可见
    }
    
    public void doWork() {
        while (running) {
            // 工作...
        }
    }
}

// 注意：volatile 不保证原子性
// count++ 不是原子操作，volatile 不能保证线程安全
```

### Lock 接口（更灵活的锁）

```java
import java.util.concurrent.locks.*;

public class LockExample {
    private final ReentrantLock lock = new ReentrantLock();
    private final Condition condition = lock.newCondition();
    
    public void doSomething() {
        lock.lock();                    // 获取锁
        try {
            // 临界区代码
            while (!conditionMet()) {
                condition.await();      // 等待，会释放锁
            }
            // 执行业务逻辑
            condition.signal();         // 唤醒一个等待线程
            // condition.signalAll();   // 唤醒所有等待线程
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            lock.unlock();              // 必须在finally中释放锁
        }
    }
    
    // 尝试获取锁（非阻塞）
    public boolean tryLock() {
        if (lock.tryLock()) {           // 立即返回，不阻塞
            try {
                // 执行业务
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;
    }
    
    // 带超时的尝试获取
    public boolean tryLockWithTimeout() throws InterruptedException {
        if (lock.tryLock(5, TimeUnit.SECONDS)) {
            try {
                // 执行业务
                return true;
            } finally {
                lock.unlock();
            }
        }
        return false;
    }
    
    // 可中断的锁获取
    public void lockInterruptibly() throws InterruptedException {
        lock.lockInterruptibly();
        try {
            // 执行业务
        } finally {
            lock.unlock();
        }
    }
}
```

### 读写锁（ReadWriteLock）

```java
public class ReadWriteLockExample {
    private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Lock readLock = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();
    
    private int data = 0;
    
    // 读操作（多个线程可同时读）
    public int read() {
        readLock.lock();
        try {
            return data;
        } finally {
            readLock.unlock();
        }
    }
    
    // 写操作（独占锁）
    public void write(int value) {
        writeLock.lock();
        try {
            data = value;
        } finally {
            writeLock.unlock();
        }
    }
}
```

---

## 🧰 原子类（java.util.concurrent.atomic）

```java
// 原子整数
AtomicInteger atomicInt = new AtomicInteger(0);
atomicInt.incrementAndGet();            // ++i，返回新值
atomicInt.getAndIncrement();            // i++，返回旧值
atomicInt.decrementAndGet();            // --i
atomicInt.addAndGet(5);                 // 加5，返回新值
atomicInt.compareAndSet(0, 1);          // CAS操作：期望值0，更新为1
int value = atomicInt.get();
atomicInt.set(100);

// 原子长整型
AtomicLong atomicLong = new AtomicLong(0L);

// 原子布尔
AtomicBoolean atomicBool = new AtomicBoolean(false);
atomicBool.compareAndSet(false, true);

// 原子引用
AtomicReference<String> atomicRef = new AtomicReference<>("initial");
atomicRef.compareAndSet("initial", "updated");

// 带版本号的原子引用（解决ABA问题）
AtomicStampedReference<String> stampedRef = 
    new AtomicStampedReference<>("value", 0);  // 初始值和版本号
stampedRef.compareAndSet("value", "newValue", 0, 1);  // 带版本号比较

// 原子更新字段（反射实现）
public class User {
    volatile int age;                   // 必须是volatile
}
AtomicIntegerFieldUpdater<User> ageUpdater = 
    AtomicIntegerFieldUpdater.newUpdater(User.class, "age");
ageUpdater.incrementAndGet(user);

// LongAdder（高并发下比AtomicLong性能更好）
LongAdder adder = new LongAdder();
adder.increment();
adder.add(5);
long sum = adder.sum();

// LongAccumulator（更通用的累加器）
LongAccumulator accumulator = new LongAccumulator(Long::max, 0);
accumulator.accumulate(10);
accumulator.accumulate(20);
long result = accumulator.get();        // 20
```

---

## 🏊 线程池（Executor框架）

### 创建线程池

```java
import java.util.concurrent.*;

// 方式1：Executors工厂方法（不推荐用于生产环境）
ExecutorService pool1 = Executors.newFixedThreadPool(10);
ExecutorService pool2 = Executors.newCachedThreadPool();
ExecutorService pool3 = Executors.newSingleThreadExecutor();
ScheduledExecutorService pool4 = Executors.newScheduledThreadPool(5);

// 方式2：ThreadPoolExecutor手动创建（推荐）
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    5,                          // 核心线程数
    10,                         // 最大线程数
    60L,                        // 空闲线程存活时间
    TimeUnit.SECONDS,           // 时间单位
    new LinkedBlockingQueue<>(100), // 任务队列（容量100）
    Executors.defaultThreadFactory(), // 线程工厂
    new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
);

// 方式3：使用ThreadPoolExecutor的子类
// ForkJoinPool（工作窃取算法，适合分治任务）
ForkJoinPool forkJoinPool = new ForkJoinPool();
```

### 提交任务

```java
// 执行无返回值任务
executor.execute(() -> System.out.println("Task"));

// 提交有返回值任务
Future<Integer> future = executor.submit(() -> {
    Thread.sleep(1000);
    return 42;
});

// 批量提交
List<Callable<Integer>> tasks = Arrays.asList(
    () -> 1, () -> 2, () -> 3
);
List<Future<Integer>> futures = executor.invokeAll(tasks);
Integer anyResult = executor.invokeAny(tasks);  // 任意一个完成即返回

// 定时任务
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(5);

// 延迟执行
scheduler.schedule(() -> System.out.println("Delayed"), 5, TimeUnit.SECONDS);

// 固定频率执行（任务开始时间间隔固定）
scheduler.scheduleAtFixedRate(
    () -> System.out.println("Fixed rate"), 
    0, 5, TimeUnit.SECONDS
);

// 固定延迟执行（任务结束到下次开始间隔固定）
scheduler.scheduleWithFixedDelay(
    () -> System.out.println("Fixed delay"), 
    0, 5, TimeUnit.SECONDS
);
```

### 处理结果

```java
// Future获取结果
try {
    Integer result = future.get();              // 阻塞等待
    Integer resultWithTimeout = future.get(5, TimeUnit.SECONDS); // 带超时
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
} catch (ExecutionException e) {
    // 任务执行异常
} catch (TimeoutException e) {
    // 超时
}

// 取消任务
future.cancel(true);                            // true表示中断执行中的线程
boolean cancelled = future.isCancelled();
boolean done = future.isDone();

// CompletableFuture（JDK 8+，推荐）
CompletableFuture<String> cf = CompletableFuture.supplyAsync(() -> {
    return "Hello";
}, executor);

cf.thenApply(s -> s + " World")                 // 转换结果
  .thenAccept(System.out::println)              // 消费结果
  .thenRun(() -> System.out.println("Done"));   // 无参数无返回值

// 组合多个异步任务
CompletableFuture<String> cf1 = CompletableFuture.supplyAsync(() -> "Hello");
CompletableFuture<String> cf2 = CompletableFuture.supplyAsync(() -> "World");

CompletableFuture<String> combined = cf1.thenCombine(cf2, (s1, s2) -> s1 + " " + s2);

// 等待所有完成
CompletableFuture<Void> all = CompletableFuture.allOf(cf1, cf2);

// 等待任意一个完成
CompletableFuture<Object> any = CompletableFuture.anyOf(cf1, cf2);

// 异常处理
CompletableFuture<String> withFallback = cf.exceptionally(ex -> "Default Value");

CompletableFuture<String> withHandle = cf.handle((result, ex) -> {
    if (ex != null) {
        return "Error: " + ex.getMessage();
    }
    return result;
});
```

### 关闭线程池

```java
// 优雅关闭
executor.shutdown();                            // 停止接受新任务，等待已提交任务完成
try {
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow();                 // 强制关闭
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
    Thread.currentThread().interrupt();
}

// 立即关闭
List<Runnable> pendingTasks = executor.shutdownNow(); // 返回未执行的任务列表
```

---

## 🧵 线程安全集合

```java
// CopyOnWriteArrayList（读多写少）
CopyOnWriteArrayList<String> cowList = new CopyOnWriteArrayList<>();
cowList.add("A");
cowList.get(0);                                 // 无锁读

// CopyOnWriteArraySet
CopyOnWriteArraySet<String> cowSet = new CopyOnWriteArraySet<>();

// ConcurrentHashMap（高并发Map）
ConcurrentHashMap<String, Integer> concurrentMap = new ConcurrentHashMap<>();
concurrentMap.put("key", 1);
concurrentMap.putIfAbsent("key", 2);            // 不存在才put
concurrentMap.compute("key", (k, v) -> v + 1);  // 原子计算

// ConcurrentLinkedQueue（无锁队列）
ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<>();
queue.offer("A");
String poll = queue.poll();

// BlockingQueue（阻塞队列）
// ArrayBlockingQueue（有界队列）
ArrayBlockingQueue<String> arrayQueue = new ArrayBlockingQueue<>(100);

// LinkedBlockingQueue（可选有界）
LinkedBlockingQueue<String> linkedQueue = new LinkedBlockingQueue<>(); // 无界
LinkedBlockingQueue<String> boundedQueue = new LinkedBlockingQueue<>(100); // 有界

// PriorityBlockingQueue（优先队列）
PriorityBlockingQueue<Task> priorityQueue = new PriorityBlockingQueue<>();

// SynchronousQueue（直接传递，不存储）
SynchronousQueue<String> syncQueue = new SynchronousQueue<>();

// DelayQueue（延迟队列）
DelayQueue<DelayedTask> delayQueue = new DelayQueue<>();

// 阻塞操作
queue.put("item");                              // 队列满时阻塞
String item = queue.take();                     // 队列空时阻塞

// 非阻塞操作（带超时）
boolean offered = queue.offer("item", 5, TimeUnit.SECONDS);
String polled = queue.poll(5, TimeUnit.SECONDS);
```

---

## 🎯 常用代码场景

### 1. 生产者-消费者模式

```java
public class ProducerConsumer {
    private final BlockingQueue<String> queue = new LinkedBlockingQueue<>(10);
    
    // 生产者
    public void produce() {
        try {
            while (true) {
                String item = produceItem();
                queue.put(item);                // 队列满时自动阻塞
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    // 消费者
    public void consume() {
        try {
            while (true) {
                String item = queue.take();     // 队列空时自动阻塞
                processItem(item);
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
```

### 2. 线程安全的单例模式（双重检查锁定）

```java
public class Singleton {
    private static volatile Singleton instance;
    
    private Singleton() {}
    
    public static Singleton getInstance() {
        if (instance == null) {                 // 第一次检查（无锁）
            synchronized (Singleton.class) {
                if (instance == null) {         // 第二次检查（有锁）
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}

// 更优雅的写法（静态内部类）
public class Singleton {
    private Singleton() {}
    
    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }
    
    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}

// 枚举方式（最佳）
public enum Singleton {
    INSTANCE;
    
    public void doSomething() {
        // ...
    }
}
```

### 3. 倒计时门闩（CountDownLatch）

```java
public class CountDownLatchExample {
    public static void main(String[] args) throws InterruptedException {
        int workerCount = 3;
        CountDownLatch latch = new CountDownLatch(workerCount);
        
        for (int i = 0; i < workerCount; i++) {
            final int id = i;
            new Thread(() -> {
                System.out.println("Worker " + id + " working...");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                System.out.println("Worker " + id + " done");
                latch.countDown();              // 计数减1
            }).start();
        }
        
        latch.await();                          // 等待所有工作完成
        System.out.println("All workers done");
    }
}
```

### 4. 循环栅栏（CyclicBarrier）

```java
public class CyclicBarrierExample {
    public static void main(String[] args) {
        int parties = 3;
        CyclicBarrier barrier = new CyclicBarrier(parties, () -> {
            System.out.println("All parties arrived, continue...");
        });
        
        for (int i = 0; i < parties; i++) {
            final int id = i;
            new Thread(() -> {
                try {
                    System.out.println("Thread " + id + " arriving...");
                    Thread.sleep(id * 1000);
                    barrier.await();            // 等待其他线程
                    System.out.println("Thread " + id + " continuing...");
                } catch (Exception e) {
                    e.printStackTrace();
                }
            }).start();
        }
    }
}
```

### 5. 信号量（Semaphore）

```java
public class SemaphoreExample {
    private final Semaphore semaphore = new Semaphore(10); // 最多10个并发
    
    public void limitedAccess() {
        try {
            semaphore.acquire();                // 获取许可，没有则阻塞
            // 执行业务（最多10个线程同时执行）
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            semaphore.release();                // 释放许可
        }
    }
    
    // 尝试获取（非阻塞）
    public boolean tryAccess() {
        if (semaphore.tryAcquire()) {
            try {
                // 执行业务
                return true;
            } finally {
                semaphore.release();
            }
        }
        return false;
    }
}
```

### 6. 并行流处理

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// 并行流（底层使用ForkJoinPool）
int sum = numbers.parallelStream()
    .mapToInt(n -> n * n)
    .sum();

// 自定义线程池（避免共享ForkJoinPool）
ForkJoinPool customPool = new ForkJoinPool(4);
try {
    int result = customPool.submit(() ->
        numbers.parallelStream()
            .mapToInt(n -> heavyComputation(n))
            .sum()
    ).get();
} catch (Exception e) {
    e.printStackTrace();
} finally {
    customPool.shutdown();
}
```

---

## ⚠️ 常见坑点速查

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| `start()` vs `run()` | `run()`只是普通方法调用 | 用 `start()` 启动新线程 |
| `sleep()` 不释放锁 | 持有锁时sleep会阻塞其他线程 | 在锁外sleep或用 `wait()` |
| `wait()` 必须在同步块内 | 否则会抛IllegalMonitorStateException | 配合 `synchronized` 使用 |
| `notify()` 随机唤醒 | 可能唤醒不到想要唤醒的线程 | 用 `notifyAll()` 或 Condition |
| 线程池异常吞没 | 任务抛异常不会打印 | 用 `try-catch` 或自定义ThreadFactory |
| `submit()` 异常处理 | 异常被包装在Future中 | 调用 `future.get()` 获取异常 |
| `volatile` 不保证原子性 | `i++` 仍可能出问题 | 用 `AtomicInteger` 或 `synchronized` |
| 线程池大小设置 | 过大导致OOM，过小性能差 | 根据任务类型（IO/CPU密集型）计算 |
| 死锁 | 互相等待对方释放锁 | 统一获取顺序，或用 `tryLock()` |
| ThreadLocal内存泄漏 | 线程池场景下值不清理 | 用完后调用 `remove()` |

---

## 📝 面试代码手写题

### 1. 手写简易线程池

```java
public class SimpleThreadPool {
    private final BlockingQueue<Runnable> taskQueue;
    private final List<Worker> workers;
    private volatile boolean isShutdown = false;
    
    public SimpleThreadPool(int poolSize, int queueCapacity) {
        taskQueue = new LinkedBlockingQueue<>(queueCapacity);
        workers = new ArrayList<>(poolSize);
        
        for (int i = 0; i < poolSize; i++) {
            Worker worker = new Worker();
            workers.add(worker);
            worker.start();
        }
    }
    
    public void execute(Runnable task) {
        if (isShutdown) throw new IllegalStateException("Pool is shutdown");
        try {
            taskQueue.put(task);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
    
    public void shutdown() {
        isShutdown = true;
        for (Worker worker : workers) {
            worker.interrupt();
        }
    }
    
    private class Worker extends Thread {
        @Override
        public void run() {
            while (!isShutdown || !taskQueue.isEmpty()) {
                try {
                    Runnable task = taskQueue.poll(1, TimeUnit.SECONDS);
                    if (task != null) {
                        task.run();
                    }
                } catch (InterruptedException e) {
                    if (isShutdown) break;
                }
            }
        }
    }
}
```

### 2. 两个线程交替打印

```java
public class AlternatePrint {
    private final Object lock = new Object();
    private boolean isOdd = true;
    
    public void printOdd() {
        for (int i = 1; i <= 100; i += 2) {
            synchronized (lock) {
                while (!isOdd) {
                    try {
                        lock.wait();
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                }
                System.out.println(Thread.currentThread().getName() + ": " + i);
                isOdd = false;
                lock.notifyAll();
            }
        }
    }
    
    public void printEven() {
        for (int i = 2; i <= 100; i += 2) {
            synchronized (lock) {
                while (isOdd) {
                    try {
                        lock.wait();
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                }
                System.out.println(Thread.currentThread().getName() + ": " + i);
                isOdd = true;
                lock.notifyAll();
            }
        }
    }
    
    public static void main(String[] args) {
        AlternatePrint ap = new AlternatePrint();
        new Thread(ap::printOdd, "Odd").start();
        new Thread(ap::printEven, "Even").start();
    }
}
```

---

> 💡 **提示**：本文档用于日常速查，系统学习请查看《学习笔记.md》
