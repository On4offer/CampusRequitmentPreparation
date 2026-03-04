package thread_order_demo;

import java.util.concurrent.BrokenBarrierException;
import java.util.concurrent.CyclicBarrier;

/**
 * 使用CyclicBarrier控制线程执行顺序
 * 原理：CyclicBarrier允许一组线程互相等待，直到到达某个公共屏障点
 * 通过为每个线程设置不同的屏障点和运行逻辑，实现顺序执行
 */
public class ThreadOrderUsingCyclicBarrier {
    public static void main(String[] args) {
        // 创建CyclicBarrier，指定需要等待的线程数和屏障动作
        // 这里我们使用多个CyclicBarrier来控制执行顺序
        CyclicBarrier barrierAB = new CyclicBarrier(2, () -> {
            System.out.println("=== A执行完成，B开始执行 ===");
        });
        
        CyclicBarrier barrierBC = new CyclicBarrier(2, () -> {
            System.out.println("=== B执行完成，C开始执行 ===");
        });
        
        CyclicBarrier barrierCD = new CyclicBarrier(2, () -> {
            System.out.println("=== C执行完成，D开始执行 ===");
        });

        // 创建4个线程，分别对应A、B、C、D
        Thread threadA = new Thread(() -> {
            System.out.println("Thread A执行");
            try {
                barrierAB.await();  // 等待与B线程的屏障点
            } catch (InterruptedException | BrokenBarrierException e) {
                e.printStackTrace();
            }
        }, "Thread-A");

        Thread threadB = new Thread(() -> {
            try {
                barrierAB.await();  // 等待与A线程的屏障点
                System.out.println("Thread B执行");
                barrierBC.await();  // 等待与C线程的屏障点
            } catch (InterruptedException | BrokenBarrierException e) {
                e.printStackTrace();
            }
        }, "Thread-B");

        Thread threadC = new Thread(() -> {
            try {
                barrierBC.await();  // 等待与B线程的屏障点
                System.out.println("Thread C执行");
                barrierCD.await();  // 等待与D线程的屏障点
            } catch (InterruptedException | BrokenBarrierException e) {
                e.printStackTrace();
            }
        }, "Thread-C");

        Thread threadD = new Thread(() -> {
            try {
                barrierCD.await();  // 等待与C线程的屏障点
                System.out.println("Thread D执行");
            } catch (InterruptedException | BrokenBarrierException e) {
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