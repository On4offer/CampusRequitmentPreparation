package thread_order_demo;

import java.util.Random;
import java.util.concurrent.CountDownLatch;

/**
 * 使用CountDownLatch控制线程执行顺序
 * 原理：CountDownLatch是一个同步辅助类，允许一个或多个线程等待其他线程完成操作
 * 通过设置不同的CountDownLatch，实现线程间的顺序依赖
 */
public class ThreadOrderUsingCountDownLatch {
    public static void main(String[] args) {
        // 创建CountDownLatch，用于控制线程间的依赖关系
        CountDownLatch latchA = new CountDownLatch(1);  // A执行完成后释放
        CountDownLatch latchB = new CountDownLatch(1);  // B执行完成后释放
        CountDownLatch latchC = new CountDownLatch(1);  // C执行完成后释放
        CountDownLatch latchD = new CountDownLatch(1);

        Random random = new Random();

        // 创建4个线程，分别对应A、B、C、D
        Thread threadA = new Thread(() -> {
            try {
                Thread.sleep(random.nextInt(1000)); // 随机延迟0-1秒
                System.out.println("Thread A执行");
                latchA.countDown();  // A执行完成，释放latchA
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-A");

        Thread threadB = new Thread(() -> {
            try {
                latchD.await();  // 等待latchA释放（即A执行完成）
                Thread.sleep(random.nextInt(1000)); // 随机延迟0-1秒
                System.out.println("Thread B执行");
                latchB.countDown();  // B执行完成，释放latchB
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-B");

        Thread threadC = new Thread(() -> {
            try {
                latchB.await();  // 等待latchB释放（即B执行完成）
                Thread.sleep(random.nextInt(1000)); // 随机延迟0-1秒
                System.out.println("Thread C执行");
                latchC.countDown();  // C执行完成，释放latchC
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
        }, "Thread-C");

        Thread threadD = new Thread(() -> {
            try {
                latchA.await();  // 等待latchC释放（即C执行完成）
                Thread.sleep(random.nextInt(1000)); // 随机延迟0-1秒
                System.out.println("Thread D执行");
                latchD.countDown();
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