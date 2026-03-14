package hashmap_principle_demo;

/**
 * HashMap 原理演示：hash 计算、下标计算、容量 2 的幂、扩容后位置规律。
 * 不实现完整 HashMap，仅用于理解 put/扩容原理。
 */
public class HashMapPrincipleDemo {

    /** 与 JDK HashMap 一致的 hash 方法：高 16 位异或，减少碰撞 */
    static int hash(Object key) {
        int h = key == null ? 0 : key.hashCode();
        return h ^ (h >>> 16);
    }

    /** 下标：(n-1) & hash，当 n 为 2 的幂时等价于 hash % n */
    static int indexFor(int hash, int tableLength) {
        return (tableLength - 1) & hash;
    }

    public static void main(String[] args) {
        int capacity = 16;   // 默认容量，2 的幂
        String key = "hello";

        int h = key.hashCode();
        int hash = hash(key);
        int index = indexFor(hash, capacity);

        System.out.println("=== HashMap 原理演示 ===");
        System.out.println("key = \"" + key + "\"");
        System.out.println("hashCode()     = " + h);
        System.out.println("hash (^>>>16)  = " + hash);
        System.out.println("index (n=16)   = (16-1) & hash = " + index);
        System.out.println();

        // 扩容后位置规律：要么原位置，要么原位置 + oldCap
        System.out.println("=== 扩容后位置 ===");
        System.out.println("容量 16 时 index = " + indexFor(hash, 16));
        System.out.println("容量 32 时 index = " + indexFor(hash, 32));
        System.out.println("规律：新下标 = 原下标 或 原下标 + 16（oldCap）");
        System.out.println();

        // 常用常量
        System.out.println("=== 常见常量（与 JDK 一致） ===");
        System.out.println("默认初始容量: 16");
        System.out.println("负载因子: 0.75");
        System.out.println("树化阈值: 链表长度 >= 8 且 table.length >= 64");
        System.out.println("退化阈值: 树节点数 <= 6 时退化为链表");
    }
}
