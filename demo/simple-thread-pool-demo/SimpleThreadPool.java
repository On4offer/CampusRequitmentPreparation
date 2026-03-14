package simple_thread_pool_demo;

import java.util.concurrent.BlockingQueue;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicBoolean;

/**
 * 手写简单线程池：固定 worker 数 + 任务队列，submit 入队，worker 循环 take 执行。
 * 考点：核心参数、执行流程（核心数→队列→最大数→拒绝）。
 */
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

    public static void main(String[] args) throws InterruptedException {
        SimpleThreadPool pool = new SimpleThreadPool(2, 10);
        for (int i = 0; i < 5; i++) {
            final int id = i;
            pool.submit(() -> System.out.println(Thread.currentThread().getName() + " run task " + id));
        }
        Thread.sleep(2000);
        pool.shutdown();
    }
}
