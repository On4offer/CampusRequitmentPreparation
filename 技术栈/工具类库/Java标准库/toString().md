### 1. 基本定义

[toString()](file://java\lang\Object.java#L237-L237) 方法是 Java 标准库中 `Object` 类的基本方法，用于返回对象的字符串表示。

### 2. 所属类和包路径

- **所属类**: `java.lang.Object`
- **包路径**: `java.lang`
- **Java 版本**: 自 Java 1.0 起可用

### 3. 方法签名

```java
public String toString()
```


### 4. 功能作用

返回对象的字符串表示形式，通常用于调试、日志记录和信息展示。

### 5. 返回值

- 返回 `String` 类型的对象字符串表示

### 6. 在代码中的使用

```java
Long result = stringRedisTemplate.execute(
        SECKILL_SCRIPT,
        Collections.emptyList(),
        voucherId.toString(), userId.toString(), String.valueOf(orderId)  // 转换为字符串参数
);
```


在这段代码中的作用：
- 将 `Long` 类型的 [voucherId](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\entity\VoucherOrder.java#L42-L42) 和 [userId](file://D:\code\java\hm-dianping\src\main\java\com\hmdp\entity\VoucherOrder.java#L37-L37) 转换为字符串
- 将 `long` 类型的 `orderId` 转换为字符串
- 作为参数传递给 Redis Lua 脚本执行方法

### 7. 底层实现原理

```java
// Object 类中的默认实现
public String toString() {
    return getClass().getName() + "@" + Integer.toHexString(hashCode());
}

// Long 类中的重写实现
public String toString() {
    return toString(value);
}

public static String toString(long i) {
    if (i == Long.MIN_VALUE)
        return "-9223372036854775808";
    int size = (i < 0) ? stringSize(-i) + 1 : stringSize(i);
    char[] buf = new char[size];
    getChars(i, size, buf);
    return new String(buf);
}
```


### 8. 示例代码

```java
// 基本数据类型的 toString() 使用
Long voucherId = 123L;
Long userId = 456L;
long orderId = 789L;

// Long 对象的 toString()
String voucherIdStr = voucherId.toString();  // "123"
String userIdStr = userId.toString();        // "456"

// 基本类型转换为字符串
String orderIdStr = String.valueOf(orderId); // "789"
// 或者
String orderIdStr2 = Long.toString(orderId); // "789"

// 自定义类重写 toString()
public class VoucherOrder {
    private Long id;
    private Long userId;
    
    @Override
    public String toString() {
        return "VoucherOrder{id=" + id + ", userId=" + userId + "}";
    }
}

VoucherOrder order = new VoucherOrder();
System.out.println(order.toString()); // 输出: VoucherOrder{id=null, userId=null}
```


### 9. 相关方法

| 方法                                                 | 功能                            |
| ---------------------------------------------------- | ------------------------------- |
| [toString()](file://java\lang\Object.java#L237-L237) | 对象的字符串表示                |
| `String.valueOf(Object obj)`                         | 安全的对象转字符串（处理 null） |
| `String.format()`                                    | 格式化字符串                    |
| `Objects.toString(Object o)`                         | Java 7+ 的安全 toString 方法    |

### 10. 不同类型的 toString() 实现

```java
// Integer 类的实现
Integer num = 123;
System.out.println(num.toString()); // "123"

// String 类的实现（返回自身）
String str = "hello";
System.out.println(str.toString()); // "hello"

// Boolean 类的实现
Boolean bool = true;
System.out.println(bool.toString()); // "true"

// Date 类的实现
Date date = new Date();
System.out.println(date.toString()); // "Mon Oct 23 10:30:45 CST 2023"
```


### 11. 注意事项

1. **null 值处理**: 直接调用 null 对象的 toString() 会抛出 NullPointerException
2. **重写建议**: 自定义类应该重写 toString() 方法提供有意义的信息
3. **性能考虑**: 频繁的字符串转换可能影响性能
4. **一致性**: 重写的 toString() 应该保持一致性，相同对象应返回相同字符串

### 12. 实际意义

在您的秒杀系统中，[toString()](file://java\lang\Object.java#L237-L237) 方法确保了：

- 将数值类型的 ID 转换为字符串参数传递给 Redis 脚本
- 实现了不同类型数据之间的转换
- 提供了标准的数据序列化方式
- 保证了 Redis 脚本参数传递的正确性

这是 Java 编程的基础方法，在数据传输和参数传递中发挥着重要作用。