package lock_demo;

import java.util.concurrent.locks.*;
import java.util.concurrent.*;
import java.util.*;

/**
 * Lock 实际应用场景示例
 * 
 * 本类演示 Lock 在实际开发中的常见应用场景：
 * 1. 线程安全的计数器
 * 2. 生产者-消费者模式
 * 3. 读写分离的数据结构
 * 4. 限流器
 * 5. 缓存实现
 */
public class LockPracticalExamples {
    
    // ========== 1. 线程安全的计数器 ==========
    /**
     * 使用 ReentrantLock 实现线程安全的计数器
     */
    public static class SafeCounter {
        private int count = 0;
        private final ReentrantLock lock = new ReentrantLock();
        
        public void increment() {
            lock.lock();
            try {
                count++;
            } finally {
                lock.unlock();
            }
        }
        
        public int getCount() {
            lock.lock();
            try {
                return count;
            } finally {
                lock.unlock();
            }
        }
    }
    
    // ========== 2. 生产者-消费者模式 ==========
    /**
     * 使用 Condition 实现生产者-消费者模式
     * 比 wait/notify 更灵活，可以有多个条件
     */
    public static class ProducerConsumer {
        private final Queue<String> queue = new LinkedList<>();
        private final int MAX_SIZE = 10;
        private final ReentrantLock lock = new ReentrantLock();
        private final Condition notFull = lock.newCondition();  // 队列未满条件
        private final Condition notEmpty = lock.newCondition(); // 队列非空条件
        
        public void produce(String item) throws InterruptedException {
            lock.lock();
            try {
                // 等待队列未满
                while (queue.size() == MAX_SIZE) {
                    System.out.println("生产者等待：队列已满");
                    notFull.await();
                }
                queue.offer(item);
                System.out.println("生产者生产: " + item + "，队列大小: " + queue.size());
                notEmpty.signal(); // 通知消费者
            } finally {
                lock.unlock();
            }
        }
        
        public String consume() throws InterruptedException {
            lock.lock();
            try {
                // 等待队列非空
                while (queue.isEmpty()) {
                    System.out.println("消费者等待：队列为空");
                    notEmpty.await();
                }
                String item = queue.poll();
                System.out.println("消费者消费: " + item + "，队列大小: " + queue.size());
                notFull.signal(); // 通知生产者
                return item;
            } finally {
                lock.unlock();
            }
        }
    }
    
    // ========== 3. 读写分离的缓存 ==========
    /**
     * 使用 ReadWriteLock 实现读写分离的缓存
     * 读多写少的场景性能更好
     */
    public static class ReadWriteCache<K, V> {
        private final Map<K, V> cache = new HashMap<>();
        private final ReadWriteLock lock = new ReentrantReadWriteLock();
        private final Lock readLock = lock.readLock();
        private final Lock writeLock = lock.writeLock();
        
        public V get(K key) {
            readLock.lock();
            try {
                return cache.get(key);
            } finally {
                readLock.unlock();
            }
        }
        
        public void put(K key, V value) {
            writeLock.lock();
            try {
                cache.put(key, value);
            } finally {
                writeLock.unlock();
            }
        }
        
        public void clear() {
            writeLock.lock();
            try {
                cache.clear();
            } finally {
                writeLock.unlock();
            }
        }
        
        public int size() {
            readLock.lock();
            try {
                return cache.size();
            } finally {
                readLock.unlock();
            }
        }
    }
    
    // ========== 4. 限流器（Rate Limiter） ==========
    /**
     * 使用 tryLock 实现简单的限流器
     * 如果无法获取锁，说明当前请求过多
     */
    public static class SimpleRateLimiter {
        private final ReentrantLock lock = new ReentrantLock();
        private final int maxConcurrent;
        private int currentCount = 0;
        
        public SimpleRateLimiter(int maxConcurrent) {
            this.maxConcurrent = maxConcurrent;
        }
        
        public boolean tryAcquire() {
            if (lock.tryLock()) {
                try {
                    if (currentCount < maxConcurrent) {
                        currentCount++;
                        return true;
                    }
                } finally {
                    lock.unlock();
                }
            }
            return false;
        }
        
        public void release() {
            lock.lock();
            try {
                if (currentCount > 0) {
                    currentCount--;
                }
            } finally {
                lock.unlock();
            }
        }
    }
    
    // ========== 5. 可重入的银行账户 ==========
    /**
     * 演示可重入锁在实际业务中的应用
     */
    public static class BankAccount {
        private double balance;
        private final ReentrantLock lock = new ReentrantLock();
        
        public BankAccount(double initialBalance) {
            this.balance = initialBalance;
        }
        
        public void deposit(double amount) {
            lock.lock();
            try {
                balance += amount;
                System.out.println(Thread.currentThread().getName() + 
                    " 存款: " + amount + "，余额: " + balance);
            } finally {
                lock.unlock();
            }
        }
        
        public boolean withdraw(double amount) {
            lock.lock();
            try {
                if (balance >= amount) {
                    balance -= amount;
                    System.out.println(Thread.currentThread().getName() + 
                        " 取款: " + amount + "，余额: " + balance);
                    return true;
                } else {
                    System.out.println(Thread.currentThread().getName() + 
                        " 取款失败：余额不足");
                    return false;
                }
            } finally {
                lock.unlock();
            }
        }
        
        /**
         * 转账操作：需要获取两个账户的锁
         * 注意：实际应用中需要防止死锁（统一锁的获取顺序）
         */
        public boolean transfer(BankAccount target, double amount) {
            // 统一锁的获取顺序：按对象地址排序，避免死锁
            ReentrantLock firstLock = this.lock.hashCode() < target.lock.hashCode() 
                ? this.lock : target.lock;
            ReentrantLock secondLock = firstLock == this.lock ? target.lock : this.lock;
            
            firstLock.lock();
            try {
                secondLock.lock();
                try {
                    if (this.balance >= amount) {
                        this.balance -= amount;
                        target.balance += amount;
                        System.out.println(Thread.currentThread().getName() + 
                            " 转账: " + amount + " 成功");
                        return true;
                    }
                    return false;
                } finally {
                    secondLock.unlock();
                }
            } finally {
                firstLock.unlock();
            }
        }
        
        public double getBalance() {
            lock.lock();
            try {
                return balance;
            } finally {
                lock.unlock();
            }
        }
    }
    
    // ========== 6. 使用 StampedLock 的乐观读 ==========
    /**
     * StampedLock 适用于读多写少的场景
     */
    public static class OptimisticReadExample {
        private int data = 0;
        private final StampedLock lock = new StampedLock();
        
        public int read() {
            // 尝试乐观读
            long stamp = lock.tryOptimisticRead();
            int value = data;
            
            // 验证是否有写操作
            if (!lock.validate(stamp)) {
                // 升级为悲观读锁
                stamp = lock.readLock();
                try {
                    value = data;
                } finally {
                    lock.unlockRead(stamp);
                }
            }
            return value;
        }
        
        public void write(int value) {
            long stamp = lock.writeLock();
            try {
                data = value;
            } finally {
                lock.unlockWrite(stamp);
            }
        }
    }
    
    // ========== 测试方法 ==========
    public static void main(String[] args) throws InterruptedException {
        System.out.println("========== 1. 线程安全的计数器 ==========");
        SafeCounter counter = new SafeCounter();
        ExecutorService executor = Executors.newFixedThreadPool(10);
        CountDownLatch latch = new CountDownLatch(100);
        
        for (int i = 0; i < 100; i++) {
            executor.submit(() -> {
                counter.increment();
                latch.countDown();
            });
        }
        latch.await();
        System.out.println("最终计数: " + counter.getCount());
        
        System.out.println("\n========== 2. 生产者-消费者模式 ==========");
        ProducerConsumer pc = new ProducerConsumer();
        Thread producer = new Thread(() -> {
            try {
                for (int i = 0; i < 5; i++) {
                    pc.produce("Item-" + i);
                    Thread.sleep(100);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        Thread consumer = new Thread(() -> {
            try {
                for (int i = 0; i < 5; i++) {
                    pc.consume();
                    Thread.sleep(150);
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        });
        
        producer.start();
        consumer.start();
        producer.join();
        consumer.join();
        
        System.out.println("\n========== 3. 读写分离的缓存 ==========");
        ReadWriteCache<String, String> cache = new ReadWriteCache<>();
        cache.put("key1", "value1");
        cache.put("key2", "value2");
        
        // 多个读线程可以同时执行
        for (int i = 0; i < 5; i++) {
            final int index = i;
            new Thread(() -> {
                System.out.println("读取 key1: " + cache.get("key1"));
            }, "ReadThread-" + index).start();
        }
        Thread.sleep(500);
        
        System.out.println("\n========== 4. 限流器 ==========");
        SimpleRateLimiter limiter = new SimpleRateLimiter(3);
        for (int i = 0; i < 10; i++) {
            final int index = i;
            new Thread(() -> {
                if (limiter.tryAcquire()) {
                    System.out.println("请求 " + index + " 被接受");
                    try {
                        Thread.sleep(1000);
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                    }
                    limiter.release();
                } else {
                    System.out.println("请求 " + index + " 被限流");
                }
            }).start();
        }
        Thread.sleep(2000);
        
        System.out.println("\n========== 5. 银行账户转账 ==========");
        BankAccount account1 = new BankAccount(1000);
        BankAccount account2 = new BankAccount(500);
        
        new Thread(() -> account1.transfer(account2, 200), "Transfer1").start();
        new Thread(() -> account2.transfer(account1, 100), "Transfer2").start();
        Thread.sleep(1000);
        
        System.out.println("账户1余额: " + account1.getBalance());
        System.out.println("账户2余额: " + account2.getBalance());
        
        executor.shutdown();
    }
}

