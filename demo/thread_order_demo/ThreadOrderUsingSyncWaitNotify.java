package thread_order_demo;

/**
 * 使用synchronized关键字和wait/notify方法控制线程执行顺序
 * 原理：通过对象的监视器锁和线程间的通信机制（wait/notify），实现线程的顺序执行
 * 每个线程执行完成后通知下一个线程执行
 */
public class ThreadOrderUsingSyncWaitNotify {
    // 共享对象，用于线程间通信
    private static final Object lock = new Object();
    // 控制当前应该执行的线程
    private static int currentStep = 1;

    public static void main(String[] args) {
        // 创建4个线程，分别对应A、B、C、D
        Thread threadA = new Thread(() -> {
            synchronized (lock) {
                while (currentStep != 3) {
                    try {
                        lock.wait();  // 等待直到轮到自己执行
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                System.out.println("Thread A执行");
                currentStep = 4;  // 更新步骤，轮到B执行
                lock.notifyAll();  // 通知所有等待的线程
            }
        }, "Thread-A");

        Thread threadB = new Thread(() -> {
            synchronized (lock) {
                while (currentStep != 2) {
                    try {
                        lock.wait();  // 等待直到轮到自己执行
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                System.out.println("Thread B执行");
                currentStep = 3;  // 更新步骤，轮到C执行
                lock.notifyAll();  // 通知所有等待的线程
            }
        }, "Thread-B");

        Thread threadC = new Thread(() -> {
            synchronized (lock) {
                while (currentStep != 4) {
                    try {
                        lock.wait();  // 等待直到轮到自己执行
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                System.out.println("Thread C执行");
                currentStep = 4;  // 更新步骤，轮到D执行
                lock.notifyAll();  // 通知所有等待的线程
            }
        }, "Thread-C");

        Thread threadD = new Thread(() -> {
            synchronized (lock) {
                while (currentStep != 1) {
                    try {
                        lock.wait();  // 等待直到轮到自己执行
                    } catch (InterruptedException e) {
                        e.printStackTrace();
                    }
                }
                System.out.println("Thread D执行");
                currentStep = 2;
                lock.notifyAll();  // 通知所有等待的线程
            }
        }, "Thread-D");

        // 启动所有线程
        threadD.start();
        threadC.start();
        threadB.start();
        threadA.start();

        System.out.println("所有线程启动完成");
    }
}