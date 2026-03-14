package redis_distributed_lock_demo;

import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.TimeUnit;

/**
 * Redis 分布式锁：本地用 ConcurrentHashMap 模拟 Redis，逻辑与真实 Redis 版一致，便于面试口述与伪代码对照。
 * 真实实现需替换为 Redis 客户端（Jedis/Lettuce）的 set NX EX、eval Lua 等。
 *
 * 考点：setNX + 过期、唯一 value 防误删、Lua 原子解锁、看门狗续期（Redisson）。
 */
public class RedisLockPseudocode {

    // ========== 模拟 Redis：真实环境为 Redis 的 key-value ==========
    private static final ConcurrentHashMap<String, String> REDIS = new ConcurrentHashMap<>();

    public static boolean setIfAbsent(String key, String value, long expireMs) {
        if (REDIS.putIfAbsent(key, value) != null) return false;
        // 真实 Redis: SET key value NX PX expireMs
        scheduleExpire(key, expireMs);
        return true;
    }

    public static void set(String key, String value) {
        REDIS.put(key, value);
    }

    public static String get(String key) {
        return REDIS.get(key);
    }

    public static void del(String key) {
        REDIS.remove(key);
    }

    private static void scheduleExpire(String key, long expireMs) {
        new Thread(() -> {
            try {
                Thread.sleep(expireMs);
                REDIS.remove(key);
            } catch (InterruptedException e) {
                Thread.currentThread().interrupt();
            }
        }).start();
    }

    // ========== 分布式锁实现 ==========

    private final String lockKey;
    private final long expireMs;
    private String lockValue;  // 唯一 value，防止误删其他客户端的锁

    public RedisLockPseudocode(String lockKey, long expireMs) {
        this.lockKey = lockKey;
        this.expireMs = expireMs;
    }

    /** 加锁：SET key uniqueValue NX PX expireMs */
    public boolean tryLock() {
        lockValue = UUID.randomUUID().toString();
        return setIfAbsent(lockKey, lockValue, expireMs);
    }

    /** 加锁：自旋 + 过期时间 */
    public void lock() throws InterruptedException {
        while (!tryLock()) {
            TimeUnit.MILLISECONDS.sleep(50);
        }
    }

    /**
     * 解锁：只能删自己的锁，用 Lua 保证「判断 value + 删除」原子性。
     * 真实 Redis: EVAL "if redis.call('get', KEYS[1]) == ARGV[1] then return redis.call('del', KEYS[1]) else return 0 end" 1 key value
     */
    public void unlock() {
        String v = get(lockKey);
        if (lockValue != null && lockValue.equals(v)) {
            del(lockKey);
        }
        // 注意：此处非原子，真实必须用 Lua。见 README 中 Lua 脚本。
    }

    public static void main(String[] args) throws InterruptedException {
        RedisLockPseudocode lock = new RedisLockPseudocode("order:1001", 5000);
        if (lock.tryLock()) {
            try {
                System.out.println("执行业务");
            } finally {
                lock.unlock();
            }
        } else {
            System.out.println("获取锁失败");
        }
    }
}
