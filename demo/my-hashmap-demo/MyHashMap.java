package my_hashmap_demo;

/**
 * 手写简易 HashMap：数组+链表，put/get、hash、扩容 2 倍，负载因子 0.75。
 * 考点：index=(n-1)&hash、高16位异或、扩容 rehash。
 */
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
                put(node.key, node.value);
                node = node.next;
            }
        }
    }

    public int size() {
        return size;
    }

    public static void main(String[] args) {
        MyHashMap<String, Integer> map = new MyHashMap<>();
        map.put("a", 1);
        map.put("b", 2);
        map.put("a", 10);
        System.out.println(map.get("a") + " " + map.get("b"));  // 10 2
    }
}
