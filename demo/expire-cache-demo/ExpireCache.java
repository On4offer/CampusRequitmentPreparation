package expire_cache_demo;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.DelayQueue;
import java.util.concurrent.Delayed;
import java.util.concurrent.TimeUnit;

/**
 * 带过期的缓存：ConcurrentHashMap + DelayQueue，后台线程 take 过期元素并删除。
 * 考点：DelayQueue 按过期时间排序，take 阻塞到队首过期。
 */
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

    public static void main(String[] args) throws InterruptedException {
        ExpireCache<String, String> cache = new ExpireCache<>();
        cache.put("a", "A", 500);
        System.out.println(cache.get("a"));  // A
        Thread.sleep(600);
        System.out.println(cache.get("a"));  // null（已过期被清理）
    }
}
