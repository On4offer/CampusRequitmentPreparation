package lock_demo;

import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.CountDownLatch;

/**
 * Lock 底层原理演示
 * 
 * 本类通过实际代码演示 Lock 的底层实现原理，包括：
 * 1. CAS 操作原理
 * 2. AQS 队列机制
 * 3. 锁升级过程
 * 4. 可重入性实现
 */
public class LockPrincipleDemo {
    
    // ========== 1. CAS 操作演示 ==========
    /**
     * CAS（Compare-And-Swap）是 Lock 实现的基础
     * 通过原子操作保证线程安全
     */
    private AtomicInteger casCounter = new AtomicInteger(0);
    
    /**
     * 模拟 CAS 操作
     * 实际 CAS 操作由 CPU 指令保证原子性
     */
    public void casDemo() {
        int oldValue, newValue;
        do {
            oldValue = casCounter.get(); // 读取当前值
            newValue = oldValue + 1;     // 计算新值
            // CAS: 如果当前值还是 oldValue，则更新为 newValue
            // 如果被其他线程修改了，则重试
        } while (!casCounter.compareAndSet(oldValue, newValue));
        
        System.out.println(Thread.currentThread().getName() + 
            " - CAS 操作成功，新值: " + casCounter.get());
    }
    
    // ========== 2. 可重入性演示 ==========
    /**
     * ReentrantLock 的可重入性
     * 同一线程可以多次获取同一个锁
     */
    private final ReentrantLock reentrantLock = new ReentrantLock();
    
    public void reentrantMethod1() {
        reentrantLock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + 
                " - 进入 method1，持有锁次数: " + reentrantLock.getHoldCount());
            reentrantMethod2(); // 递归调用，不会死锁
        } finally {
            reentrantLock.unlock();
        }
    }
    
    public void reentrantMethod2() {
        reentrantLock.lock(); // 同一线程再次获取锁
        try {
            System.out.println(Thread.currentThread().getName() + 
                " - 进入 method2，持有锁次数: " + reentrantLock.getHoldCount());
            reentrantMethod3();
        } finally {
            reentrantLock.unlock();
        }
    }
    
    public void reentrantMethod3() {
        reentrantLock.lock(); // 第三次获取锁
        try {
            System.out.println(Thread.currentThread().getName() + 
                " - 进入 method3，持有锁次数: " + reentrantLock.getHoldCount());
        } finally {
            reentrantLock.unlock();
        }
    }
    
    // ========== 3. 公平锁 vs 非公平锁演示 ==========
    /**
     * 公平锁：按照线程等待的先后顺序获取锁
     * 非公平锁：允许插队，性能更好
     */
    private final ReentrantLock fairLock = new ReentrantLock(true); // 公平锁
    private final ReentrantLock unfairLock = new ReentrantLock(false); // 非公平锁
    
    public void fairLockDemo() {
        fairLock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + 
                " - 公平锁执行，等待队列长度: " + fairLock.getQueueLength());
        } finally {
            fairLock.unlock();
        }
    }
    
    public void unfairLockDemo() {
        unfairLock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + 
                " - 非公平锁执行，等待队列长度: " + unfairLock.getQueueLength());
        } finally {
            unfairLock.unlock();
        }
    }
    
    // ========== 4. 锁状态查询 ==========
    /**
     * 演示如何查询锁的状态信息
     */
    public void lockStatusDemo() {
        ReentrantLock lock = new ReentrantLock();
        
        System.out.println("锁状态信息：");
        System.out.println("  - 是否被锁定: " + lock.isLocked());
        System.out.println("  - 是否公平锁: " + lock.isFair());
        System.out.println("  - 等待队列长度: " + lock.getQueueLength());
        System.out.println("  - 是否有线程等待: " + lock.hasQueuedThreads());
        
        lock.lock();
        try {
            System.out.println("\n获取锁后：");
            System.out.println("  - 是否被锁定: " + lock.isLocked());
            System.out.println("  - 持有锁的线程: " + Thread.currentThread().getName());
            System.out.println("  - 当前线程持有锁次数: " + lock.getHoldCount());
        } finally {
            lock.unlock();
        }
    }
    
    // ========== 5. 锁竞争演示 ==========
    /**
     * 演示多个线程竞争同一个锁的情况
     * 观察线程的等待和唤醒过程
     */
    private int sharedResource = 0;
    private final ReentrantLock competitionLock = new ReentrantLock();
    
    public void accessResource(String threadName) {
        System.out.println(threadName + " - 尝试获取锁...");
        competitionLock.lock();
        try {
            System.out.println(threadName + " - 成功获取锁，访问共享资源");
            System.out.println(threadName + " - 等待队列长度: " + 
                competitionLock.getQueueLength());
            sharedResource++;
            Thread.sleep(500); // 模拟业务处理
            System.out.println(threadName + " - 资源值: " + sharedResource);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            System.out.println(threadName + " - 释放锁");
            competitionLock.unlock();
        }
    }
    
    // ========== 6. synchronized 锁升级演示 ==========
    /**
     * synchronized 的锁升级过程：
     * 无锁 → 偏向锁 → 轻量级锁 → 重量级锁
     * 
     * 注意：锁升级是 JVM 自动完成的，我们只能通过观察来理解
     */
    private final Object syncLock = new Object();
    private int syncCount = 0;
    
    public void synchronizedLockUpgrade() {
        // 第一次访问：偏向锁
        synchronized (syncLock) {
            syncCount++;
            System.out.println(Thread.currentThread().getName() + 
                " - 第一次访问（偏向锁）");
        }
        
        // 多线程竞争：轻量级锁或重量级锁
        synchronized (syncLock) {
            syncCount++;
            System.out.println(Thread.currentThread().getName() + 
                " - 多线程竞争（轻量级/重量级锁）");
        }
    }
    
    // ========== 测试方法 ==========
    public static void main(String[] args) throws InterruptedException {
        LockPrincipleDemo demo = new LockPrincipleDemo();
        
        System.out.println("========== 1. CAS 操作演示 ==========");
        CountDownLatch casLatch = new CountDownLatch(5);
        for (int i = 0; i < 5; i++) {
            new Thread(() -> {
                demo.casDemo();
                casLatch.countDown();
            }, "CAS-Thread-" + i).start();
        }
        casLatch.await();
        
        System.out.println("\n========== 2. 可重入性演示 ==========");
        new Thread(() -> demo.reentrantMethod1(), "ReentrantThread").start();
        Thread.sleep(500);
        
        System.out.println("\n========== 3. 锁状态查询 ==========");
        demo.lockStatusDemo();
        
        System.out.println("\n========== 4. 锁竞争演示 ==========");
        for (int i = 0; i < 5; i++) {
            final int index = i;
            new Thread(() -> {
                demo.accessResource("Competition-Thread-" + index);
            }).start();
            Thread.sleep(100); // 错开启动时间
        }
        Thread.sleep(3000);
        
        System.out.println("\n========== 5. synchronized 锁升级演示 ==========");
        for (int i = 0; i < 3; i++) {
            new Thread(() -> demo.synchronizedLockUpgrade(), 
                "SyncThread-" + i).start();
        }
        Thread.sleep(1000);
        
        System.out.println("\n========== 原理总结 ==========");
        System.out.println("1. CAS 操作：通过 CPU 指令保证原子性，是 Lock 实现的基础");
        System.out.println("2. AQS 队列：管理等待线程，实现公平锁和非公平锁");
        System.out.println("3. 可重入性：记录持有线程和重入次数，避免死锁");
        System.out.println("4. 锁升级：synchronized 根据竞争情况自动升级锁");
        System.out.println("5. 性能优化：偏向锁、轻量级锁减少系统调用开销");
    }
}

