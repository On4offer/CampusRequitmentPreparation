# Java基础数据类型有哪些？各占多少字节？

## 一、Java 基本数据类型（8种）

| 类型 | 字节数 | 位数 | 默认值 | 取值范围 | 包装类型 |
|------|--------|------|--------|---------|---------|
| **byte** | 1 | 8 | 0 | -128 ~ 127 | Byte |
| **short** | 2 | 16 | 0 | -32768 ~ 32767 | Short |
| **int** | 4 | 32 | 0 | -2³¹ ~ 2³¹-1 | Integer |
| **long** | 8 | 64 | 0L | -2⁶³ ~ 2⁶³-1 | Long |
| **float** | 4 | 32 | 0.0f | ±3.4E38（约7位有效数字） | Float |
| **double** | 8 | 64 | 0.0d | ±1.8E308（约15位有效数字） | Double |
| **char** | 2 | 16 | '\u0000' | 0 ~ 65535（Unicode字符） | Character |
| **boolean** | 1（JVM规范未明确） | - | false | true, false | Boolean |

## 二、各类型详细说明

### 2.1 整型类型

#### byte（1字节）
```java
byte b = 100;  // 正确
byte c = 128;  // 编译错误：超出范围
```
- 最小的整数类型
- 常用于节省内存（如文件读写、网络传输）

#### short（2字节）
```java
short s = 10000;
```
- 较少使用，通常用 int 代替

#### int（4字节）
```java
int i = 2147483647;  // 最大值
int j = -2147483648; // 最小值
```
- 最常用的整数类型
- Java 中整数默认为 int

#### long（8字节）
```java
long l1 = 10000000000L;  // 必须加 L 或 l
long l2 = 100L;
```
- 用于大数值
- 必须加 L 后缀

### 2.2 浮点类型

#### float（4字节）
```java
float f1 = 3.14f;  // 必须加 f 或 F
float f2 = 3.14F;
```
- 单精度浮点数
- 精度约 7 位有效数字
- 必须加 f 后缀

#### double（8字节）
```java
double d1 = 3.14;  // 默认为 double
double d2 = 3.14d;
```
- 双精度浮点数
- 精度约 15 位有效数字
- Java 中浮点数默认为 double

### 2.3 字符类型

#### char（2字节）
```java
char c1 = 'A';
char c2 = 65;        // ASCII 码
char c3 = '\u0041';  // Unicode 编码
char c4 = '中';      // Unicode 字符
```
- 使用 UTF-16 编码
- 可以存储 Unicode 字符
- 单引号括起来

### 2.4 布尔类型

#### boolean
```java
boolean flag1 = true;
boolean flag2 = false;
```
- 只有两个值：true、false
- 不能与整数类型转换
- JVM 规范未明确占用字节数（通常为 1 字节）

## 三、类型转换

### 3.1 自动类型转换（隐式）

从小到大自动转换：

```
byte → short → int → long → float → double
     char → int → long → float → double
```

```java
byte b = 10;
int i = b;        // 自动转换
long l = i;       // 自动转换
double d = l;     // 自动转换
```

### 3.2 强制类型转换（显式）

从大到小需要强制转换，可能丢失精度：

```java
int i = 100;
byte b = (byte) i;  // 强制转换

double d = 3.99;
int j = (int) d;    // 结果为 3，丢失小数部分
```

### 3.3 特殊情况

```java
// 整数运算
int a = 10;
int b = 3;
double c = a / b;  // 结果为 3.0，不是 3.333...
// 原因：a/b 先按 int 运算，结果为 3，再转换为 double

// 正确做法
double c = (double) a / b;  // 结果为 3.333...
```

## 四、包装类型与自动装箱

### 4.1 包装类型

每个基本类型都有对应的包装类型：

```java
Integer i = new Integer(10);  // 已过时
Integer j = Integer.valueOf(10);  // 推荐
```

### 4.2 自动装箱与拆箱

```java
// 自动装箱
Integer i = 10;  // 等价于 Integer.valueOf(10)

// 自动拆箱
int j = i;       // 等价于 i.intValue()
```

### 4.3 缓存机制

```java
Integer a = 100;
Integer b = 100;
System.out.println(a == b);  // true，使用缓存

Integer c = 200;
Integer d = 200;
System.out.println(c == d);  // false，创建新对象
```

- Byte、Short、Long：-128 ~ 127
- Integer：-128 ~ 127（可调整）
- Character：0 ~ 127

## 五、常见面试题

### 5.1 为什么 float 精度不够？

```java
float f = 0.1f;
double d = 0.1;
System.out.println(f);  // 0.1
System.out.println(d);  // 0.1
System.out.println(f == d);  // false
```

**原因**：浮点数使用 IEEE 754 标准，二进制无法精确表示某些十进制小数。

### 5.2 为什么 char 占用 2 字节？

Java 使用 UTF-16 编码，可以表示 Unicode 字符集（包括中文等）。

### 5.3 boolean 占用多少字节？

JVM 规范未明确，通常为 1 字节，但可能被优化为 1 bit。

### 5.4 整数溢出

```java
int max = Integer.MAX_VALUE;  // 2147483647
int overflow = max + 1;       // -2147483648（溢出）
```

**解决方案**：
- 使用 long 类型
- 使用 BigInteger 类

## 六、实际应用场景

### 6.1 选择合适的数据类型

```java
// 用户年龄：byte（0-127）
byte age = 25;

// 商品价格：BigDecimal（避免精度问题）
BigDecimal price = new BigDecimal("99.99");

// 订单数量：int
int orderCount = 10000;

// 时间戳：long
long timestamp = System.currentTimeMillis();

// 状态标识：boolean
boolean isActive = true;
```

### 6.2 性能考虑

```java
// 大数组使用 byte 而非 int
byte[] data = new byte[1024 * 1024];  // 1MB
int[] data2 = new int[1024 * 1024];   // 4MB
```

### 6.3 数据库映射

| Java 类型 | MySQL 类型 | 说明 |
|-----------|------------|------|
| int | INT | 4字节 |
| long | BIGINT | 8字节 |
| float | FLOAT | 4字节 |
| double | DOUBLE | 8字节 |
| String | VARCHAR | 可变长度 |

## 七、面试标准回答（1分钟）

「Java 有 8 种基本数据类型：byte（1字节）、short（2字节）、int（4字节）、long（8字节）、float（4字节）、double（8字节）、char（2字节）、boolean（1字节）。整数类型有 byte、short、int、long，浮点类型有 float、double，字符类型是 char，布尔类型是 boolean。类型转换时，从小到大自动转换，从大到小需要强制转换。注意浮点数精度问题和整数溢出问题。」

## 八、常见追问

**Q1：为什么 Java 没有 unsigned 类型？**

Java 设计者认为无符号类型会增加复杂性，可以用更大范围的有符号类型代替。

**Q2：float 和 double 的区别？**

float 是单精度，4字节，精度约7位；double 是双精度，8字节，精度约15位。默认使用 double。

**Q3：char 能存储中文吗？**

可以，char 使用 UTF-16 编码，可以存储 Unicode 字符，包括中文。

**Q4：如何避免浮点数精度问题？**

使用 BigDecimal 类进行精确计算。

## 九、小结表

| 类型 | 字节 | 范围 | 应用场景 |
|------|------|------|---------|
| byte | 1 | -128~127 | 小整数、节省内存 |
| short | 2 | -32768~32767 | 较少使用 |
| int | 4 | -2³¹~2³¹-1 | 默认整数类型 |
| long | 8 | -2⁶³~2⁶³-1 | 大整数、时间戳 |
| float | 4 | ±3.4E38 | 单精度浮点 |
| double | 8 | ±1.8E308 | 默认浮点类型 |
| char | 2 | 0~65535 | 单个字符 |
| boolean | 1 | true/false | 布尔标志 |
