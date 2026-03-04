# Java线程执行顺序控制学习文档

## 1. 线程执行顺序的基本概念

在Java多线程编程中，线程的执行顺序默认是由操作系统的线程调度器决定的，这是一种抢占式调度方式。线程调度器会根据线程的优先级、时间片等因素来决定哪个线程获得CPU执行权。

但在实际开发中，我们经常需要控制线程的执行顺序，例如：
- 依赖关系：线程B需要线程A的执行结果
- 资源竞争：需要避免多个线程同时访问共享资源
- 业务逻辑：需要按照特定顺序执行某些操作

## 2. 线程执行顺序控制的核心原理

线程执行顺序控制的本质是线程间的同步，主要通过以下机制实现：

### 2.1 线程阻塞
让一个线程暂停执行，直到满足特定条件后再继续执行。

### 2.2 线程间通信
线程之间通过某种方式交换信息，以协调它们的执行顺序。

### 2.3 同步工具类
Java提供了多种同步工具类，用于实现复杂的线程同步逻辑。

## 3. 线程执行顺序控制的五种方法

### 3.1 使用join()方法

#### 原理
`join()`方法是Thread类的一个实例方法，它的作用是等待调用该方法的线程执行完成。当线程A调用线程B的join()方法时，线程A会被阻塞，直到线程B执行完成后，线程A才会继续执行。

#### 关键代码
```java
threadA.start();
threadA.join();  // 等待threadA执行完成
threadB.start();
threadB.join();  // 等待threadB执行完成
```

#### 适用场景
- 简单的顺序执行控制
- 线程之间存在明确的依赖关系

### 3.2 使用CountDownLatch

#### 原理
`CountDownLatch`是一个同步辅助类，它包含一个计数器，初始化为一个大于0的值。当线程调用`await()`方法时，如果计数器大于0，线程会被阻塞；当线程调用`countDown()`方法时，计数器的值减1，当计数器的值变为0时，所有等待的线程会被唤醒。

#### 关键代码
```java
CountDownLatch latchA = new CountDownLatch(1);
CountDownLatch latchB = new CountDownLatch(1);

Thread threadA = new Thread(() -> {
    System.out.println("Thread A执行");
    latchA.countDown();
});

Thread threadB = new Thread(() -> {
    latchA.await();  // 等待latchA计数器变为0
    System.out.println("Thread B执行");
    latchB.countDown();
});
```

#### 适用场景
- 一个线程需要等待多个线程完成操作
- 需要实现复杂的依赖关系

### 3.3 使用CyclicBarrier

#### 原理
`CyclicBarrier`是一个同步辅助类，它允许一组线程互相等待，直到所有线程都到达某个公共屏障点。当线程调用`await()`方法时，如果没有达到屏障点，线程会被阻塞；当所有线程都到达屏障点时，所有线程会被唤醒，并且可以执行一个预先设置的屏障动作。

#### 关键代码
```java
CyclicBarrier barrier = new CyclicBarrier(2, () -> {
    System.out.println("屏障动作执行");
});

Thread threadA = new Thread(() -> {
    System.out.println("Thread A执行");
    barrier.await();
});

Thread threadB = new Thread(() -> {
    barrier.await();
    System.out.println("Thread B执行");
});
```

#### 适用场景
- 多个线程需要互相等待，直到都准备好
- 需要在线程到达屏障点时执行某个动作

### 3.4 使用Semaphore

#### 原理
`Semaphore`是一个计数信号量，它维护了一组许可证。当线程调用`acquire()`方法时，如果有可用的许可证，线程会获取许可证并继续执行；如果没有可用的许可证，线程会被阻塞。当线程调用`release()`方法时，会释放一个许可证。

#### 关键代码
```java
Semaphore semaphoreA = new Semaphore(1);
Semaphore semaphoreB = new Semaphore(0);

Thread threadA = new Thread(() -> {
    semaphoreA.acquire();
    System.out.println("Thread A执行");
    semaphoreB.release();
});

Thread threadB = new Thread(() -> {
    semaphoreB.acquire();
    System.out.println("Thread B执行");
});
```

#### 适用场景
- 控制同时访问某个资源的线程数量
- 实现复杂的线程同步逻辑

### 3.5 使用synchronized和wait/notify

#### 原理
`synchronized`关键字用于实现线程间的互斥访问，它可以修饰方法或代码块。`wait()`和`notify()`/`notifyAll()`方法是Object类的方法，用于实现线程间的通信。当线程调用`wait()`方法时，会释放对象的锁并进入等待状态；当线程调用`notify()`/`notifyAll()`方法时，会唤醒等待该对象锁的线程。

#### 关键代码
```java
Object lock = new Object();
int currentStep = 1;

Thread threadA = new Thread(() -> {
    synchronized (lock) {
        while (currentStep != 1) {
            lock.wait();
        }
        System.out.println("Thread A执行");
        currentStep = 2;
        lock.notifyAll();
    }
});

Thread threadB = new Thread(() -> {
    synchronized (lock) {
        while (currentStep != 2) {
            lock.wait();
        }
        System.out.println("Thread B执行");
        lock.notifyAll();
    }
});
```

#### 适用场景
- 需要实现复杂的线程间通信
- 对性能要求较高

## 4. 各种方法的比较

| 方法 | 实现难度 | 灵活性 | 适用场景 | 性能 |
|------|----------|--------|----------|------|
| join() | 简单 | 低 | 简单的顺序执行 | 高 |
| CountDownLatch | 中等 | 中 | 复杂的依赖关系 | 高 |
| CyclicBarrier | 中等 | 中 | 线程间互相等待 | 中 |
| Semaphore | 复杂 | 高 | 复杂的同步逻辑 | 高 |
| synchronized+wait/notify | 复杂 | 高 | 底层线程通信 | 高 |

## 5. 最佳实践和注意事项

### 5.1 避免死锁
在使用同步工具类时，要注意避免死锁。死锁是指两个或多个线程互相等待对方释放资源，导致所有线程都无法继续执行的情况。

避免死锁的方法：
- 避免嵌套锁
- 设定获取锁的超时时间
- 按照固定顺序获取锁

### 5.2 性能考虑
线程同步会带来一定的性能开销，因此在使用时要注意：
- 只在必要时使用同步
- 尽量减小同步块的范围
- 选择合适的同步工具类

### 5.3 异常处理
在使用线程同步工具类时，要注意处理异常，特别是`InterruptedException`。当线程在等待时被中断，会抛出`InterruptedException`，我们需要捕获并处理这个异常。

## 6. 代码示例分析

### 6.1 join()方法示例

```java
public class ThreadOrderUsingJoin {
    public static void main(String[] args) {
        Thread threadA = new Thread(() -> System.out.println("Thread A执行"));
        Thread threadB = new Thread(() -> System.out.println("Thread B执行"));
        
        try {
            threadA.start();
            threadA.join();  // 等待threadA执行完成
            threadB.start();
            threadB.join();  // 等待threadB执行完成
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}
```

### 6.2 CountDownLatch示例

```java
public class ThreadOrderUsingCountDownLatch {
    public static void main(String[] args) {
        CountDownLatch latchA = new CountDownLatch(1);
        CountDownLatch latchB = new CountDownLatch(1);
        
        Thread threadA = new Thread(() -> {
            System.out.println("Thread A执行");
            latchA.countDown();
        });
        
        Thread threadB = new Thread(() -> {
            try {
                latchA.await();
                System.out.println("Thread B执行");
                latchB.countDown();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        
        threadB.start();
        threadA.start();
    }
}
```

## 7. 总结

线程执行顺序控制是Java多线程编程中的一个重要概念，它允许我们协调多个线程的执行，以满足特定的业务需求。Java提供了多种方式来控制线程的执行顺序，每种方式都有其适用场景和优缺点。

在实际开发中，我们应该根据具体的业务需求和性能要求，选择合适的线程执行顺序控制方法。同时，我们也应该注意避免死锁、考虑性能影响，并正确处理异常。

通过学习和掌握这些线程执行顺序控制方法，我们可以编写出更加健壮、高效的多线程程序。