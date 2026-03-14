package lru_cache_demo;

import java.util.HashMap;
import java.util.Map;

/**
 * 手写 LRU：HashMap + 双向链表。O(1) get/put，淘汰最久未访问。
 * 考点：为什么用 HashMap（O(1) 查找）+ 双向链表（O(1) 删除/移动）。
 */
public class LRUCacheHandWritten<K, V> {
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

    public LRUCacheHandWritten(int capacity) {
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

    public static void main(String[] args) {
        LRUCacheHandWritten<Integer, String> cache = new LRUCacheHandWritten<>(2);
        cache.put(1, "a");
        cache.put(2, "b");
        cache.get(1);
        cache.put(3, "c");
        System.out.println(cache.get(2));  // null（已淘汰）
        System.out.println(cache.get(1));  // a
        System.out.println(cache.get(3));  // c
    }
}
