package collection_framework_demo;

import java.util.*;

/**
 * Java 集合框架常用用法与选型：List、Set、Map。
 * 考点：ArrayList/LinkedList、HashSet/TreeSet、HashMap 区别与适用场景。
 */
public class CollectionFrameworkDemo {

    /** List：ArrayList 随机访问快，LinkedList 头插删快 */
    static void listDemo() {
        System.out.println("=== List ===");
        List<String> arrayList = new ArrayList<>();
        arrayList.add("a");
        arrayList.add("b");
        arrayList.add(1, "x");           // 按索引插入
        System.out.println("ArrayList: " + arrayList + ", get(1)=" + arrayList.get(1));

        List<String> linkedList = new LinkedList<>();
        linkedList.addFirst("head");
        linkedList.addLast("tail");
        linkedList.add(1, "mid");
        System.out.println("LinkedList: " + linkedList);
    }

    /** Set：HashSet 无序去重，TreeSet 有序去重 */
    static void setDemo() {
        System.out.println("=== Set ===");
        Set<String> hashSet = new HashSet<>();
        hashSet.add("b");
        hashSet.add("a");
        hashSet.add("a");
        System.out.println("HashSet(无序去重): " + hashSet);

        Set<String> treeSet = new TreeSet<>();
        treeSet.add("b");
        treeSet.add("a");
        treeSet.add("c");
        System.out.println("TreeSet(有序去重): " + treeSet);
    }

    /** Map：HashMap 无序 K-V，TreeMap 按 key 有序 */
    static void mapDemo() {
        System.out.println("=== Map ===");
        Map<String, Integer> hashMap = new HashMap<>();
        hashMap.put("b", 2);
        hashMap.put("a", 1);
        hashMap.put("a", 10);            // 覆盖
        System.out.println("HashMap: " + hashMap + ", get(a)=" + hashMap.get("a"));

        Map<String, Integer> treeMap = new TreeMap<>();
        treeMap.put("b", 2);
        treeMap.put("a", 1);
        treeMap.put("c", 3);
        System.out.println("TreeMap(按 key 有序): " + treeMap);
    }

    public static void main(String[] args) {
        listDemo();
        setDemo();
        mapDemo();
    }
}
