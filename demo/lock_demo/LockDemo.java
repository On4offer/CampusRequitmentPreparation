package lock_demo;

import java.util.concurrent.locks.*;

/**
 * Lock 接口及其实现类的各种使用方式演示
 * 
 * Lock 是 Java 5 引入的显式锁接口，提供了比 synchronized 更灵活的锁机制
 */
public class LockDemo {
    
    // ========== 1. ReentrantLock - 可重入锁 ==========
    /**
     * ReentrantLock 是最常用的 Lock 实现
     * 功能类似 synchronized，但提供了更多特性
     */
    private final ReentrantLock reentrantLock = new ReentrantLock();
    private int reentrantCount = 0;
    
    public void reentrantLockDemo() {
        reentrantLock.lock(); // 获取锁
        try {
            reentrantCount++;
            System.out.println(Thread.currentThread().getName() + " - ReentrantLock，count: " + reentrantCount);
        } finally {
            reentrantLock.unlock(); // 必须在 finally 中释放锁
        }
    }
    
    // ========== 2. ReentrantLock - 可中断锁 ==========
    /**
     * lockInterruptibly() 允许在等待锁时响应中断
     */
    public void interruptibleLockDemo() throws InterruptedException {
        try {
            reentrantLock.lockInterruptibly(); // 可中断的锁获取
            try {
                System.out.println(Thread.currentThread().getName() + " - 获取到可中断锁");
                Thread.sleep(2000);
            } finally {
                reentrantLock.unlock();
            }
        } catch (InterruptedException e) {
            System.out.println(Thread.currentThread().getName() + " - 锁获取被中断");
        }
    }
    
    // ========== 3. ReentrantLock - 尝试获取锁 ==========
    /**
     * tryLock() 尝试获取锁，不会阻塞
     * tryLock(timeout, unit) 在指定时间内尝试获取锁
     */
    public void tryLockDemo() {
        if (reentrantLock.tryLock()) { // 立即尝试获取锁
            try {
                System.out.println(Thread.currentThread().getName() + " - 成功获取锁");
            } finally {
                reentrantLock.unlock();
            }
        } else {
            System.out.println(Thread.currentThread().getName() + " - 锁被占用，执行其他逻辑");
        }
    }
    
    public void tryLockWithTimeoutDemo() throws InterruptedException {
        if (reentrantLock.tryLock(1, java.util.concurrent.TimeUnit.SECONDS)) {
            try {
                System.out.println(Thread.currentThread().getName() + " - 在超时时间内获取到锁");
            } finally {
                reentrantLock.unlock();
            }
        } else {
            System.out.println(Thread.currentThread().getName() + " - 超时未获取到锁");
        }
    }
    
    // ========== 4. ReentrantLock - 公平锁 ==========
    /**
     * 公平锁：按照线程等待的先后顺序获取锁
     * 非公平锁：允许插队，性能更好（默认）
     */
    private final ReentrantLock fairLock = new ReentrantLock(true); // 公平锁
    
    public void fairLockDemo() {
        fairLock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + " - 公平锁执行");
        } finally {
            fairLock.unlock();
        }
    }
    
    // ========== 5. ReadWriteLock - 读写锁 ==========
    /**
     * ReadWriteLock 允许多个读线程同时访问，但写线程独占
     * 适用于读多写少的场景
     */
    private final ReadWriteLock readWriteLock = new ReentrantReadWriteLock();
    private final Lock readLock = readWriteLock.readLock();
    private final Lock writeLock = readWriteLock.writeLock();
    private String sharedData = "初始数据";
    
    public String readData() {
        readLock.lock(); // 读锁，多个线程可以同时获取
        try {
            System.out.println(Thread.currentThread().getName() + " - 读取数据: " + sharedData);
            Thread.sleep(100); // 模拟读取操作
            return sharedData;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return null;
        } finally {
            readLock.unlock();
        }
    }
    
    public void writeData(String data) {
        writeLock.lock(); // 写锁，独占访问
        try {
            System.out.println(Thread.currentThread().getName() + " - 写入数据: " + data);
            Thread.sleep(100); // 模拟写入操作
            sharedData = data;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            writeLock.unlock();
        }
    }
    
    // ========== 6. Condition - 条件变量 ==========
    /**
     * Condition 提供了类似 wait/notify 的功能，但更灵活
     * 一个 Lock 可以创建多个 Condition
     */
    private final ReentrantLock conditionLock = new ReentrantLock();
    private final Condition condition = conditionLock.newCondition();
    private boolean ready = false;
    
    public void awaitCondition() throws InterruptedException {
        conditionLock.lock();
        try {
            while (!ready) {
                System.out.println(Thread.currentThread().getName() + " - 等待条件满足...");
                condition.await(); // 等待，类似 wait()
            }
            System.out.println(Thread.currentThread().getName() + " - 条件满足，继续执行");
        } finally {
            conditionLock.unlock();
        }
    }
    
    public void signalCondition() {
        conditionLock.lock();
        try {
            ready = true;
            condition.signal(); // 唤醒一个等待的线程，类似 notify()
            // condition.signalAll(); // 唤醒所有等待的线程，类似 notifyAll()
            System.out.println(Thread.currentThread().getName() + " - 通知等待的线程");
        } finally {
            conditionLock.unlock();
        }
    }
    
    // ========== 7. StampedLock - 乐观读锁 ==========
    /**
     * StampedLock 提供了乐观读锁，在读多写少的场景下性能更好
     */
    private final StampedLock stampedLock = new StampedLock();
    private int stampedCount = 0;
    
    public int optimisticRead() {
        // 乐观读：不阻塞，返回一个戳（stamp）
        long stamp = stampedLock.tryOptimisticRead();
        int value = stampedCount;
        
        // 验证戳是否有效（在读期间是否有写操作）
        if (!stampedLock.validate(stamp)) {
            // 戳无效，升级为悲观读锁
            stamp = stampedLock.readLock();
            try {
                value = stampedCount;
            } finally {
                stampedLock.unlockRead(stamp);
            }
        }
        return value;
    }
    
    public void write() {
        long stamp = stampedLock.writeLock();
        try {
            stampedCount++;
            System.out.println(Thread.currentThread().getName() + " - StampedLock写入，count: " + stampedCount);
        } finally {
            stampedLock.unlockWrite(stamp);
        }
    }
    
    // ========== 测试方法 ==========
    public static void main(String[] args) throws InterruptedException {
        LockDemo demo = new LockDemo();
        
        System.out.println("========== 1. ReentrantLock 基本使用 ==========");
        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                for (int j = 0; j < 3; j++) {
                    demo.reentrantLockDemo();
                }
            }, "ReentrantThread-" + i).start();
        }
        Thread.sleep(1000);
        
        System.out.println("\n========== 2. tryLock 测试 ==========");
        new Thread(() -> {
            demo.reentrantLock.lock();
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                demo.reentrantLock.unlock();
            }
        }, "HolderThread").start();
        
        Thread.sleep(100);
        new Thread(() -> demo.tryLockDemo(), "TryLockThread").start();
        Thread.sleep(1500);
        
        System.out.println("\n========== 3. ReadWriteLock 测试 ==========");
        // 多个读线程可以同时执行
        for (int i = 0; i < 3; i++) {
            new Thread(() -> demo.readData(), "ReadThread-" + i).start();
        }
        Thread.sleep(500);
        // 写线程独占
        new Thread(() -> demo.writeData("新数据"), "WriteThread").start();
        Thread.sleep(500);
        
        System.out.println("\n========== 4. Condition 测试 ==========");
        Thread awaitThread = new Thread(() -> {
            try {
                demo.awaitCondition();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "AwaitThread");
        awaitThread.start();
        
        Thread.sleep(1000);
        new Thread(() -> demo.signalCondition(), "SignalThread").start();
        awaitThread.join();
        
        System.out.println("\n========== 5. StampedLock 测试 ==========");
        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                System.out.println(Thread.currentThread().getName() + " - 乐观读结果: " + demo.optimisticRead());
            }, "OptimisticReadThread-" + i).start();
        }
        Thread.sleep(100);
        new Thread(() -> demo.write(), "StampedWriteThread").start();
        Thread.sleep(500);
    }
}
