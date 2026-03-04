package framework;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 集合框架示例
 * 包含List、Set、Map等集合的使用
 */
public class CollectionFramework {
    public static void main(String[] args) {
        // List接口实现类
        System.out.println("===== List示例 =====");
        // ArrayList - 动态数组
        List<String> arrayList = new ArrayList<>();
        arrayList.add("Java");
        arrayList.add("Python");
        arrayList.add("C++");
        arrayList.add("JavaScript");
        System.out.println("ArrayList: " + arrayList);
        System.out.println("获取第一个元素: " + arrayList.get(0));
        arrayList.set(1, "Go"); // 修改元素
        System.out.println("修改后的ArrayList: " + arrayList);
        
        // LinkedList - 双向链表
        List<Integer> linkedList = new LinkedList<>();
        linkedList.add(1);
        linkedList.add(2);
        linkedList.add(3);
        System.out.println("LinkedList: " + linkedList);
        linkedList.addFirst(0); // 在头部添加
        linkedList.addLast(4); // 在尾部添加
        System.out.println("添加元素后的LinkedList: " + linkedList);
        
        // Set接口实现类
        System.out.println("\n===== Set示例 =====");
        // HashSet - 无序不重复
        Set<String> hashSet = new HashSet<>();
        hashSet.add("苹果");
        hashSet.add("香蕉");
        hashSet.add("橙子");
        hashSet.add("苹果"); // 重复元素不会添加
        System.out.println("HashSet: " + hashSet);
        
        // TreeSet - 有序集合
        Set<Integer> treeSet = new TreeSet<>();
        treeSet.add(5);
        treeSet.add(2);
        treeSet.add(8);
        treeSet.add(1);
        System.out.println("TreeSet: " + treeSet); // 自动排序
        
        // Map接口实现类
        System.out.println("\n===== Map示例 =====");
        // HashMap - 键值对映射
        Map<String, Integer> hashMap = new HashMap<>();
        hashMap.put("语文", 85);
        hashMap.put("数学", 92);
        hashMap.put("英语", 78);
        System.out.println("HashMap: " + hashMap);
        System.out.println("数学成绩: " + hashMap.get("数学"));
        
        // 遍历Map
        System.out.println("遍历Map的键值对:");
        for (Map.Entry<String, Integer> entry : hashMap.entrySet()) {
            System.out.println(entry.getKey() + ": " + entry.getValue());
        }
        
        // TreeMap - 按键排序的Map
        Map<String, String> treeMap = new TreeMap<>();
        treeMap.put("b", "香蕉");
        treeMap.put("a", "苹果");
        treeMap.put("c", "橙子");
        System.out.println("TreeMap: " + treeMap); // 按键排序
        
        // Collections工具类
        System.out.println("\n===== Collections工具类 =====");
        List<Integer> numbers = new ArrayList<>(Arrays.asList(3, 1, 4, 1, 5, 9, 2, 6));
        System.out.println("原始列表: " + numbers);
        Collections.sort(numbers); // 排序
        System.out.println("排序后: " + numbers);
        Collections.shuffle(numbers); // 打乱顺序
        System.out.println("打乱后: " + numbers);
        System.out.println("最大值: " + Collections.max(numbers));
        System.out.println("最小值: " + Collections.min(numbers));
        Collections.fill(numbers, 0); // 填充
        System.out.println("填充后: " + numbers);
        
        // Stream API 简单示例
        System.out.println("\n===== Stream API 简单示例 =====");
        List<String> languages = Arrays.asList("Java", "Python", "C++", "JavaScript", "Go", "Rust");
        // 过滤长度大于3的字符串并转换为大写
        List<String> result = languages.stream()
                                      .filter(s -> s.length() > 3)
                                      .map(String::toUpperCase)
                                      .collect(Collectors.toList());
        System.out.println("过滤并转换后的结果: " + result);
        
        // 计算元素总长度
        int totalLength = languages.stream()
                                  .mapToInt(String::length)
                                  .sum();
        System.out.println("所有字符串的总长度: " + totalLength);
    }
}