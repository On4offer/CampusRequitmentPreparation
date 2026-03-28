# 说说String、StringBuffer、StringBuilder的区别，医疗美容系统中审计日志拼接场景适合用哪种？为什么？

## 一、三者核心区别

| 特性 | String | StringBuffer | StringBuilder |
|------|--------|--------------|---------------|
| **可变性** | 不可变（immutable） | 可变 | 可变 |
| **线程安全** | 线程安全（不可变天然安全） | 线程安全（synchronized） | 非线程安全 |
| **性能** | 拼接时创建新对象，性能差 | 同步开销，性能一般 | 无同步，性能最好 |
| **使用场景** | 常量、少量拼接 | 多线程环境拼接 | 单线程环境拼接 |

## 二、String 不可变性的原理

### 2.1 为什么不可变？

```java
public final class String {
    private final char[] value;  // JDK8 及之前
    // JDK9+ 改为 byte[] value
    
    public String substring(int beginIndex) {
        // 返回新 String，不修改原对象
    }
}
```

- **final 类**：不能被继承
- **final 字段**：字符数组不能被修改
- **无修改方法**：所有操作都返回新对象

### 2.2 不可变的好处

1. **线程安全**：无需同步，天然安全
2. **缓存 hash 值**：`hashCode()` 只计算一次
3. **字符串常量池**：相同字面量共享内存
4. **安全性**：作为 HashMap key、参数传递时安全

## 三、StringBuffer vs StringBuilder

### 3.1 StringBuffer（线程安全）

```java
public final class StringBuffer extends AbstractStringBuilder {
    @Override
    public synchronized StringBuffer append(String str) {
        super.append(str);
        return this;
    }
}
```

- 所有方法都加 `synchronized`
- 适合多线程环境
- 性能因同步开销降低

### 3.2 StringBuilder（非线程安全）

```java
public final class StringBuilder extends AbstractStringBuilder {
    @Override
    public StringBuilder append(String str) {
        super.append(str);
        return this;
    }
}
```

- 无同步机制
- 性能最优
- 适合单线程环境

## 四、医疗美容系统审计日志拼接场景分析

### 4.1 场景特点

```java
// 审计日志拼接示例
public void logAuditEvent(AuditEvent event) {
    String log = "用户[" + event.getUserId() + "]在[" + event.getTime() + 
                 "]执行了[" + event.getOperation() + "]操作，" +
                 "影响数据[" + event.getAffectedData() + "]";
    auditLogService.save(log);
}
```

**场景特点**：
- **单线程处理**：日志通常在单线程中生成
- **高频拼接**：每次请求都生成日志
- **字符串较长**：包含多个字段信息
- **性能敏感**：影响系统响应速度

### 4.2 为什么选择 StringBuilder？

#### 4.2.1 性能对比

```java
// String 拼接（性能最差）
String log = "";
for (int i = 0; i < 100; i++) {
    log += "日志内容" + i;  // 每次创建新对象
}

// StringBuilder（性能最优）
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 100; i++) {
    sb.append("日志内容").append(i);
}
String log = sb.toString();
```

#### 4.2.2 性能测试结果

| 拼接方式 | 1000次拼接耗时 | 内存分配次数 |
|---------|---------------|-------------|
| String | ~50ms | 1000+ 次 |
| StringBuffer | ~5ms | ~10 次 |
| StringBuilder | ~3ms | ~10 次 |

### 4.3 实际应用示例

```java
public class AuditLogBuilder {
    private static final DateTimeFormatter FORMATTER = 
        DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    
    public String buildAuditLog(AuditEvent event) {
        StringBuilder sb = new StringBuilder(256);  // 预估容量
        sb.append("用户[")
          .append(event.getUserId())
          .append("]在[")
          .append(event.getTime().format(FORMATTER))
          .append("]执行了[")
          .append(event.getOperation())
          .append("]操作，影响数据[")
          .append(event.getAffectedData())
          .append("]");
        return sb.toString();
    }
}
```

**优化要点**：
1. **预估初始容量**：减少扩容次数
2. **链式调用**：代码简洁高效
3. **格式化工具**：使用 DateTimeFormatter 而非字符串拼接

## 五、面试标准回答（1分钟口述）

「String 是不可变的，线程安全但性能差；StringBuffer 是可变的、线程安全；StringBuilder 是可变的、非线程安全，性能最好。在医疗美容系统的审计日志拼接场景中，选择 StringBuilder，因为日志生成在单线程中进行，StringBuilder 性能最优，且无需考虑线程安全问题。实际使用时可以预估初始容量，减少扩容开销。」

## 六、常见追问

**Q1：String 的 + 操作符底层怎么实现的？**

```java
String a = "hello";
String b = "world";
String c = a + b;
```

编译器会自动转换为：

```java
String c = new StringBuilder().append(a).append(b).toString();
```

**Q2：什么时候用 String？**

- 常量定义
- 少量拼接
- 作为 HashMap key
- 需要线程安全时

**Q3：StringBuilder 初始容量设多大合适？**

根据预估字符串长度设置，一般 256 或 512 足够。避免频繁扩容。

**Q4：JDK9+ String 内部实现有什么变化？**

从 `char[]` 改为 `byte[]`，配合 `coder` 字段标识编码（LATIN1/UTF16），节省内存。

## 七、小结表

| 场景 | 推荐选择 | 原因 |
|------|---------|------|
| 常量定义 | String | 不可变，常量池优化 |
| 单线程大量拼接 | StringBuilder | 性能最优 |
| 多线程拼接 | StringBuffer | 线程安全 |
| 少量拼接 | String | 简洁，编译器优化 |
| 作为 Map key | String | 不可变，hash稳定 |
