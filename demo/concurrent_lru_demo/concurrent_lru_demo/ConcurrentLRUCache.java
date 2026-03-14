package concurrent_lru_demo;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.locks.ReentrantReadWriteLock;

/**
 * 线程安全 LRU：HashMap+双向链表 基础上，用 ReentrantReadWriteLock 保护；
 * get 用读锁（可并发读），put/移动节点用写锁。
 * 大厂可能考「LRU 的并发版」或「读写锁应用」。
 */
public class ConcurrentLRUCache<K, V> {
    static class Node<K, V> {
        K key;
        V value;
        Node<K, V> prev, next;
        Node(K key, V value) {
            this.key = key;
            this.value = value;
        }
    }

    private final ConcurrentHashMap<K, Node<K, V>> map = new ConcurrentHashMap<>();
    private final int capacity;
    private final Node<K, V> head = new Node<>(null, null);
    private final Node<K, V> tail = new Node<>(null, null);
    private final ReentrantReadWriteLock rwLock = new ReentrantReadWriteLock();

    public ConcurrentLRUCache(int capacity) {
        this.capacity = capacity;
        head.next = tail;
        tail.prev = head;
    }

    /** 先读锁查是否存在，再写锁移动；获取写锁后必须从 map 再取一次节点，避免升级间隙被淘汰导致链表错乱。 */
    public V get(K key) {
        rwLock.readLock().lock();
        try {
            Node<K, V> node = map.get(key);
            if (node == null) return null;
            rwLock.readLock().unlock();
            rwLock.writeLock().lock();
            try {
                Node<K, V> current = map.get(key);
                if (current == null) return null;  // 读锁释放后可能已被淘汰
                moveToHead(current);
                return current.value;
            } finally {
                rwLock.writeLock().unlock();
            }
        } finally {
            if (rwLock.getReadHoldCount() > 0) rwLock.readLock().unlock();
        }
    }

    /** 简化版 get：全程写锁，易实现；读多时可用上面「先读锁查再写锁移动」提升并发 */
    public V getSimple(K key) {
        rwLock.writeLock().lock();
        try {
            Node<K, V> node = map.get(key);
            if (node == null) return null;
            moveToHead(node);
            return node.value;
        } finally {
            rwLock.writeLock().unlock();
        }
    }

    public void put(K key, V value) {
        rwLock.writeLock().lock();
        try {
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
        } finally {
            rwLock.writeLock().unlock();
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

    public static void main(String[] args) {
        ConcurrentLRUCache<Integer, String> cache = new ConcurrentLRUCache<>(2);
        cache.put(1, "a");
        cache.put(2, "b");
        cache.getSimple(1);
        cache.put(3, "c");
        System.out.println(cache.getSimple(2));  // null
        System.out.println(cache.getSimple(1));  // a
        System.out.println(cache.getSimple(3));  // c
    }
}
