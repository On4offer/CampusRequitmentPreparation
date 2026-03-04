package thread_order_demo;

import java.util.concurrent.Semaphore;

/**
 * 使用Semaphore控制线程执行顺序
 * 原理：Semaphore是一个计数信号量，用于控制同时访问特定资源的线程数量
 * 通过设置初始信号量的值和线程间的信号量传递，实现顺序执行
 */
public class ThreadOrderUsingSemaphore {
    public static void main(String[] args) {
        // 创建Semaphore，控制线程执行顺序
        Semaphore semaphoreA = new Semaphore(1);  // A线程初始有1个许可证
        Semaphore semaphoreB = new Semaphore(0);  // B线程初始有0个许可证
        Semaphore semaphoreC = new Semaphore(0);  // C线程初始有0个许可证
        Semaphore semaphoreD = new Semaphore(0);  // D线程初始有0个许可证

        // 创建4个线程，分别对应A、B、C、D
        Thread threadA = new Thread(() -> {
            try {
                semaphoreA.acquire();  // 获取A的许可证
                System.out.println("Thread A执行");
                semaphoreC.release();  // 释放B的许可证
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-A");

        Thread threadB = new Thread(() -> {
            try {
                semaphoreB.acquire();  // 获取B的许可证
                System.out.println("Thread B执行");
                semaphoreD.release();  // 释放C的许可证
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-B");

        Thread threadC = new Thread(() -> {
            try {
                semaphoreC.acquire();  // 获取C的许可证
                System.out.println("Thread C执行");
                semaphoreB.release();  // 释放D的许可证
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-C");

        Thread threadD = new Thread(() -> {
            try {
                semaphoreD.acquire();  // 获取D的许可证
                System.out.println("Thread D执行");
                semaphoreA.release();
            } catch (InterruptedException e) {
                e.printStackTrace();
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