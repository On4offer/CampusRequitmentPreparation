package fair_lock_demo;

import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 公平锁 vs 非公平锁演示。非公平：lock 时先 CAS 抢一次，吞吐高可能饥饿；
 * 公平：严格 FIFO 排队，避免饥饿，吞吐一般更低。
 */
public class FairLockDemo {
    public static void main(String[] args) {
        Lock nonFair = new ReentrantLock();       // 默认 false，非公平
        Lock fair = new ReentrantLock(true);      // 公平锁

        Runnable task = () -> {
            nonFair.lock();
            try {
                System.out.println(Thread.currentThread().getName() + " got nonFair lock");
            } finally {
                nonFair.unlock();
            }
        };
        for (int i = 0; i < 3; i++) {
            new Thread(task, "T" + i).start();
        }

        try {
            Thread.sleep(500);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }

        System.out.println("--- fair lock ---");
        Runnable fairTask = () -> {
            fair.lock();
            try {
                System.out.println(Thread.currentThread().getName() + " got fair lock");
            } finally {
                fair.unlock();
            }
        };
        for (int i = 0; i < 3; i++) {
            new Thread(fairTask, "F" + i).start();
        }
    }
}
