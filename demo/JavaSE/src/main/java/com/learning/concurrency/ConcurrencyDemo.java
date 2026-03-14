package com.learning.concurrency;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 多线程与并发示例
 * 演示Java中的线程创建、同步、线程池等并发编程特性
 */
public class ConcurrencyDemo {
    public static void main(String[] args) {
        // 1. 线程创建方式
        System.out.println("=== 1. 线程创建方式 ===");
        
        // 方式1：继承Thread类
        Thread thread1 = new MyThread();
        thread1.start();
        
        // 方式2：实现Runnable接口
        Thread thread2 = new Thread(new MyRunnable());
        thread2.start();
        
        // 方式3：使用匿名内部类
        Thread thread3 = new Thread(new Runnable() {
            @Override
            public void run() {
                System.out.println("线程3 (匿名内部类) 正在执行");
            }
        });
        thread3.start();
        
        // 方式4：使用Lambda表达式
        Thread thread4 = new Thread(() -> {
            System.out.println("线程4 (Lambda表达式) 正在执行");
        });
        thread4.start();
        
        // 方式5：使用Callable和Future
        System.out.println("\n=== 2. Callable和Future示例 ===");
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Callable<String> callable = new MyCallable();
        Future<String> future = executor.submit(callable);
        
        try {
            // 获取Callable的返回值，会阻塞直到任务完成
            String result = future.get();
            System.out.println("Callable执行结果: " + result);
        } catch (InterruptedException | ExecutionException e) {
            e.printStackTrace();
        } finally {
            executor.shutdown();
        }
        
        // 3. 线程同步机制
        System.out.println("\n=== 3. 线程同步机制 ===");
        
        // 3.1 synchronized关键字
        System.out.println("\n--- 3.1 synchronized关键字 ---");
        SyncCounter syncCounter = new SyncCounter();
        
        Thread t1 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                syncCounter.increment();
            }
        });
        
        Thread t2 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                syncCounter.increment();
            }
        });
        
        t1.start();
        t2.start();
        
        try {
            t1.join();
            t2.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("同步计数器结果: " + syncCounter.getCount());
        
        // 3.2 Lock接口
        System.out.println("\n--- 3.2 Lock接口 ---");
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
        
        try {
            t3.join();
            t4.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("Lock计数器结果: " + lockCounter.getCount());
        
        // 3.3 原子类
        System.out.println("\n--- 3.3 原子类 ---");
        AtomicCounter atomicCounter = new AtomicCounter();
        
        Thread t5 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                atomicCounter.increment();
            }
        });
        
        Thread t6 = new Thread(() -> {
            for (int i = 0; i < 1000; i++) {
                atomicCounter.increment();
            }
        });
        
        t5.start();
        t6.start();
        
        try {
            t5.join();
            t6.join();
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        System.out.println("原子计数器结果: " + atomicCounter.getCount());
        
        // 4. 线程池
        System.out.println("\n=== 4. 线程池示例 ===");
        
        // 创建固定大小的线程池
        ExecutorService threadPool = Executors.newFixedThreadPool(3);
        
        for (int i = 0; i < 10; i++) {
            final int taskId = i;
            threadPool.execute(() -> {
                System.out.println("任务 " + taskId + " 由线程 " + Thread.currentThread().getName() + " 执行");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }
        
        threadPool.shutdown();
        
        // 5. 并发工具类
        System.out.println("\n=== 5. 并发工具类 ===");
        
        // 5.1 CountDownLatch
        System.out.println("\n--- 5.1 CountDownLatch ---");
        CountDownLatch latch = new CountDownLatch(3);
        
        for (int i = 0; i < 3; i++) {
            final int workerId = i;
            new Thread(() -> {
                System.out.println("工作线程 " + workerId + " 开始工作");
                try {
                    Thread.sleep(1000);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("工作线程 " + workerId + " 完成工作");
                latch.countDown();
            }).start();
        }
        
        try {
            System.out.println("主线程等待所有工作线程完成...");
            latch.await();
            System.out.println("所有工作线程已完成，主线程继续执行");
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
        
        // 5.2 CyclicBarrier
        System.out.println("\n--- 5.2 CyclicBarrier ---");
        CyclicBarrier barrier = new CyclicBarrier(3, () -> {
            System.out.println("所有线程都已到达屏障点！");
        });
        
        for (int i = 0; i < 3; i++) {
            final int participantId = i;
            new Thread(() -> {
                try {
                    System.out.println("参与者 " + participantId + " 正在准备");
                    Thread.sleep((participantId + 1) * 500);
                    System.out.println("参与者 " + participantId + " 已到达屏障点");
                    barrier.await();
                    System.out.println("参与者 " + participantId + " 继续执行");
                } catch (InterruptedException | BrokenBarrierException e) {
                    e.printStackTrace();
                }
            }).start();
        }
        
        // 6. 线程状态和生命周期
        System.out.println("\n=== 6. 线程状态示例 ===");
        Thread stateThread = new Thread(() -> {
            try {
                System.out.println("线程正在运行");
                Thread.sleep(2000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        });
        
        System.out.println("新建线程状态: " + stateThread.getState());
        stateThread.start();
        System.out.println("启动后线程状态: " + stateThread.getState());
        
        try {
            Thread.sleep(100);
            System.out.println("运行中线程状态: " + stateThread.getState());
            stateThread.join();
            System.out.println("结束后线程状态: " + stateThread.getState());
        } catch (InterruptedException e) {
            e.printStackTrace();
        }
    }
}

// 线程创建方式1：继承Thread类
class MyThread extends Thread {
    @Override
    public void run() {
        System.out.println("线程1 (继承Thread类) 正在执行");
    }
}

// 线程创建方式2：实现Runnable接口
class MyRunnable implements Runnable {
    @Override
    public void run() {
        System.out.println("线程2 (实现Runnable接口) 正在执行");
    }
}

// 线程创建方式5：实现Callable接口
class MyCallable implements Callable<String> {
    @Override
    public String call() throws Exception {
        System.out.println("Callable任务正在执行");
        Thread.sleep(1000);
        return "Callable任务执行完成";
    }
}

// 使用synchronized实现同步
class SyncCounter {
    private int count = 0;
    
    public synchronized void increment() {
        count++;
    }
    
    public synchronized int getCount() {
        return count;
    }
}

// 使用Lock实现同步
class LockCounter {
    private int count = 0;
    private final Lock lock = new ReentrantLock();
    
    public void increment() {
        lock.lock();
        try {
            count++;
        } finally {
            lock.unlock();
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

// 使用原子类实现线程安全
class AtomicCounter {
    private final AtomicInteger count = new AtomicInteger(0);
    
    public void increment() {
        count.incrementAndGet();
    }
    
    public int getCount() {
        return count.get();
    }
}