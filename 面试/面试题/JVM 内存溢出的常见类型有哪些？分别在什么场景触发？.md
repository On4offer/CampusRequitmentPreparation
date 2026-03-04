好 👍，这道题和 **内存模型**联系紧密，考察你对 OOM 的认识。我帮你整理成 **面试问答标准答案**：

------

## 📌 面试题：JVM 内存溢出的常见类型有哪些？分别在什么场景触发？

### ⭐ 标准回答

在 JVM 中，常见的内存溢出（`OutOfMemoryError`，简称 OOM）主要有以下几类：

------

### 1. **Java 堆溢出（Java Heap Space）**

- **触发场景**：
  - 创建了大量对象且无法被 GC 回收，例如：大集合不断添加元素。
  - 大对象（如超大数组）直接申请超出堆大小。
- **报错信息**：`java.lang.OutOfMemoryError: Java heap space`
- **解决方式**：
  - 调整堆大小（`-Xmx`、`-Xms`）。
  - 检查是否有内存泄漏（对象未释放）。

------

### 2. **栈溢出（StackOverflowError / Unable to create new native thread）**

- **触发场景**：
  - 方法递归过深，导致栈帧过多。
  - 创建过多线程，导致操作系统无法分配新的线程栈空间。
- **报错信息**：
  - `java.lang.StackOverflowError`
  - `java.lang.OutOfMemoryError: Unable to create new native thread`
- **解决方式**：
  - 优化递归逻辑。
  - 调整线程数或设置栈大小（`-Xss`）。

------

### 3. **方法区/元空间溢出（PermGen/Metaspace）**

- **触发场景**：
  - JDK7 及之前：永久代（PermGen）中类信息过多（大量动态生成类）。
  - JDK8 之后：元空间（Metaspace）存放在本地内存，过多动态生成类时可能溢出。
- **报错信息**：
  - `java.lang.OutOfMemoryError: PermGen space`（JDK7 及之前）
  - `java.lang.OutOfMemoryError: Metaspace`（JDK8 及之后）
- **解决方式**：
  - 增大元空间大小（`-XX:MaxMetaspaceSize`）。
  - 减少动态代理或类加载。

------

### 4. **运行时常量池溢出**

- **触发场景**：
  - 不断向常量池中添加字符串（如无限调用 `String.intern()`）。
  - 大量反射、动态生成的常量。
- **报错信息**：
  - JDK7 之前：`java.lang.OutOfMemoryError: PermGen space`
  - JDK8 之后：属于 Metaspace 溢出的一部分。
- **解决方式**：优化常量池使用，避免无界增加。

------

### 5. **直接内存溢出（Direct Buffer Memory）**

- **触发场景**：
  - NIO 使用 `ByteBuffer.allocateDirect()` 分配了大量堆外内存，但未及时释放。
  - 分配超过 `-XX:MaxDirectMemorySize` 限制。
- **报错信息**：`java.lang.OutOfMemoryError: Direct buffer memory`
- **解决方式**：
  - 调整 `-XX:MaxDirectMemorySize`。
  - 检查堆外内存使用是否合理。

------

### 📊 总结对比表

| 类型              | 报错信息                                                | 场景                | 调优参数                |
| ----------------- | ------------------------------------------------------- | ------------------- | ----------------------- |
| 堆溢出            | Java heap space                                         | 大量对象 / 大对象   | -Xmx / -Xms             |
| 栈溢出            | StackOverflowError / Unable to create new native thread | 递归过深 / 线程过多 | -Xss                    |
| 方法区/元空间溢出 | PermGen space / Metaspace                               | 动态生成类过多      | -XX:MaxMetaspaceSize    |
| 常量池溢出        | PermGen space / Metaspace                               | intern() 或常量过多 | -XX:MaxMetaspaceSize    |
| 直接内存溢出      | Direct buffer memory                                    | NIO 堆外内存不足    | -XX:MaxDirectMemorySize |

------

### 🔍 面试追问

1. JDK7 和 JDK8 在方法区的区别是什么？
    👉 JDK7 用 PermGen，JDK8 改为 Metaspace，使用本地内存。
2. 如何判断是内存泄漏还是内存溢出？
    👉 泄漏：对象不再使用但仍有引用；溢出：确实需要的内存超出配置。
3. 实际项目中常见的 OOM 有哪些？
    👉 堆溢出（大集合）、线程过多（Tomcat 线程池配置不当）、Metaspace（动态代理过多）、直接内存（Netty/NIO）。

------

要不要我帮你写一份 **“实战 OOM 排查方法总结”**（jmap、jconsole、MAT 分析堆 dump 文件），这样能把回答从“理论”拉到“实战”？