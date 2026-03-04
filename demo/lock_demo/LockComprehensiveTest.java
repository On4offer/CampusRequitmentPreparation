package lock_demo;

import java.util.concurrent.*;
import java.util.concurrent.locks.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Lock 综合测试
 * 
 * 本类提供全面的测试，包括：
 * 1. 性能测试
 * 2. 并发安全性测试
 * 3. 死锁检测
 * 4. 各种场景的压力测试
 */
public class LockComprehensiveTest {
    
    private static final int THREAD_COUNT = 20;
    private static final int OPERATION_COUNT = 10000;
    
    // ========== 1. 性能对比测试 ==========
    public static class PerformanceTest {
        private int syncCount = 0;
        private int lockCount = 0;
        private final Object syncLock = new Object();
        private final ReentrantLock reentrantLock = new ReentrantLock();
        
        public void syncIncrement() {
            synchronized (syncLock) {
                syncCount++;
            }
        }
        
        public void lockIncrement() {
            reentrantLock.lock();
            try {
                lockCount++;
            } finally {
                reentrantLock.unlock();
            }
        }
        
        public void runTest() throws InterruptedException {
            System.out.println("========== 性能对比测试 ==========");
            System.out.println("线程数: " + THREAD_COUNT + "，操作数: " + OPERATION_COUNT);
            
            // synchronized 测试
            long syncStart = System.currentTimeMillis();
            CountDownLatch syncLatch = new CountDownLatch(THREAD_COUNT);
            for (int i = 0; i < THREAD_COUNT; i++) {
                new Thread(() -> {
                    for (int j = 0; j < OPERATION_COUNT; j++) {
                        syncIncrement();
                    }
                    syncLatch.countDown();
                }).start();
            }
            syncLatch.await();
            long syncEnd = System.currentTimeMillis();
            
            // Lock 测试
            long lockStart = System.currentTimeMillis();
            CountDownLatch lockLatch = new CountDownLatch(THREAD_COUNT);
            for (int i = 0; i < THREAD_COUNT; i++) {
                new Thread(() -> {
                    for (int j = 0; j < OPERATION_COUNT; j++) {
                        lockIncrement();
                    }
                    lockLatch.countDown();
                }).start();
            }
            lockLatch.await();
            long lockEnd = System.currentTimeMillis();
            
            System.out.println("synchronized 耗时: " + (syncEnd - syncStart) + "ms");
            System.out.println("Lock 耗时: " + (lockEnd - lockStart) + "ms");
            System.out.println("synchronized 结果: " + syncCount);
            System.out.println("Lock 结果: " + lockCount);
        }
    }
    
    // ========== 2. 并发安全性测试 ==========
    public static class ConcurrencySafetyTest {
        private int unsafeCount = 0;
        private int safeCount = 0;
        private final ReentrantLock lock = new ReentrantLock();
        
        public void unsafeIncrement() {
            unsafeCount++; // 非线程安全
        }
        
        public void safeIncrement() {
            lock.lock();
            try {
                safeCount++;
            } finally {
                lock.unlock();
            }
        }
        
        public void runTest() throws InterruptedException {
            System.out.println("\n========== 并发安全性测试 ==========");
            CountDownLatch latch = new CountDownLatch(THREAD_COUNT);
            
            for (int i = 0; i < THREAD_COUNT; i++) {
                new Thread(() -> {
                    for (int j = 0; j < OPERATION_COUNT; j++) {
                        unsafeIncrement();
                        safeIncrement();
                    }
                    latch.countDown();
                }).start();
            }
            latch.await();
            
            int expected = THREAD_COUNT * OPERATION_COUNT;
            System.out.println("预期结果: " + expected);
            System.out.println("非线程安全结果: " + unsafeCount + 
                (unsafeCount == expected ? " ✓" : " ✗ (数据丢失)"));
            System.out.println("线程安全结果: " + safeCount + 
                (safeCount == expected ? " ✓" : " ✗"));
        }
    }
    
    // ========== 3. 可重入性测试 ==========
    public static class ReentrancyTest {
        private final ReentrantLock lock = new ReentrantLock();
        private int depth = 0;
        
        public void recursiveMethod(int level) {
            lock.lock();
            try {
                depth++;
                System.out.println(Thread.currentThread().getName() + 
                    " - 进入第 " + depth + " 层，持有锁次数: " + lock.getHoldCount());
                if (level > 0) {
                    recursiveMethod(level - 1);
                }
            } finally {
                depth--;
                lock.unlock();
            }
        }
        
        public void runTest() {
            System.out.println("\n========== 可重入性测试 ==========");
            new Thread(() -> recursiveMethod(5), "ReentrantThread").start();
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    // ========== 4. 公平锁 vs 非公平锁测试 ==========
    public static class FairnessTest {
        private final ReentrantLock fairLock = new ReentrantLock(true);
        private final ReentrantLock unfairLock = new ReentrantLock(false);
        
        public void testFairLock() throws InterruptedException {
            System.out.println("\n========== 公平锁测试 ==========");
            CountDownLatch latch = new CountDownLatch(5);
            
            for (int i = 0; i < 5; i++) {
                final int index = i;
                new Thread(() -> {
                    fairLock.lock();
                    try {
                        System.out.println("公平锁 - 线程 " + index + " 获取锁");
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    } finally {
                        fairLock.unlock();
                    }
                    latch.countDown();
                }, "FairThread-" + index).start();
                Thread.sleep(10); // 错开启动时间
            }
            latch.await();
        }
        
        public void testUnfairLock() throws InterruptedException {
            System.out.println("\n========== 非公平锁测试 ==========");
            CountDownLatch latch = new CountDownLatch(5);
            
            for (int i = 0; i < 5; i++) {
                final int index = i;
                new Thread(() -> {
                    unfairLock.lock();
                    try {
                        System.out.println("非公平锁 - 线程 " + index + " 获取锁");
                        Thread.sleep(100);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    } finally {
                        unfairLock.unlock();
                    }
                    latch.countDown();
                }, "UnfairThread-" + index).start();
                Thread.sleep(10);
            }
            latch.await();
        }
    }
    
    // ========== 5. tryLock 超时测试 ==========
    public static class TryLockTest {
        private final ReentrantLock lock = new ReentrantLock();
        
        public void runTest() throws InterruptedException {
            System.out.println("\n========== tryLock 超时测试 ==========");
            
            // 线程1：持有锁5秒
            Thread holder = new Thread(() -> {
                lock.lock();
                try {
                    System.out.println("线程1: 持有锁5秒");
                    Thread.sleep(5000);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                } finally {
                    lock.unlock();
                    System.out.println("线程1: 释放锁");
                }
            });
            holder.start();
            
            Thread.sleep(100);
            
            // 线程2：尝试获取锁，超时时间2秒
            Thread tryLockThread = new Thread(() -> {
                try {
                    System.out.println("线程2: 尝试获取锁（超时2秒）");
                    if (lock.tryLock(2, TimeUnit.SECONDS)) {
                        try {
                            System.out.println("线程2: 成功获取锁");
                        } finally {
                            lock.unlock();
                        }
                    } else {
                        System.out.println("线程2: 超时未获取到锁");
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            tryLockThread.start();
            
            holder.join();
            tryLockThread.join();
        }
    }
    
    // ========== 6. 死锁检测测试 ==========
    public static class DeadlockTest {
        private final ReentrantLock lock1 = new ReentrantLock();
        private final ReentrantLock lock2 = new ReentrantLock();
        
        public void method1() {
            lock1.lock();
            try {
                System.out.println(Thread.currentThread().getName() + " 获取 lock1");
                Thread.sleep(100);
                lock2.lock(); // 可能导致死锁
                try {
                    System.out.println(Thread.currentThread().getName() + " 获取 lock2");
                } finally {
                    lock2.unlock();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock1.unlock();
            }
        }
        
        public void method2() {
            lock2.lock();
            try {
                System.out.println(Thread.currentThread().getName() + " 获取 lock2");
                Thread.sleep(100);
                lock1.lock(); // 可能导致死锁
                try {
                    System.out.println(Thread.currentThread().getName() + " 获取 lock1");
                } finally {
                    lock1.unlock();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock2.unlock();
            }
        }
        
        public void runTest() throws InterruptedException {
            System.out.println("\n========== 死锁检测测试 ==========");
            System.out.println("警告：此测试可能产生死锁，请使用 jstack 检测");
            
            Thread t1 = new Thread(() -> method1(), "Thread1");
            Thread t2 = new Thread(() -> method2(), "Thread2");
            
            t1.start();
            t2.start();
            
            // 等待一段时间后检测死锁
            Thread.sleep(2000);
            
            // 检测死锁（简化版）
            if (t1.isAlive() && t2.isAlive()) {
                System.out.println("检测到可能的死锁！");
                System.out.println("使用 jstack 命令查看详细信息：");
                System.out.println("  jstack <pid>");
            }
            
            t1.interrupt();
            t2.interrupt();
        }
    }
    
    // ========== 7. ReadWriteLock 性能测试 ==========
    public static class ReadWriteLockTest {
        private final ReadWriteLock lock = new ReentrantReadWriteLock();
        private final Lock readLock = lock.readLock();
        private final Lock writeLock = lock.writeLock();
        private int data = 0;
        
        public int read() {
            readLock.lock();
            try {
                return data;
            } finally {
                readLock.unlock();
            }
        }
        
        public void write(int value) {
            writeLock.lock();
            try {
                data = value;
            } finally {
                writeLock.unlock();
            }
        }
        
        public void runTest() throws InterruptedException {
            System.out.println("\n========== ReadWriteLock 性能测试 ==========");
            System.out.println("场景：10个读线程，2个写线程");
            
            CountDownLatch latch = new CountDownLatch(12);
            long start = System.currentTimeMillis();
            
            // 读线程
            for (int i = 0; i < 10; i++) {
                new Thread(() -> {
                    for (int j = 0; j < 1000; j++) {
                        read();
                    }
                    latch.countDown();
                }, "ReadThread-" + i).start();
            }
            
            // 写线程
            for (int i = 0; i < 2; i++) {
                new Thread(() -> {
                    for (int j = 0; j < 100; j++) {
                        write(j);
                    }
                    latch.countDown();
                }, "WriteThread-" + i).start();
            }
            
            latch.await();
            long end = System.currentTimeMillis();
            System.out.println("ReadWriteLock 耗时: " + (end - start) + "ms");
            System.out.println("最终数据值: " + data);
        }
    }
    
    // ========== 主测试方法 ==========
    public static void main(String[] args) throws InterruptedException {
        System.out.println("========================================");
        System.out.println("      Lock 综合测试套件");
        System.out.println("========================================\n");
        
        // 1. 性能测试
        new PerformanceTest().runTest();
        
        // 2. 并发安全性测试
        new ConcurrencySafetyTest().runTest();
        
        // 3. 可重入性测试
        new ReentrancyTest().runTest();
        
        // 4. 公平锁测试
        new FairnessTest().testFairLock();
        new FairnessTest().testUnfairLock();
        
        // 5. tryLock 测试
        new TryLockTest().runTest();
        
        // 6. 死锁检测（可选，可能产生死锁）
        // new DeadlockTest().runTest();
        
        // 7. ReadWriteLock 测试
        new ReadWriteLockTest().runTest();
        
        System.out.println("\n========================================");
        System.out.println("      所有测试完成");
        System.out.println("========================================");
    }
}

