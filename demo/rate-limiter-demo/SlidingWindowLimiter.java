package rate_limiter_demo;

import java.util.concurrent.atomic.AtomicInteger;

/**
 * 固定窗口计数限流（简化版滑动窗口）：时间窗口内最多 limit 次请求。
 */
public class SlidingWindowLimiter {
    private final int limit;
    private final long windowMs;
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

    public static void main(String[] args) throws InterruptedException {
        SlidingWindowLimiter limiter = new SlidingWindowLimiter(2, 1000);
        for (int i = 0; i < 5; i++) {
            System.out.println(i + ": " + limiter.tryAcquire());
        }
        Thread.sleep(1100);
        System.out.println("after reset: " + limiter.tryAcquire());
    }
}
