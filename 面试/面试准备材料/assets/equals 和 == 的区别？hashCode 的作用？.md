# Java 中 equals() 和 == 的区别？hashCode() 有什么作用？

## 一、核心概念

### 1.1 == 运算符

**== 的作用**：
- **基本数据类型**：比较的是**值**是否相等
- **引用数据类型**：比较的是**内存地址**是否相同（是否指向同一个对象）

### 1.2 equals() 方法

**equals() 的作用**：
- **默认实现**：继承自`Object`类，底层实现是`==`，比较的是地址
- **重写后**：用来比较**对象的内容是否相等**

### 1.3 hashCode() 方法

**hashCode() 的作用**：
- 返回对象的**哈希值**（int类型）
- 在集合框架中用来**确定对象存放的位置**，提升查找效率

---

## 二、== 运算符详解

### 2.1 基本数据类型比较

```java
// 基本数据类型：比较值
int a = 10;
int b = 10;
System.out.println(a == b);  // true，值相等

double x = 3.14;
double y = 3.14;
System.out.println(x == y);  // true，值相等
```

**特点**：
- 直接比较**值**
- 不涉及对象引用

### 2.2 引用数据类型比较

```java
// 引用数据类型：比较地址
String str1 = new String("hello");
String str2 = new String("hello");
System.out.println(str1 == str2);  // false，地址不同

String str3 = "hello";
String str4 = "hello";
System.out.println(str3 == str4);  // true，字符串常量池，地址相同

// 对象比较
Object obj1 = new Object();
Object obj2 = new Object();
System.out.println(obj1 == obj2);  // false，地址不同

Object obj3 = obj1;
System.out.println(obj1 == obj3);  // true，指向同一个对象
```

**关键点**：
- `==`比较的是**引用地址**，不是对象内容
- 两个不同的对象，即使内容相同，`==`也返回false

### 2.3 字符串常量池

```java
// 字符串常量池
String s1 = "hello";  // 在常量池中创建
String s2 = "hello";  // 从常量池中获取
System.out.println(s1 == s2);  // true，指向同一个对象

String s3 = new String("hello");  // 在堆中创建新对象
System.out.println(s1 == s3);  // false，地址不同
System.out.println(s1.equals(s3));  // true，内容相同
```

---

## 三、equals() 方法详解

### 3.1 Object类的equals()实现

```java
// Object类的equals()方法
public boolean equals(Object obj) {
    return (this == obj);  // 默认比较地址
}
```

**默认实现**：
- 直接使用`==`比较
- 比较的是**对象地址**

### 3.2 String类的equals()重写

```java
// String类的equals()方法
public boolean equals(Object anObject) {
    if (this == anObject) {
        return true;  // 地址相同，直接返回true
    }
    if (anObject instanceof String) {
        String anotherString = (String)anObject;
        int n = value.length;
        if (n == anotherString.value.length) {
            char v1[] = value;
            char v2[] = anotherString.value;
            int i = 0;
            while (n-- != 0) {
                if (v1[i] != v2[i])
                    return false;
                i++;
            }
            return true;  // 逐个字符比较
        }
    }
    return false;
}
```

**特点**：
- **先比较地址**：地址相同直接返回true
- **再比较内容**：逐个字符比较
- **比较的是内容**，不是地址

### 3.3 自定义类重写equals()

```java
// 自定义类重写equals()
public class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public boolean equals(Object obj) {
        // 1. 地址相同
        if (this == obj) return true;
        
        // 2. 类型检查
        if (obj == null || getClass() != obj.getClass()) return false;
        
        // 3. 类型转换
        Person person = (Person) obj;
        
        // 4. 比较关键字段
        return age == person.age &&
               Objects.equals(name, person.name);
    }
}
```

**重写equals()的规范**：
1. **自反性**：`x.equals(x)`必须返回true
2. **对称性**：`x.equals(y)`和`y.equals(x)`结果相同
3. **传递性**：`x.equals(y)`且`y.equals(z)`，则`x.equals(z)`必须为true
4. **一致性**：多次调用结果相同
5. **非空性**：`x.equals(null)`必须返回false

---

## 四、hashCode() 方法详解

### 4.1 Object类的hashCode()实现

```java
// Object类的hashCode()方法
public native int hashCode();

// 默认实现：返回对象的内存地址（经过处理）
```

**特点**：
- **native方法**：由JVM实现
- **默认返回**：对象内存地址的哈希值
- **不同对象**：通常返回不同的hashCode

### 4.2 String类的hashCode()实现

```java
// String类的hashCode()方法
public int hashCode() {
    int h = hash;
    if (h == 0 && value.length > 0) {
        char val[] = value;
        for (int i = 0; i < value.length; i++) {
            h = 31 * h + val[i];  // 31是经验值
        }
        hash = h;
    }
    return h;
}
```

**特点**：
- **基于内容计算**：相同内容的字符串，hashCode相同
- **31的选择**：31是质数，能减少哈希冲突
- **缓存机制**：计算后缓存，避免重复计算

### 4.3 hashCode()的作用

**作用1：在HashMap/HashSet中定位**

```java
// HashMap中使用hashCode定位
public V get(Object key) {
    Node<K,V> e;
    return (e = getNode(hash(key), key)) == null ? null : e.value;
}

final Node<K,V> getNode(int hash, Object key) {
    Node<K,V>[] tab; Node<K,V> first, e; int n; K k;
    if ((tab = table) != null && (n = tab.length) > 0 &&
        (first = tab[(n - 1) & hash]) != null) {
        // 先用hashCode定位桶
        if (first.hash == hash &&
            ((k = first.key) == key || (key != null && key.equals(k))))
            return first;
        // 再用equals比较
        if ((e = first.next) != null) {
            do {
                if (e.hash == hash &&
                    ((k = e.key) == key || (key != null && key.equals(k))))
                    return e;
            } while ((e = e.next) != null);
        }
    }
    return null;
}
```

**流程**：
1. **hashCode定位桶**：`index = (n - 1) & hash`
2. **equals比较内容**：在桶内用equals比较

**作用2：提升查找效率**

- **直接定位**：通过hashCode直接定位到桶，O(1)
- **减少比较**：只需要在桶内比较，不需要遍历整个集合

---

## 五、equals() 和 hashCode() 的关系

### 5.1 核心约定

**Java规范要求**：
1. **如果两个对象equals()相等，那么它们的hashCode()必须相等**
2. **如果两个对象equals()不相等，它们的hashCode()可以相等（哈希冲突）**
3. **如果两个对象hashCode()相等，equals()不一定相等（哈希冲突）**

### 5.2 为什么需要这个约定？

**在HashMap中的使用**：

```java
// HashMap的put方法
public V put(K key, V value) {
    return putVal(hash(key), key, value, false, true);
}

final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                boolean evict) {
    Node<K,V>[] tab; Node<K,V> p; int n, i;
    if ((tab = table) == null || (n = tab.length) == 0)
        n = (tab = resize()).length;
    if ((p = tab[i = (n - 1) & hash]) == null)
        tab[i] = new Node<>(hash, key, value, null);
    else {
        Node<K,V> e; K k;
        if (p.hash == hash &&
            ((k = p.key) == key || (key != null && key.equals(k))))
            e = p;  // 找到相同key，覆盖
        // ...
    }
}
```

**流程**：
1. **hashCode定位**：`index = (n - 1) & hash`
2. **equals比较**：在桶内用equals比较key

**如果违反约定**：
- **equals相等但hashCode不同**：可能存储在不同的桶，导致重复存储
- **hashCode相同但equals不同**：存储在同一个桶，但能正确区分（通过equals）

### 5.3 违反约定的后果

**示例1：只重写equals()，不重写hashCode()**

```java
public class Person {
    private String name;
    private int age;
    
    @Override
    public boolean equals(Object obj) {
        // 重写了equals
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }
    
    // ❌ 没有重写hashCode()
}

// 问题演示
Person p1 = new Person("张三", 20);
Person p2 = new Person("张三", 20);

System.out.println(p1.equals(p2));  // true，内容相同
System.out.println(p1.hashCode() == p2.hashCode());  // false，hashCode不同

Set<Person> set = new HashSet<>();
set.add(p1);
set.add(p2);
System.out.println(set.size());  // 2，重复存储！❌
```

**问题**：
- equals相等但hashCode不同
- HashSet/HashMap会认为这是两个不同的对象
- 导致**重复存储**

**示例2：只重写hashCode()，不重写equals()**

```java
public class Person {
    private String name;
    private int age;
    
    @Override
    public int hashCode() {
        // 重写了hashCode
        return Objects.hash(name, age);
    }
    
    // ❌ 没有重写equals()
}

// 问题演示
Person p1 = new Person("张三", 20);
Person p2 = new Person("张三", 20);

System.out.println(p1.hashCode() == p2.hashCode());  // true，hashCode相同
System.out.println(p1.equals(p2));  // false，equals不同（默认比较地址）

Map<Person, String> map = new HashMap<>();
map.put(p1, "value1");
System.out.println(map.get(p2));  // null，找不到！❌
```

**问题**：
- hashCode相同但equals不同
- HashMap会认为这是两个不同的key
- 导致**查找失败**

### 5.4 正确实现

```java
// 正确实现：同时重写equals()和hashCode()
public class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Person person = (Person) obj;
        return age == person.age && Objects.equals(name, person.name);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(name, age);  // 使用相同的字段
    }
}

// 正确使用
Person p1 = new Person("张三", 20);
Person p2 = new Person("张三", 20);

System.out.println(p1.equals(p2));  // true
System.out.println(p1.hashCode() == p2.hashCode());  // true

Set<Person> set = new HashSet<>();
set.add(p1);
set.add(p2);
System.out.println(set.size());  // 1，正确！✅
```

**关键点**：
- **使用相同的字段**：equals和hashCode使用相同的字段
- **保证一致性**：equals相等，hashCode必须相等

---

## 六、在HashMap中的使用流程

### 6.1 put操作流程

```
put(key, value)
   │
   ▼
计算hashCode：hash = key.hashCode()
   │
   ▼
定位桶：index = (n - 1) & hash
   │
   ▼
桶为空？
   ├─→ 是 → 直接插入
   │
   └─→ 否 → 遍历链表/树
         │
         ├─→ hashCode相同 && equals相同 → 覆盖value
         │
         └─→ 都不相同 → 插入新节点
```

### 6.2 get操作流程

```
get(key)
   │
   ▼
计算hashCode：hash = key.hashCode()
   │
   ▼
定位桶：index = (n - 1) & hash
   │
   ▼
桶为空？
   ├─→ 是 → 返回null
   │
   └─→ 否 → 遍历链表/树
         │
         ├─→ hashCode相同 && equals相同 → 返回value
         │
         └─→ 都不相同 → 继续查找
```

### 6.3 代码示例

```java
// HashMap中的使用
Map<String, String> map = new HashMap<>();

// put操作
map.put("key1", "value1");
// 1. "key1".hashCode() 计算hash值
// 2. (n - 1) & hash 定位桶
// 3. 如果桶为空，直接插入
// 4. 如果桶不为空，用equals比较key

// get操作
String value = map.get("key1");
// 1. "key1".hashCode() 计算hash值
// 2. (n - 1) & hash 定位桶
// 3. 在桶内用equals比较key
// 4. 找到返回value，找不到返回null
```

---

## 七、实际应用场景

### 7.1 场景1：自定义类作为HashMap的key

```java
// 订单类作为HashMap的key
public class Order {
    private Long orderId;
    private String userId;
    
    // 必须重写equals和hashCode
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Order order = (Order) obj;
        return Objects.equals(orderId, order.orderId) &&
               Objects.equals(userId, order.userId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(orderId, userId);
    }
}

// 使用
Map<Order, String> orderMap = new HashMap<>();
Order order1 = new Order(1L, "user1");
Order order2 = new Order(1L, "user1");

orderMap.put(order1, "订单信息");
String info = orderMap.get(order2);  // 能正确找到
```

### 7.2 场景2：使用Set去重

```java
// 使用Set去重
public class Product {
    private String productId;
    private String name;
    
    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        Product product = (Product) obj;
        return Objects.equals(productId, product.productId);
    }
    
    @Override
    public int hashCode() {
        return Objects.hash(productId);
    }
}

// 使用
Set<Product> productSet = new HashSet<>();
productSet.add(new Product("P001", "商品1"));
productSet.add(new Product("P001", "商品1"));  // 重复，不会添加
System.out.println(productSet.size());  // 1
```

---

## 八、常见面试追问

### Q1：为什么hashCode()相等，equals()不一定相等？

**答**：
- **哈希冲突**：不同的对象可能计算出相同的hashCode
- **示例**：
  ```java
  String s1 = "Aa";
  String s2 = "BB";
  System.out.println(s1.hashCode() == s2.hashCode());  // true（哈希冲突）
  System.out.println(s1.equals(s2));  // false
  ```
- **原因**：hashCode是int类型，只有2^32种可能，但对象数量可能更多

### Q2：HashMap在put时如何用equals和hashCode？

**答**：
1. **hashCode定位桶**：`index = (n - 1) & hash`
2. **equals比较内容**：在桶内用equals比较key
3. **如果equals相同**：覆盖value
4. **如果equals不同**：插入新节点

**流程**：
```java
// 先用hashCode定位
int index = (n - 1) & hash;
// 再用equals比较
if (key.equals(existingKey)) {
    // 覆盖
} else {
    // 插入
}
```

### Q3：String为什么适合作为HashMap的key？

**答**：
1. **重写了equals和hashCode**：保证一致性
2. **不可变类**：hashCode不会改变
3. **性能好**：hashCode计算高效
4. **使用方便**：不需要额外实现

### Q4：如何正确重写equals()和hashCode()？

**答**：

**方法1：手动实现**
```java
@Override
public boolean equals(Object obj) {
    if (this == obj) return true;
    if (obj == null || getClass() != obj.getClass()) return false;
    Person person = (Person) obj;
    return age == person.age && Objects.equals(name, person.name);
}

@Override
public int hashCode() {
    return Objects.hash(name, age);
}
```

**方法2：使用IDE生成**
- IntelliJ IDEA：Alt + Insert → equals() and hashCode()
- Eclipse：Source → Generate hashCode() and equals()

**方法3：使用Lombok**
```java
@EqualsAndHashCode
public class Person {
    private String name;
    private int age;
}
```

### Q5：equals()和hashCode()的性能影响？

**答**：
- **hashCode性能**：影响HashMap的查找效率
  - 好的hashCode：分布均匀，冲突少，性能好
  - 差的hashCode：分布不均，冲突多，性能差
- **equals性能**：影响桶内的比较效率
  - 简单比较：性能好
  - 复杂比较：性能差

---

## 九、面试回答模板

### 9.1 核心回答（1分钟）

"==比较基本类型的值或对象的地址，equals()默认比较地址，但通常被重写来比较对象内容。hashCode()返回对象的哈希值，在HashMap/HashSet中用来定位桶，提升查找效率。核心约定是：如果两个对象equals()相等，hashCode()必须相等；但hashCode()相等，equals()不一定相等。必须同时重写equals()和hashCode()，使用相同的字段，保证一致性，否则在集合中会出现问题。"

### 9.2 扩展回答（3分钟）

"从实现细节看，==对于基本类型比较值，对于引用类型比较地址。equals()默认是==，但String等类重写了equals()来比较内容。hashCode()在HashMap中先用来定位桶，再用equals()在桶内比较。如果只重写equals()不重写hashCode()，会导致equals相等的对象存储在不同的桶，重复存储。如果只重写hashCode()不重写equals()，会导致hashCode相同但equals不同的对象查找失败。正确做法是同时重写，使用相同的字段，保证equals相等时hashCode也相等。"

### 9.3 加分项

- 能说出equals()和hashCode()的规范要求
- 了解HashMap中hashCode和equals的使用流程
- 知道违反约定的后果
- 理解为什么String适合作为HashMap的key
- 能说出如何正确重写equals()和hashCode()
