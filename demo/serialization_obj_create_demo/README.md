# Java 通过序列化/反序列化创建对象 Demo

本 Demo 演示了 Java 中创建对象的五种方式之一：**通过反序列化（Deserialization）创建对象**。

## 1. Demo 运行说明

该 Demo 包含两个类：
- `User.java`: 实现了 `Serializable` 接口的模型类。
- `SerializationDemo.java`: 演示序列化与反序列化过程的主类。

### 运行方式
可以直接在 IDE 中运行 `SerializationDemo.java` 的 `main` 方法，或者使用命令行：
```bash
javac -d . User.java SerializationDemo.java
java serialization_obj_create_demo.SerializationDemo
```

### 预期输出
你会发现反序列化过程中**没有调用 User 类的构造函数**。
```text
调用了构造函数: User(String name, int age)
原始对象: User{name='张三', age=25}
对象已序列化到文件 user.ser
------------------------------------
反序列化完成，创建了新对象
反序列化后的对象: User{name='张三', age=25}
originalUser == deserializedUser: false
```

---

## 2. 面试题知识点总结：Java 创建对象的方式

在 Java 面试中，这通常是一个经典问题。Java 中主要有以下 5 种创建对象的方式：

### (1) 使用 `new` 关键字
最常见的方式。会调用类的构造函数。
```java
User user = new User("张三", 25);
```

### (2) 使用 `Class.newInstance()` (反射)
通过反射机制创建对象。底层调用类的**无参构造函数**。
*(注：Java 9 之后建议使用 `clazz.getDeclaredConstructor().newInstance()`)。*

### (3) 使用 `Constructor.newInstance()` (反射)
也是反射，但比 `Class.newInstance()` 更强大，可以调用**有参构造函数**和**私有构造函数**。

### (4) 使用 `clone()` 方法
通过对象的克隆机制创建。需要类实现 `Cloneable` 接口并重写 `clone()` 方法。
**特点：** 不会调用构造函数，而是直接复制内存中的数据。

### (5) 通过序列化/反序列化 (Serialization/Deserialization)
将对象序列化为字节流（如存入文件或网络传输），再通过反序列化还原。
**特点：**
- **不调用任何构造函数**（针对实现 `Serializable` 接口的类）。
- 虚拟机通过字节流中的数据直接恢复对象状态。
- 要求类必须实现 `java.io.Serializable` 接口。

---

## 3. 深入：反序列化为什么不调用构造函数？

反序列化创建对象时，Java 虚拟机会从字节流中读取数据来初始化成员变量。

- 如果该类实现了 `Serializable` 接口，它会调用**第一个非序列化父类**的无参构造函数来初始化继承自父类的状态，而当前类的构造函数则完全被跳过。
- 这也是为什么在设计单例模式时，如果类实现了序列化接口，必须提供 `readResolve()` 方法来防止通过反序列化破坏单例。

