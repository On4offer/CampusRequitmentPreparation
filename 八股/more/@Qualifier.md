### **`@Qualifier` 注解简介**

**背景**：在 Spring 框架中，当使用 `@Autowired` 注入依赖时，如果存在多个同类型的 Bean，Spring **无法判断注入哪个**，就会抛出异常。此时可以使用 **`@Qualifier` 注解指定注入的 Bean 名称**，配合 `@Autowired` 使用，以避免歧义。

------

### **一、基本用法**

```java
@Component("mysqlUserRepository")
public class MySqlUserRepository implements UserRepository {}

@Component("mongoUserRepository")
public class MongoUserRepository implements UserRepository {}

@Service
public class UserService {

    @Autowired
    @Qualifier("mysqlUserRepository") // 指定注入哪一个 Bean
    private UserRepository userRepository;

}
```

#### 工作机制：

- `@Autowired` 按类型匹配；
- `@Qualifier` **按名称精确指定**需要注入的 Bean；
- 两者组合，解决了多实现类场景下的注入问题。

------

### **二、适用场景**

- 存在多个同类型 Bean（如多个实现类）；
- 注入接口时不确定注入哪个具体实现；
- 在使用 `@Autowired` 进行字段、方法、构造器注入时精确指定目标 Bean。

------

### **三、常见错误示例**

```java
@Autowired
private UserRepository userRepository; // 报错：多个实现，Spring 不知道选哪个
```

解决方法：

```java
@Autowired
@Qualifier("mongoUserRepository")
private UserRepository userRepository;
```

------

### **四、配合 `@Component` 指定 Bean 名称**

可以使用 `@Component("beanName")` 指定 Bean 的名称，供 `@Qualifier` 使用。

```java
@Component("orderServiceImplA")
public class OrderServiceImplA implements OrderService {}
```

------

### **五、配合构造器注入使用**

```java
@Service
public class PaymentService {

    private final PaymentProcessor processor;

    @Autowired
    public PaymentService(@Qualifier("alipayProcessor") PaymentProcessor processor) {
        this.processor = processor;
    }
}
```

------

### **六、小结一句话**

> **`@Qualifier` 是用来辅助 `@Autowired` 精确指定注入 Bean 名称的注解，主要解决多个同类型 Bean 注入歧义问题，是接口注入多实现时的利器。**

------

是否需要我进一步展示 `@Primary` 与 `@Qualifier` 的区别，或者在 XML 配置中的替代用法？