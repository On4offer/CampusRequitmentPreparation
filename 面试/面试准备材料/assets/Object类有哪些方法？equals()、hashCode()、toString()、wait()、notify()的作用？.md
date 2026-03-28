# Object类有哪些方法？equals()、hashCode()、toString()、wait()、notify()的作用？

## 一、Object 类的方法总览

Object 类是 Java 中所有类的根类，定义了以下方法：

| 方法 | 修饰符 | 作用 |
|------|--------|------|
| `clone()` | protected | 创建并返回对象的副本 |
| `equals(Object obj)` | public | 判断两个对象是否相等 |
| `finalize()` | protected | 垃圾回收前调用（已废弃） |
| `getClass()` | public | 获取对象的运行时类 |
| `hashCode()` | public | 返回对象的哈希码 |
| `notify()` | public | 唤醒在此对象监视器上等待的单个线程 |
| `notifyAll()` | public | 唤醒在此对象监视器上等待的所有线程 |
| `toString()` | public | 返回对象的字符串表示 |
| `wait()` | public | 导致当前线程等待 |
| `wait(long timeout)` | public | 导致当前线程等待指定时间 |
| `wait(long timeout, int nanos)` | public | 导致当前线程等待指定时间（纳秒精度） |

## 二、核心方法详解

### 2.1 equals() 方法

#### 2.1.1 默认实现

```java
public boolean equals(Object obj) {
    return (this == obj);
}
```

- 默认比较的是对象的引用（内存地址）
- 等价于 `==` 操作符

#### 2.1.2 重写 equals() 的规范

```java
public class User {
    private String name;
    private int age;

    @Override
    public boolean equals(Object obj) {
        // 1. 自反性：x.equals(x) 必须返回 true
        if (this == obj) return true;
        
        // 2. 非空性：x.equals(null) 必须返回 false
        if (obj == null) return false;
        
        // 3. 类型检查：x.equals(y) 必须类型相同
        if (getClass() != obj.getClass()) return false;
        
        // 4. 强制转换
        User other = (User) obj;
        
        // 5. 字段比较：对称性、传递性、一致性
        return age == other.age && 
               Objects.equals(name, other.name);
    }
}
```

#### 2.1.5 equals() 的五大特性

1. **自反性**：`x.equals(x)` 返回 true
2. **对称性**：`x.equals(y)` 等价于 `y.equals(x)`
3. **传递性**：`x.equals(y)` 且 `y.equals(z)`，则 `x.equals(z)`
4. **一致性**：多次调用结果一致
5. **非空性**：`x.equals(null)` 返回 false

### 2.2 hashCode() 方法

#### 2.2.1 默认实现

```java
public native int hashCode();
```

- 返回对象的内存地址的整数表示
- 本地方法，由 JVM 实现

#### 2.2.2 重写 hashCode() 的规范

```java
@Override
public int hashCode() {
    // 使用 Objects.hash() 自动计算
    return Objects.hash(name, age);
    
    // 或者手动计算
    // int result = 17;
    // result = 31 * result + age;
    // result = 31 * result + (name == null ? 0 : name.hashCode());
    // return result;
}
```

#### 2.2.3 equals() 和 hashCode() 的契约

**重要原则**：如果两个对象 `equals()` 返回 true，那么它们的 `hashCode()` 必须相同。

```java
// 正确示例
User u1 = new User("张三", 25);
User u2 = new User("张三", 25);
System.out.println(u1.equals(u2));     // true
System.out.println(u1.hashCode() == u2.hashCode());  // true

// 错误示例：只重写 equals 不重写 hashCode
HashSet<User> set = new HashSet<>();
set.add(u1);
System.out.println(set.contains(u2));  // false！因为 hashCode 不同
```

#### 2.2.4 HashMap 中的使用

```java
HashMap<User, String> map = new HashMap<>();
User key = new User("张三", 25);
map.put(key, "管理员");

// 查找时
User searchKey = new User("张三", 25);
String value = map.get(searchKey);  // 如果 hashCode 不一致，找不到
```

### 2.3 toString() 方法

#### 2.3.1 默认实现

```java
public String toString() {
    return getClass().getName() + "@" + Integer.toHexString(hashCode());
}
```

- 返回类名 + @ + 哈希码
- 例如：`User@1b6d3586`

#### 2.3.2 重写 toString()

```java
@Override
public String toString() {
    return "User{name='" + name + "', age=" + age + "}";
}

// 或者使用 StringBuilder
@Override
public String toString() {
    return new StringBuilder()
        .append("User{")
        .append("name='").append(name).append("'")
        .append(", age=").append(age)
        .append("}")
        .toString();
}
```

#### 2.3.3 应用场景

```java
User user = new User("张三", 25);
System.out.println(user);  // 自动调用 toString()
logger.info("用户信息：{}", user);  // 日志输出
```

### 2.4 wait()、notify()、notifyAll() 方法

#### 2.4.1 方法说明

```java
// wait()：让当前线程等待，释放锁
public final void wait() throws InterruptedException

// notify()：唤醒一个等待的线程
public final void notify()

// notifyAll()：唤醒所有等待的线程
public final void notifyAll()
```

#### 2.4.2 使用场景：生产者消费者模式

```java
class SharedResource {
    private int data;
    private boolean hasData = false;

    public synchronized void produce(int value) throws InterruptedException {
        while (hasData) {
            wait();  // 等待消费者消费
        }
        data = value;
        hasData = true;
        notify();  // 唤醒消费者
    }

    public synchronized int consume() throws InterruptedException {
        while (!hasData) {
            wait();  // 等待生产者生产
        }
        hasData = false;
        notify();  // 唤醒生产者
        return data;
    }
}
```

#### 2.4.3 注意事项

1. **必须在 synchronized 代码块中调用**
2. **wait() 会释放锁，notify() 不会释放锁**
3. **notify() 随机唤醒一个线程，notifyAll() 唤醒所有线程**
4. **wait() 可能被中断，需要处理 InterruptedException**

### 2.5 clone() 方法

#### 2.5.1 默认实现

```java
protected native Object clone() throws CloneNotSupportedException;
```

- 浅拷贝
- 需要实现 Cloneable 接口

#### 2.5.2 使用示例

```java
class User implements Cloneable {
    private String name;
    private int age;

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();  // 浅拷贝
    }
}

User u1 = new User("张三", 25);
User u2 = (User) u1.clone();
```

### 2.6 getClass() 方法

```java
User user = new User("张三", 25);
Class<?> clazz = user.getClass();
System.out.println(clazz.getName());  // User
System.out.println(clazz.getSimpleName());  // User
```

## 三、实际应用示例

### 3.1 完整的实体类

```java
public class User implements Cloneable, Serializable {
    private String name;
    private int age;

    public User(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object obj) {
        if (this == obj) return true;
        if (obj == null || getClass() != obj.getClass()) return false;
        User user = (User) obj;
        return age == user.age && Objects.equals(name, user.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }

    @Override
    public String toString() {
        return "User{name='" + name + "', age=" + age + "}";
    }

    @Override
    protected Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}
```

### 3.2 在集合中的使用

```java
Set<User> users = new HashSet<>();
users.add(new User("张三", 25));
users.add(new User("张三", 25));  // 不会重复添加

System.out.println(users.size());  // 1
```

## 四、面试标准回答（2分钟）

「Object 类是所有类的根类，定义了 11 个方法。equals() 用于判断对象相等，默认比较引用，重写时需遵循自反性、对称性等原则；hashCode() 返回哈希码，如果 equals() 返回 true，hashCode() 必须相同，这在 HashMap 中很重要；toString() 返回对象的字符串表示，默认是类名@哈希码；wait()、notify()、notifyAll() 用于线程间通信，必须在 synchronized 中使用；clone() 用于对象拷贝，需要实现 Cloneable 接口；getClass() 获取对象的运行时类。」

## 五、常见追问

**Q1：为什么重写 equals() 必须重写 hashCode()？**

为了满足 HashMap 等基于哈希的集合的正确性。如果 equals() 相等但 hashCode() 不同，会导致无法正确查找。

**Q2：wait() 和 sleep() 的区别？**

wait() 释放锁，属于 Object 类；sleep() 不释放锁，属于 Thread 类。

**Q3：notify() 和 notifyAll() 的区别？**

notify() 唤醒一个线程，notifyAll() 唤醒所有线程。notifyAll() 更安全，避免死锁。

**Q4：浅拷贝和深拷贝的区别？**

浅拷贝只复制基本类型和引用，深拷贝递归复制所有对象。clone() 默认是浅拷贝。

## 六、小结表

| 方法 | 作用 | 重写必要性 |
|------|------|-----------|
| equals() | 判断对象相等 | 需要自定义比较逻辑时 |
| hashCode() | 返回哈希码 | 重写 equals() 时必须重写 |
| toString() | 字符串表示 | 建议重写，方便调试 |
| wait() | 线程等待 | 通常不重写 |
| notify() | 唤醒线程 | 通常不重写 |
| clone() | 对象拷贝 | 需要自定义拷贝逻辑时 |
| getClass() | 获取类信息 | 不重写 |
