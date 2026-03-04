# Comparable 和 Comparator 的区别？在什么场景下使用？

## 一、核心概念

### 1.1 Comparable 接口

**Comparable 接口**：
- **包路径**：`java.lang.Comparable`
- **定义**：对象**内部比较规则**接口，类自身实现排序逻辑
- **方法**：`int compareTo(T o)`
- **特点**：**自然排序**，一个类只能有一种自然顺序

### 1.2 Comparator 接口

**Comparator 接口**：
- **包路径**：`java.util.Comparator`
- **定义**：**外部比较器**接口，在类外部定义排序逻辑
- **方法**：`int compare(T o1, T o2)`
- **特点**：**定制排序**，可以为同一个类定义多种不同的比较规则

### 1.3 核心区别

| 对比项 | Comparable | Comparator |
|--------|-----------|-----------|
| **包路径** | `java.lang` | `java.util` |
| **实现位置** | 类内部实现 | 类外部实现 |
| **方法签名** | `compareTo(T o)` | `compare(T o1, T o2)` |
| **排序类型** | 自然排序 | 定制排序 |
| **比较规则数量** | 一个类一种 | 可以有多种 |
| **修改灵活性** | 需要修改类 | 不需要修改类 |

---

## 二、Comparable 接口详解

### 2.1 接口定义

```java
// Comparable 接口定义
public interface Comparable<T> {
    /**
     * 比较此对象与指定对象的顺序
     * @param o 要比较的对象
     * @return 负整数、零或正整数，分别表示此对象小于、等于或大于指定对象
     */
    int compareTo(T o);
}
```

### 2.2 返回值规则

**compareTo() 返回值**：
- **负数**：当前对象 < 参数对象
- **0**：当前对象 = 参数对象
- **正数**：当前对象 > 参数对象

### 2.3 实现示例

```java
// 学生类实现 Comparable
public class Student implements Comparable<Student> {
    private String name;
    private int age;
    private int score;
    
    public Student(String name, int age, int score) {
        this.name = name;
        this.age = age;
        this.score = score;
    }
    
    // 实现 compareTo 方法：按年龄排序
    @Override
    public int compareTo(Student o) {
        // 升序：this.age - o.age
        // 降序：o.age - this.age
        return this.age - o.age;
    }
    
    // getter 方法
    public String getName() { return name; }
    public int getAge() { return age; }
    public int getScore() { return score; }
    
    @Override
    public String toString() {
        return "Student{name='" + name + "', age=" + age + ", score=" + score + '}';
    }
}

// 使用示例
public class ComparableExample {
    public static void main(String[] args) {
        List<Student> students = new ArrayList<>();
        students.add(new Student("张三", 20, 85));
        students.add(new Student("李四", 18, 90));
        students.add(new Student("王五", 22, 80));
        
        // 直接排序（使用 Comparable）
        Collections.sort(students);
        
        // 输出：按年龄升序
        for (Student s : students) {
            System.out.println(s);
        }
        // Student{name='李四', age=18, score=90}
        // Student{name='张三', age=20, score=85}
        // Student{name='王五', age=22, score=80}
    }
}
```

### 2.4 常见实现类

**Java 内置类已实现 Comparable**：
- `String`：按字典序排序
- `Integer`、`Long`、`Double` 等：按数值大小排序
- `Date`：按时间先后排序
- `BigDecimal`：按数值大小排序

```java
// String 实现 Comparable
String[] names = {"张三", "李四", "王五"};
Arrays.sort(names);  // 按字典序排序

// Integer 实现 Comparable
List<Integer> numbers = Arrays.asList(3, 1, 4, 1, 5);
Collections.sort(numbers);  // 按数值大小排序：[1, 1, 3, 4, 5]
```

---

## 三、Comparator 接口详解

### 3.1 接口定义

```java
// Comparator 接口定义
@FunctionalInterface
public interface Comparator<T> {
    /**
     * 比较两个参数的顺序
     * @param o1 第一个要比较的对象
     * @param o2 第二个要比较的对象
     * @return 负整数、零或正整数，分别表示第一个参数小于、等于或大于第二个参数
     */
    int compare(T o1, T o2);
    
    // 其他默认方法...
}
```

### 3.2 实现方式

#### 方式1：匿名内部类

```java
// 使用匿名内部类实现 Comparator
List<Student> students = new ArrayList<>();
students.add(new Student("张三", 20, 85));
students.add(new Student("李四", 18, 90));
students.add(new Student("王五", 22, 80));

// 按分数降序排序
Collections.sort(students, new Comparator<Student>() {
    @Override
    public int compare(Student o1, Student o2) {
        return o2.getScore() - o1.getScore();  // 降序
    }
});
```

#### 方式2：Lambda 表达式（推荐）

```java
// 使用 Lambda 表达式（JDK 8+）
Collections.sort(students, (o1, o2) -> o2.getScore() - o1.getScore());

// 或使用方法引用
Collections.sort(students, Comparator.comparing(Student::getScore).reversed());
```

#### 方式3：实现类

```java
// 定义多个比较器类
public class StudentScoreComparator implements Comparator<Student> {
    @Override
    public int compare(Student o1, Student o2) {
        return o2.getScore() - o1.getScore();  // 按分数降序
    }
}

public class StudentNameComparator implements Comparator<Student> {
    @Override
    public int compare(Student o1, Student o2) {
        return o1.getName().compareTo(o2.getName());  // 按姓名升序
    }
}

// 使用
Collections.sort(students, new StudentScoreComparator());  // 按分数排序
Collections.sort(students, new StudentNameComparator());   // 按姓名排序
```

### 3.3 Comparator 工具方法（JDK 8+）

**Comparator 提供的便捷方法**：

```java
// 1. comparing：按指定字段排序
Comparator<Student> byAge = Comparator.comparing(Student::getAge);

// 2. thenComparing：多条件排序
Comparator<Student> multiSort = Comparator
    .comparing(Student::getScore)      // 先按分数
    .thenComparing(Student::getAge)   // 再按年龄
    .thenComparing(Student::getName); // 最后按姓名

// 3. reversed：反转排序
Comparator<Student> reversed = Comparator.comparing(Student::getAge).reversed();

// 4. nullsFirst / nullsLast：处理 null 值
Comparator<Student> nullSafe = Comparator
    .nullsFirst(Comparator.comparing(Student::getName));

// 5. naturalOrder / reverseOrder：自然排序
Comparator<String> natural = Comparator.naturalOrder();
Comparator<String> reverse = Comparator.reverseOrder();
```

### 3.4 多条件排序示例

```java
// 多条件排序：先按分数降序，分数相同按年龄升序，年龄相同按姓名升序
Comparator<Student> complexComparator = Comparator
    .comparing(Student::getScore, Comparator.reverseOrder())  // 分数降序
    .thenComparing(Student::getAge)                            // 年龄升序
    .thenComparing(Student::getName);                           // 姓名升序

Collections.sort(students, complexComparator);
```

---

## 四、区别对比

### 4.1 详细对比表

| 对比项 | Comparable | Comparator |
|--------|-----------|-----------|
| **包路径** | `java.lang.Comparable` | `java.util.Comparator` |
| **实现位置** | 类内部实现 | 类外部实现 |
| **方法签名** | `int compareTo(T o)` | `int compare(T o1, T o2)` |
| **参数数量** | 1个（另一个是this） | 2个 |
| **排序类型** | 自然排序 | 定制排序 |
| **比较规则** | 一个类一种 | 可以有多种 |
| **修改灵活性** | 需要修改类源码 | 不需要修改类 |
| **使用场景** | 固定唯一的排序规则 | 多种排序规则 |
| **在集合中使用** | `Collections.sort(list)` | `Collections.sort(list, comparator)` |
| **TreeSet/TreeMap** | 构造时不需要参数 | 构造时需要传入Comparator |

### 4.2 使用方式对比

```java
// Comparable：类内部实现
public class Student implements Comparable<Student> {
    @Override
    public int compareTo(Student o) {
        return this.age - o.age;
    }
}

// 使用：直接排序
Collections.sort(students);

// ============================================

// Comparator：类外部实现
public class StudentAgeComparator implements Comparator<Student> {
    @Override
    public int compare(Student o1, Student o2) {
        return o1.getAge() - o2.getAge();
    }
}

// 使用：传入比较器
Collections.sort(students, new StudentAgeComparator());
```

---

## 五、使用场景

### 5.1 Comparable 适用场景

✅ **排序规则固定唯一**
- 类的排序规则是固定的，不会改变
- 例如：`Student` 类始终按学号排序

✅ **类自身定义排序逻辑**
- 排序逻辑是类的固有属性
- 例如：`String` 按字典序，`Integer` 按数值大小

✅ **简单直接的使用**
- 只需要一种排序方式
- 使用简单，直接调用 `Collections.sort(list)`

**示例场景**：
```java
// 订单类：始终按订单号排序
public class Order implements Comparable<Order> {
    private Long orderId;
    
    @Override
    public int compareTo(Order o) {
        return this.orderId.compareTo(o.orderId);
    }
}
```

### 5.2 Comparator 适用场景

✅ **多种排序规则**
- 同一个类需要按不同字段排序
- 例如：`Student` 可以按年龄、分数、姓名分别排序

✅ **不修改类源码**
- 不想或不能修改类的源码
- 例如：使用第三方库的类

✅ **临时排序需求**
- 只需要在特定场景下排序
- 例如：某个页面按销量排序，另一个页面按价格排序

✅ **复杂排序逻辑**
- 需要多条件排序
- 例如：先按分数，再按年龄，最后按姓名

**示例场景**：
```java
// 商品类：不同页面需要不同排序
public class Product {
    private String name;
    private double price;
    private int sales;
    private Date createTime;
}

// 商品列表页面：按价格排序
Collections.sort(products, Comparator.comparing(Product::getPrice));

// 热销页面：按销量排序
Collections.sort(products, Comparator.comparing(Product::getSales).reversed());

// 新品页面：按创建时间排序
Collections.sort(products, Comparator.comparing(Product::getCreateTime).reversed());
```

---

## 六、代码示例

### 6.1 完整示例：学生排序

```java
// 学生类（不实现 Comparable）
public class Student {
    private String name;
    private int age;
    private int score;
    
    public Student(String name, int age, int score) {
        this.name = name;
        this.age = age;
        this.score = score;
    }
    
    // getter 方法
    public String getName() { return name; }
    public int getAge() { return age; }
    public int getScore() { return score; }
    
    @Override
    public String toString() {
        return "Student{name='" + name + "', age=" + age + ", score=" + score + '}';
    }
}

// 测试类
public class SortExample {
    public static void main(String[] args) {
        List<Student> students = new ArrayList<>();
        students.add(new Student("张三", 20, 85));
        students.add(new Student("李四", 18, 90));
        students.add(new Student("王五", 22, 80));
        students.add(new Student("赵六", 20, 88));
        
        System.out.println("原始顺序：");
        students.forEach(System.out::println);
        
        // 方式1：按年龄排序（Lambda）
        Collections.sort(students, (s1, s2) -> s1.getAge() - s2.getAge());
        System.out.println("\n按年龄排序：");
        students.forEach(System.out::println);
        
        // 方式2：按分数降序（方法引用）
        Collections.sort(students, Comparator.comparing(Student::getScore).reversed());
        System.out.println("\n按分数降序：");
        students.forEach(System.out::println);
        
        // 方式3：多条件排序（先分数降序，再年龄升序）
        Collections.sort(students, Comparator
            .comparing(Student::getScore).reversed()
            .thenComparing(Student::getAge));
        System.out.println("\n多条件排序（分数降序，年龄升序）：");
        students.forEach(System.out::println);
    }
}
```

### 6.2 TreeSet/TreeMap 中的使用

```java
// TreeSet 使用 Comparable
Set<String> treeSet1 = new TreeSet<>();  // String 实现了 Comparable
treeSet1.add("张三");
treeSet1.add("李四");
treeSet1.add("王五");
// 自动按字典序排序

// TreeSet 使用 Comparator
Set<Student> treeSet2 = new TreeSet<>(
    Comparator.comparing(Student::getScore).reversed()
);
treeSet2.add(new Student("张三", 20, 85));
treeSet2.add(new Student("李四", 18, 90));
// 按分数降序排序

// TreeMap 使用 Comparator
Map<Student, String> treeMap = new TreeMap<>(
    Comparator.comparing(Student::getAge)
);
treeMap.put(new Student("张三", 20, 85), "value1");
treeMap.put(new Student("李四", 18, 90), "value2");
// 按年龄排序
```

---

## 七、常见面试追问

### Q1：一个类能同时使用 Comparable 和 Comparator 吗？

**答**：
- ✅ **可以同时使用**
- **Comparable**：定义类的**自然排序**（默认排序）
- **Comparator**：提供**额外的排序规则**（覆盖自然排序）

**示例**：
```java
// Student 实现 Comparable（自然排序：按年龄）
public class Student implements Comparable<Student> {
    @Override
    public int compareTo(Student o) {
        return this.age - o.age;
    }
}

// 使用自然排序
Collections.sort(students);  // 按年龄排序

// 使用 Comparator 覆盖自然排序
Collections.sort(students, Comparator.comparing(Student::getScore));  // 按分数排序
```

### Q2：Comparator 如何实现多条件排序？

**答**：
- 使用 `thenComparing()` 方法链式调用
- 先比较第一个条件，相等时再比较第二个条件

**示例**：
```java
Comparator<Student> multiSort = Comparator
    .comparing(Student::getScore)      // 第一条件：分数
    .thenComparing(Student::getAge)    // 第二条件：年龄
    .thenComparing(Student::getName); // 第三条件：姓名
```

### Q3：为什么推荐使用 Comparator？

**答**：
1. **解耦**：排序逻辑不写在类中，类更简洁
2. **灵活**：可以为同一个类定义多种排序规则
3. **不修改源码**：不需要修改类的源码
4. **符合开闭原则**：对扩展开放，对修改关闭

### Q4：什么时候用 Comparable，什么时候用 Comparator？

**答**：

**使用 Comparable**：
- ✅ 排序规则固定唯一
- ✅ 排序逻辑是类的固有属性
- ✅ 只需要一种排序方式

**使用 Comparator**：
- ✅ 需要多种排序规则
- ✅ 不想修改类源码
- ✅ 临时排序需求
- ✅ 复杂排序逻辑

---

## 八、面试回答模板

### 8.1 核心回答（1分钟）

"Comparable 是对象内部的比较接口，定义自然排序，类自身实现 compareTo 方法，一个类只能有一种自然顺序，比如 String、Integer 都实现了 Comparable。Comparator 是外部比较器，在类外部定义排序逻辑，实现 compare 方法，可以为同一个类定义多种不同的比较规则。区别是 Comparable 在类内部实现，排序规则固定；Comparator 在类外部实现，排序规则灵活。使用场景上，固定唯一的排序规则用 Comparable，多种排序规则用 Comparator。"

### 8.2 扩展回答（3分钟）

"从实现角度看，Comparable 接口在 java.lang 包中，类实现 compareTo 方法，定义自然排序，使用简单，直接调用 Collections.sort(list) 即可。Comparator 接口在 java.util 包中，在类外部实现 compare 方法，定义定制排序，需要传入比较器，比如 Collections.sort(list, comparator)。JDK 8 提供了 Comparator 的便捷方法，如 comparing、thenComparing、reversed 等，支持链式调用实现多条件排序。选择上，如果排序规则固定唯一，用 Comparable；如果需要多种排序规则或不想修改类源码，用 Comparator。实际项目中，Comparator 更灵活，推荐使用。"

### 8.3 加分项

- 能说出 Comparable 和 Comparator 的包路径和方法签名
- 了解 JDK 8 中 Comparator 的便捷方法
- 知道如何在 TreeSet/TreeMap 中使用
- 理解为什么推荐使用 Comparator
- 能说出多条件排序的实现方式