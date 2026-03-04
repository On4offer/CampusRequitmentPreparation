Spring 中创建 Bean 实例的方法主要有以下 **三种方式**，你可以理解为三种“实例化策略”：

------

## **1. 构造方法实例化（Constructor Instantiation）**（最常见）

Spring 使用 Java 反射机制，通过构造器创建对象。

### 示例：

```java
@Component
public class MyBean {
    public MyBean() {
        System.out.println("构造方法创建");
    }
}
```

Spring 使用：

```java
clazz.getDeclaredConstructor().newInstance();
```

### 特点：

- 支持无参和有参构造
- 可配合 `@Autowired` 构造器实现构造函数注入

------

## **2. 静态工厂方法实例化（Static Factory Method）**

通过调用某个类的静态方法返回实例。

### 示例：

```java
public class MyStaticFactory {
    public static MyBean createInstance() {
        return new MyBean();
    }
}
```

Spring 配置（XML）：

```xml
<bean id="myBean" class="com.example.MyStaticFactory" factory-method="createInstance"/>
```

### 特点：

- 不需要公开构造器
- 工厂方法可以封装复杂逻辑

------

## **3. 实例工厂方法实例化（Instance Factory Method）**

先创建一个工厂对象，然后通过该对象的方法创建 Bean。

### 示例：

```java
public class MyFactory {
    public MyBean create() {
        return new MyBean();
    }
}
```

Spring 配置：

```xml
<bean id="factory" class="com.example.MyFactory"/>
<bean id="myBean" factory-bean="factory" factory-method="create"/>
```

### 特点：

- 更灵活，支持依赖注入到工厂类中
- 常用于需要预处理逻辑的对象创建

------

## **对比总结表**

| 创建方式     | 是否使用反射 | 是否需要工厂类 | 是否支持依赖注入 | 使用频率 |
| ------------ | ------------ | -------------- | ---------------- | -------- |
| 构造方法     | 是           | 否             | 支持             | 非常常用 |
| 静态工厂方法 | 否（用方法） | 是（类级）     | 限制较多         | 较少     |
| 实例工厂方法 | 否（用方法） | 是（对象级）   | 工厂类支持注入   | 特殊场景 |

------

## 补充：还有一种间接方式——**FactoryBean 接口**

这是 Spring 的一种高级扩展机制。

实现 `org.springframework.beans.factory.FactoryBean<T>` 接口，可以控制 Bean 的创建过程。

### 示例：

```java
public class MyFactoryBean implements FactoryBean<MyBean> {
    @Override
    public MyBean getObject() {
        return new MyBean();
    }

    @Override
    public Class<?> getObjectType() {
        return MyBean.class;
    }
}
```

Spring 会调用 `getObject()` 来获取最终的 Bean。

------

### 总结一句话：

> Spring 创建 Bean 实例主要通过构造方法、静态工厂方法、实例工厂方法三种形式，此外还支持通过 `FactoryBean` 进行更复杂的定制创建。

需要我帮你画个图或流程图来对比它们的调用顺序吗？