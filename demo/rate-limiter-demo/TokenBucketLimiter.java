package rate_limiter_demo;

import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.locks.LockSupport;

/**
 * 令牌桶限流：固定速率放令牌，取到令牌才通过；允许突发（桶内有令牌时）。
 */
public class TokenBucketLimiter {
    private final int capacity;
    private final AtomicInteger tokens;
    private long lastRefillTime;
    private final long refillIntervalNs;

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

    public static void main(String[] args) throws InterruptedException {
        TokenBucketLimiter limiter = new TokenBucketLimiter(2, 2);
        for (int i = 0; i < 5; i++) {
            System.out.println(i + ": " + limiter.tryAcquire());
            Thread.sleep(200);
        }
    }
}
