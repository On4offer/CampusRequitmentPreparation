package deadlock_demo;

/**
 * 死锁示例：两线程各持有一把锁并等待对方释放。
 * 考点：死锁四条件（互斥、占有且等待、不可抢占、循环等待）；如何避免（统一加锁顺序、tryLock 超时）。
 */
public class DeadlockDemo {
    private static final Object A = new Object();
    private static final Object B = new Object();

    public static void main(String[] args) {
        new Thread(() -> {
            synchronized (A) {
                System.out.println("Thread1 持有 A");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                synchronized (B) {
                    System.out.println("Thread1 持有 B");
                }
            }
        }, "T1").start();

        new Thread(() -> {
            synchronized (B) {
                System.out.println("Thread2 持有 B");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                synchronized (A) {
                    System.out.println("Thread2 持有 A");
                }
            }
        }, "T2").start();
    }
}
