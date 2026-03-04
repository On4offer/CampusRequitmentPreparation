package features;

import java.util.*;
import java.util.stream.*;
import java.util.function.*;
import java.time.*;
import java.time.format.*;
import java.util.concurrent.*;
import java.util.Optional;
import java.lang.annotation.Repeatable;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;

/**
 * Java新特性示例
 * 包含Lambda表达式、Stream API、Optional、时间日期API、接口默认方法等
 */
public class JavaNewFeatures {
    public static void main(String[] args) {
        System.out.println("===== Java新特性示例 =====\n");
        
        // 1. Lambda表达式
        System.out.println("1. Lambda表达式：");
        
        // 替代匿名内部类
        Runnable task = () -> System.out.println("使用Lambda表达式创建Runnable");
        new Thread(task).start();
        
        // 带参数的Lambda表达式
        BinaryOperator<Integer> add = (a, b) -> a + b;
        System.out.println("10 + 20 = " + add.apply(10, 20));
        
        // 带类型声明的Lambda表达式
        BinaryOperator<Integer> multiply = (Integer x, Integer y) -> x * y;
        System.out.println("5 * 6 = " + multiply.apply(5, 6));
        
        // 多行Lambda表达式
        BinaryOperator<Integer> complexOperation = (a, b) -> {
            int sum = a + b;
            int product = a * b;
            return sum + product;
        };
        System.out.println("复杂运算结果: " + complexOperation.apply(3, 4));
        
        // 集合排序使用Lambda
        List<String> fruits = Arrays.asList("Apple", "Banana", "Orange", "Mango", "Grape");
        System.out.println("排序前: " + fruits);
        fruits.sort((s1, s2) -> s1.compareTo(s2));
        System.out.println("按字母排序后: " + fruits);
        
        // 按长度排序
        fruits.sort((s1, s2) -> Integer.compare(s1.length(), s2.length()));
        System.out.println("按长度排序后: " + fruits);
        System.out.println();
        
        // 2. 函数式接口
        System.out.println("2. 函数式接口：");
        
        // Predicate - 断言接口
        Predicate<Integer> isEven = n -> n % 2 == 0;
        System.out.println("10是偶数: " + isEven.test(10));
        System.out.println("15是偶数: " + isEven.test(15));
        
        // Function - 函数接口
        Function<String, Integer> stringLength = s -> s.length();
        System.out.println("'Hello'的长度: " + stringLength.apply("Hello"));
        
        // Consumer - 消费接口
        Consumer<String> printUpperCase = s -> System.out.println(s.toUpperCase());
        printUpperCase.accept("java new features");
        
        // Supplier - 供应接口
        Supplier<Double> randomNumber = Math::random;
        System.out.println("随机数: " + randomNumber.get());
        
        // 自定义函数式接口使用
        Calculator addCalculator = (a, b) -> a + b;
        Calculator multiplyCalculator = (a, b) -> a * b;
        System.out.println("函数式接口加法: " + addCalculator.calculate(10, 20));
        System.out.println("函数式接口乘法: " + multiplyCalculator.calculate(10, 20));
        System.out.println();
        
        // 3. Stream API
        System.out.println("3. Stream API：");
        
        List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // 过滤和映射
        List<Integer> evenSquares = numbers.stream()
                                         .filter(n -> n % 2 == 0) // 过滤偶数
                                         .map(n -> n * n) // 计算平方
                                         .collect(Collectors.toList());
        System.out.println("偶数的平方: " + evenSquares);
        
        // 排序和去重
        List<Integer> distinctSorted = Arrays.asList(5, 3, 7, 3, 8, 5, 1, 9)
                                           .stream()
                                           .distinct() // 去重
                                           .sorted() // 排序
                                           .collect(Collectors.toList());
        System.out.println("去重排序后: " + distinctSorted);
        
        // 查找和匹配
        boolean hasEven = numbers.stream().anyMatch(n -> n % 2 == 0);
        boolean allPositive = numbers.stream().allMatch(n -> n > 0);
        Optional<Integer> firstEven = numbers.stream().filter(n -> n % 2 == 0).findFirst();
        
        System.out.println("是否有偶数: " + hasEven);
        System.out.println("是否全为正数: " + allPositive);
        System.out.println("第一个偶数: " + firstEven.orElse(0));
        
        // 归约操作
        int sum = numbers.stream().reduce(0, Integer::sum);
        int product = numbers.stream().reduce(1, (a, b) -> a * b);
        Optional<Integer> max = numbers.stream().reduce(Integer::max);
        
        System.out.println("总和: " + sum);
        System.out.println("乘积: " + product);
        System.out.println("最大值: " + max.orElse(0));
        
        // 并行流
        long startTime = System.currentTimeMillis();
        long count = Stream.iterate(1, n -> n + 1)
                          .limit(1000000)
                          .parallel() // 并行流
                          .filter(n -> n % 2 == 0)
                          .count();
        long endTime = System.currentTimeMillis();
        System.out.println("并行流计算偶数个数: " + count + ", 耗时: " + (endTime - startTime) + "ms");
        System.out.println();
        
        // 4. Optional类
        System.out.println("4. Optional类：");
        
        // 创建Optional
        Optional<String> empty = Optional.empty();
        Optional<String> nonEmpty = Optional.of("Hello Optional");
        Optional<String> nullable = Optional.ofNullable(null);
        
        // 判断值是否存在
        System.out.println("empty是否存在值: " + empty.isPresent());
        System.out.println("nonEmpty是否存在值: " + nonEmpty.isPresent());
        System.out.println("nullable是否存在值: " + nullable.isPresent());
        
        // 获取值
        System.out.println("获取值: " + nonEmpty.get());
        System.out.println("获取值(或默认值): " + nullable.orElse("默认值"));
        System.out.println("获取值(或生成默认值): " + nullable.orElseGet(() -> "生成的默认值"));
        
        // ifPresent
        nonEmpty.ifPresent(value -> System.out.println("存在值: " + value));
        
        // map和flatMap
        Optional<Integer> length = nonEmpty.map(String::length);
        System.out.println("字符串长度: " + length.orElse(0));
        
        // orElseThrow
        try {
            empty.orElseThrow(() -> new IllegalArgumentException("值不存在"));
        } catch (IllegalArgumentException e) {
            System.out.println("捕获异常: " + e.getMessage());
        }
        System.out.println();
        
        // 5. Java 8 日期时间API
        System.out.println("5. Java 8 日期时间API：");
        
        // LocalDate
        LocalDate today = LocalDate.now();
        System.out.println("今天日期: " + today);
        
        LocalDate specificDate = LocalDate.of(2024, 12, 25);
        System.out.println("指定日期: " + specificDate);
        
        // LocalTime
        LocalTime currentTime = LocalTime.now();
        System.out.println("当前时间: " + currentTime);
        
        // LocalDateTime
        LocalDateTime dateTime = LocalDateTime.now();
        System.out.println("当前日期时间: " + dateTime);
        
        // 格式化
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
        String formattedDateTime = dateTime.format(formatter);
        System.out.println("格式化日期时间: " + formattedDateTime);
        
        // 解析
        LocalDateTime parsedDateTime = LocalDateTime.parse("2024-01-01 10:00:00", formatter);
        System.out.println("解析日期时间: " + parsedDateTime);
        
        // 日期计算
        LocalDate nextWeek = today.plusWeeks(1);
        LocalDate lastMonth = today.minusMonths(1);
        
        System.out.println("下周今天: " + nextWeek);
        System.out.println("上个月今天: " + lastMonth);
        
        // 判断
        boolean isAfter = today.isAfter(LocalDate.of(2020, 1, 1));
        boolean isLeapYear = today.isLeapYear();
        
        System.out.println("今天在2020-01-01之后: " + isAfter);
        System.out.println("今年是闰年: " + isLeapYear);
        System.out.println();
        
        // 6. 接口默认方法和静态方法
        System.out.println("6. 接口默认方法和静态方法：");
        
        Vehicle car = new Car();
        car.start();
        car.stop();
        car.drive(); // 调用默认方法
        
        Vehicle. honk(); // 调用静态方法
        
        // 7. 方法引用
        System.out.println("\n7. 方法引用：");
        
        // 静态方法引用
        List<String> names = Arrays.asList("Alice", "Bob", "Charlie", "David");
        names.forEach(System.out::println);
        
        // 实例方法引用
        String str = "Hello Java";  
        Supplier<Integer> lengthSupplier = str::length;
        System.out.println("字符串长度: " + lengthSupplier.get());
        
        // 构造方法引用
        List<Integer> ids = Arrays.asList(1, 2, 3);
        List<Person> persons = ids.stream()
                                 .map(Person::new)
                                 .collect(Collectors.toList());
        System.out.println("创建的Person列表: " + persons);
        
        // 8. 重复注解
        System.out.println("\n8. 重复注解：");
        
        Class<TestClass> testClass = TestClass.class;
        if (testClass.isAnnotationPresent(Roles.class)) {
            Roles roles = testClass.getAnnotation(Roles.class);
            for (Role role : roles.value()) {
                System.out.println("角色: " + role.name());
            }
        }
        
        // 9. 其他新特性
        System.out.println("\n9. 其他新特性：");
        
        // String.join
        String joined = String.join(", ", "Java", "Python", "C++", "JavaScript");
        System.out.println("字符串连接: " + joined);
        
        // 菱形操作符改进
        Map<String, List<String>> map = new HashMap<>(); // Java 7+ 支持
        map.put("programming", Arrays.asList("Java", "Python"));
        System.out.println("菱形操作符Map: " + map);
        
        // try-with-resources（在IO示例中有详细介绍）
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.println("try-with-resources示例");
        }
    }
}

// 自定义函数式接口
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

// 接口默认方法和静态方法示例
interface Vehicle {
    void start();
    void stop();
    
    // 默认方法
    default void drive() {
        System.out.println("车辆正在行驶");
    }
    
    // 静态方法
    static void honk() {
        System.out.println("车辆鸣笛");
    }
}

// 接口实现类
class Car implements Vehicle {
    @Override
    public void start() {
        System.out.println("汽车启动");
    }
    
    @Override
    public void stop() {
        System.out.println("汽车停止");
    }
}

// Person类用于方法引用示例
class Person {
    private int id;
    private String name = "Person-" + id;
    
    public Person(int id) {
        this.id = id;
    }
    
    @Override
    public String toString() {
        return "Person{id=" + id + "}";
    }
}

// 重复注解示例
@interface Roles {
    Role[] value();
}

@Repeatable(Roles.class)
@interface Role {
    String name();
}

@Role(name = "admin")
@Role(name = "user")
class TestClass {
    // 测试类
}