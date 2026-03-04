package multithread;

import java.util.concurrent.*;
import java.util.concurrent.atomic.*;
import java.util.*;
import java.util.concurrent.locks.*;

/**
 * 高级并发编程示例
 * 包含线程池、并发集合、原子变量、并发工具类等
 */
public class ConcurrentProgramming {
    public static void main(String[] args) throws InterruptedException, ExecutionException {
        System.out.println("===== Java高级并发编程示例 =====\n");
        
        // 1. 线程池的使用
        System.out.println("1. 线程池的使用：");
        
        // 创建固定大小的线程池
        ExecutorService fixedThreadPool = Executors.newFixedThreadPool(3);
        
        // 提交任务
        for (int i = 1; i <= 10; i++) {
            final int taskId = i;
            fixedThreadPool.submit(() -> {
                System.out.println("任务 " + taskId + " 由线程 " + Thread.currentThread().getName() + " 执行");
                try {
                    Thread.sleep(200); // 模拟任务执行时间
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("任务 " + taskId + " 执行完成");
            });
        }
        
        // 关闭线程池
        fixedThreadPool.shutdown();
        fixedThreadPool.awaitTermination(10, TimeUnit.SECONDS);
        System.out.println();
        
        // 2. 线程池类型对比
        System.out.println("2. 不同类型的线程池：");
        
        // CachedThreadPool - 可缓存线程池
        ExecutorService cachedThreadPool = Executors.newCachedThreadPool();
        System.out.println("CachedThreadPool创建");
        cachedThreadPool.shutdown();
        
        // SingleThreadExecutor - 单线程执行器
        ExecutorService singleThreadExecutor = Executors.newSingleThreadExecutor();
        System.out.println("SingleThreadExecutor创建");
        singleThreadExecutor.shutdown();
        
        // ScheduledThreadPool - 调度线程池
        ScheduledExecutorService scheduledThreadPool = Executors.newScheduledThreadPool(2);
        System.out.println("ScheduledThreadPool创建");
        
        // 延迟执行任务
        scheduledThreadPool.schedule(() -> {
            System.out.println("延迟2秒执行的任务");
        }, 2, TimeUnit.SECONDS);
        
        // 定时执行任务
        ScheduledFuture<?> scheduledFuture = scheduledThreadPool.scheduleAtFixedRate(() -> {
            System.out.println("每1秒执行一次的任务 - " + new Date());
        }, 0, 1, TimeUnit.SECONDS);
        
        // 3秒后取消定时任务
        Thread.sleep(3000);
        scheduledFuture.cancel(false);
        scheduledThreadPool.shutdown();
        System.out.println();
        
        // 3. 自定义线程池
        System.out.println("3. 自定义线程池：");
        
        ThreadPoolExecutor customThreadPool = new ThreadPoolExecutor(
            2, // 核心线程数
            5, // 最大线程数
            60, TimeUnit.SECONDS, // 空闲线程存活时间
            new LinkedBlockingQueue<>(10), // 工作队列
            new ThreadFactory() {
                private int counter = 1;
                @Override
                public Thread newThread(Runnable r) {
                    return new Thread(r, "自定义线程-" + counter++);
                }
            },
            new ThreadPoolExecutor.CallerRunsPolicy() // 拒绝策略
        );
        
        // 提交任务到自定义线程池
        for (int i = 1; i <= 15; i++) {
            final int taskId = i;
            customThreadPool.execute(() -> {
                System.out.println("自定义线程池 - 任务 " + taskId + " 由线程 " + Thread.currentThread().getName() + " 执行");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }
        
        customThreadPool.shutdown();
        customThreadPool.awaitTermination(5, TimeUnit.SECONDS);
        System.out.println();
        
        // 4. Future和Callable
        System.out.println("4. Future和Callable的使用：");
        
        ExecutorService futureTaskPool = Executors.newFixedThreadPool(2);
        List<Future<Integer>> futures = new ArrayList<>();
        
        // 提交Callable任务
        for (int i = 1; i <= 5; i++) {
            final int taskId = i;
            Future<Integer> taskFuture = futureTaskPool.submit(() -> {
                System.out.println("计算任务 " + taskId + " 开始");
                Thread.sleep(300);
                int result = taskId * 10;
                System.out.println("计算任务 " + taskId + " 结果: " + result);
                return result;
            });
            futures.add(taskFuture);
        }
        
        // 获取并汇总结果
        int totalResult = 0;
        for (Future<Integer> f : futures) {
            totalResult += f.get(); // 阻塞直到任务完成
        }
        
        System.out.println("所有任务结果总和: " + totalResult);
        futureTaskPool.shutdown();
        System.out.println();
        
        // 5. 并发集合
        System.out.println("5. 并发集合的使用：");
        
        // ConcurrentHashMap - 线程安全的HashMap
        ConcurrentHashMap<String, Integer> concurrentHashMap = new ConcurrentHashMap<>();
        
        ExecutorService mapPool = Executors.newFixedThreadPool(5);
        for (int i = 1; i <= 100; i++) {
            final int key = i;
            mapPool.submit(() -> {
                concurrentHashMap.put("key" + key, key);
            });
        }
        
        mapPool.shutdown();
        mapPool.awaitTermination(2, TimeUnit.SECONDS);
        System.out.println("ConcurrentHashMap大小: " + concurrentHashMap.size());
        
        // CopyOnWriteArrayList - 线程安全的List
        CopyOnWriteArrayList<String> cowList = new CopyOnWriteArrayList<>();
        
        ExecutorService listPool = Executors.newFixedThreadPool(3);
        for (int i = 1; i <= 10; i++) {
            final int value = i;
            listPool.submit(() -> {
                cowList.add("元素" + value);
            });
        }
        
        listPool.shutdown();
        listPool.awaitTermination(1, TimeUnit.SECONDS);
        System.out.println("CopyOnWriteArrayList内容: " + cowList);
        
        // ConcurrentLinkedQueue - 无界并发队列
        ConcurrentLinkedQueue<String> queue = new ConcurrentLinkedQueue<>();
        queue.offer("元素1");
        queue.offer("元素2");
        queue.offer("元素3");
        
        System.out.println("ConcurrentLinkedQueue出队: " + queue.poll());
        System.out.println("队列大小: " + queue.size());
        System.out.println();
        
        // 6. 原子变量
        System.out.println("6. 原子变量的使用：");
        
        AtomicInteger atomicCounter = new AtomicInteger(0);
        ExecutorService atomicPool = Executors.newFixedThreadPool(10);
        
        for (int i = 0; i < 1000; i++) {
            atomicPool.submit(() -> {
                atomicCounter.incrementAndGet(); // 原子递增
            });
        }
        
        atomicPool.shutdown();
        atomicPool.awaitTermination(2, TimeUnit.SECONDS);
        System.out.println("原子递增结果: " + atomicCounter.get());
        
        // AtomicReference
        AtomicReference<String> atomicRef = new AtomicReference<>("初始值");
        boolean updated = atomicRef.compareAndSet("初始值", "新值");
        System.out.println("AtomicReference更新成功: " + updated);
        System.out.println("更新后的值: " + atomicRef.get());
        
        // AtomicStampedReference - 解决ABA问题
        AtomicStampedReference<String> stampedRef = new AtomicStampedReference<>("A", 0);
        int stamp = stampedRef.getStamp();
        boolean stampedUpdated = stampedRef.compareAndSet("A", "B", stamp, stamp + 1);
        System.out.println("AtomicStampedReference更新成功: " + stampedUpdated);
        System.out.println("当前版本: " + stampedRef.getStamp());
        System.out.println();
        
        // 7. 并发工具类
        System.out.println("7. 并发工具类：");
        
        // CountDownLatch - 倒计时门闩
        CountDownLatch latch = new CountDownLatch(3);
        
        ExecutorService latchPool = Executors.newFixedThreadPool(3);
        for (int i = 1; i <= 3; i++) {
            final int workerId = i;
            latchPool.submit(() -> {
                System.out.println("工作线程" + workerId + " 开始工作");
                try {
                    Thread.sleep(1000 + workerId * 100);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                System.out.println("工作线程" + workerId + " 完成工作");
                latch.countDown(); // 计数减1
            });
        }
        
        System.out.println("主线程等待所有工作线程完成...");
        latch.await(); // 等待计数为0
        System.out.println("所有工作线程完成，主线程继续执行");
        latchPool.shutdown();
        
        // CyclicBarrier - 循环栅栏
        CyclicBarrier barrier = new CyclicBarrier(3, () -> {
            System.out.println("所有线程都到达栅栏，执行barrier动作");
        });
        
        ExecutorService barrierPool = Executors.newFixedThreadPool(3);
        for (int i = 1; i <= 3; i++) {
            final int threadId = i;
            barrierPool.submit(() -> {
                try {
                    System.out.println("线程" + threadId + " 第一阶段工作");
                    Thread.sleep(threadId * 200);
                    System.out.println("线程" + threadId + " 到达第一阶段栅栏");
                    barrier.await(); // 等待其他线程
                    
                    System.out.println("线程" + threadId + " 第二阶段工作");
                    Thread.sleep(threadId * 100);
                    System.out.println("线程" + threadId + " 到达第二阶段栅栏");
                    barrier.await(); // 等待其他线程
                    
                } catch (Exception e) {
                    e.printStackTrace();
                }
            });
        }
        
        barrierPool.shutdown();
        barrierPool.awaitTermination(5, TimeUnit.SECONDS);
        System.out.println();
        
        // 8. 读写锁
        System.out.println("8. 读写锁：");
        ReadWriteLockDemo rwLockDemo = new ReadWriteLockDemo();
        
        ExecutorService rwLockPool = Executors.newFixedThreadPool(10);
        
        // 创建5个读线程
        for (int i = 1; i <= 5; i++) {
            rwLockPool.submit(() -> {
                try {
                    rwLockDemo.read();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }
        
        // 创建2个写线程
        for (int i = 1; i <= 2; i++) {
            final int value = i * 10;
            rwLockPool.submit(() -> {
                try {
                    rwLockDemo.write(value);
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
            });
        }
        
        rwLockPool.shutdown();
        rwLockPool.awaitTermination(3, TimeUnit.SECONDS);
    }
}

// 读写锁示例
class ReadWriteLockDemo {
    private int value = 0;
    private final ReadWriteLock rwLock = new ReentrantReadWriteLock();
    private final Lock readLock = rwLock.readLock();
    private final Lock writeLock = rwLock.writeLock();
    
    // 读操作 - 可以多个线程同时读
    public void read() throws InterruptedException {
        readLock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + " 开始读取值: " + value);
            Thread.sleep(100); // 模拟读操作
            System.out.println(Thread.currentThread().getName() + " 读取完成");
        } finally {
            readLock.unlock();
        }
    }
    
    // 写操作 - 只能一个线程写
    public void write(int newValue) throws InterruptedException {
        writeLock.lock();
        try {
            System.out.println(Thread.currentThread().getName() + " 开始写入值: " + newValue);
            Thread.sleep(200); // 模拟写操作
            value = newValue;
            System.out.println(Thread.currentThread().getName() + " 写入完成，新值: " + value);
        } finally {
            writeLock.unlock();
        }
    }
}

// 自定义拒绝策略
class CustomRejectionPolicy implements RejectedExecutionHandler {
    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
        System.out.println("任务被拒绝执行: " + r.toString());
        // 可以根据需要进行日志记录、任务保存等处理
    }
}

// CompletableFuture示例（Java 8+）
class CompletableFutureDemo {
    public static void main(String[] args) throws Exception {
        System.out.println("\n===== CompletableFuture示例 =====");
        
        // 创建CompletableFuture
        CompletableFuture<String> future1 = CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(1000);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            return "任务1结果";
        });
        
        CompletableFuture<String> future2 = CompletableFuture.supplyAsync(() -> {
            try {
                Thread.sleep(500);
            } catch (InterruptedException e) {
                e.printStackTrace();
            }
            return "任务2结果";
        });
        
        // 组合多个CompletableFuture
        CompletableFuture<String> combinedFuture = future1.thenCombine(future2, 
            (result1, result2) -> result1 + " + " + result2);
        
        // 等待结果
        String result = combinedFuture.get();
        System.out.println("组合结果: " + result);
        
        // 异常处理
        CompletableFuture<String> exceptionFuture = CompletableFuture.supplyAsync(() -> {
            // 确保返回String类型
            if (true) {
                throw new RuntimeException("出错了");
            }
            return "不会执行到这里";
        }).exceptionally(ex -> {
            System.out.println("捕获到异常: " + ex.getMessage());
            return "默认结果"; // 明确返回String类型
        });
        
        System.out.println("异常处理后的结果: " + exceptionFuture.get());
    }
}