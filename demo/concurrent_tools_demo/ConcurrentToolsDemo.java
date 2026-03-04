package concurrent_tools_demo;

import java.util.concurrent.*;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * 并发工具类演示：CountDownLatch、CyclicBarrier、Semaphore
 * 
 * 这三个工具类都是基于AQS（AbstractQueuedSynchronizer）实现的
 * 用于协调多个线程之间的同步
 */
public class ConcurrentToolsDemo {

    // ========== 1. CountDownLatch 演示 ==========
    /**
     * CountDownLatch：倒计时门闩
     * 
     * 原理：
     * - 初始化时设置一个计数器（count）
     * - 线程调用 countDown() 时计数器减1
     * - 调用 await() 的线程会阻塞，直到计数器减为0
     * - 计数器只能使用一次，不能重置
     * 
     * 使用场景：
     * - 等待多个线程完成后再执行主线程
     * - 等待多个服务初始化完成后再启动主服务
     * - 并行计算后汇总结果
     */
    public static void countDownLatchDemo() throws InterruptedException {
        System.out.println("\n========== CountDownLatch 演示 ==========");
        
        int workerCount = 5;
        CountDownLatch latch = new CountDownLatch(workerCount);
        
        // 模拟5个工人完成工作
        for (int i = 1; i <= workerCount; i++) {
            final int workerId = i;
            new Thread(() -> {
                try {
                    System.out.println("工人" + workerId + " 开始工作...");
                    Thread.sleep((long) (Math.random() * 2000 + 1000)); // 模拟工作时间
                    System.out.println("工人" + workerId + " 完成工作！");
                    latch.countDown(); // 完成工作，计数器减1
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Worker-" + workerId).start();
        }
        
        System.out.println("主线程等待所有工人完成工作...");
        latch.await(); // 等待所有工人完成
        System.out.println("所有工人都完成了工作，主线程继续执行！");
    }
    
    /**
     * CountDownLatch 实际应用场景：等待多个服务启动
     */
    public static void countDownLatchServiceStartupDemo() throws InterruptedException {
        System.out.println("\n========== CountDownLatch 服务启动场景 ==========");
        
        CountDownLatch serviceLatch = new CountDownLatch(3);
        
        // 模拟三个服务的启动
        String[] services = {"数据库服务", "缓存服务", "消息队列服务"};
        
        for (String service : services) {
            new Thread(() -> {
                try {
                    System.out.println(service + " 正在启动...");
                    Thread.sleep((long) (Math.random() * 1000 + 500));
                    System.out.println(service + " 启动完成！");
                    serviceLatch.countDown();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }).start();
        }
        
        System.out.println("等待所有服务启动完成...");
        serviceLatch.await();
        System.out.println("所有服务已启动，应用可以开始提供服务！");
    }

    // ========== 2. CyclicBarrier 演示 ==========
    /**
     * CyclicBarrier：循环屏障
     * 
     * 原理：
     * - 初始化时设置一个参与线程数（parties）
     * - 线程调用 await() 时会阻塞，直到指定数量的线程都到达屏障点
     * - 当所有线程到达后，屏障会打开，所有线程继续执行
     * - 可以重复使用（cyclic），可以设置一个回调任务在所有线程到达后执行
     * 
     * 使用场景：
     * - 多线程分阶段计算，每个阶段需要等待所有线程完成
     * - 多线程数据分片处理，需要等待所有分片处理完成后再进行下一步
     * - 模拟多线程赛跑，等待所有选手准备就绪
     */
    public static void cyclicBarrierDemo() throws InterruptedException {
        System.out.println("\n========== CyclicBarrier 演示 ==========");
        
        int threadCount = 4;
        CyclicBarrier barrier = new CyclicBarrier(threadCount, () -> {
            System.out.println("\n所有线程都已到达屏障点，屏障打开！\n");
        });
        
        for (int i = 1; i <= threadCount; i++) {
            final int threadId = i;
            new Thread(() -> {
                try {
                    System.out.println("线程" + threadId + " 执行第一阶段任务...");
                    Thread.sleep((long) (Math.random() * 1000 + 500));
                    System.out.println("线程" + threadId + " 第一阶段完成，等待其他线程...");
                    
                    barrier.await(); // 等待所有线程到达
                    
                    System.out.println("线程" + threadId + " 执行第二阶段任务...");
                    Thread.sleep((long) (Math.random() * 1000 + 500));
                    System.out.println("线程" + threadId + " 第二阶段完成！");
                    
                    barrier.await(); // 再次等待所有线程到达
                    
                    System.out.println("线程" + threadId + " 执行第三阶段任务...");
                } catch (InterruptedException | BrokenBarrierException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Thread-" + threadId).start();
        }
        
        Thread.sleep(5000); // 等待演示完成
    }
    
    /**
     * CyclicBarrier 实际应用场景：多线程分阶段计算
     */
    public static void cyclicBarrierCalculationDemo() throws InterruptedException {
        System.out.println("\n========== CyclicBarrier 分阶段计算场景 ==========");
        
        int dataSize = 12;
        int threadCount = 3;
        int[] data = new int[dataSize];
        int[] results = new int[threadCount];
        
        // 初始化数据
        for (int i = 0; i < dataSize; i++) {
            data[i] = i + 1;
        }
        
        CyclicBarrier barrier = new CyclicBarrier(threadCount, () -> {
            int sum = 0;
            for (int result : results) {
                sum += result;
            }
            System.out.println("所有线程计算完成，总和为: " + sum);
        });
        
        int chunkSize = dataSize / threadCount;
        for (int i = 0; i < threadCount; i++) {
            final int threadIndex = i;
            final int start = i * chunkSize;
            final int end = (i == threadCount - 1) ? dataSize : (i + 1) * chunkSize;
            
            new Thread(() -> {
                try {
                    // 第一阶段：计算自己负责的数据段的和
                    int sum = 0;
                    for (int j = start; j < end; j++) {
                        sum += data[j];
                    }
                    results[threadIndex] = sum;
                    System.out.println("线程" + threadIndex + " 计算完成，结果为: " + sum);
                    
                    barrier.await(); // 等待所有线程计算完成
                    
                    System.out.println("线程" + threadIndex + " 继续执行后续操作...");
                } catch (InterruptedException | BrokenBarrierException e) {
                    Thread.currentThread().interrupt();
                }
            }, "CalcThread-" + threadIndex).start();
        }
        
        Thread.sleep(3000);
    }

    // ========== 3. Semaphore 演示 ==========
    /**
     * Semaphore：信号量
     * 
     * 原理：
     * - 初始化时设置许可证数量（permits）
     * - 线程调用 acquire() 获取许可证，如果没有可用许可证则阻塞
     * - 线程调用 release() 释放许可证，其他等待的线程可以获取
     * - 可以控制同时访问某个资源的线程数量
     * 
     * 使用场景：
     * - 限制同时访问某个资源的线程数量（如数据库连接池）
     * - 控制并发数（如限流）
     * - 实现生产者-消费者模式
     */
    public static void semaphoreDemo() throws InterruptedException {
        System.out.println("\n========== Semaphore 演示 ==========");
        
        int permits = 3; // 允许3个线程同时访问
        Semaphore semaphore = new Semaphore(permits);
        
        int threadCount = 10;
        for (int i = 1; i <= threadCount; i++) {
            final int threadId = i;
            new Thread(() -> {
                try {
                    System.out.println("线程" + threadId + " 尝试获取资源...");
                    semaphore.acquire(); // 获取许可证
                    
                    System.out.println("线程" + threadId + " 获取到资源，开始使用...");
                    Thread.sleep((long) (Math.random() * 2000 + 1000)); // 模拟使用资源
                    System.out.println("线程" + threadId + " 使用完毕，释放资源");
                    
                    semaphore.release(); // 释放许可证
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Thread-" + threadId).start();
        }
        
        Thread.sleep(10000); // 等待演示完成
    }
    
    /**
     * Semaphore 实际应用场景：数据库连接池
     */
    public static void semaphoreConnectionPoolDemo() throws InterruptedException {
        System.out.println("\n========== Semaphore 连接池场景 ==========");
        
        int poolSize = 5; // 连接池大小为5
        Semaphore connectionPool = new Semaphore(poolSize);
        AtomicInteger connectionId = new AtomicInteger(0);
        
        // 模拟10个线程需要使用数据库连接
        int requestCount = 10;
        for (int i = 1; i <= requestCount; i++) {
            final int requestId = i;
            new Thread(() -> {
                try {
                    System.out.println("请求" + requestId + " 尝试获取数据库连接...");
                    connectionPool.acquire();
                    
                    int connId = connectionId.incrementAndGet();
                    System.out.println("请求" + requestId + " 获取到连接[" + connId + "]，执行数据库操作...");
                    Thread.sleep((long) (Math.random() * 1500 + 500));
                    System.out.println("请求" + requestId + " 操作完成，释放连接[" + connId + "]");
                    
                    connectionPool.release();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Request-" + requestId).start();
        }
        
        Thread.sleep(8000);
    }
    
    /**
     * Semaphore 实际应用场景：限流
     */
    public static void semaphoreRateLimitDemo() throws InterruptedException {
        System.out.println("\n========== Semaphore 限流场景 ==========");
        
        int maxConcurrent = 3; // 最大并发数为3
        Semaphore rateLimiter = new Semaphore(maxConcurrent);
        
        // 模拟20个请求
        for (int i = 1; i <= 20; i++) {
            final int requestId = i;
            new Thread(() -> {
                try {
                    System.out.println("请求" + requestId + " 尝试通过限流器...");
                    rateLimiter.acquire();
                    
                    System.out.println("请求" + requestId + " 通过限流器，处理中...");
                    Thread.sleep(1000); // 模拟处理时间
                    System.out.println("请求" + requestId + " 处理完成");
                    
                    rateLimiter.release();
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            }, "Request-" + requestId).start();
            
            Thread.sleep(100); // 模拟请求间隔
        }
        
        Thread.sleep(10000);
    }

    // ========== 综合对比演示 ==========
    /**
     * 对比三个工具类的区别
     */
    public static void comparisonDemo() {
        System.out.println("\n========== 三个工具类对比 ==========");
        System.out.println("1. CountDownLatch:");
        System.out.println("   - 一次性使用，计数器减到0后不能再使用");
        System.out.println("   - 一个或多个线程等待其他线程完成");
        System.out.println("   - 适用于：等待多个任务完成");
        
        System.out.println("\n2. CyclicBarrier:");
        System.out.println("   - 可重复使用（cyclic）");
        System.out.println("   - 多个线程互相等待，都到达后继续执行");
        System.out.println("   - 适用于：分阶段任务，需要同步点");
        
        System.out.println("\n3. Semaphore:");
        System.out.println("   - 控制并发数量");
        System.out.println("   - 可以获取和释放许可证");
        System.out.println("   - 适用于：限流、资源池管理");
    }

    // ========== 主方法 ==========
    public static void main(String[] args) throws InterruptedException {
        System.out.println("========================================");
        System.out.println("并发工具类演示：CountDownLatch、CyclicBarrier、Semaphore");
        System.out.println("========================================");
        
        // CountDownLatch 演示
        countDownLatchDemo();
        Thread.sleep(1000);
        countDownLatchServiceStartupDemo();
        Thread.sleep(2000);
        
        // CyclicBarrier 演示
        cyclicBarrierDemo();
        Thread.sleep(1000);
        cyclicBarrierCalculationDemo();
        Thread.sleep(2000);
        
        // Semaphore 演示
        semaphoreDemo();
        Thread.sleep(1000);
        semaphoreConnectionPoolDemo();
        Thread.sleep(1000);
        semaphoreRateLimitDemo();
        
        // 对比说明
        comparisonDemo();
    }
}

