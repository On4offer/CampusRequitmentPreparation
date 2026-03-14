package producer_consumer_wait_notify_demo;

import java.util.LinkedList;

/**
 * 用 wait/notify 实现生产者-消费者。
 * 考点：wait/notify 必须在 synchronized 块内；用 while 判断条件防虚假唤醒。
 */
public class WaitNotifyProducerConsumer {
    private static final int CAPACITY = 3;
    private static final LinkedList<Integer> queue = new LinkedList<>();
    private static final Object lock = new Object();

    static class Producer implements Runnable {
        @Override
        public void run() {
            int value = 0;
            try {
                while (true) {
                    synchronized (lock) {
                        while (queue.size() == CAPACITY) {
                            lock.wait();
                        }
                        queue.add(value);
                        System.out.println("Producer 生产: " + value++);
                        lock.notifyAll();
                    }
                    Thread.sleep(80);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    static class Consumer implements Runnable {
        @Override
        public void run() {
            try {
                while (true) {
                    synchronized (lock) {
                        while (queue.isEmpty()) {
                            lock.wait();
                        }
                        int v = queue.poll();
                        System.out.println("Consumer 消费: " + v);
                        lock.notifyAll();
                    }
                    Thread.sleep(80);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }
    }

    public static void main(String[] args) throws InterruptedException {
        Thread p = new Thread(new Producer());
        Thread c = new Thread(new Consumer());
        p.start();
        c.start();
        Thread.sleep(2000);
        p.interrupt();
        c.interrupt();
    }
}
