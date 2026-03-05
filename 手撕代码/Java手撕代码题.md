# Java 手撕代码题（校招常考）

> 算法题在单独文件夹，本文件仅整理 **Java 语言/并发/设计模式/数据结构实现** 类手撕题。

---

## 一、单例模式（必考）

### 1. 懒汉式 + 双检锁 DCL（线程安全）

```java
public class Singleton {
    private static volatile Singleton instance;  // volatile 防止指令重排

    private Singleton() {}

    public static Singleton getInstance() {
        if (instance == null) {
            synchronized (Singleton.class) {
                if (instance == null) {
                    instance = new Singleton();
                }
            }
        }
        return instance;
    }
}
```

**要点**：`volatile` 防止 new 时「分配内存→初始化→引用赋值」被重排导致半初始化对象被读到。

### 2. 饿汉式（类加载即创建）

```java
public class Singleton {
    private static final Singleton INSTANCE = new Singleton();
    private Singleton() {}
    public static Singleton getInstance() {
        return INSTANCE;
    }
}
```

### 3. 静态内部类（懒加载 + 线程安全）

```java
public class Singleton {
    private Singleton() {}

    private static class Holder {
        private static final Singleton INSTANCE = new Singleton();
    }

    public static Singleton getInstance() {
        return Holder.INSTANCE;
    }
}
```

---

## 二、生产者-消费者（阻塞队列版）

```java
import java.util.LinkedList;
import java.util.Queue;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class BlockingQueue<T> {
    private final Queue<T> queue = new LinkedList<>();
    private final int capacity;
    private final Lock lock = new ReentrantLock();
    private final Condition notFull = lock.newCondition();
    private final Condition notEmpty = lock.newCondition();

    public BlockingQueue(int capacity) {
        this.capacity = capacity;
    }

    public void put(T item) throws InterruptedException {
        lock.lock();
        try {
            while (queue.size() == capacity) {
                notFull.await();
            }
            queue.offer(item);
            notEmpty.signal();
        } finally {
            lock.unlock();
        }
    }

    public T take() throws InterruptedException {
        lock.lock();
        try {
            while (queue.isEmpty()) {
                notEmpty.await();
            }
            T item = queue.poll();
            notFull.signal();
            return item;
        } finally {
            lock.unlock();
        }
    }
}
```

**扩展**：用 `wait/notify` 实现、用 `ArrayBlockingQueue` 直接写生产者消费者示例。

---

## 三、手写 LRU（Least Recently Used）

### 方式一：LinkedHashMap（面试可先说思路再写）

```java
import java.util.LinkedHashMap;
import java.util.Map;

public class LRUCache<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LRUCache(int capacity) {
        super(capacity, 0.75f, true);  // accessOrder=true 按访问顺序
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }
}
```

### 方式二：HashMap + 双向链表（常要求手写）

```java
import java.util.HashMap;
import java.util.Map;

public class LRUCache<K, V> {
    static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev, next;
        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    private final Map<K, Node<K, V>> map = new HashMap<>();
    private final int capacity;
    private final Node<K, V> head = new Node<>(null, null);
    private final Node<K, V> tail = new Node<>(null, null);

    public LRUCache(int capacity) {
        this.capacity = capacity;
        head.next = tail;
        tail.prev = head;
    }

    public V get(K key) {
        Node<K, V> node = map.get(key);
        if (node == null) return null;
        moveToHead(node);
        return node.value;
    }

    public void put(K key, V value) {
        Node<K, V> node = map.get(key);
        if (node != null) {
            node.value = value;
            moveToHead(node);
            return;
        }
        node = new Node<>(key, value);
        map.put(key, node);
        addToHead(node);
        if (map.size() > capacity) {
            Node<K, V> removed = removeTail();
            map.remove(removed.key);
        }
    }

    private void moveToHead(Node<K, V> node) {
        removeNode(node);
        addToHead(node);
    }

    private void addToHead(Node<K, V> node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    private void removeNode(Node<K, V> node) {
        node.prev.next = node.next;
        node.next.prev = node.prev;
    }

    private Node<K, V> removeTail() {
        Node<K, V> node = tail.prev;
        removeNode(node);
        return node;
    }
}
```

---

## 四、两个线程交替打印（1-100 或 ABAB）

### 用 synchronized + wait/notify

```java
public class AlternatePrint {
    private static final Object lock = new Object();
    private static int count = 1;
    private static final int MAX = 100;

    public static void main(String[] args) {
        Thread t1 = new Thread(() -> {
            synchronized (lock) {
                while (count <= MAX) {
                    if (count % 2 == 1) {
                        System.out.println(Thread.currentThread().getName() + ": " + count++);
                        lock.notify();
                    } else {
                        try {
                            lock.wait();
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
                lock.notify();
            }
        }, "A");

        Thread t2 = new Thread(() -> {
            synchronized (lock) {
                while (count <= MAX) {
                    if (count % 2 == 0) {
                        System.out.println(Thread.currentThread().getName() + ": " + count++);
                        lock.notify();
                    } else {
                        try {
                            lock.wait();
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                        }
                    }
                }
                lock.notify();
            }
        }, "B");

        t1.start();
        t2.start();
    }
}
```

### 用 ReentrantLock + Condition（可扩展多线程）

```java
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class AlternatePrintLock {
    private static final Lock lock = new ReentrantLock();
    private static final Condition cond = lock.newCondition();
    private static int count = 1;
    private static final int MAX = 100;

    public static void main(String[] args) {
        Thread t1 = new Thread(() -> {
            lock.lock();
            try {
                while (count <= MAX) {
                    if (count % 2 == 1) {
                        System.out.println("A: " + count++);
                        cond.signal();
                    } else {
                        cond.await();
                    }
                }
                cond.signal();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        });

        Thread t2 = new Thread(() -> {
            lock.lock();
            try {
                while (count <= MAX) {
                    if (count % 2 == 0) {
                        System.out.println("B: " + count++);
                        cond.signal();
                    } else {
                        cond.await();
                    }
                }
                cond.signal();
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        });

        t1.start();
        t2.start();
    }
}
```

---

## 五、三个线程顺序打印 ABC（循环多轮）

```java
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class PrintABC {
    private static final Lock lock = new ReentrantLock();
    private static final Condition condA = lock.newCondition();
    private static final Condition condB = lock.newCondition();
    private static final Condition condC = lock.newCondition();
    private static int state = 0;  // 0-A, 1-B, 2-C

    public static void main(String[] args) {
        Thread a = new Thread(() -> {
            lock.lock();
            try {
                for (int i = 0; i < 5; i++) {
                    while (state != 0) condA.await();
                    System.out.print("A");
                    state = 1;
                    condB.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        });

        Thread b = new Thread(() -> {
            lock.lock();
            try {
                for (int i = 0; i < 5; i++) {
                    while (state != 1) condB.await();
                    System.out.print("B");
                    state = 2;
                    condC.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        });

        Thread c = new Thread(() -> {
            lock.lock();
            try {
                for (int i = 0; i < 5; i++) {
                    while (state != 2) condC.await();
                    System.out.print("C");
                    state = 0;
                    condA.signal();
                }
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            } finally {
                lock.unlock();
            }
        });

        a.start();
        b.start();
        c.start();
    }
}
```

---

## 六、手写简单 ArrayList（核心方法）

```java
import java.util.Arrays;

public class MyArrayList<E> {
    private Object[] elementData;
    private int size;
    private static final int DEFAULT_CAPACITY = 10;

    public MyArrayList() {
        this.elementData = new Object[DEFAULT_CAPACITY];
    }

    public MyArrayList(int initialCapacity) {
        this.elementData = new Object[Math.max(initialCapacity, 0)];
    }

    public void add(E e) {
        ensureCapacity(size + 1);
        elementData[size++] = e;
    }

    public void add(int index, E e) {
        rangeCheckForAdd(index);
        ensureCapacity(size + 1);
        System.arraycopy(elementData, index, elementData, index + 1, size - index);
        elementData[index] = e;
        size++;
    }

    @SuppressWarnings("unchecked")
    public E get(int index) {
        rangeCheck(index);
        return (E) elementData[index];
    }

    @SuppressWarnings("unchecked")
    public E remove(int index) {
        rangeCheck(index);
        E old = (E) elementData[index];
        int numMoved = size - index - 1;
        if (numMoved > 0) {
            System.arraycopy(elementData, index + 1, elementData, index, numMoved);
        }
        elementData[--size] = null;
        return old;
    }

    public int size() {
        return size;
    }

    private void ensureCapacity(int minCapacity) {
        if (minCapacity > elementData.length) {
            int newCapacity = elementData.length + (elementData.length >> 1);
            if (newCapacity < minCapacity) newCapacity = minCapacity;
            elementData = Arrays.copyOf(elementData, newCapacity);
        }
    }

    private void rangeCheck(int index) {
        if (index < 0 || index >= size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }

    private void rangeCheckForAdd(int index) {
        if (index < 0 || index > size) {
            throw new IndexOutOfBoundsException("Index: " + index + ", Size: " + size);
        }
    }
}
```

---

## 七、手写简单 HashMap（put/get，数组+链表）

```java
public class MyHashMap<K, V> {
    static class Node<K, V> {
        final int hash;
        final K key;
        V value;
        Node<K, V> next;
        Node(int hash, K key, V value, Node<K, V> next) {
            this.hash = hash;
            this.key = key;
            this.value = value;
            this.next = next;
        }
    }

    private Node<K, V>[] table;
    private int size;
    private static final int DEFAULT_CAPACITY = 16;
    private static final float LOAD_FACTOR = 0.75f;

    @SuppressWarnings("unchecked")
    public MyHashMap() {
        table = (Node<K, V>[]) new Node[DEFAULT_CAPACITY];
    }

    static int hash(Object key) {
        int h = key == null ? 0 : key.hashCode();
        return h ^ (h >>> 16);
    }

    public V put(K key, V value) {
        int hash = hash(key);
        int index = (table.length - 1) & hash;
        Node<K, V> p = table[index];
        for (; p != null; p = p.next) {
            if (p.hash == hash && (key == p.key || (key != null && key.equals(p.key)))) {
                V old = p.value;
                p.value = value;
                return old;
            }
        }
        table[index] = new Node<>(hash, key, value, table[index]);
        size++;
        if (size > table.length * LOAD_FACTOR) {
            resize();
        }
        return null;
    }

    public V get(K key) {
        int hash = hash(key);
        int index = (table.length - 1) & hash;
        for (Node<K, V> p = table[index]; p != null; p = p.next) {
            if (p.hash == hash && (key == p.key || (key != null && key.equals(p.key)))) {
                return p.value;
            }
        }
        return null;
    }

    @SuppressWarnings("unchecked")
    private void resize() {
        Node<K, V>[] oldTab = table;
        table = (Node<K, V>[]) new Node[oldTab.length << 1];
        size = 0;
        for (Node<K, V> node : oldTab) {
            while (node != null) {
                put((K) node.key, node.value);
                node = node.next;
            }
        }
    }

    public int size() {
        return size;
    }
}
```

---

## 八、死锁示例（口述 + 代码）

```java
public class DeadLockDemo {
    private static final Object A = new Object();
    private static final Object B = new Object();

    public static void main(String[] args) {
        new Thread(() -> {
            synchronized (A) {
                System.out.println("Thread1 持有 A");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                synchronized (B) {
                    System.out.println("Thread1 持有 B");
                }
            }
        }, "T1").start();

        new Thread(() -> {
            synchronized (B) {
                System.out.println("Thread2 持有 B");
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                synchronized (A) {
                    System.out.println("Thread2 持有 A");
                }
            }
        }, "T2").start();
    }
}
```

**如何避免**：统一加锁顺序、使用 tryLock 超时、死锁检测。

---

## 九、用 wait/notify 实现生产者消费者

```java
public class WaitNotifyProducerConsumer {
    private static final int CAPACITY = 5;
    private static final LinkedList<Integer> queue = new LinkedList<>();
    private static final Object lock = new Object();

    static class Producer implements Runnable {
        @Override
        public void run() {
            int value = 0;
            while (true) {
                synchronized (lock) {
                    while (queue.size() == CAPACITY) {
                        try {
                            lock.wait();
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            return;
                        }
                    }
                    queue.add(value);
                    System.out.println("Producer 生产: " + value++);
                    lock.notifyAll();
                }
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }

    static class Consumer implements Runnable {
        @Override
        public void run() {
            while (true) {
                synchronized (lock) {
                    while (queue.isEmpty()) {
                        try {
                            lock.wait();
                        } catch (InterruptedException e) {
                            Thread.currentThread().interrupt();
                            return;
                        }
                    }
                    int value = queue.poll();
                    System.out.println("Consumer 消费: " + value);
                    lock.notifyAll();
                }
                try {
                    Thread.sleep(100);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
            }
        }
    }

    public static void main(String[] args) {
        new Thread(new Producer()).start();
        new Thread(new Consumer()).start();
    }
}
```

---

## 十、手写简单线程池（固定 worker + 任务队列）

```java
import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;

public class SimpleThreadPool {
    private final BlockingQueue<Runnable> workQueue;
    private final Thread[] workers;
    private final AtomicBoolean shutdown = new AtomicBoolean(false);

    public SimpleThreadPool(int coreSize, int queueCapacity) {
        this.workQueue = new LinkedBlockingQueue<>(queueCapacity);
        this.workers = new Thread[coreSize];
        for (int i = 0; i < coreSize; i++) {
            workers[i] = new Worker("worker-" + i);
            workers[i].start();
        }
    }

    public void submit(Runnable task) {
        if (shutdown.get()) {
            throw new IllegalStateException("pool is shutdown");
        }
        try {
            workQueue.put(task);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }

    public void shutdown() {
        shutdown.set(true);
        for (Thread w : workers) {
            w.interrupt();
        }
    }

    class Worker extends Thread {
        Worker(String name) {
            super(name);
        }
        @Override
        public void run() {
            while (!shutdown.get() || !workQueue.isEmpty()) {
                try {
                    Runnable task = workQueue.take();
                    task.run();
                } catch (InterruptedException e) {
                    if (shutdown.get()) break;
                    Thread.currentThread().interrupt();
                }
            }
        }
    }
}
```

**要点**：固定线程数、无界或有限队列、worker 循环 take 执行；可扩展 submit 返回 Future（用另一队列存结果，get 时 take）。

---

## 十一、限流器

### 1. 令牌桶（固定速率放令牌，取到令牌才通过）

```java
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.LockSupport;

public class TokenBucketLimiter {
    private final int capacity;           // 桶容量
    private final AtomicInteger tokens;   // 当前令牌数
    private long lastRefillTime;          // 上次补充时间
    private final long refillIntervalNs;  // 每颗令牌间隔（纳秒）

    public TokenBucketLimiter(int capacity, int permitsPerSecond) {
        this.capacity = capacity;
        this.tokens = new AtomicInteger(capacity);
        this.lastRefillTime = System.nanoTime();
        this.refillIntervalNs = 1_000_000_000L / permitsPerSecond;
    }

    public boolean tryAcquire() {
        refill();
        int n;
        do {
            n = tokens.get();
            if (n <= 0) return false;
        } while (!tokens.compareAndSet(n, n - 1));
        return true;
    }

    public void acquire() {
        while (!tryAcquire()) {
            LockSupport.parkNanos(refillIntervalNs);
        }
    }

    private void refill() {
        long now = System.nanoTime();
        long need = (now - lastRefillTime) / refillIntervalNs;
        if (need <= 0) return;
        lastRefillTime = now;
        int current, next;
        do {
            current = tokens.get();
            next = Math.min(capacity, current + (int) need);
        } while (next > current && !tokens.compareAndSet(current, next));
    }
}
```

### 2. 滑动窗口计数（简化：固定窗口内限制次数）

```java
import java.util.concurrent.atomic.AtomicInteger;

public class SlidingWindowLimiter {
    private final int limit;           // 时间窗口内最大请求数
    private final long windowMs;       // 窗口大小（毫秒）
    private final AtomicInteger count = new AtomicInteger(0);
    private volatile long windowStart = System.currentTimeMillis();

    public SlidingWindowLimiter(int limit, long windowMs) {
        this.limit = limit;
        this.windowMs = windowMs;
    }

    public synchronized boolean tryAcquire() {
        long now = System.currentTimeMillis();
        if (now - windowStart >= windowMs) {
            windowStart = now;
            count.set(0);
        }
        if (count.get() >= limit) return false;
        count.incrementAndGet();
        return true;
    }
}
```

---

## 十二、带过期的缓存（过期自动删）

```java
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.DelayQueue;
import java.util.concurrent.Delayed;
import java.util.concurrent.TimeUnit;

public class ExpireCache<K, V> {
    private final ConcurrentHashMap<K, Node<K, V>> map = new ConcurrentHashMap<>();
    private final DelayQueue<Node<K, V>> delayQueue = new DelayQueue<>();

    static class Node<K, V> implements Delayed {
        K key;
        V value;
        long expireTime;

        Node(K key, V value, long ttlMs) {
            this.key = key;
            this.value = value;
            this.expireTime = System.currentTimeMillis() + ttlMs;
        }

        @Override
        public long getDelay(TimeUnit unit) {
            return unit.convert(expireTime - System.currentTimeMillis(), TimeUnit.MILLISECONDS);
        }
        @Override
        public int compareTo(Delayed o) {
            return Long.compare(this.expireTime, ((Node<?, ?>) o).expireTime);
        }
    }

    public ExpireCache() {
        Thread cleaner = new Thread(() -> {
            while (true) {
                try {
                    Node<K, V> node = delayQueue.take();
                    map.remove(node.key, node);
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    break;
                }
            }
        });
        cleaner.setDaemon(true);
        cleaner.start();
    }

    public void put(K key, V value, long ttlMs) {
        Node<K, V> node = new Node<>(key, value, ttlMs);
        map.put(key, node);
        delayQueue.offer(node);
    }

    public V get(K key) {
        Node<K, V> node = map.get(key);
        return node == null ? null : node.value;
    }
}
```

---

## 十三、公平锁 vs 非公平锁（理解即可）

```java
// 非公平锁：新线程可能直接抢到锁，吞吐高，可能饥饿
ReentrantLock nonFair = new ReentrantLock();           // 默认 false

// 公平锁：严格按等待顺序获得锁，避免饥饿，吞吐一般更低
ReentrantLock fair = new ReentrantLock(true);

// 使用方式相同
fair.lock();
try {
    // ...
} finally {
    fair.unlock();
}
```

**要点**：公平锁内部用 FIFO 队列排队；非公平 lock() 时先 CAS 抢一次，抢不到再排队。

---

## 十四、其他高频考点（可扩展手写）

| 考点 | 说明 |
|------|------|
| 深拷贝 | 实现 Cloneable 或序列化/反序列化，注意引用类型递归拷贝 |
| 反转链表 | 见算法文件夹 |
| 多线程打印奇偶数 | 同「两个线程交替打印」，条件改为奇偶 |
| 实现 Callable + Future 取结果 | 用阻塞队列存结果，get() 时 take |

---

**建议**：单例 DCL、LRU（链表+HashMap）、生产者消费者、交替打印至少能闭卷写；ArrayList/HashMap 能讲清扩容与 put 流程；冲大厂可加练线程池、限流、带过期缓存。
