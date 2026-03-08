# 📋 Java 泛型反射与注解 - 常用API与使用场景速查

> 日常开发常用泛型、反射、注解API与代码模板，配合《学习笔记.md》系统学习使用。

---

## 🧬 泛型速查

### 常用泛型符号约定

| 符号 | 含义 | 使用场景 |
|------|------|----------|
| `T` | Type | 通用类型参数 |
| `E` | Element | 集合元素 |
| `K` | Key | Map的键 |
| `V` | Value | Map的值 |
| `N` | Number | 数值类型 |
| `R` | Return | 返回值类型 |
| `?` | 通配符 | 未知类型 |

### 泛型类定义与使用

```java
// 定义泛型类
public class Box<T> {
    private T value;
    
    public void set(T value) {
        this.value = value;
    }
    
    public T get() {
        return value;
    }
}

// 使用
Box<String> stringBox = new Box<>();
stringBox.set("Hello");
String value = stringBox.get();     // 无需强转

Box<Integer> intBox = new Box<>();
intBox.set(100);
```

### 泛型方法

```java
public class GenericMethods {
    // 普通泛型方法
    public static <T> void print(T item) {
        System.out.println(item);
    }
    
    // 泛型方法（类上无泛型也可定义）
    public static <T> T getFirst(List<T> list) {
        return list.isEmpty() ? null : list.get(0);
    }
    
    // 泛型方法（多个类型参数）
    public static <K, V> Map<K, V> createMap(K key, V value) {
        Map<K, V> map = new HashMap<>();
        map.put(key, value);
        return map;
    }
    
    // 泛型方法（限定类型）
    public static <T extends Comparable<T>> T max(T a, T b) {
        return a.compareTo(b) > 0 ? a : b;
    }
    
    // 可变参数泛型方法
    @SafeVarargs
    public final <T> List<T> asList(T... items) {
        return Arrays.asList(items);
    }
}

// 调用
GenericMethods.print("Hello");                    // 自动推断为String
GenericMethods.<Integer>print(100);               // 显式指定类型
String first = GenericMethods.getList(list);      // 自动推断
Integer max = GenericMethods.max(10, 20);         // 返回20
```

### 泛型接口

```java
// 定义
public interface Processor<T, R> {
    R process(T input);
}

// 实现1：指定具体类型
public class StringLengthProcessor implements Processor<String, Integer> {
    @Override
    public Integer process(String input) {
        return input.length();
    }
}

// 实现2：保持泛型
public class IdentityProcessor<T> implements Processor<T, T> {
    @Override
    public T process(T input) {
        return input;
    }
}

// 使用
Processor<String, Integer> processor = new StringLengthProcessor();
Integer length = processor.process("Hello");      // 5
```

### 通配符

```java
// ? 无界通配符（任意类型）
public void printList(List<?> list) {
    for (Object item : list) {
        System.out.println(item);
    }
}

// ? extends T 上界通配符（T或T的子类）- 生产者，只能读
public void readNumbers(List<? extends Number> list) {
    for (Number num : list) {       // 可以安全读取为Number
        System.out.println(num.doubleValue());
    }
    // list.add(100);               // ✗ 编译错误，不能添加
}

// ? super T 下界通配符（T或T的父类）- 消费者，只能写
public void writeIntegers(List<? super Integer> list) {
    list.add(100);                  // ✓ 可以添加Integer
    list.add(200);
    // Integer i = list.get(0);     // ✗ 编译错误，只能作为Object读取
}

// PECS原则示例
public class Collections {
    // Producer Extends（从src读取到dest）
    public static <T> void copy(List<? super T> dest, List<? extends T> src) {
        for (T item : src) {
            dest.add(item);
        }
    }
}
```

### 类型边界

```java
// 上界（extends）
public class NumberBox<T extends Number> {
    private T value;
    
    public double doubleValue() {
        return value.doubleValue();     // 可以调用Number的方法
    }
}
// NumberBox<Integer> box1 = new NumberBox<>();  // ✓
// NumberBox<String> box2 = new NumberBox<>();   // ✗ 编译错误

// 多重边界（类在前，接口在后）
public <T extends Number & Comparable<T>> T findMax(List<T> list) {
    T max = list.get(0);
    for (T item : list) {
        if (item.compareTo(max) > 0) {
            max = item;
        }
    }
    return max;
}
```

### 泛型与数组（注意事项）

```java
// 不能直接创建泛型数组
// List<String>[] array = new List<String>[10];  // ✗ 编译错误

// 解决方案1：使用Object数组+强转（有警告）
@SuppressWarnings("unchecked")
List<String>[] array = (List<String>[]) new List[10];

// 解决方案2：使用List代替数组
List<List<String>> listOfLists = new ArrayList<>();

// 解决方案3：使用泛型集合类
public class GenericArray<T> {
    private Object[] array;
    
    @SuppressWarnings("unchecked")
    public T get(int index) {
        return (T) array[index];
    }
    
    public void set(int index, T value) {
        array[index] = value;
    }
}
```

---

## 🔍 反射速查

### 获取Class对象

```java
// 方式1：类名.class
Class<String> clazz1 = String.class;

// 方式2：对象.getClass()
String str = "Hello";
Class<? extends String> clazz2 = str.getClass();

// 方式3：Class.forName()（全限定名）
Class<?> clazz3 = Class.forName("java.lang.String");

// 方式4：类加载器
ClassLoader loader = Thread.currentThread().getContextClassLoader();
Class<?> clazz4 = loader.loadClass("java.lang.String");

// 基本类型的Class
Class<Integer> intClass = int.class;
Class<Void> voidClass = void.class;

// 数组的Class
Class<int[]> intArrayClass = int[].class;
Class<String[][]> string2DArrayClass = String[][].class;
```

### 创建对象

```java
// 方式1：调用无参构造（类必须有默认构造）
Class<?> clazz = Class.forName("com.example.User");
Object obj = clazz.newInstance();  // JDK 9已废弃

// 方式2：通过Constructor（推荐）
Constructor<?> constructor = clazz.getDeclaredConstructor();
Object obj2 = constructor.newInstance();

// 调用有参构造
Constructor<?> paramConstructor = clazz.getDeclaredConstructor(String.class, int.class);
Object obj3 = paramConstructor.newInstance("张三", 25);
```

### 访问字段

```java
public class User {
    public String name;                 // 公有字段
    private int age;                    // 私有字段
    public static final String TYPE = "USER";  // 静态字段
}

Class<?> clazz = User.class;

// 获取公有字段（包括继承的）
Field nameField = clazz.getField("name");

// 获取所有声明的字段（不包括继承的，包括私有）
Field[] allFields = clazz.getDeclaredFields();

// 获取指定声明字段（包括私有）
Field ageField = clazz.getDeclaredField("age");

// 获取字段值
User user = new User();
Object nameValue = nameField.get(user);

// 设置字段值
nameField.set(user, "李四");

// 访问私有字段（必须设置accessible）
ageField.setAccessible(true);           // 暴力访问
int age = (int) ageField.get(user);
ageField.set(user, 30);

// 访问静态字段
Field typeField = clazz.getField("TYPE");
String type = (String) typeField.get(null);  // 静态字段传null

// 获取字段信息
String fieldName = ageField.getName();
Class<?> fieldType = ageField.getType();
int modifiers = ageField.getModifiers();
boolean isPrivate = Modifier.isPrivate(modifiers);
```

### 调用方法

```java
public class UserService {
    public void sayHello() {
        System.out.println("Hello");
    }
    
    public String greet(String name) {
        return "Hello, " + name;
    }
    
    private void secretMethod() {
        System.out.println("Secret");
    }
    
    public static void staticMethod() {
        System.out.println("Static");
    }
}

Class<?> clazz = UserService.class;
UserService service = new UserService();

// 获取公有方法（包括继承的）
Method sayHelloMethod = clazz.getMethod("sayHello");

// 获取指定公有方法（含参数类型）
Method greetMethod = clazz.getMethod("greet", String.class);

// 获取所有声明的方法（包括私有，不包括继承的）
Method[] allMethods = clazz.getDeclaredMethods();

// 获取私有方法
Method secretMethod = clazz.getDeclaredMethod("secretMethod");

// 调用方法
sayHelloMethod.invoke(service);                 // 无参方法

// 调用有参方法
String result = (String) greetMethod.invoke(service, "张三");

// 调用私有方法
secretMethod.setAccessible(true);
secretMethod.invoke(service);

// 调用静态方法
Method staticMethod = clazz.getMethod("staticMethod");
staticMethod.invoke(null);                      // 静态方法传null

// 获取方法信息
String methodName = greetMethod.getName();
Class<?> returnType = greetMethod.getReturnType();
Class<?>[] paramTypes = greetMethod.getParameterTypes();
Class<?>[] exceptionTypes = greetMethod.getExceptionTypes();
int modifiers = greetMethod.getModifiers();
```

### 操作数组

```java
// 创建数组
int[] intArray = (int[]) Array.newInstance(int.class, 5);
String[] strArray = (String[]) Array.newInstance(String.class, 10);

// 多维数组
int[][] matrix = (int[][]) Array.newInstance(int[].class, 3);

// 获取/设置元素
Array.set(intArray, 0, 100);
int value = (int) Array.get(intArray, 0);

// 获取数组长度
int length = Array.getLength(intArray);
```

### 获取泛型信息

```java
// 获取父类的泛型参数
public class StringList extends ArrayList<String> {}

Type genericSuperclass = StringList.class.getGenericSuperclass();
if (genericSuperclass instanceof ParameterizedType) {
    ParameterizedType paramType = (ParameterizedType) genericSuperclass;
    Type[] actualTypeArgs = paramType.getActualTypeArguments();
    Class<?> typeArg = (Class<?>) actualTypeArgs[0];
    System.out.println(typeArg);  // class java.lang.String
}

// 获取字段的泛型类型
public class Container {
    private List<String> items;
    private Map<String, Integer> map;
}

Field itemsField = Container.class.getDeclaredField("items");
Type genericType = itemsField.getGenericType();
if (genericType instanceof ParameterizedType) {
    ParameterizedType paramType = (ParameterizedType) genericType;
    Type[] typeArgs = paramType.getActualTypeArguments();
    // typeArgs[0] = String
}

// 获取方法的泛型参数和返回值
Method method = MyClass.class.getMethod("process", List.class);
Type[] paramTypes = method.getGenericParameterTypes();
Type returnType = method.getGenericReturnType();
```

### 动态代理

```java
// 定义接口
public interface HelloService {
    String sayHello(String name);
}

// 实现类
public class HelloServiceImpl implements HelloService {
    @Override
    public String sayHello(String name) {
        return "Hello, " + name;
    }
}

// 创建代理
public class ProxyFactory {
    @SuppressWarnings("unchecked")
    public static <T> T createProxy(Class<T> interfaceClass, T target) {
        return (T) Proxy.newProxyInstance(
            interfaceClass.getClassLoader(),
            new Class<?>[] { interfaceClass },
            new InvocationHandler() {
                @Override
                public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
                    System.out.println("Before: " + method.getName());
                    Object result = method.invoke(target, args);
                    System.out.println("After: " + method.getName());
                    return result;
                }
            }
        );
    }
}

// 使用
HelloService target = new HelloServiceImpl();
HelloService proxy = ProxyFactory.createProxy(HelloService.class, target);
String result = proxy.sayHello("张三");  // 会打印Before/After
```

---

## 🏷️ 注解速查

### 内置注解

```java
// @Override - 标记方法重写
@Override
public String toString() { return "..."; }

// @Deprecated - 标记已废弃
@Deprecated
public void oldMethod() { }

// @SuppressWarnings - 抑制警告
@SuppressWarnings("unchecked")
@SuppressWarnings({"rawtypes", "unchecked"})
@SuppressWarnings("all")

// @FunctionalInterface - 标记函数式接口
@FunctionalInterface
public interface MyFunction {
    void apply();  // 只能有一个抽象方法
}

// @SafeVarargs - 抑制可变参数泛型警告（JDK 7+）
@SafeVarargs
public final <T> void printAll(T... items) { }
```

### 元注解（定义注解的注解）

```java
// @Retention - 注解保留策略
@Retention(RetentionPolicy.SOURCE)   // 仅源码，编译后丢弃
@Retention(RetentionPolicy.CLASS)    // 编译到class，运行时不可见（默认）
@Retention(RetentionPolicy.RUNTIME)  // 运行时保留，可通过反射获取

// @Target - 注解作用目标
@Target(ElementType.TYPE)            // 类、接口、枚举
@Target(ElementType.FIELD)           // 字段
@Target(ElementType.METHOD)          // 方法
@Target(ElementType.PARAMETER)       // 参数
@Target(ElementType.CONSTRUCTOR)     // 构造器
@Target(ElementType.LOCAL_VARIABLE)  // 局部变量
@Target(ElementType.ANNOTATION_TYPE) // 注解
@Target(ElementType.PACKAGE)         // 包
@Target(ElementType.TYPE_PARAMETER)  // 类型参数（JDK 8+）
@Target(ElementType.TYPE_USE)        // 类型使用（JDK 8+）

// 组合多个目标
@Target({ElementType.TYPE, ElementType.METHOD})

// @Documented - 包含在Javadoc中
@Documented

// @Inherited - 子类继承该注解
@Inherited

// @Repeatable - 可重复注解（JDK 8+）
@Repeatable(Schedules.class)
```

### 自定义注解

```java
// 定义注解
@Retention(RetentionPolicy.RUNTIME)
@Target({ElementType.TYPE, ElementType.METHOD})
@Documented
public @interface MyAnnotation {
    // 属性（无参方法形式）
    String value();                     // 必需属性
    String name() default "default";    // 有默认值
    int count() default 0;
    Class<?> clazz() default Void.class;
    String[] tags() default {};         // 数组属性
    
    // 属性类型限制：基本类型、String、Class、枚举、注解、以及这些的数组
}

// 使用注解
@MyAnnotation("test")
public class MyClass { }

@MyAnnotation(value = "test", name = "custom", count = 5)
public void myMethod() { }

// 可重复注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@Repeatable(Schedules.class)  // 指定容器注解
public @interface Schedule {
    String day();
}

@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Schedules {
    Schedule[] value();  // 必须叫value，类型为被重复注解的数组
}

// 使用可重复注解
@Schedule(day = "Monday")
@Schedule(day = "Friday")
public void doWork() { }
```

### 读取注解

```java
// 检查是否存在注解
boolean hasAnnotation = clazz.isAnnotationPresent(MyAnnotation.class);

// 获取注解
MyAnnotation annotation = clazz.getAnnotation(MyAnnotation.class);
if (annotation != null) {
    String value = annotation.value();
    String name = annotation.name();
    int count = annotation.count();
}

// 获取所有注解
Annotation[] annotations = clazz.getAnnotations();
Annotation[] declaredAnnotations = clazz.getDeclaredAnnotations();  // 不包括继承的

// 获取方法上的注解
Method method = clazz.getMethod("doSomething");
MyAnnotation methodAnno = method.getAnnotation(MyAnnotation.class);

// 获取字段上的注解
Field field = clazz.getDeclaredField("myField");
MyAnnotation fieldAnno = field.getAnnotation(MyAnnotation.class);

// 获取参数上的注解
Method paramMethod = clazz.getMethod("process", String.class);
Annotation[][] paramAnnotations = paramMethod.getParameterAnnotations();
// paramAnnotations[0] 是第一个参数的所有注解

// 获取可重复注解
Schedule[] schedules = method.getAnnotationsByType(Schedule.class);
```

---

## 🎯 常用代码场景

### 1. 通用DAO实现（泛型+反射）

```java
public abstract class BaseDao<T> {
    private final Class<T> entityClass;
    
    @SuppressWarnings("unchecked")
    public BaseDao() {
        // 获取泛型参数类型
        Type genericSuperclass = getClass().getGenericSuperclass();
        ParameterizedType paramType = (ParameterizedType) genericSuperclass;
        this.entityClass = (Class<T>) paramType.getActualTypeArguments()[0];
    }
    
    public T findById(Long id) throws Exception {
        // 使用entityClass进行查询
        String sql = "SELECT * FROM " + entityClass.getSimpleName() + " WHERE id = ?";
        // 执行查询并映射结果...
        return entityClass.getDeclaredConstructor().newInstance();
    }
    
    public List<T> findAll() {
        // 查询所有
        return new ArrayList<>();
    }
}

// 使用
public class UserDao extends BaseDao<User> {
    // 自动获得User类型的CRUD方法
}
```

### 2. 对象拷贝工具（反射）

```java
public class BeanUtils {
    public static void copyProperties(Object source, Object target) {
        Class<?> sourceClass = source.getClass();
        Class<?> targetClass = target.getClass();
        
        for (Field sourceField : sourceClass.getDeclaredFields()) {
            try {
                Field targetField = targetClass.getDeclaredField(sourceField.getName());
                if (targetField.getType().equals(sourceField.getType())) {
                    sourceField.setAccessible(true);
                    targetField.setAccessible(true);
                    targetField.set(target, sourceField.get(source));
                }
            } catch (NoSuchFieldException | IllegalAccessException e) {
                // 字段不存在或类型不匹配，跳过
            }
        }
    }
}

// 使用
User source = new User("张三", 20);
UserDTO target = new UserDTO();
BeanUtils.copyProperties(source, target);
```

### 3. 简单的依赖注入容器

```java
@Component
public class UserService {
    @Autowired
    private UserDao userDao;
}

// 容器实现
public class SimpleContainer {
    private final Map<Class<?>, Object> beans = new HashMap<>();
    
    public void scan(String packageName) throws Exception {
        // 扫描包下的所有类
        Set<Class<?>> classes = scanPackage(packageName);
        
        // 创建@Component标注的类的实例
        for (Class<?> clazz : classes) {
            if (clazz.isAnnotationPresent(Component.class)) {
                Object instance = clazz.getDeclaredConstructor().newInstance();
                beans.put(clazz, instance);
            }
        }
        
        // 处理@Autowired依赖注入
        for (Object bean : beans.values()) {
            for (Field field : bean.getClass().getDeclaredFields()) {
                if (field.isAnnotationPresent(Autowired.class)) {
                    field.setAccessible(true);
                    Object dependency = beans.get(field.getType());
                    field.set(bean, dependency);
                }
            }
        }
    }
    
    @SuppressWarnings("unchecked")
    public <T> T getBean(Class<T> clazz) {
        return (T) beans.get(clazz);
    }
}
```

### 4. 方法执行时间统计（动态代理）

```java
public class TimingProxy implements InvocationHandler {
    private final Object target;
    
    public static <T> T create(T target, Class<T> interfaceType) {
        return (T) Proxy.newProxyInstance(
            interfaceType.getClassLoader(),
            new Class<?>[] { interfaceType },
            new TimingProxy(target)
        );
    }
    
    private TimingProxy(Object target) {
        this.target = target;
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        long start = System.currentTimeMillis();
        try {
            return method.invoke(target, args);
        } finally {
            long elapsed = System.currentTimeMillis() - start;
            System.out.println(method.getName() + " took " + elapsed + "ms");
        }
    }
}

// 使用
UserService proxy = TimingProxy.create(new UserServiceImpl(), UserService.class);
proxy.findUser(1L);  // 会打印执行时间
```

### 5. JSON字段映射（注解+反射）

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface JsonField {
    String value();     // JSON中的字段名
}

public class User {
    @JsonField("user_name")
    private String userName;
    
    @JsonField("user_age")
    private int userAge;
    
    // getters and setters
}

public class JsonSerializer {
    public static String toJson(Object obj) throws Exception {
        StringBuilder json = new StringBuilder("{");
        Class<?> clazz = obj.getClass();
        
        Field[] fields = clazz.getDeclaredFields();
        for (int i = 0; i < fields.length; i++) {
            Field field = fields[i];
            field.setAccessible(true);
            
            String jsonKey = field.getName();
            if (field.isAnnotationPresent(JsonField.class)) {
                jsonKey = field.getAnnotation(JsonField.class).value();
            }
            
            Object value = field.get(obj);
            json.append("\"").append(jsonKey).append("\":");
            if (value instanceof String) {
                json.append("\"").append(value).append("\"");
            } else {
                json.append(value);
            }
            
            if (i < fields.length - 1) {
                json.append(",");
            }
        }
        
        json.append("}");
        return json.toString();
    }
}
```

---

## ⚠️ 常见坑点速查

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| 泛型类型擦除 | `List<String>`和`List<Integer>`运行时相同 | 用`instanceof`判断或传递`Class<T>`参数 |
| 不能创建泛型数组 | `new T[10]`编译错误 | 用`Object[]`+强转或`Array.newInstance()` |
| 反射访问私有成员 | 直接访问抛异常 | 先调用`setAccessible(true)` |
| 反射性能问题 | 反射调用比直接调用慢 | 缓存`Method`/`Field`对象，或用`MethodHandle` |
| 注解保留策略 | `RetentionPolicy.CLASS`运行时获取不到 | 需要运行时读取用`RUNTIME` |
| 泛型通配符赋值 | `List<Number>`和`List<Integer>`不兼容 | 用`List<? extends Number>` |
| 类型转换警告 | 泛型数组强转有警告 | 加`@SuppressWarnings("unchecked")` |

---

> 💡 **提示**：本文档用于日常速查，系统学习请查看《学习笔记.md》
