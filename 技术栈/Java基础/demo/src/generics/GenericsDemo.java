package generics;

import java.util.*;

/**
 * 泛型编程示例
 * 包含泛型类、泛型方法、泛型接口、通配符等
 */
public class GenericsDemo {
    public static void main(String[] args) {
        // 泛型类的使用
        System.out.println("===== 泛型类示例 =====");
        Box<String> stringBox = new Box<>("Hello Generics");
        System.out.println("字符串盒子内容: " + stringBox.getContent());
        
        Box<Integer> integerBox = new Box<>(100);
        System.out.println("整数盒子内容: " + integerBox.getContent());
        
        // 泛型方法的使用
        System.out.println("\n===== 泛型方法示例 =====");
        String reversed = reverse("Java");
        System.out.println("反转字符串: " + reversed);
        
        Integer[] intArray = {1, 2, 3, 4, 5};
        printArray(intArray);
        
        String[] stringArray = {"Hello", "World", "Java"};
        printArray(stringArray);
        
        // 泛型接口的使用
        System.out.println("\n===== 泛型接口示例 =====");
        Calculator<Integer> intCalculator = new IntegerCalculator();
        System.out.println("10 + 20 = " + intCalculator.add(10, 20));
        System.out.println("50 - 30 = " + intCalculator.subtract(50, 30));
        
        Calculator<Double> doubleCalculator = new DoubleCalculator();
        System.out.println("3.5 + 2.5 = " + doubleCalculator.add(3.5, 2.5));
        System.out.println("10.0 - 4.5 = " + doubleCalculator.subtract(10.0, 4.5));
        
        // 通配符的使用
        System.out.println("\n===== 通配符示例 =====");
        List<Integer> intList = Arrays.asList(1, 2, 3, 4, 5);
        List<Double> doubleList = Arrays.asList(1.1, 2.2, 3.3);
        List<String> stringList = Arrays.asList("A", "B", "C");
        
        System.out.println("整数列表元素: ");
        printList(intList);
        
        System.out.println("浮点数列表元素: ");
        printList(doubleList);
        
        System.out.println("字符串列表元素: ");
        printList(stringList);
        
        // 上界通配符
        System.out.println("\n===== 上界通配符示例 =====");
        List<Integer> integers = Arrays.asList(1, 2, 3, 4, 5);
        List<Double> doubles = Arrays.asList(1.1, 2.2, 3.3);
        
        System.out.println("整数列表最大值: " + findMax(integers));
        System.out.println("浮点数列表最大值: " + findMax(doubles));
        
        // 下界通配符
        System.out.println("\n===== 下界通配符示例 =====");
        List<Number> numbers = new ArrayList<>();
        addIntegers(numbers);
        addDoubles(numbers);
        System.out.println("混合数字列表: " + numbers);
        
        // 泛型擦除和类型检查
        System.out.println("\n===== 泛型擦除示例 =====");
        // 运行时泛型类型会被擦除，只保留原始类型
        List<String> list1 = new ArrayList<>();
        List<Integer> list2 = new ArrayList<>();
        
        // 以下代码输出true，因为泛型擦除后，两个list都是ArrayList类型
        System.out.println("list1和list2的类型是否相同: " + (list1.getClass() == list2.getClass()));
        
        // 泛型集合的安全操作
        System.out.println("\n===== 泛型集合的安全操作 =====");
        SafeList<String> safeList = new SafeList<>();
        safeList.add("Java");
        safeList.add("Python");
        safeList.add("C++");
        
        System.out.println("安全列表的大小: " + safeList.size());
        System.out.println("索引1的元素: " + safeList.get(1));
        
        // 自定义泛型工具类
        System.out.println("\n===== 自定义泛型工具类 =====");
        Pair<String, Integer> pair = new Pair<>("Age", 30);
        System.out.println("键: " + pair.getFirst() + ", 值: " + pair.getSecond());
        
        Pair<String, String> stringPair = new Pair<>("Name", "张三");
        System.out.println("键: " + stringPair.getFirst() + ", 值: " + stringPair.getSecond());
    }
    
    // 泛型方法示例 - 反转字符串
    public static <T> T reverse(String str) {
        return (T) new StringBuilder(str).reverse().toString();
    }
    
    // 泛型方法示例 - 打印数组
    public static <T> void printArray(T[] array) {
        for (T element : array) {
            System.out.print(element + " ");
        }
        System.out.println();
    }
    
    // 使用通配符的方法 - 打印任意类型的列表
    public static void printList(List<?> list) {
        for (Object element : list) {
            System.out.print(element + " ");
        }
        System.out.println();
    }
    
    // 上界通配符示例 - 查找最大值
    public static <T extends Comparable<? super T>> T findMax(List<T> list) {
        if (list == null || list.isEmpty()) {
            return null;
        }
        
        T max = list.get(0);
        for (T element : list) {
            if (element.compareTo(max) > 0) {
                max = element;
            }
        }
        return max;
    }
    
    // 下界通配符示例 - 添加整数到数字列表
    public static void addIntegers(List<? super Integer> list) {
        list.add(100);
        list.add(200);
    }
    
    // 下界通配符示例 - 添加浮点数到数字列表
    public static void addDoubles(List<? super Double> list) {
        list.add(3.14);
        list.add(2.71);
    }
}

// 泛型类示例
class Box<T> {
    private T content;
    
    public Box(T content) {
        this.content = content;
    }
    
    public T getContent() {
        return content;
    }
    
    public void setContent(T content) {
        this.content = content;
    }
}

// 泛型接口示例
interface Calculator<T> {
    T add(T a, T b);
    T subtract(T a, T b);
}

// 泛型接口实现类
class IntegerCalculator implements Calculator<Integer> {
    @Override
    public Integer add(Integer a, Integer b) {
        return a + b;
    }
    
    @Override
    public Integer subtract(Integer a, Integer b) {
        return a - b;
    }
}

// 泛型接口实现类
class DoubleCalculator implements Calculator<Double> {
    @Override
    public Double add(Double a, Double b) {
        return a + b;
    }
    
    @Override
    public Double subtract(Double a, Double b) {
        return a - b;
    }
}

// 安全的泛型列表封装类
class SafeList<T> {
    private List<T> list = new ArrayList<>();
    
    public void add(T element) {
        list.add(element);
    }
    
    public T get(int index) {
        if (index < 0 || index >= list.size()) {
            throw new IndexOutOfBoundsException("索引越界: " + index);
        }
        return list.get(index);
    }
    
    public int size() {
        return list.size();
    }
}

// 泛型键值对类
class Pair<K, V> {
    private K first;
    private V second;
    
    public Pair(K first, V second) {
        this.first = first;
        this.second = second;
    }
    
    public K getFirst() {
        return first;
    }
    
    public V getSecond() {
        return second;
    }
    
    public void setFirst(K first) {
        this.first = first;
    }
    
    public void setSecond(V second) {
        this.second = second;
    }
}