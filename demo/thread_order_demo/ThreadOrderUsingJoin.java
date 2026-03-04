package thread_order_demo;

/**
 * 使用join()方法控制线程执行顺序
 * 原理：调用线程的join()方法后，当前线程会等待被调用线程执行完成后再继续执行
 */
public class ThreadOrderUsingJoin {
    public static void main(String[] args) {
        // 创建4个线程，分别对应A、B、C、D
        Thread threadA = new Thread(() -> {
            try {
                Thread.sleep((long) (Math.random() * 1000));
                System.out.println("Thread A执行");
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                System.out.println("Thread A执行完成");
            }
        }, "Thread-A");

        Thread threadB = new Thread(() -> {
            try {
                Thread.sleep((long) (Math.random() * 1000));
                System.out.println("Thread B执行");
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                System.out.println("Thread B执行完成");
            }
        }, "Thread-B");

        Thread threadC = new Thread(() -> {
            try {
                Thread.sleep((long) (Math.random() * 1000));
                System.out.println("Thread C执行");
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                System.out.println("Thread C执行完成");
            }
        }, "Thread-C");

        Thread threadD = new Thread(() -> {
            try {
                Thread.sleep((long) (Math.random() * 1000));
                System.out.println("Thread D执行");
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                System.out.println("Thread D执行完成");
            }
        }, "Thread-D");

        // 创建自定义线程X，让它等待Thread A执行完成后再执行
        Thread threadX = new Thread(() -> {
            try {
                System.out.println("Thread X开始执行，先等待Thread A完成");
                threadA.join();  // 线程X等待Thread A执行完成
                System.out.println("Thread X继续执行，因为Thread A已完成");
                Thread.sleep((long) (Math.random() * 1000));
            } catch (InterruptedException e) {
                e.printStackTrace();
            } finally {
                System.out.println("Thread X执行完成");
            }
        }, "Thread-X");

        try {
            // 启动线程A和线程X
            threadA.start();  // 启动线程A
            threadX.start();  // 启动线程X（它会在内部等待A完成）
            
            // 主线程继续等待其他线程按顺序执行
            threadA.join();   // 主线程也等待A执行完成（可选，根据需求决定）

            threadX.join();   // 等待X执行完成
            threadB.start();  // 启动线程B
            threadB.join();   // 等待B执行完成
            
            threadC.start();  // 启动线程C
            threadC.join();   // 等待C执行完成
            
            threadD.start();  // 启动线程D
            threadD.join();   // 等待D执行完成
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        System.out.println("所有线程执行完成");
    }
}