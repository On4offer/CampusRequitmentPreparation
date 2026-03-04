# 什么是Java反射？请介绍一下反射的概念及其应用？

## 一、反射的核心概念

### 1.1 定义

**Java反射（Reflection）** 是Java语言提供的一种**在运行时动态获取和操作类信息**的机制。它允许程序在运行时：

- 获取任意类的完整信息（类名、方法、字段、构造器等）
- 创建类的实例对象
- 调用对象的方法
- 访问和修改对象的字段（包括私有成员）
- 获取注解信息

**核心思想**：反射让程序能够"自省"，在运行时动态地了解和使用类的结构，而不需要在编译时就知道类的具体信息。

### 1.2 反射的核心API

反射的核心API位于 `java.lang.reflect` 包中：

| 类 | 作用 |
|---|---|
| `Class` | 代表一个类的类对象，是反射的入口 |
| `Field` | 代表类的成员变量（字段） |
| `Method` | 代表类的方法 |
| `Constructor` | 代表类的构造方法 |
| `Annotation` | 代表类的注解信息 |

---

## 二、反射的基本使用

### 2.1 获取Class对象的三种方式

```java
// 方式1：Class.forName() - 最常用，通过全限定类名获取
Class<?> clazz1 = Class.forName("java.lang.String");

// 方式2：类名.class - 编译时确定
Class<String> clazz2 = String.class;

// 方式3：对象.getClass() - 通过实例对象获取
String str = "Hello";
Class<? extends String> clazz3 = str.getClass();
```

### 2.2 反射操作示例

```java
import java.lang.reflect.*;

public class ReflectionExample {
    public static void main(String[] args) throws Exception {
        // 1. 获取Class对象
        Class<?> studentClass = Class.forName("com.example.Student");
        
        // 2. 创建对象实例（推荐方式）
        Constructor<?> constructor = studentClass.getDeclaredConstructor(String.class, int.class);
        Object student = constructor.newInstance("张三", 20);
        
        // 3. 获取并操作私有字段
        Field nameField = studentClass.getDeclaredField("name");
        nameField.setAccessible(true); // 突破private限制
        nameField.set(student, "李四");
        String name = (String) nameField.get(student);
        System.out.println("姓名: " + name);
        
        // 4. 获取并调用方法
        Method studyMethod = studentClass.getDeclaredMethod("study", String.class);
        studyMethod.invoke(student, "Java反射");
        
        // 5. 获取所有方法
        Method[] methods = studentClass.getDeclaredMethods();
        for (Method method : methods) {
            System.out.println("方法: " + method.getName());
        }
    }
}

class Student {
    private String name;
    private int age;
    
    public Student(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public void study(String subject) {
        System.out.println(name + "正在学习 " + subject);
    }
    
    private void privateMethod() {
        System.out.println("私有方法被调用");
    }
}
```

### 2.3 常用反射操作

```java
// 获取所有字段（包括私有）
Field[] fields = clazz.getDeclaredFields();

// 获取所有方法（包括私有）
Method[] methods = clazz.getDeclaredMethods();

// 获取所有构造方法
Constructor<?>[] constructors = clazz.getDeclaredConstructors();

// 判断字段/方法是否为私有（与运算）
field.getModifiers() & Modifier.PRIVATE

// 获取注解信息
Annotation[] annotations = clazz.getAnnotations();
```

---

## 三、反射的主要应用场景

### 3.1 Spring框架（IoC容器）

**核心应用**：Spring通过反射实现控制反转（IoC）和依赖注入（DI）

```java
// Spring容器内部实现原理（简化版）
public class SpringContainer {
    public <T> T getBean(Class<T> clazz) {
        // 1. 通过反射创建对象
        Constructor<T> constructor = clazz.getDeclaredConstructor();
        T instance = constructor.newInstance();
        
        // 2. 通过反射注入依赖（@Autowired）
        // 获取目标类的所有字段（包括private、protected等）
        Field[] fields = clazz.getDeclaredFields();
        // 遍历每个字段，检查是否有@Autowired注解
        for (Field field : fields) {
            if (field.isAnnotationPresent(Autowired.class)) {
                field.setAccessible(true);	// 开启字段的访问权限（即使是private字段也能赋值）
                Object dependency = getBean(field.getType());	// 递归调用getBean，创建依赖字段的实例（比如User里的Order字段）
                field.set(instance, dependency);	// 将依赖实例赋值给当前对象的这个字段（完成注入）
            }
        }
        
        return instance;
    }
}
```

**实际应用**：
- `@Component`、`@Service`、`@Repository` 等注解的类，Spring通过反射扫描并创建Bean
- `@Autowired` 注解的字段，Spring通过反射注入依赖对象
- `@Value` 注解的字段，Spring通过反射从配置文件中读取值并注入

### 3.2 ORM框架（MyBatis/Hibernate）

**核心应用**：将数据库记录映射为Java对象

```java
// MyBatis结果集映射（简化版）
public <T> T mapRow(ResultSet rs, Class<T> clazz) throws Exception {
    T instance = clazz.getDeclaredConstructor().newInstance();
    
    // 通过反射获取所有字段
    Field[] fields = clazz.getDeclaredFields();
    for (Field field : fields) {
        field.setAccessible(true);
        String columnName = getColumnName(field); // 获取数据库列名
        Object value = rs.getObject(columnName);
        field.set(instance, value);
    }
    
    return instance;
}
```

### 3.3 动态代理（AOP实现）

**核心应用**：Spring AOP通过反射实现动态代理

```java
// JDK动态代理（基于反射）
public class DynamicProxy implements InvocationHandler {
    private Object target;
    
    public Object createProxy(Object target) {
        this.target = target;
        return Proxy.newProxyInstance(
            target.getClass().getClassLoader(),
            target.getClass().getInterfaces(),
            this
        );
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        // 反射调用目标方法
        System.out.println("方法执行前");
        Object result = method.invoke(target, args);
        System.out.println("方法执行后");
        return result;
    }
}
```

### 3.4 注解处理

**核心应用**：读取和处理自定义注解

```java
// 处理自定义注解
public void processAnnotations(Object obj) {
    Class<?> clazz = obj.getClass();
    
    // 获取类上的注解
    if (clazz.isAnnotationPresent(MyAnnotation.class)) {
        MyAnnotation annotation = clazz.getAnnotation(MyAnnotation.class);
        System.out.println("注解值: " + annotation.value());
    }
    
    // 获取方法上的注解
    Method[] methods = clazz.getDeclaredMethods();
    for (Method method : methods) {
        if (method.isAnnotationPresent(Test.class)) {
            // 执行测试方法
            method.invoke(obj);
        }
    }
}
```

### 3.5 通用工具类

**核心应用**：BeanUtils、JSON序列化等

```java
// 对象属性复制工具（类似BeanUtils）
public static void copyProperties(Object source, Object target) throws Exception {
    Class<?> sourceClass = source.getClass();
    Class<?> targetClass = target.getClass();
    
    Field[] sourceFields = sourceClass.getDeclaredFields();
    for (Field sourceField : sourceFields) {
        sourceField.setAccessible(true);
        String fieldName = sourceField.getName();
        
        try {
            Field targetField = targetClass.getDeclaredField(fieldName);
            targetField.setAccessible(true);
            Object value = sourceField.get(source);
            targetField.set(target, value);
        } catch (NoSuchFieldException e) {
            // 忽略不存在的字段
        }
    }
}
```

---

## 四、反射的优缺点

### 4.1 优点

1. **灵活性高**：可以在运行时动态决定要使用的类，提高代码的灵活性和可扩展性
2. **框架基础**：是Spring、MyBatis等主流框架的核心技术
3. **通用性强**：可以编写通用的工具类和框架代码

### 4.2 缺点

1. **性能开销**：
   - 反射调用比直接调用慢**10-100倍**
   - JVM无法对反射代码进行优化
   - 适合在框架初始化时使用，不适合在频繁调用的业务代码中使用

2. **安全性问题**：
   - 可以突破访问权限，访问私有成员
   - 可能破坏封装性，导致安全问题

3. **代码可读性差**：
   - 反射代码难以理解和维护
   - IDE无法进行代码检查和自动补全

4. **编译期检查失效**：
   - 反射相关的错误只能在运行时发现
   - 增加了调试难度

---

## 五、性能优化建议

### 5.1 缓存反射对象

```java
// 缓存Class、Method、Field等对象，避免重复获取
private static final Map<String, Class<?>> CLASS_CACHE = new ConcurrentHashMap<>();
private static final Map<Class<?>, Method[]> METHOD_CACHE = new ConcurrentHashMap<>();

public Class<?> getCachedClass(String className) throws ClassNotFoundException {
    return CLASS_CACHE.computeIfAbsent(className, 
        k -> Class.forName(k));
}
```

### 5.2 使用MethodHandle（Java 7+）

```java
// MethodHandle比反射性能更好
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle methodHandle = lookup.findVirtual(
    String.class, "substring", 
    MethodType.methodType(String.class, int.class)
);
String result = (String) methodHandle.invoke("Hello", 2);
```

---

## 六、面试回答要点

### 6.1 核心回答模板

**定义**：Java反射是运行时动态获取和操作类信息的机制，核心是`Class`类。

**核心API**：`Class`、`Field`、`Method`、`Constructor`。

**主要应用**：
1. **Spring框架**：IoC容器通过反射创建Bean并注入依赖
2. **ORM框架**：MyBatis/Hibernate通过反射将数据库记录映射为对象
3. **动态代理**：AOP通过反射实现方法拦截和增强
4. **注解处理**：通过反射读取注解信息并执行相应逻辑

**优缺点**：
- 优点：灵活性高，是框架的基础技术
- 缺点：性能开销大（慢10-100倍），安全性问题，代码可读性差

**优化**：缓存反射对象，使用MethodHandle替代反射。

### 6.2 加分项

- 能说出反射在Spring中的具体应用（Bean创建、依赖注入）
- 了解反射的性能问题及优化方案
- 知道反射与直接调用的性能差异
- 能说出反射的安全隐患及如何避免

---

## 七、常见面试追问

### Q1：反射能访问私有成员吗？

**答**：可以。通过 `field.setAccessible(true)` 可以突破访问权限限制，访问私有字段和方法。

### Q2：反射的性能问题如何解决？

**答**：
1. 缓存反射对象（Class、Method、Field）
2. 使用MethodHandle替代反射
3. 在框架初始化时使用反射，避免在频繁调用的业务代码中使用

### Q3：反射在Spring中是如何应用的？

**答**：
1. **Bean创建**：通过反射扫描`@Component`等注解的类，创建Bean实例
2. **依赖注入**：通过反射获取`@Autowired`注解的字段，注入依赖对象
3. **AOP代理**：通过反射实现动态代理，拦截方法调用

### Q4：反射和直接调用有什么区别？

**答**：
- **直接调用**：编译时确定，性能高，类型安全
- **反射调用**：运行时确定，性能低（慢10-100倍），但灵活性高
