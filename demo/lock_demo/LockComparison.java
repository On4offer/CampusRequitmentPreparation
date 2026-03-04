package lock_demo;

import java.util.concurrent.locks.ReentrantLock;
import java.util.concurrent.CountDownLatch;

/**
 * synchronized 和 Lock 的对比演示
 * 
 * 本类通过实际代码演示两者的差异和使用场景
 */
public class LockComparison {
    
    private static final int THREAD_COUNT = 10;
    private static final int OPERATION_COUNT = 10000;
    
    // ========== 1. 性能对比 ==========
    /**
     * 性能对比：在低竞争情况下，synchronized 性能更好（JVM 优化）
     * 在高竞争情况下，ReentrantLock 性能可能更好
     */
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
    
    // ========== 2. 功能对比 ==========
    
    /**
     * synchronized: 自动释放锁
     * Lock: 必须手动释放锁（容易忘记）
     */
    public void syncAutoRelease() {
        synchronized (syncLock) {
            // 即使发生异常，锁也会自动释放
            if (syncCount > 1000) {
                throw new RuntimeException("测试异常");
            }
            syncCount++;
        }
    }
    
    public void lockManualRelease() {
        reentrantLock.lock();
        try {
            // 必须在 finally 中释放锁
            if (lockCount > 1000) {
                throw new RuntimeException("测试异常");
            }
            lockCount++;
        } finally {
            reentrantLock.unlock(); // 必须手动释放
        }
    }
    
    /**
     * synchronized: 不可中断
     * Lock: 可以中断（lockInterruptibly）
     */
    public void syncUninterruptible() {
        synchronized (syncLock) {
            try {
                Thread.sleep(5000); // 无法被中断
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }
    
    public void lockInterruptible() throws InterruptedException {
        reentrantLock.lockInterruptibly(); // 可以响应中断
        try {
            Thread.sleep(5000);
        } finally {
            reentrantLock.unlock();
        }
    }
    
    /**
     * synchronized: 无法尝试获取锁
     * Lock: 可以尝试获取锁（tryLock）
     */
    public boolean syncTryLock() {
        // synchronized 无法尝试获取锁，只能阻塞等待
        synchronized (syncLock) {
            return true;
        }
    }
    
    public boolean lockTryLock() {
        // Lock 可以尝试获取锁，不会阻塞
        if (reentrantLock.tryLock()) {
            try {
                return true;
            } finally {
                reentrantLock.unlock();
            }
        }
        return false;
    }
    
    /**
     * synchronized: 非公平锁（无法指定）
     * Lock: 可以指定公平锁或非公平锁
     */
    private final ReentrantLock fairLock = new ReentrantLock(true);
    
    public void fairLockDemo() {
        fairLock.lock();
        try {
            // 公平锁：按照等待顺序获取锁
        } finally {
            fairLock.unlock();
        }
    }
    
    /**
     * synchronized: 只能有一个条件变量（wait/notify）
     * Lock: 可以有多个条件变量（Condition）
     */
    private final ReentrantLock multiConditionLock = new ReentrantLock();
    private final java.util.concurrent.locks.Condition condition1 = multiConditionLock.newCondition();
    private final java.util.concurrent.locks.Condition condition2 = multiConditionLock.newCondition();
    
    public void multiConditionDemo() {
        multiConditionLock.lock();
        try {
            // 可以针对不同的条件使用不同的 Condition
            condition1.await(); // 等待条件1
            condition2.await(); // 等待条件2
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        } finally {
            multiConditionLock.unlock();
        }
    }
    
    // ========== 性能测试 ==========
    public void performanceTest() throws InterruptedException {
        System.out.println("========== 性能对比测试 ==========");
        
        // synchronized 性能测试
        CountDownLatch syncLatch = new CountDownLatch(THREAD_COUNT);
        long syncStart = System.currentTimeMillis();
        
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
        
        // Lock 性能测试
        CountDownLatch lockLatch = new CountDownLatch(THREAD_COUNT);
        long lockStart = System.currentTimeMillis();
        
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
        
        System.out.println("synchronized 耗时: " + (syncEnd - syncStart) + "ms, 结果: " + syncCount);
        System.out.println("Lock 耗时: " + (lockEnd - lockStart) + "ms, 结果: " + lockCount);
    }
    
    // ========== 使用场景对比 ==========
    
    /**
     * synchronized 适用场景：
     * 1. 简单的同步需求
     * 2. 不需要高级特性（可中断、尝试获取、公平锁等）
     * 3. 代码简洁性优先
     */
    public void syncUseCase() {
        // 简单的计数器
        synchronized (syncLock) {
            syncCount++;
        }
    }
    
    /**
     * Lock 适用场景：
     * 1. 需要可中断的锁
     * 2. 需要尝试获取锁
     * 3. 需要公平锁
     * 4. 需要多个条件变量
     * 5. 需要更细粒度的控制
     */
    public void lockUseCase() {
        // 需要尝试获取锁的场景
        if (reentrantLock.tryLock()) {
            try {
                // 执行需要锁的操作
            } finally {
                reentrantLock.unlock();
            }
        } else {
            // 锁被占用，执行其他逻辑
        }
    }
    
    public static void main(String[] args) throws InterruptedException {
        LockComparison comparison = new LockComparison();
        
        System.out.println("========== 功能对比演示 ==========");
        System.out.println("1. 自动释放 vs 手动释放");
        System.out.println("   synchronized: 自动释放锁（即使发生异常）");
        System.out.println("   Lock: 必须在 finally 中手动释放");
        
        System.out.println("\n2. 可中断性");
        System.out.println("   synchronized: 不可中断");
        System.out.println("   Lock: 可以使用 lockInterruptibly() 响应中断");
        
        System.out.println("\n3. 尝试获取锁");
        System.out.println("   synchronized: 无法尝试获取，只能阻塞");
        System.out.println("   Lock: 可以使用 tryLock() 尝试获取");
        
        System.out.println("\n4. 公平锁");
        System.out.println("   synchronized: 非公平锁（无法指定）");
        System.out.println("   Lock: 可以指定公平锁或非公平锁");
        
        System.out.println("\n5. 条件变量");
        System.out.println("   synchronized: 只有一个条件（wait/notify）");
        System.out.println("   Lock: 可以有多个条件（Condition）");
        
        // 运行性能测试
        comparison.performanceTest();
        
        System.out.println("\n========== 使用建议 ==========");
        System.out.println("优先使用 synchronized 的情况：");
        System.out.println("  - 简单的同步需求");
        System.out.println("  - 不需要高级特性");
        System.out.println("  - 代码简洁性优先");
        System.out.println("\n优先使用 Lock 的情况：");
        System.out.println("  - 需要可中断的锁");
        System.out.println("  - 需要尝试获取锁");
        System.out.println("  - 需要公平锁");
        System.out.println("  - 需要多个条件变量");
        System.out.println("  - 需要更细粒度的控制");
    }
}

