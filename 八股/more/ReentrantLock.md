好的！我们来详细介绍一下 `ReentrantLock`，它是 Java 中的一种 **可重入锁**，属于 `java.util.concurrent.locks` 包，提供了比 `synchronized` 更加灵活和可控的锁机制。

------

## 一、什么是 `ReentrantLock`？

`**ReentrantLock**` 是 Java 5 引入的 **显式锁**，它是 `Lock` 接口的一个实现。与 `synchronized` 不同，`ReentrantLock` 提供了更多的控制选项，比如 **可重入性、可中断性、公平性、尝试锁等**。

### **ReentrantLock** 主要特点：

1. **可重入性**：同一个线程可以多次获取同一把锁，而不会导致死锁。
2. **公平性**：可以指定锁是否公平，即按线程请求锁的顺序来分配锁。
3. **中断锁等待**：通过 `lockInterruptibly()` 方法，可以在等待锁时响应中断。
4. **尝试锁**：`tryLock()` 方法让线程尝试获取锁，如果未能获取锁就不会阻塞。

------

## 二、`ReentrantLock` 的特性与优势

### **1. 可重入性（Reentrancy）**

**可重入**意味着同一个线程可以多次获取同一把锁，而不会发生死锁。

```java
public class ReentrantLockExample {
    private final ReentrantLock lock = new ReentrantLock();

    public void method1() {
        lock.lock();
        try {
            System.out.println("Method 1");
            method2();  // 同一个线程在 method2 中再获得锁
        } finally {
            lock.unlock();
        }
    }

    public void method2() {
        lock.lock();  // 同一线程可以再次获得锁
        try {
            System.out.println("Method 2");
        } finally {
            lock.unlock();
        }
    }
}
```

- 同一个线程在 `method1()` 中调用 `method2()`，线程可以重新获取同一把锁。

------

### **2. 公平锁与非公平锁**

**公平锁**：多个线程请求锁时，**按请求的顺序**分配锁，保证“先来先得”。

**非公平锁**：默认的锁策略，允许线程在获取锁时“插队”，可能导致某些线程长时间无法获取锁。

```java
ReentrantLock lock = new ReentrantLock(true); // 公平锁
ReentrantLock lock = new ReentrantLock(false); // 非公平锁（默认）
```

- **公平锁**适用于要求线程公平的场景（如公平的线程调度队列）。
- **非公平锁**一般会提高系统的吞吐量，因为它允许线程抢占锁。

------

### **3. 中断锁等待（`lockInterruptibly()`）**

`ReentrantLock` 提供了 `lockInterruptibly()` 方法，允许线程在等待锁时响应中断，这在一些特定场景（如长时间等待时，需要对中断做出反应）非常有用。

```java
public void method() {
    try {
        lock.lockInterruptibly(); // 可以响应中断
        // 执行任务
    } catch (InterruptedException e) {
        System.out.println("Thread was interrupted");
    } finally {
        lock.unlock();
    }
}
```

- 使用 `lockInterruptibly()` 可以避免 `synchronized` 无法响应中断的问题。

------

### **4. 尝试获取锁（`tryLock()`）**

`tryLock()` 方法允许线程尝试获得锁，如果锁不可用，线程不会阻塞，而是继续执行。这种方式可以避免传统锁的阻塞问题，适用于某些“尝试锁”场景。

```java
public void tryLockExample() {
    if (lock.tryLock()) {
        try {
            // 获取锁后执行任务
            System.out.println("Lock acquired!");
        } finally {
            lock.unlock();
        }
    } else {
        System.out.println("Could not acquire lock.");
    }
}
```

- 如果 **锁不可用**，`tryLock()` 会立即返回 `false`，线程可以继续做其他事情，或者选择稍后重试。

------

## 三、`ReentrantLock` 与 `synchronized` 的比较

| 特性           | `ReentrantLock`            | `synchronized`                   |
| -------------- | -------------------------- | -------------------------------- |
| **可重入性**   | 是（支持重入锁）           | 是（默认支持）                   |
| **公平性**     | 可以配置公平锁             | 无法控制公平性                   |
| **中断支持**   | 支持 `lockInterruptibly()` | 不支持中断                       |
| **尝试获取锁** | 支持 `tryLock()`           | 不支持                           |
| **条件变量**   | 支持 `Condition`           | 使用 `Object.wait()`、`notify()` |
| **可扩展性**   | 更灵活，支持多种功能       | 简单易用，但灵活性差             |

------

## 四、使用场景

### **1. 高并发场景：**

`ReentrantLock` 的灵活性使得它非常适合 **高并发环境**，尤其是在需要 **可中断锁**、**公平锁**、或者**尝试锁**的情况下。

### **2. 任务排队：**

需要 **公平性**，例如生产者消费者模式，或者希望线程按顺序获得锁的场景，使用公平锁非常合适。

### **3. 死锁避免：**

使用 `ReentrantLock` 的 **可中断性**，可以让线程在获取锁时被中断，从而避免死锁。

------

## 五、`ReentrantLock` 示例代码

```java
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class ReentrantLockExample {
    private final Lock lock = new ReentrantLock();

    public void method1() {
        lock.lock();  // 获取锁
        try {
            System.out.println(Thread.currentThread().getName() + " 正在执行 method1");
            method2();  // 同一个线程在 method2 中再获取锁
        } finally {
            lock.unlock();  // 释放锁
        }
    }

    public void method2() {
        lock.lock();  // 获取锁
        try {
            System.out.println(Thread.currentThread().getName() + " 正在执行 method2");
        } finally {
            lock.unlock();  // 释放锁
        }
    }

    public static void main(String[] args) {
        ReentrantLockExample example = new ReentrantLockExample();
        new Thread(example::method1).start();
        new Thread(example::method1).start();
    }
}
```

### 运行结果：

```
Thread-0 正在执行 method1
Thread-0 正在执行 method2
Thread-1 正在执行 method1
Thread-1 正在执行 method2
```

### 说明：

- 线程 0 和线程 1 分别获取并执行了 `method1()`，`method2()`；
- 同一个线程可以通过 `ReentrantLock` 多次获取锁而不会导致死锁。

------

## 六、总结

| 特性         | 说明                                             |
| ------------ | ------------------------------------------------ |
| **可重入性** | 同一个线程可以多次获取同一个锁                   |
| **公平性**   | 支持公平锁，保证线程按照请求锁的顺序执行         |
| **中断支持** | 支持中断，可以在等待锁时响应中断                 |
| **尝试锁**   | 支持 `tryLock()` 方法，非阻塞尝试获取锁          |
| **灵活性**   | 提供更细粒度的控制，比如条件变量、重入、锁超时等 |

`ReentrantLock` 提供了比 `synchronized` 更加灵活和强大的锁控制方式，适用于需要更多控制功能的并发场景。

是否需要我帮助你理解某些特性或场景，或者提供更复杂的示例？