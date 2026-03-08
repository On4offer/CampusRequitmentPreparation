# 📋 Java 新特性 - 常用API与使用场景速查

> 日常开发常用Java 8+新特性、Lambda、Stream、Optional、日期时间API等，配合《学习笔记.md》系统学习使用。

---

## 🎯 Lambda表达式速查

### 基本语法

```java
// 无参数
() -> System.out.println("Hello")

// 单参数（可省略括号）
x -> x * 2
(x) -> x * 2

// 多参数
(a, b) -> a + b

// 带类型声明
(Integer a, Integer b) -> a + b

// 多行代码块
(a, b) -> {
    int sum = a + b;
    return sum;
}
```

### 常见使用场景

```java
// 1. Runnable线程
new Thread(() -> System.out.println("Running")).start();

// 2. Comparator排序
list.sort((a, b) -> a.length() - b.length());
list.sort(Comparator.comparing(String::length));

// 3. ActionListener
button.addActionListener(e -> {
    System.out.println("Clicked");
});

// 4. 集合遍历
list.forEach(item -> System.out.println(item));
list.forEach(System.out::println);  // 方法引用

// 5. 自定义函数式接口
@FunctionalInterface
interface Calculator {
    int calculate(int a, int b);
}

Calculator add = (a, b) -> a + b;
Calculator multiply = (a, b) -> a * b;
int result = add.calculate(3, 5);  // 8
```

---

## 🔧 内置函数式接口

### 核心接口速查表

| 接口 | 方法签名 | 用途 | 示例 |
|------|----------|------|------|
| `Supplier<T>` | `T get()` | 供给/工厂 | `() -> new Random()` |
| `Consumer<T>` | `void accept(T)` | 消费 | `s -> System.out.println(s)` |
| `BiConsumer<T,U>` | `void accept(T,U)` | 双参数消费 | `(k, v) -> map.put(k, v)` |
| `Function<T,R>` | `R apply(T)` | 转换 | `s -> s.length()` |
| `BiFunction<T,U,R>` | `R apply(T,U)` | 双参数转换 | `(a, b) -> a + b` |
| `Predicate<T>` | `boolean test(T)` | 断言/过滤 | `s -> s.length() > 5` |
| `BiPredicate<T,U>` | `boolean test(T,U)` | 双参数断言 | `(a, b) -> a > b` |
| `UnaryOperator<T>` | `T apply(T)` | 一元操作 | `x -> x * 2` |
| `BinaryOperator<T>` | `T apply(T,T)` | 二元操作 | `(a, b) -> a + b` |

### 使用示例

```java
// Supplier - 延迟加载
Supplier<List<String>> listSupplier = () -> new ArrayList<>();
List<String> list = listSupplier.get();

// 简化写法
Supplier<List<String>> listSupplier2 = ArrayList::new;

// Consumer - 消费处理
Consumer<String> printer = s -> System.out.println(s);
printer.accept("Hello");

// 链式Consumer
Consumer<String> printUpper = s -> System.out.println(s.toUpperCase());
printer.andThen(printUpper).accept("hello");

// Function - 类型转换
Function<String, Integer> lengthFunc = String::length;
int len = lengthFunc.apply("Hello");  // 5

// 函数组合
Function<Integer, Integer> multiply2 = x -> x * 2;
Function<Integer, Integer> add10 = x -> x + 10;
Function<Integer, Integer> multiplyThenAdd = multiply2.andThen(add10);
int result = multiplyThenAdd.apply(5);  // 20 (5*2+10)

Function<Integer, Integer> addThenMultiply = multiply2.compose(add10);
int result2 = addThenMultiply.apply(5);  // 30 ((5+10)*2)

// Predicate - 条件判断
Predicate<Integer> isEven = n -> n % 2 == 0;
boolean test = isEven.test(4);  // true

// Predicate组合
Predicate<Integer> isPositive = n -> n > 0;
Predicate<Integer> isEvenAndPositive = isEven.and(isPositive);
Predicate<Integer> isOdd = isEven.negate();
Predicate<Integer> isLessThan100 = n -> n < 100;
Predicate<Integer> isEvenOrLessThan100 = isEven.or(isLessThan100);

// BiFunction - 两参数转换
BiFunction<String, String, String> concat = (a, b) -> a + " " + b;
String fullName = concat.apply("John", "Doe");

// BinaryOperator - 同类型二元操作
BinaryOperator<Integer> add = Integer::sum;
BinaryOperator<Integer> max = BinaryOperator.maxBy(Comparator.naturalOrder());
```

---

## 🌊 Stream API速查

### 创建Stream

```java
// 从集合创建
List<String> list = Arrays.asList("a", "b", "c");
Stream<String> stream1 = list.stream();              // 顺序流
Stream<String> stream2 = list.parallelStream();      // 并行流

// 从数组创建
Stream<String> stream3 = Arrays.stream(new String[]{"a", "b", "c"});
IntStream intStream = Arrays.stream(new int[]{1, 2, 3});

// 从值创建
Stream<String> stream4 = Stream.of("a", "b", "c");
Stream<String> emptyStream = Stream.empty();

// 无限流
Stream<Integer> infiniteStream = Stream.iterate(0, n -> n + 2);  // 0, 2, 4, 6...
Stream<Integer> limited = Stream.iterate(0, n -> n < 100, n -> n + 2);  // JDK 9+ 有限迭代

Stream<Double> randomStream = Stream.generate(Math::random);

// 限制无限流
Stream<Integer> limitedStream = Stream.iterate(0, n -> n + 1)
    .limit(100);

// 从文件创建
try (Stream<String> lines = Files.lines(Paths.get("file.txt"))) {
    // 处理每一行
}

// 从字符串创建
IntStream chars = "Hello".chars();
```

### 中间操作（返回Stream）

```java
List<Integer> numbers = Arrays.asList(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);

// filter - 过滤
numbers.stream()
    .filter(n -> n % 2 == 0)           // 偶数
    .forEach(System.out::println);

// map - 转换
numbers.stream()
    .map(n -> n * n)                   // 平方
    .collect(Collectors.toList());

// flatMap - 扁平化
List<List<Integer>> nested = Arrays.asList(
    Arrays.asList(1, 2),
    Arrays.asList(3, 4),
    Arrays.asList(5, 6)
);
List<Integer> flat = nested.stream()
    .flatMap(List::stream)             // 将多个List合并为一个Stream
    .collect(Collectors.toList());     // [1, 2, 3, 4, 5, 6]

// distinct - 去重
Arrays.asList(1, 2, 2, 3, 3, 3).stream()
    .distinct()
    .collect(Collectors.toList());     // [1, 2, 3]

// sorted - 排序
numbers.stream()
    .sorted()                          // 自然排序
    .collect(Collectors.toList());

numbers.stream()
    .sorted(Comparator.reverseOrder()) // 倒序
    .collect(Collectors.toList());

numbers.stream()
    .sorted(Comparator.comparing(n -> -n)) // 自定义排序
    .collect(Collectors.toList());

// peek - 查看（调试用）
numbers.stream()
    .peek(n -> System.out.println("Processing: " + n))
    .map(n -> n * 2)
    .collect(Collectors.toList());

// limit - 限制数量
numbers.stream()
    .limit(5)
    .collect(Collectors.toList());     // [1, 2, 3, 4, 5]

// skip - 跳过
numbers.stream()
    .skip(5)
    .collect(Collectors.toList());     // [6, 7, 8, 9, 10]

// takeWhile - 一直取直到条件不满足（JDK 9+）
numbers.stream()
    .takeWhile(n -> n < 6)
    .collect(Collectors.toList());     // [1, 2, 3, 4, 5]

// dropWhile - 一直丢直到条件满足（JDK 9+）
numbers.stream()
    .dropWhile(n -> n < 6)
    .collect(Collectors.toList());     // [6, 7, 8, 9, 10]
```

### 终结操作（返回结果）

```java
// forEach - 遍历
numbers.stream().forEach(System.out::println);

// forEachOrdered - 保证顺序遍历（并行流中有意义）
numbers.parallelStream().forEachOrdered(System.out::println);

// collect - 收集
List<Integer> list = numbers.stream().collect(Collectors.toList());
Set<Integer> set = numbers.stream().collect(Collectors.toSet());

// toArray
Integer[] array = numbers.stream().toArray(Integer[]::new);

// reduce - 归约
int sum = numbers.stream().reduce(0, (a, b) -> a + b);
int sum2 = numbers.stream().reduce(0, Integer::sum);
Optional<Integer> sumOptional = numbers.stream().reduce(Integer::sum);

// 字符串连接
String joined = Stream.of("a", "b", "c")
    .reduce("", (a, b) -> a + "," + b);

// min/max
Optional<Integer> min = numbers.stream().min(Comparator.naturalOrder());
Optional<Integer> max = numbers.stream().max(Comparator.naturalOrder());

// count
long count = numbers.stream().filter(n -> n > 5).count();

// anyMatch/allMatch/noneMatch
boolean hasEven = numbers.stream().anyMatch(n -> n % 2 == 0);
boolean allPositive = numbers.stream().allMatch(n -> n > 0);
boolean noNegative = numbers.stream().noneMatch(n -> n < 0);

// findFirst/findAny
Optional<Integer> first = numbers.stream().findFirst();
Optional<Integer> any = numbers.stream().findAny();  // 并行流中更高效
```

### Collectors收集器

```java
// 转换为集合
List<String> list = stream.collect(Collectors.toList());
Set<String> set = stream.collect(Collectors.toSet());
Collection<String> collection = stream.collect(Collectors.toCollection(ArrayList::new));
Map<String, Integer> map = stream.collect(Collectors.toMap(
    s -> s,                    // keyMapper
    String::length             // valueMapper
));

// 处理key冲突
Map<String, Integer> map2 = stream.collect(Collectors.toMap(
    s -> s,
    String::length,
    (existing, replacement) -> existing  // 冲突时保留已有值
));

// 指定Map类型
Map<String, Integer> linkedHashMap = stream.collect(Collectors.toMap(
    s -> s,
    String::length,
    (e1, e2) -> e1,
    LinkedHashMap::new
));

// 分组
Map<Integer, List<String>> groupedByLength = stream.collect(
    Collectors.groupingBy(String::length)
);

// 分组计数
Map<Integer, Long> countByLength = stream.collect(
    Collectors.groupingBy(String::length, Collectors.counting())
);

// 分区（按条件分成两组）
Map<Boolean, List<Integer>> partitioned = numbers.stream()
    .collect(Collectors.partitioningBy(n -> n % 2 == 0));
// partitioned.get(true)  - 偶数
// partitioned.get(false) - 奇数

// 连接字符串
String joined = stream.collect(Collectors.joining());           // 直接连接
String joined2 = stream.collect(Collectors.joining(", "));      // 带分隔符
String joined3 = stream.collect(Collectors.joining(", ", "[", "]")); // 带前后缀

// 统计
IntSummaryStatistics stats = numbers.stream()
    .collect(Collectors.summarizingInt(Integer::intValue));
stats.getCount();
stats.getSum();
stats.getMin();
stats.getAverage();
stats.getMax();

//  averagingInt/averagingLong/averagingDouble
//  summingInt/summingLong/summingDouble

// 归约
Integer sum = numbers.stream().collect(Collectors.reducing(0, Integer::sum));

// mapping（在收集前转换）
Map<Integer, List<String>> lengthToUpperCase = stream.collect(
    Collectors.groupingBy(
        String::length,
        Collectors.mapping(String::toUpperCase, Collectors.toList())
    )
);

// flatMapping（扁平化映射）
Map<String, List<Integer>> flatMapped = stream.collect(
    Collectors.groupingBy(
        s -> s.substring(0, 1),
        Collectors.flatMapping(
            s -> s.chars().boxed(),
            Collectors.toList()
        )
    )
);
```

### 原始类型特化流

```java
// IntStream
IntStream intStream = IntStream.of(1, 2, 3);
IntStream range = IntStream.range(1, 10);        // 1-9
IntStream rangeClosed = IntStream.rangeClosed(1, 10);  // 1-10

int sum = intStream.sum();
OptionalInt max = intStream.max();
OptionalInt min = intStream.min();
int average = intStream.average().orElse(0);

// LongStream
LongStream longStream = LongStream.of(1L, 2L, 3L);

// DoubleStream
DoubleStream doubleStream = DoubleStream.of(1.0, 2.0, 3.0);

// 装箱/拆箱
Stream<Integer> boxed = intStream.boxed();       // IntStream -> Stream<Integer>
IntStream unboxed = stream.mapToInt(Integer::intValue);  // Stream<Integer> -> IntStream

// 对象流转原始流
int totalLength = strings.stream()
    .mapToInt(String::length)
    .sum();
```

---

## 🔍 Optional速查

### 创建Optional

```java
// 创建包含非空值的Optional
Optional<String> optional1 = Optional.of("value");
// Optional.of(null);  // 会抛出NullPointerException

// 创建可包含null的Optional
Optional<String> optional2 = Optional.ofNullable(getValue());
Optional<String> optional3 = Optional.ofNullable(null);  // 空Optional

// 创建空Optional
Optional<String> empty = Optional.empty();
```

### 常用操作

```java
Optional<String> optional = Optional.of("Hello");

// 判断是否有值
boolean present = optional.isPresent();
boolean empty = optional.isEmpty();  // JDK 11+

// 获取值（不推荐直接使用）
String value = optional.get();  // 空时抛NoSuchElementException

// 安全获取值（推荐）
String valueOrDefault = optional.orElse("default");
String valueOrElseGet = optional.orElseGet(() -> computeDefault());
String valueOrThrow = optional.orElseThrow();  // JDK 10+
String valueOrThrowCustom = optional.orElseThrow(() -> new RuntimeException("Empty"));

// ifPresent（有值时执行）
optional.ifPresent(System.out::println);

// ifPresentOrElse（JDK 9+）
optional.ifPresentOrElse(
    v -> System.out.println("Value: " + v),
    () -> System.out.println("Empty")
);

// filter（条件过滤）
Optional<String> filtered = optional.filter(s -> s.length() > 3);

// map（值转换）
Optional<Integer> length = optional.map(String::length);

// flatMap（避免嵌套Optional）
Optional<Optional<String>> nested = optional.map(this::getOptional);
Optional<String> flat = optional.flatMap(this::getOptional);

// stream（JDK 9+）
optional.stream().forEach(System.out::println);
```

### 使用场景

```java
// 场景1：避免空指针
// 传统写法
String result = getString();
if (result != null) {
    return result.toUpperCase();
} else {
    return "DEFAULT";
}

// Optional写法
return Optional.ofNullable(getString())
    .map(String::toUpperCase)
    .orElse("DEFAULT");

// 场景2：链式调用避免空指针
// 传统写法
String city = null;
if (user != null) {
    Address address = user.getAddress();
    if (address != null) {
        city = address.getCity();
    }
}

// Optional写法
String city = Optional.ofNullable(user)
    .map(User::getAddress)
    .map(Address::getCity)
    .orElse("Unknown");

// 场景3：方法返回Optional表示可能无值
public Optional<User> findUserById(Long id) {
    User user = userRepository.findById(id);
    return Optional.ofNullable(user);
}

// 调用
User user = findUserById(1L)
    .orElseThrow(() -> new UserNotFoundException("User not found"));

// 场景4：异常替代
public String readFile(String path) {
    return Optional.ofNullable(readContent(path))
        .orElseThrow(() -> new FileReadException("Failed to read: " + path));
}
```

---

## 📅 新日期时间API（java.time）

### 核心类速查

| 类 | 说明 | 示例 |
|----|------|------|
| `LocalDate` | 日期（年月日） | 2024-03-15 |
| `LocalTime` | 时间（时分秒） | 14:30:00 |
| `LocalDateTime` | 日期时间 | 2024-03-15T14:30:00 |
| `ZonedDateTime` | 带时区的日期时间 | 2024-03-15T14:30+08:00[Asia/Shanghai] |
| `Instant` | 时间戳（UTC） | 2024-03-15T06:30:00Z |
| `Duration` | 时间段（秒/纳秒） | PT2H30M |
| `Period` | 日期间隔（年月日） | P1Y2M3D |
| `DateTimeFormatter` | 日期格式化 | yyyy-MM-dd |

### 创建与获取

```java
// 当前日期时间
LocalDate today = LocalDate.now();
LocalTime now = LocalTime.now();
LocalDateTime dateTime = LocalDateTime.now();
ZonedDateTime zoned = ZonedDateTime.now();
ZonedDateTime zonedInNY = ZonedDateTime.now(ZoneId.of("America/New_York"));

// 指定值创建
LocalDate date = LocalDate.of(2024, 3, 15);
LocalTime time = LocalTime.of(14, 30, 0);
LocalDateTime dateTime2 = LocalDateTime.of(2024, 3, 15, 14, 30);

// 从字符串解析
LocalDate parsedDate = LocalDate.parse("2024-03-15");
LocalDateTime parsedDateTime = LocalDateTime.parse("2024-03-15T14:30:00");

// 时间戳
Instant instant = Instant.now();
long epochMilli = instant.toEpochMilli();
Instant fromEpoch = Instant.ofEpochMilli(1710505800000L);

// 转换
LocalDateTime fromInstant = LocalDateTime.ofInstant(instant, ZoneId.systemDefault());
Instant toInstant = dateTime.atZone(ZoneId.systemDefault()).toInstant();
```

### 日期时间操作

```java
LocalDate date = LocalDate.of(2024, 3, 15);

// 加减操作
LocalDate nextDay = date.plusDays(1);
LocalDate lastWeek = date.minusWeeks(1);
LocalDate nextMonth = date.plusMonths(1);
LocalDate nextYear = date.plusYears(1);
LocalDateTime later = dateTime.plusHours(2).plusMinutes(30);

// 修改特定字段
LocalDate withDay = date.withDayOfMonth(1);      // 设为当月1日
LocalDate withMonth = date.withMonth(6);         // 设为6月
LocalDate withYear = date.withYear(2025);        // 设为2025年
LocalDate firstDayOfMonth = date.with(TemporalAdjusters.firstDayOfMonth());
LocalDate lastDayOfMonth = date.with(TemporalAdjusters.lastDayOfMonth());
LocalDate firstDayOfNextMonth = date.with(TemporalAdjusters.firstDayOfNextMonth());
LocalDate nextMonday = date.with(TemporalAdjusters.next(DayOfWeek.MONDAY));

// 获取信息
int year = date.getYear();
int month = date.getMonthValue();
Month monthEnum = date.getMonth();  // MARCH
int day = date.getDayOfMonth();
DayOfWeek dayOfWeek = date.getDayOfWeek();  // FRIDAY
int dayOfYear = date.getDayOfYear();

// 比较
boolean isBefore = date.isBefore(LocalDate.now());
boolean isAfter = date.isAfter(LocalDate.now());
boolean isEqual = date.isEqual(anotherDate);

// 计算间隔
Period period = Period.between(startDate, endDate);
int years = period.getYears();
int months = period.getMonths();
int days = period.getDays();

long daysBetween = ChronoUnit.DAYS.between(startDate, endDate);
long hoursBetween = ChronoUnit.HOURS.between(startTime, endTime);

Duration duration = Duration.between(startTime, endTime);
long seconds = duration.getSeconds();
long millis = duration.toMillis();
```

### 格式化与解析

```java
// 预定义格式
DateTimeFormatter isoDate = DateTimeFormatter.ISO_LOCAL_DATE;      // 2024-03-15
DateTimeFormatter isoDateTime = DateTimeFormatter.ISO_LOCAL_DATE_TIME;  // 2024-03-15T14:30:00

// 自定义格式
DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
DateTimeFormatter chineseFormatter = DateTimeFormatter.ofPattern(
    "yyyy年MM月dd日",
    Locale.CHINA
);

// 格式化
String formatted = dateTime.format(formatter);
String chinese = date.format(chineseFormatter);

// 解析
LocalDateTime parsed = LocalDateTime.parse("2024-03-15 14:30:00", formatter);

// 带时区的格式化
DateTimeFormatter zonedFormatter = DateTimeFormatter.ofPattern(
    "yyyy-MM-dd HH:mm:ss z"
);
String zonedString = zonedDateTime.format(zonedFormatter);
```

### 时区处理

```java
// 所有可用时区
Set<String> zoneIds = ZoneId.getAvailableZoneIds();

// 常用时区
ZoneId shanghai = ZoneId.of("Asia/Shanghai");
ZoneId newYork = ZoneId.of("America/New_York");
ZoneId utc = ZoneId.of("UTC");

// 带时区的时间
ZonedDateTime zdt = ZonedDateTime.now(shanghai);

// 时区转换
ZonedDateTime nyTime = zdt.withZoneSameInstant(newYork);

// OffsetDateTime
OffsetDateTime offsetDateTime = OffsetDateTime.now();
```

---

## 🎯 常用代码场景

### 1. 列表去重排序

```java
// 去重并保持顺序
List<String> unique = list.stream()
    .distinct()
    .collect(Collectors.toList());

// 去重并排序
List<String> sortedUnique = list.stream()
    .distinct()
    .sorted()
    .collect(Collectors.toList());

// 根据属性去重
List<User> uniqueUsers = users.stream()
    .collect(Collectors.collectingAndThen(
        Collectors.toMap(
            User::getId,
            Function.identity(),
            (existing, replacement) -> existing
        ),
        map -> new ArrayList<>(map.values())
    ));
```

### 2. 分组统计

```java
// 按部门分组
Map<String, List<Employee>> byDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDepartment));

// 分组计数
Map<String, Long> countByDept = employees.stream()
    .collect(Collectors.groupingBy(Employee::getDepartment, Collectors.counting()));

// 分组求平均工资
Map<String, Double> avgSalaryByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.averagingDouble(Employee::getSalary)
    ));

// 分组取最高工资
Map<String, Optional<Employee>> maxSalaryByDept = employees.stream()
    .collect(Collectors.groupingBy(
        Employee::getDepartment,
        Collectors.maxBy(Comparator.comparing(Employee::getSalary))
    ));
```

### 3. 分页处理

```java
public <T> List<T> getPage(List<T> list, int pageNum, int pageSize) {
    return list.stream()
        .skip((pageNum - 1) * pageSize)
        .limit(pageSize)
        .collect(Collectors.toList());
}

// 获取第2页，每页10条
List<User> page2 = getPage(users, 2, 10);
```

### 4. 文件处理

```java
// 读取文件所有行
List<String> lines = Files.readAllLines(Paths.get("file.txt"));

// 带过滤的读取
try (Stream<String> stream = Files.lines(Paths.get("file.txt"))) {
    List<String> filtered = stream
        .filter(line -> line.contains("ERROR"))
        .collect(Collectors.toList());
}

// 统计文件行数
long lineCount = Files.lines(Paths.get("file.txt")).count();

// 查找文件
try (Stream<Path> paths = Files.walk(Paths.get("/home/user"))) {
    List<Path> javaFiles = paths
        .filter(Files::isRegularFile)
        .filter(p -> p.toString().endsWith(".java"))
        .collect(Collectors.toList());
}
```

### 5. 日期时间工具类

```java
public class DateUtils {
    private static final DateTimeFormatter DEFAULT_FORMATTER = 
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    // 获取当前时间字符串
    public static String now() {
        return LocalDateTime.now().format(DEFAULT_FORMATTER);
    }
    
    // 格式化
    public static String format(LocalDateTime dateTime, String pattern) {
        return dateTime.format(DateTimeFormatter.ofPattern(pattern));
    }
    
    // 解析
    public static LocalDateTime parse(String str, String pattern) {
        return LocalDateTime.parse(str, DateTimeFormatter.ofPattern(pattern));
    }
    
    // 获取当天开始/结束
    public static LocalDateTime startOfDay(LocalDate date) {
        return date.atStartOfDay();
    }
    
    public static LocalDateTime endOfDay(LocalDate date) {
        return date.atTime(LocalTime.MAX);
    }
    
    // 获取本周一
    public static LocalDate getMonday(LocalDate date) {
        return date.with(TemporalAdjusters.previousOrSame(DayOfWeek.MONDAY));
    }
    
    // 获取本月第一天
    public static LocalDate getFirstDayOfMonth(LocalDate date) {
        return date.with(TemporalAdjusters.firstDayOfMonth());
    }
    
    // 计算年龄
    public static int calculateAge(LocalDate birthDate) {
        return Period.between(birthDate, LocalDate.now()).getYears();
    }
    
    // 判断是否闰年
    public static boolean isLeapYear(int year) {
        return Year.of(year).isLeap();
    }
    
    // 日期范围遍历
    public static List<LocalDate> getDateRange(LocalDate start, LocalDate end) {
        List<LocalDate> dates = new ArrayList<>();
        LocalDate current = start;
        while (!current.isAfter(end)) {
            dates.add(current);
            current = current.plusDays(1);
        }
        return dates;
    }
}
```

---

## ⚠️ 常见坑点速查

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| Stream只能消费一次 | 第二次操作抛异常 | 需要多次使用先collect到List |
| 并行流线程安全 | 并发修改共享变量 | 使用Concurrent集合或避免共享状态 |
| Optional不要滥用 | 不要所有地方都用 | 主要用于返回值和链式操作 |
| Optional不要用于字段 | 增加包装开销 | 字段直接用null判断 |
| 日期格式化线程不安全 | SimpleDateFormat的问题 | 使用DateTimeFormatter（线程安全）|
| LocalDateTime无时区 | 不能直接转时间戳 | 先指定时区再转换 |
| Stream的sorted内存消耗 | 大数据量排序 | 考虑数据库排序或分批处理 |
| Lambda中的变量捕获 | 必须是final或 effectively final | 使用数组或Atomic类包装 |

---

> 💡 **提示**：本文档用于日常速查，系统学习请查看《学习笔记.md》
