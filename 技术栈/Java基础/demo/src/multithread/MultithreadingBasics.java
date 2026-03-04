package multithread;

import java.util.concurrent.*;
import java.util.concurrent.locks.*;
import java.util.*;

/**
 * 多线程编程基础示例
 * 包含线程创建、生命周期、同步机制等
 */
public class MultithreadingBasics {
    public static void main(String[] args) throws InterruptedException {
        System.out.println("===== Java多线程编程基础示例 =====\n");
        
        // 1. 创建并启动线程的方式
        System.out.println("1. 创建并启动线程的方式：");
        
        // 方式1：继承Thread类
        Thread thread1 = new MyThread("线程1");
        thread1.start();
        
        // 方式2：实现Runnable接口
        Thread thread2 = new Thread(new MyRunnable(), "线程2");
        thread2.start();
        
        // 方式3：使用Lambda表达式
        Thread thread3 = new Thread(() -> {
            for (int i = 1; i <= 5; i++) {
                System.out.println(Thread.currentThread().getName() + " - 计数: " + i);
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "线程3");
        thread3.start();
        
        // 等待所有线程完成
        thread1.join();
        thread2.join();
        thread3.join();
        System.out.println();
        
        // 2. 线程状态演示
        System.out.println("2. 线程状态演示：");
        Thread stateThread = new Thread(() -> {
            try {
                System.out.println("线程运行中...");
                Thread.sleep(1000);
                System.out.println("线程即将结束...");
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "状态演示线程");
        
        System.out.println("初始状态: " + stateThread.getState());
        stateThread.start();
        Thread.sleep(100);
        System.out.println("启动后状态: " + stateThread.getState());
        stateThread.join();
        System.out.println("结束后状态: " + stateThread.getState());
        System.out.println();
        
        // 3. 线程优先级
        System.out.println("3. 线程优先级：");
        Thread highPriorityThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println(Thread.currentThread().getName() + " 运行");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "高优先级线程");
        
        Thread lowPriorityThread = new Thread(() -> {
            for (int i = 0; i < 5; i++) {
                System.out.println(Thread.currentThread().getName() + " 运行");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            }
        }, "低优先级线程");
        
        highPriorityThread.setPriority(Thread.MAX_PRIORITY);
        lowPriorityThread.setPriority(Thread.MIN_PRIORITY);
        
        highPriorityThread.start();
        lowPriorityThread.start();
        
        highPriorityThread.join();
        lowPriorityThread.join();
        System.out.println();
        
        // 4. 线程同步 - synchronized关键字
        System.out.println("4. 线程同步 - synchronized关键字：");
        Counter counter = new Counter();
        
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                counter.increment();
            }
        });
        
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                counter.increment();
            }
        });
        
        t1.start();
        t2.start();
        
        t1.join();
        t2.join();
        
        System.out.println("最终计数（应该是2000）: " + counter.getCount());
        System.out.println();
        
        // 5. 使用Lock接口进行同步
        System.out.println("5. 使用Lock接口进行同步：");
        LockCounter lockCounter = new LockCounter();
        
        Thread t3 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                lockCounter.increment();
            }
        });
        
        Thread t4 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                lockCounter.increment();
            }
        });
        
        t3.start();
        t4.start();
        
        t3.join();
        t4.join();
        
        System.out.println("Lock同步最终计数（应该是2000）: " + lockCounter.getCount());
        System.out.println();
        
        // 6. 线程通信 - wait/notify
        System.out.println("6. 线程通信 - wait/notify：");
        Message message = new Message();
        Producer producer = new Producer(message);
        Consumer consumer = new Consumer(message);
        
        Thread producerThread = new Thread(producer);
        Thread consumerThread = new Thread(consumer);
        
        producerThread.start();
        consumerThread.start();
        
        producerThread.join();
        consumerThread.join();
        System.out.println();
        
        // 7. ThreadLocal的使用
        System.out.println("7. ThreadLocal的使用：");
        ThreadLocalDemo threadLocalDemo = new ThreadLocalDemo();
        
        Thread threadA = new Thread(() -> {
            threadLocalDemo.setUserInfo("用户A");
            try {
                Thread.sleep(200);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            threadLocalDemo.printUserInfo();
            threadLocalDemo.clear(); // 避免内存泄漏
        }, "线程A");
        
        Thread threadB = new Thread(() -> {
            threadLocalDemo.setUserInfo("用户B");
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            threadLocalDemo.printUserInfo();
            threadLocalDemo.clear(); // 避免内存泄漏
        }, "线程B");
        
        threadA.start();
        threadB.start();
        
        threadA.join();
        threadB.join();
    }
}

// 方式1：继承Thread类
class MyThread extends Thread {
    public MyThread(String name) {
        super(name);
    }
    
    @Override
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(getName() + " - 计数: " + i);
            try {
                sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

// 方式2：实现Runnable接口
class MyRunnable implements Runnable {
    @Override
    public void run() {
        for (int i = 1; i <= 5; i++) {
            System.out.println(Thread.currentThread().getName() + " - 计数: " + i);
            try {
                Thread.sleep(100);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
    }
}

// 线程同步示例 - 使用synchronized
class Counter {
    private int count = 0;
    
    // 同步方法
    public synchronized void increment() {
        count++;
    }
    
    // 同步代码块
    public void decrement() {
        synchronized (this) {
            count--;
        }
    }
    
    public synchronized int getCount() {
        return count;
    }
}

// 使用Lock接口进行同步
class LockCounter {
    private int count = 0;
    private final Lock lock = new ReentrantLock();
    
    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock(); // 确保锁一定会释放
        }
    }
    
    public int getCount() {
        lock.lock();
        try {
            return count;
        } finally {
            lock.unlock();
        }
    }
}

// 线程通信示例 - 消息类
class Message {
    private String content;
    private boolean hasMessage = false;
    
    // 生产消息
    public synchronized void put(String message) throws InterruptedException {
        // 如果有消息，等待消费者消费
        while (hasMessage) {
            wait(); // 等待通知
        }
        // 生产新消息
        this.content = message;
        hasMessage = true;
        System.out.println("生产消息: " + message);
        notify(); // 通知消费者
    }
    
    // 消费消息
    public synchronized String get() throws InterruptedException {
        // 如果没有消息，等待生产者生产
        while (!hasMessage) {
            wait(); // 等待通知
        }
        // 消费消息
        hasMessage = false;
        notify(); // 通知生产者
        System.out.println("消费消息: " + content);
        return content;
    }
}

// 生产者
class Producer implements Runnable {
    private final Message message;
    
    public Producer(Message message) {
        this.message = message;
    }
    
    @Override
    public void run() {
        String[] messages = {"消息1", "消息2", "消息3", "消息4", "消息5"};
        
        for (String msg : messages) {
            try {
                message.put(msg);
                Thread.sleep(200); // 模拟生产过程
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }
        
        try {
            message.put("EXIT"); // 发送退出信号
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

// 消费者
class Consumer implements Runnable {
    private final Message message;
    
    public Consumer(Message message) {
        this.message = message;
    }
    
    @Override
    public void run() {
        String msg;
        try {
            // 消费消息直到收到退出信号
            while (!(msg = message.get()).equals("EXIT")) {
                Thread.sleep(300); // 模拟消费过程
            }
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

// ThreadLocal示例
class ThreadLocalDemo {
    // 创建ThreadLocal变量
    private final ThreadLocal<String> userThreadLocal = ThreadLocal.withInitial(() -> "默认用户");
    
    public void setUserInfo(String userInfo) {
        userThreadLocal.set(userInfo);
        System.out.println(Thread.currentThread().getName() + " 设置用户信息: " + userInfo);
    }
    
    public void printUserInfo() {
        System.out.println(Thread.currentThread().getName() + " 获取用户信息: " + userThreadLocal.get());
    }
    
    // 清理ThreadLocal，避免内存泄漏
    public void clear() {
        userThreadLocal.remove();
    }
}