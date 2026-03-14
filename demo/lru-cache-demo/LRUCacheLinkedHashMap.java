package lru_cache_demo;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * 基于 LinkedHashMap 的 LRU 缓存（accessOrder=true + removeEldestEntry）。
 * 面试可先说思路再写此类。
 */
public class LRUCacheLinkedHashMap<K, V> extends LinkedHashMap<K, V> {
    private final int capacity;

    public LRUCacheLinkedHashMap(int capacity) {
        super(capacity, 0.75f, true);  // accessOrder=true 按访问顺序
        this.capacity = capacity;
    }

    @Override
    protected boolean removeEldestEntry(Map.Entry<K, V> eldest) {
        return size() > capacity;
    }

    public static void main(String[] args) {
        LRUCacheLinkedHashMap<Integer, String> cache = new LRUCacheLinkedHashMap<>(2);
        cache.put(1, "a");
        cache.put(2, "b");
        cache.get(1);
        cache.put(3, "c");  // 2 被淘汰
        System.out.println(cache);  // {1=a, 3=c}
    }
}
