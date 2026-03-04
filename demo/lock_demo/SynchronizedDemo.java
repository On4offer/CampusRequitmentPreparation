package lock_demo;

/**
 * synchronized 关键字的各种使用方式演示
 * 
 * synchronized 是 Java 内置的同步机制，基于 JVM 的监视器锁（Monitor Lock）实现
 */
public class SynchronizedDemo {
    
    // ========== 1. 实例方法锁 ==========
    /**
     * 实例方法锁：锁的是当前对象实例（this）
     * 多个线程访问同一个对象的此方法时，会互斥执行
     */
    private int instanceCount = 0;
    
    public synchronized void instanceMethodLock() {
        instanceCount++;
        System.out.println(Thread.currentThread().getName() + " - 实例方法锁，count: " + instanceCount);
    }
    
    // ========== 2. 静态方法锁 ==========
    /**
     * 静态方法锁：锁的是类对象（Class对象）
     * 所有线程访问此静态方法时，都会互斥执行
     */
    private static int staticCount = 0;
    
    public static synchronized void staticMethodLock() {
        staticCount++;
        System.out.println(Thread.currentThread().getName() + " - 静态方法锁，count: " + staticCount);
    }
    
    // ========== 3. 代码块锁 - 对象锁 ==========
    /**
     * 代码块锁：锁的是指定的对象
     * 可以更细粒度地控制锁的范围
     */
    private final Object lockObject = new Object();
    private int blockCount = 0;
    
    public void blockLock() {
        // 只对需要同步的代码块加锁，提高并发性能
        synchronized (lockObject) {
            blockCount++;
            System.out.println(Thread.currentThread().getName() + " - 代码块锁，count: " + blockCount);
        }
        // 这里不需要同步的代码可以并发执行
    }
    
    // ========== 4. 代码块锁 - 类锁 ==========
    /**
     * 代码块锁：锁的是类对象
     * 等价于静态方法锁
     */
    public void classBlockLock() {
        synchronized (SynchronizedDemo.class) {
            staticCount++;
            System.out.println(Thread.currentThread().getName() + " - 类锁代码块，count: " + staticCount);
        }
    }
    
    // ========== 5. 可重入性演示 ==========
    /**
     * synchronized 是可重入锁
     * 同一个线程可以多次获取同一个锁
     */
    public synchronized void reentrantMethod1() {
        System.out.println(Thread.currentThread().getName() + " - 进入 reentrantMethod1");
        reentrantMethod2(); // 调用另一个同步方法，不会死锁
    }
    
    public synchronized void reentrantMethod2() {
        System.out.println(Thread.currentThread().getName() + " - 进入 reentrantMethod2");
    }
    
    // ========== 6. wait/notify 使用 ==========
    /**
     * synchronized 配合 wait/notify 实现线程间通信
     */
    private boolean flag = false;
    
    public synchronized void waitMethod() throws InterruptedException {
        while (!flag) {
            System.out.println(Thread.currentThread().getName() + " - 等待条件满足...");
            wait(); // 释放锁，等待被唤醒
        }
        System.out.println(Thread.currentThread().getName() + " - 条件满足，继续执行");
    }
    
    public synchronized void notifyMethod() {
        flag = true;
        notify(); // 唤醒一个等待的线程
        // notifyAll(); // 唤醒所有等待的线程
        System.out.println(Thread.currentThread().getName() + " - 通知等待的线程");
    }
    
    // ========== 测试方法 ==========
    public static void main(String[] args) throws InterruptedException {
        SynchronizedDemo demo = new SynchronizedDemo();
        
        System.out.println("========== 1. 实例方法锁测试 ==========");
        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                for (int j = 0; j < 3; j++) {
                    demo.instanceMethodLock();
                }
            }, "Thread-" + i).start();
        }
        Thread.sleep(1000);
        
        System.out.println("\n========== 2. 静态方法锁测试 ==========");
        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                for (int j = 0; j < 3; j++) {
                    SynchronizedDemo.staticMethodLock();
                }
            }, "StaticThread-" + i).start();
        }
        Thread.sleep(1000);
        
        System.out.println("\n========== 3. 代码块锁测试 ==========");
        for (int i = 0; i < 3; i++) {
            new Thread(() -> {
                for (int j = 0; j < 3; j++) {
                    demo.blockLock();
                }
            }, "BlockThread-" + i).start();
        }
        Thread.sleep(1000);
        
        System.out.println("\n========== 4. 可重入性测试 ==========");
        new Thread(() -> demo.reentrantMethod1(), "ReentrantThread").start();
        Thread.sleep(500);
        
        System.out.println("\n========== 5. wait/notify 测试 ==========");
        Thread waitThread = new Thread(() -> {
            try {
                demo.waitMethod();
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "WaitThread");
        waitThread.start();
        
        Thread.sleep(1000);
        new Thread(() -> demo.notifyMethod(), "NotifyThread").start();
        waitThread.join();
    }
}

