package simple_future_demo;

import java.util.concurrent.*;

/**
 * 手写简易 Future：用阻塞队列存结果，worker 执行 Callable 后 put 结果，get() 时 take 阻塞取。
 * 大厂手撕题「实现 Callable + Future 取结果」的典型手写实现方式。
 */
public class SimpleFuture<V> implements Future<V> {
    private final BlockingQueue<V> resultQueue = new LinkedBlockingQueue<>(1);
    private volatile boolean done;
    private volatile boolean cancelled;

    /** 在单独线程中执行 task，结果放入 resultQueue */
    public static <V> SimpleFuture<V> submit(Callable<V> task) {
        SimpleFuture<V> future = new SimpleFuture<>();
        Thread t = new Thread(() -> {
            try {
                V result = task.call();
                future.resultQueue.put(result);
                future.done = true;
            } catch (Exception e) {
                future.done = true;
                if (!(e instanceof InterruptedException)) {
                    throw new RuntimeException(e);
                }
            }
        });
        t.start();
        return future;
    }

    @Override
    public V get() throws InterruptedException, ExecutionException {
        if (cancelled) throw new CancellationException();
        if (done && !resultQueue.isEmpty()) {
            V v = resultQueue.poll();
            if (v != null) return v;
        }
        return resultQueue.take();
    }

    @Override
    public V get(long timeout, TimeUnit unit) throws InterruptedException, ExecutionException, TimeoutException {
        if (cancelled) throw new CancellationException();
        V v = resultQueue.poll();
        if (v != null) return v;
        v = resultQueue.poll(timeout, unit);
        if (v == null) throw new TimeoutException();
        return v;
    }

    @Override
    public boolean cancel(boolean mayInterruptIfRunning) {
        cancelled = true;
        return true;
    }

    @Override
    public boolean isCancelled() {
        return cancelled;
    }

    @Override
    public boolean isDone() {
        return done;
    }

    public static void main(String[] args) throws Exception {
        SimpleFuture<Integer> f = SimpleFuture.submit(() -> {
            Thread.sleep(300);
            return 42;
        });
        System.out.println("主线程可先做别的事");
        System.out.println("get() = " + f.get());
    }
}
