package alternate_print_demo;

import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 两线程交替打印 1~100（或 ABAB）。用 ReentrantLock + Condition。
 * 考点：while 判断条件防虚假唤醒；state/奇偶控制谁打印。
 */
public class AlternatePrint {
    private static final Lock lock = new ReentrantLock();
    private static final Condition cond = lock.newCondition();
    private static int count = 1;
    private static final int MAX = 10;

    public static void main(String[] args) {
        Thread t1 = new Thread(() -> {
            lock.lock();
            try {
                while (count <= MAX) {
                    if (count % 2 == 1) {
                        System.out.println(Thread.currentThread().getName() + ": " + count++);
                        cond.signal();
                    } else {
                        cond.await();
                    }
                }
                cond.signal();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        }, "A");

        Thread t2 = new Thread(() -> {
            lock.lock();
            try {
                while (count <= MAX) {
                    if (count % 2 == 0) {
                        System.out.println(Thread.currentThread().getName() + ": " + count++);
                        cond.signal();
                    } else {
                        cond.await();
                    }
                }
                cond.signal();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        }, "B");

        t1.start();
        t2.start();
    }
}
