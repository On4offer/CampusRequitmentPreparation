# Java的三大特性？多态是怎么体现的？如何实现多态？

## 一、Java的三大特性

Java 的三大特性是：**封装**、**继承**、**多态**。

| 特性 | 概念 | 作用 | 示例 |
|------|------|------|------|
| **封装** | 将数据和行为封装在类中，对外提供公共接口 | 隐藏实现细节，提高安全性和可维护性 | `private` 字段 + `public`  getter/setter |
| **继承** | 子类继承父类的属性和方法 | 代码复用，建立类层次结构 | `class Son extends Father` |
| **多态** | 同一行为在不同对象上有不同的表现 | 提高代码的灵活性和可扩展性 | 父类引用指向子类对象 |

### 1.1 封装

**封装**是指将对象的状态（属性）和行为（方法）封装在一起，对外只暴露必要的接口，隐藏实现细节。

**示例**：
```java
public class Patient {
    // 私有属性（封装）
    private String name;
    private int age;
    private String id;
    
    // 公共接口
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        if (age >= 0) {
            this.age = age;
        }
    }
}
```

### 1.2 继承

**继承**是指子类继承父类的属性和方法，实现代码复用，并可以在子类中扩展或重写父类的方法。

**示例**：
```java
// 父类
public class Person {
    protected String name;
    protected int age;
    
    public void eat() {
        System.out.println(name + " 在吃饭");
    }
}

// 子类
public class Doctor extends Person {
    private String specialty;
    
    public void treatPatient() {
        System.out.println(name + " 医生正在治疗病人");
    }
    
    // 重写父类方法
    @Override
    public void eat() {
        System.out.println(name + " 医生在医院食堂吃饭");
    }
}
```

### 1.3 多态

**多态**是指同一行为在不同对象上有不同的表现形式，即父类引用指向子类对象，调用方法时会根据实际对象类型执行相应的方法。

**示例**：
```java
public class PolymorphismDemo {
    public static void main(String[] args) {
        Person person1 = new Person();
        Person person2 = new Doctor();  // 父类引用指向子类对象
        
        person1.eat();  // 调用 Person 的 eat 方法
        person2.eat();  // 调用 Doctor 的 eat 方法（多态）
        
        // 向下转型
        if (person2 instanceof Doctor) {
            Doctor doctor = (Doctor) person2;
            doctor.treatPatient();
        }
    }
}
```

## 二、多态的体现

### 2.1 多态的表现形式

#### 2.1.1 方法重写（Override）

子类重写父类的方法，当父类引用指向子类对象时，调用该方法会执行子类的实现。

**示例**：
```java
public class Animal {
    public void makeSound() {
        System.out.println("动物发出声音");
    }
}

public class Dog extends Animal {
    @Override
    public void makeSound() {
        System.out.println("狗汪汪叫");
    }
}

public class Cat extends Animal {
    @Override
    public void makeSound() {
        System.out.println("猫喵喵叫");
    }
}

public class Test {
    public static void main(String[] args) {
        Animal[] animals = new Animal[3];
        animals[0] = new Animal();
        animals[1] = new Dog();
        animals[2] = new Cat();
        
        for (Animal animal : animals) {
            animal.makeSound();  // 多态体现
        }
    }
}
```

**输出**：
```
动物发出声音
狗汪汪叫
猫喵喵叫
```

#### 2.1.2 方法重载（Overload）

同一个类中，方法名相同但参数列表不同，根据参数类型和数量调用不同的方法。

**示例**：
```java
public class Calculator {
    // 方法重载
    public int add(int a, int b) {
        return a + b;
    }
    
    public double add(double a, double b) {
        return a + b;
    }
    
    public int add(int a, int b, int c) {
        return a + b + c;
    }
}

public class Test {
    public static void main(String[] args) {
        Calculator calculator = new Calculator();
        System.out.println(calculator.add(1, 2));        // 调用第一个方法
        System.out.println(calculator.add(1.5, 2.5));    // 调用第二个方法
        System.out.println(calculator.add(1, 2, 3));     // 调用第三个方法
    }
}
```

### 2.2 多态的应用场景

#### 2.2.1 医疗美容系统中的多态

```java
// 抽象服务类
public abstract class Service {
    public abstract void perform();
    public abstract double getPrice();
}

// 具体服务实现
public class FacialService extends Service {
    @Override
    public void perform() {
        System.out.println("执行面部护理服务");
    }
    
    @Override
    public double getPrice() {
        return 299.0;
    }
}

public class BodyService extends Service {
    @Override
    public void perform() {
        System.out.println("执行身体护理服务");
    }
    
    @Override
    public double getPrice() {
        return 399.0;
    }
}

public class NailService extends Service {
    @Override
    public void perform() {
        System.out.println("执行美甲服务");
    }
    
    @Override
    public double getPrice() {
        return 199.0;
    }
}

// 服务管理器
public class ServiceManager {
    public void processService(Service service) {
        service.perform();
        System.out.println("服务价格: " + service.getPrice());
    }
}

// 测试
public class Test {
    public static void main(String[] args) {
        ServiceManager manager = new ServiceManager();
        
        // 多态：同一方法处理不同类型的服务
        manager.processService(new FacialService());
        manager.processService(new BodyService());
        manager.processService(new NailService());
    }
}
```

**输出**：
```
执行面部护理服务
服务价格: 299.0
执行身体护理服务
服务价格: 399.0
执行美甲服务
服务价格: 199.0
```

## 三、多态的实现原理

### 3.1 动态绑定（Dynamic Binding）

**动态绑定**是多态的核心实现机制，指在运行时根据对象的实际类型来确定调用哪个方法。

**执行过程**：
1. 编译器检查方法签名，确保方法存在
2. 运行时，JVM 确定对象的实际类型
3. 根据实际类型调用对应的方法实现

### 3.2 方法表（Method Table）

JVM 为每个类维护一个方法表，记录该类的所有方法信息。当调用方法时，JVM 通过方法表查找并调用相应的方法。

**方法表结构**：
- 包含类的所有方法（包括继承的方法）
- 子类重写的方法会覆盖父类的方法条目
- 方法表在类加载时生成

### 3.3 向上转型和向下转型

#### 3.3.1 向上转型（Upcasting）

将子类类型转换为父类类型，是隐式的、安全的。

```java
Animal animal = new Dog();  // 向上转型
```

#### 3.3.2 向下转型（Downcasting）

将父类类型转换为子类类型，需要显式转换，可能抛出 `ClassCastException`。

```java
Animal animal = new Dog();
if (animal instanceof Dog) {
    Dog dog = (Dog) animal;  // 向下转型
    dog.bark();
}
```

## 四、多态的优缺点

### 4.1 优点

1. **代码灵活性**：同一方法可以处理不同类型的对象
2. **可扩展性**：新增子类不需要修改现有代码
3. **代码复用**：父类的方法可以被多个子类复用
4. **解耦**：降低了代码之间的耦合度

### 4.2 缺点

1. **性能开销**：动态绑定会增加运行时开销
2. **类型信息丢失**：向上转型后，无法直接访问子类特有的方法
3. **复杂性增加**：多态使得代码逻辑更复杂，调试难度增大

## 五、多态与设计模式

### 5.1 策略模式

```java
// 策略接口
public interface PaymentStrategy {
    void pay(double amount);
}

// 具体策略
public class WeChatPay implements PaymentStrategy {
    @Override
    public void pay(double amount) {
        System.out.println("微信支付: " + amount);
    }
}

public class Alipay implements PaymentStrategy {
    @Override
    public void pay(double amount) {
        System.out.println("支付宝支付: " + amount);
    }
}

// 上下文
public class PaymentContext {
    private PaymentStrategy strategy;
    
    public PaymentContext(PaymentStrategy strategy) {
        this.strategy = strategy;
    }
    
    public void processPayment(double amount) {
        strategy.pay(amount);
    }
}

// 测试
public class Test {
    public static void main(String[] args) {
        PaymentContext context = new PaymentContext(new WeChatPay());
        context.processPayment(100.0);
        
        context = new PaymentContext(new Alipay());
        context.processPayment(200.0);
    }
}
```

### 5.2 工厂模式

```java
// 产品接口
public interface Product {
    void use();
}

// 具体产品
public class ProductA implements Product {
    @Override
    public void use() {
        System.out.println("使用产品A");
    }
}

public class ProductB implements Product {
    @Override
    public void use() {
        System.out.println("使用产品B");
    }
}

// 工厂类
public class ProductFactory {
    public static Product createProduct(String type) {
        if ("A".equals(type)) {
            return new ProductA();
        } else if ("B".equals(type)) {
            return new ProductB();
        }
        return null;
    }
}

// 测试
public class Test {
    public static void main(String[] args) {
        Product product = ProductFactory.createProduct("A");
        product.use();  // 多态
        
        product = ProductFactory.createProduct("B");
        product.use();  // 多态
    }
}
```

## 六、面试标准回答（2分钟）

「Java 的三大特性是封装、继承和多态。封装是将数据和行为封装在类中，对外提供公共接口；继承是子类继承父类的属性和方法，实现代码复用；多态是同一行为在不同对象上有不同的表现。多态的体现包括方法重写和方法重载，通过动态绑定实现。在医疗美容系统中，我们可以使用多态来处理不同类型的服务，如面部护理、身体护理等，提高代码的灵活性和可扩展性。多态的实现原理是动态绑定和方法表机制，父类引用指向子类对象时，会根据实际对象类型调用相应的方法。」

## 七、常见追问

**Q1：多态的必要条件是什么？**

1. 继承关系
2. 方法重写
3. 父类引用指向子类对象

**Q2：方法重写和方法重载的区别？**

- 方法重写：发生在父子类之间，方法名、参数列表、返回类型都相同
- 方法重载：发生在同一个类中，方法名相同，参数列表不同

**Q3：多态的运行时和编译时类型？**

- 编译时类型：变量声明的类型
- 运行时类型：变量实际指向的对象类型

**Q4：为什么多态需要方法重写？**

方法重写是多态的基础，只有子类重写了父类的方法，才能在运行时根据实际对象类型调用相应的方法实现。

## 八、小结表

| 特性 | 概念 | 实现方式 | 应用场景 |
|------|------|---------|---------|
| 封装 | 隐藏实现细节 | private 字段 + public 方法 | 所有类的设计 |
| 继承 | 代码复用 | extends 关键字 | 类层次结构 |
| 多态 | 同一行为不同表现 | 方法重写 + 父类引用 | 策略模式、工厂模式等 |
