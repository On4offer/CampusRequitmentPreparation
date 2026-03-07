public class AlternatePrint { // 交替打印奇偶数的类
    private static int num = 1; // 共享计数器，初始值为1
    private static final Object lock = new Object(); // 锁对象，用于线程同步

    public static void main(String[] args) { // 主方法
        // 创建线程1，用于打印奇数
        Thread t1 = new Thread(() -> {
            synchronized (lock) { // 获取锁，保证线程安全
                while (num <= 100) { // 循环直到num超过100
                    if (num % 2 == 1) { // 判断num是否为奇数
                        System.out.println(Thread.currentThread().getName() + ": " + num++); // 打印奇数并递增
                        lock.notify(); // 唤醒等待的线程
                    } else { // 如果是偶数，线程1等待
                        try {
                            lock.wait(); // 释放锁并等待唤醒
                        } catch (InterruptedException e) { // 捕获中断异常
                            Thread.currentThread().interrupt(); // 重新设置中断标志
                        }
                    }
                }
            }
        }, "A"); // 线程名称为A
        // 创建线程2，用于打印偶数
        Thread t2 = new Thread(() -> {
            synchronized (lock) { // 获取锁，保证线程安全
                while (num <= 100) { // 循环直到num超过100
                    if (num % 2 == 0) { // 判断num是否为偶数
                        System.out.println(Thread.currentThread().getName() + ": " + num++); // 打印偶数并递增
                        lock.notify(); // 唤醒等待的线程
                    } else { // 如果是奇数，线程2等待
                        try {
                            lock.wait(); // 释放锁并等待唤醒
                        } catch (InterruptedException e) { // 捕获中断异常
                            Thread.currentThread().interrupt(); // 重新设置中断标志
                        }
                    }
                }
            }
        }, "B"); // 线程名称为B
        t1.start(); // 启动线程1
        t2.start(); // 启动线程2
    }
}