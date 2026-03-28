# exception 和 error 它的一个区别有啥呀？throw 和 throws 的区别？

## 一、Exception 与 Error 的区别

### 1.1 核心区别

| 特性 | Exception | Error |
|------|-----------|-------|
| **继承关系** | 继承自 `Throwable` | 继承自 `Throwable` |
| **类型** | 可检查异常（Checked）和非检查异常（Unchecked） | 都是非检查异常（Unchecked） |
| **发生原因** | 程序逻辑错误，外部资源异常等 | 系统级错误，如内存不足、栈溢出等 |
| **处理方式** | 应该捕获并处理 | 通常无法恢复，不应该捕获 |
| **影响范围** | 单个线程 | 整个应用程序 |
| **示例** | `NullPointerException`、`IOException` | `OutOfMemoryError`、`StackOverflowError` |

### 1.2 详细分析

#### 1.2.1 Exception

**Exception** 表示程序运行过程中出现的**可预期**的异常情况，通常是由程序逻辑错误或外部资源问题引起的。

**分类**：
- **Checked Exception**（可检查异常）：编译器要求必须处理的异常
- **Unchecked Exception**（非检查异常）：编译器不强制要求处理的异常

**Checked Exception 示例**：
```java
// IOException、SQLException 等
public void readFile(String path) throws IOException {
    FileInputStream fis = new FileInputStream(path);
    // 操作文件
    fis.close();
}
```

**Unchecked Exception 示例**：
```java
// NullPointerException、ArrayIndexOutOfBoundsException 等
public void processArray(int[] array) {
    System.out.println(array[10]);  // 可能抛出 ArrayIndexOutOfBoundsException
}
```

#### 1.2.2 Error

**Error** 表示程序运行过程中出现的**不可预期**的严重错误，通常是由系统级问题引起的，如内存不足、栈溢出等。

**特点**：
- 都是 `RuntimeException` 的子类
- 通常无法恢复，不应该被捕获
- 表示应用程序无法继续运行的严重问题

**Error 示例**：
```java
// StackOverflowError
public void recursiveCall() {
    recursiveCall();  // 无限递归，导致栈溢出
}

// OutOfMemoryError
public void allocateMemory() {
    List<byte[]> list = new ArrayList<>();
    while (true) {
        list.add(new byte[1024 * 1024]);  // 无限分配内存
    }
}
```

### 1.3 继承关系图

```
Throwable
├── Exception
│   ├── RuntimeException (Unchecked)
│   │   ├── NullPointerException
│   │   ├── ArrayIndexOutOfBoundsException
│   │   ├── IllegalArgumentException
│   │   └── ...
│   └── 其他 Checked Exception
│       ├── IOException
│       ├── SQLException
│       ├── ClassNotFoundException
│       └── ...
└── Error
    ├── OutOfMemoryError
    ├── StackOverflowError
    ├── VirtualMachineError
    └── ...
```

## 二、throw 与 throws 的区别

### 2.1 核心区别

| 特性 | throw | throws |
|------|-------|--------|
| **作用** | 手动抛出异常 | 声明方法可能抛出的异常 |
| **位置** | 方法体内 | 方法签名后 |
| **使用场景** | 当满足特定条件时抛出异常 | 告诉调用者此方法可能抛出的异常 |
| **数量** | 每次只能抛出一个异常 | 可以声明多个异常 |
| **语法** | `throw new Exception();` | `method() throws Exception1, Exception2;` |

### 2.2 详细分析

#### 2.2.1 throw

**throw** 用于手动抛出一个异常对象，通常在方法体内使用。

**使用场景**：
- 当程序遇到不符合预期的情况时
- 当需要将检查异常转换为非检查异常时
- 当需要自定义异常时

**示例**：
```java
public void validateAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("年龄不能为负数");
    }
    if (age > 150) {
        throw new IllegalArgumentException("年龄超出合理范围");
    }
    System.out.println("年龄验证通过");
}
```

#### 2.2.2 throws

**throws** 用于在方法签名中声明该方法可能抛出的异常，告诉调用者需要处理这些异常。

**使用场景**：
- 方法内部可能抛出检查异常，但不想在方法内部处理
- 方法调用了其他可能抛出检查异常的方法
- 声明方法可能抛出的非检查异常（虽然不是必须的）

**示例**：
```java
// 声明可能抛出 IOException 和 SQLException
public void processData() throws IOException, SQLException {
    readFile();  // 可能抛出 IOException
    saveData();  // 可能抛出 SQLException
}

// 调用方需要处理这些异常
public void callProcessData() {
    try {
        processData();
    } catch (IOException e) {
        System.err.println("文件读取失败: " + e.getMessage());
    } catch (SQLException e) {
        System.err.println("数据保存失败: " + e.getMessage());
    }
}
```

### 2.3 组合使用

```java
public void processUserInput(String input) throws IllegalArgumentException {
    if (input == null || input.isEmpty()) {
        throw new IllegalArgumentException("输入不能为空");
    }
    // 处理输入
    System.out.println("处理输入: " + input);
}

// 调用方
public void handleInput() {
    try {
        processUserInput("");
    } catch (IllegalArgumentException e) {
        System.err.println("输入错误: " + e.getMessage());
    }
}
```

## 三、异常处理最佳实践

### 3.1 正确处理异常

```java
// 错误的做法
public void badPractice() {
    try {
        // 可能抛出异常的代码
    } catch (Exception e) {
        // 什么都不做，吞掉异常
    }
}

// 正确的做法
public void goodPractice() {
    try {
        // 可能抛出异常的代码
    } catch (IOException e) {
        // 记录日志
        logger.error("文件操作失败", e);
        // 重新抛出或处理
        throw new RuntimeException("文件操作失败", e);
    }
}
```

### 3.2 医疗美容系统中的异常处理

```java
public class PatientService {
    private final Logger logger = LoggerFactory.getLogger(PatientService.class);
    
    public Patient getPatient(String patientId) throws PatientNotFoundException {
        if (patientId == null || patientId.isEmpty()) {
            throw new IllegalArgumentException("患者ID不能为空");
        }
        
        Patient patient = patientRepository.findById(patientId);
        if (patient == null) {
            throw new PatientNotFoundException("患者不存在: " + patientId);
        }
        
        return patient;
    }
    
    public void registerPatient(Patient patient) throws ValidationException {
        try {
            validatePatient(patient);
            patientRepository.save(patient);
        } catch (Exception e) {
            logger.error("注册患者失败", e);
            throw new ValidationException("患者信息验证失败", e);
        }
    }
    
    private void validatePatient(Patient patient) {
        if (patient.getName() == null || patient.getName().isEmpty()) {
            throw new IllegalArgumentException("患者姓名不能为空");
        }
        if (patient.getAge() < 0 || patient.getAge() > 150) {
            throw new IllegalArgumentException("年龄无效");
        }
    }
}

// 自定义异常
public class PatientNotFoundException extends RuntimeException {
    public PatientNotFoundException(String message) {
        super(message);
    }
}

public class ValidationException extends Exception {
    public ValidationException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

## 四、异常链

**异常链**是指在捕获一个异常后，将其作为新异常的原因重新抛出，这样可以保留原始异常的信息。

```java
public void processFile(String path) throws BusinessException {
    try {
        FileInputStream fis = new FileInputStream(path);
        // 处理文件
        fis.close();
    } catch (IOException e) {
        // 包装成业务异常，保留原始异常信息
        throw new BusinessException("文件处理失败", e);
    }
}

public class BusinessException extends Exception {
    public BusinessException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

## 五、面试标准回答（2分钟）

「Exception 和 Error 都是继承自 Throwable 的异常类。Exception 表示程序可预期的异常，分为检查异常和非检查异常，应该被捕获和处理；Error 表示系统级的严重错误，如内存不足、栈溢出等，通常无法恢复，不应该被捕获。throw 用于手动抛出异常，在方法体内使用；throws 用于声明方法可能抛出的异常，在方法签名后使用。在医疗美容系统中，我们应该合理使用异常处理，对用户输入验证使用 IllegalArgumentException，对业务逻辑错误使用自定义异常，并正确记录异常信息。」

## 六、常见追问

**Q1：Checked Exception 和 Unchecked Exception 的区别？**

Checked Exception 是编译器要求必须处理的异常，如 IOException；Unchecked Exception 是编译器不强制要求处理的异常，如 NullPointerException，它们都是 RuntimeException 的子类。

**Q2：什么时候使用 throw，什么时候使用 throws？**

当需要在方法内部主动抛出异常时使用 throw；当方法可能抛出异常但不想在内部处理时，使用 throws 声明这些异常，让调用方处理。

**Q3：如何自定义异常？**

自定义异常通常继承自 Exception（检查异常）或 RuntimeException（非检查异常），并提供适当的构造方法。

**Q4：异常处理的性能影响？**

异常处理会影响性能，因为异常的创建和抛出会涉及栈跟踪的生成。因此，不应该将异常用于正常的控制流程，只应该用于异常情况。

## 七、小结表

| 对比项 | Exception | Error |
|--------|-----------|-------|
| 性质 | 程序逻辑错误 | 系统级严重错误 |
| 处理方式 | 应该捕获处理 | 不应该捕获 |
| 继承关系 | 继承自 Throwable | 继承自 Throwable |
| 示例 | NullPointerException, IOException | OutOfMemoryError, StackOverflowError |

| 对比项 | throw | throws |
|--------|-------|--------|
| 作用 | 抛出异常 | 声明异常 |
| 位置 | 方法体内 | 方法签名后 |
| 语法 | throw new Exception() | method() throws Exception |
| 数量 | 一次一个 | 可多个 |
