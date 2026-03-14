package abc_order_print_demo;

import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

/**
 * 三线程顺序打印 ABC，循环多轮。state=0→A, 1→B, 2→C，各用独立 Condition 精确唤醒。
 */
public class PrintABC {
    private static final Lock lock = new ReentrantLock();
    private static final Condition condA = lock.newCondition();
    private static final Condition condB = lock.newCondition();
    private static final Condition condC = lock.newCondition();
    private static int state = 0;  // 0-A, 1-B, 2-C
    private static final int ROUNDS = 3;

    public static void main(String[] args) {
        Thread a = new Thread(() -> {
            lock.lock();
            try {
                for (int i = 0; i < ROUNDS; i++) {
                    while (state != 0) condA.await();
                    System.out.print("A");
                    state = 1;
                    condB.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        }, "A");

        Thread b = new Thread(() -> {
            lock.lock();
            try {
                for (int i = 0; i < ROUNDS; i++) {
                    while (state != 1) condB.await();
                    System.out.print("B");
                    state = 2;
                    condC.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        }, "B");

        Thread c = new Thread(() -> {
            lock.lock();
            try {
                for (int i = 0; i < ROUNDS; i++) {
                    while (state != 2) condC.await();
                    System.out.print("C");
                    state = 0;
                    condA.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        }, "C");

        a.start();
        b.start();
        c.start();
    }
}
