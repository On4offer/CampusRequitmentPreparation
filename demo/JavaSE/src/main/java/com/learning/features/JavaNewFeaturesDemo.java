package com.learning.features;

import java.time.*;
import java.time.format.*;
import java.time.temporal.*;
import java.util.*;
import java.util.stream.*;
import java.util.function.*;
import java.util.concurrent.*;
import java.lang.annotation.Repeatable;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

/**
 * Java新特性示例
 * 演示Java 8及以上版本的新特性
 */
public class JavaNewFeaturesDemo {
    public static void main(String[] args) {
        // 1. Lambda表达式
        System.out.println("=== 1. Lambda表达式 ===");
        
        // 无参数Lambda
        Runnable runnable = () -> System.out.println("Hello Lambda!");
        runnable.run();
        
        // 单参数Lambda
        Consumer<String> consumer = (s) -> System.out.println("消费: " + s);
        consumer.accept("Lambda表达式");
        
        // 多参数Lambda
        BiFunction<Integer, Integer, Integer> add = (a, b) -> a + b;
        System.out.println("10 + 20 = " + add.apply(10, 20));
        
        // 带返回值的Lambda
        Supplier<String> supplier = () -> "Lambda提供的值";
        System.out.println("Supplier结果: " + supplier.get());
        
        // 2. 函数式接口
        System.out.println("\n=== 2. 函数式接口 ===");
        
        // Predicate - 用于判断
        Predicate<Integer> isEven = n -> n % 2 == 0;
        System.out.println("10是偶数: " + isEven.test(10));
        System.out.println("15是偶数: " + isEven.test(15));
        
        // Function - 用于转换
        Function<String, Integer> strLength = s -> s.length();
        System.out.println("'Java'的长度: " + strLength.apply("Java"));
        
        // Consumer - 用于消费
        List<String> names = Arrays.asList("张三", "李四", "王五");
        names.forEach(name -> System.out.println("Hello, " + name));
        
        // Supplier - 用于提供
        Supplier<Double> randomSupplier = Math::random;
        System.out.println("随机数: " + randomSupplier.get());
        
        // 3. Stream API
        System.out.println("\n=== 3. Stream API ===");
        
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // 过滤
        List<Integer> evenNumbers = numbers.stream()
                .filter(n -> n % 2 == 0)
                .collect(Collectors.toList());
        System.out.println("偶数列表: " + evenNumbers);
        
        // 映射
        List<Integer> squares = numbers.stream()
                .map(n -> n * n)
                .collect(Collectors.toList());
        System.out.println("平方列表: " + squares);
        
        // 排序
        List<Integer> sortedList = numbers.stream()
                .sorted((a, b) -> b - a)
                .collect(Collectors.toList());
        System.out.println("降序排序: " + sortedList);
        
        // 聚合操作
        int sum = numbers.stream().reduce(0, (a, b) -> a + b);
        System.out.println("总和: " + sum);
        
        Optional<Integer> max = numbers.stream().max(Integer::compareTo);
        System.out.println("最大值: " + max.orElse(0));
        
        // 并行流
        long count = numbers.parallelStream()
                .filter(n -> n > 5)
                .count();
        System.out.println("大于5的元素个数: " + count);
        
        // 4. Optional类
        System.out.println("\n=== 4. Optional类 ===");
        
        // 创建Optional
        Optional<String> optionalEmpty = Optional.empty();
        Optional<String> optionalOf = Optional.of("非空值");
        Optional<String> optionalOfNullable = Optional.ofNullable(null);
        
        // isPresent检查
        System.out.println("optionalOf是否有值: " + optionalOf.isPresent());
        System.out.println("optionalEmpty是否有值: " + optionalEmpty.isPresent());
        
        // ifPresent消费
        optionalOf.ifPresent(value -> System.out.println("Optional值: " + value));
        
        // orElse获取值
        String value1 = optionalOfNullable.orElse("默认值");
        System.out.println("orElse结果: " + value1);
        
        // orElseGet获取值
        String value2 = optionalOfNullable.orElseGet(() -> "通过Supplier提供的默认值");
        System.out.println("orElseGet结果: " + value2);
        
        // map转换
        Optional<Integer> lengthOptional = optionalOf.map(String::length);
        System.out.println("字符串长度: " + lengthOptional.orElse(0));
        
        // 5. 方法引用
        System.out.println("\n=== 5. 方法引用 ===");
        
        // 静态方法引用
        Function<String, Integer> parseInt = Integer::parseInt;
        System.out.println("'123'转整数: " + parseInt.apply("123"));
        
        // 实例方法引用
        List<String> fruits = Arrays.asList("Apple", "Banana", "Orange");
        fruits.forEach(System.out::println);
        
        // 对象方法引用
        String str = "hello world";
        Supplier<String> toUpperCase = str::toUpperCase;
        System.out.println("转大写: " + toUpperCase.get());
        
        // 构造方法引用
        Supplier<List<String>> listSupplier = ArrayList::new;
        List<String> newList = listSupplier.get();
        newList.add("Java");
        System.out.println("新列表: " + newList);
        
        // 6. 接口默认方法和静态方法
        System.out.println("\n=== 6. 接口默认方法和静态方法 ===");
        MyInterface myInterface = new MyInterfaceImpl();
        myInterface.defaultMethod();
        MyInterface.staticMethod();
        
        // 7. 日期时间API
        System.out.println("\n=== 7. 日期时间API ===");
        
        // LocalDate
        LocalDate today = LocalDate.now();
        System.out.println("今天日期: " + today);
        LocalDate specificDate = LocalDate.of(2023, 12, 25);
        System.out.println("指定日期: " + specificDate);
        
        // LocalTime
        LocalTime now = LocalTime.now();
        System.out.println("当前时间: " + now);
        
        // LocalDateTime
        LocalDateTime dateTime = LocalDateTime.now();
        System.out.println("当前日期时间: " + dateTime);
        
        // 格式化和解析
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String formatted = dateTime.format(formatter);
        System.out.println("格式化后: " + formatted);
        
        // 8. 重复注解和类型注解
        System.out.println("\n=== 8. 重复注解示例 ===");
        try {
            Class<?> annotatedClass = RepeatedAnnotationsExample.class;
            // 获取所有注解
            Arrays.stream(annotatedClass.getAnnotations()).forEach(anno -> {
                System.out.println("类注解: " + anno);
            });
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

// 函数式接口示例
@FunctionalInterface
interface MyFunctionalInterface {
    void doSomething(String input);
    
    // 允许有默认方法
    default void defaultMethod() {
        System.out.println("默认方法");
    }
    
    // 允许有静态方法
    static void staticMethod() {
        System.out.println("静态方法");
    }
}

// 接口默认方法和静态方法示例
interface MyInterface {
    void abstractMethod();
    
    default void defaultMethod() {
        System.out.println("接口默认方法实现");
    }
    
    static void staticMethod() {
        System.out.println("接口静态方法");
    }
}

class MyInterfaceImpl implements MyInterface {
    @Override
    public void abstractMethod() {
        System.out.println("实现抽象方法");
    }
    
    // 可以覆盖默认方法
    @Override
    public void defaultMethod() {
        System.out.println("覆盖后的默认方法");
        MyInterface.super.defaultMethod(); // 调用接口默认实现
    }
}

// 自定义可重复注解
@interface MyAnnotations {
    MyAnnotation[] value();
}

@Repeatable(MyAnnotations.class)
@interface MyAnnotation {
    String value();
}

@MyAnnotation("First")
@MyAnnotation("Second")
class RepeatedAnnotationsExample {
    // 类体
}

// 接口默认方法可以有实现
interface Vehicle {
    void start();
    
    default void honk() {
        System.out.println("Vehicle honking");
    }
}

interface FourWheeler {
    void drive();
    
    default void honk() {
        System.out.println("FourWheeler honking");
    }
}

// 解决默认方法冲突
class Car implements Vehicle, FourWheeler {
    @Override
    public void start() {
        System.out.println("Car starting");
    }
    
    @Override
    public void drive() {
        System.out.println("Car driving");
    }
    
    // 解决默认方法冲突
    @Override
    public void honk() {
        Vehicle.super.honk(); // 选择Vehicle接口的实现
    }
}