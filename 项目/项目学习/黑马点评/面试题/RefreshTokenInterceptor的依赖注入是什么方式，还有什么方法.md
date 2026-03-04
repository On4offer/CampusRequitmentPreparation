```java
    private StringRedisTemplate stringRedisTemplate;

    public RefreshTokenInterceptor(StringRedisTemplate stringRedisTemplate) {
        this.stringRedisTemplate = stringRedisTemplate;
    }
```

## 两个声明的不同作用

### 1. 成员变量声明
```java
private StringRedisTemplate stringRedisTemplate;
```

- **作用**：声明一个成员变量，用于在类的各个方法中使用
- **性质**：变量声明，不涉及初始化
- **作用域**：整个类的所有方法都可以访问

### 2. 构造器参数注入
```java
public RefreshTokenInterceptor(StringRedisTemplate stringRedisTemplate) {
    this.stringRedisTemplate = stringRedisTemplate;
}
```

- **作用**：通过构造器参数接收外部传入的依赖对象，并赋值给成员变量
- **性质**：对象初始化过程
- **时机**：创建对象实例时执行

## 完整流程

```java
// 1. 声明成员变量（占位符）
private StringRedisTemplate stringRedisTemplate;

// 2. 通过构造器注入实际对象
public RefreshTokenInterceptor(StringRedisTemplate stringRedisTemplate) {
    // 将传入的对象赋值给成员变量
    this.stringRedisTemplate = stringRedisTemplate;
}

// 3. 在方法中使用
@Override
public boolean preHandle(...) {
    // 使用已注入的 Redis 模板
    Map<Object, Object> userMap = stringRedisTemplate.opsForHash().entries(key);
    // ...
}
```


## 类比理解

这就像给手机充电的过程：
```java
// 1. 声明手机有一个充电接口
private 充电接口 charger;

// 2. 通过构造器连接充电器（注入电源）
public Phone(充电接口 charger) {
    this.charger = charger;  // 连接充电器
}

// 3. 使用充电功能
public void charge() {
    charger.充电();  // 使用充电功能
}
```


## 总结

- **成员变量声明**：声明"我需要一个工具"
- **构造器注入**：提供"具体的工具实例"
- 两者配合完成依赖注入，不是重复，而是分工合作

这是标准的依赖注入模式，确保了类的松耦合和可测试性。

是的，除了构造器注入，还有其他几种常见的依赖注入方式：

## 1. 字段注入（Field Injection）
```java
@Component
public class RefreshTokenInterceptor implements HandlerInterceptor {
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    
    // 不需要构造器
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 直接使用
        Map<Object, Object> userMap = stringRedisTemplate.opsForHash().entries(key);
        // ...
    }
}
```


## 2. Setter 方法注入（Setter Injection）
```java
@Component
public class RefreshTokenInterceptor implements HandlerInterceptor {
    private StringRedisTemplate stringRedisTemplate;
    
    @Autowired
    public void setStringRedisTemplate(StringRedisTemplate stringRedisTemplate) {
        this.stringRedisTemplate = stringRedisTemplate;
    }
    
    @Override
    public boolean preHandle(HttpServletRequest request, HttpServletResponse response, Object handler) throws Exception {
        // 使用注入的依赖
        Map<Object, Object> userMap = stringRedisTemplate.opsForHash().entries(key);
        // ...
    }
}
```


## 3. 方法参数注入（Method Parameter Injection）
```java
@Component
public class RefreshTokenInterceptor implements HandlerInterceptor {
    private StringRedisTemplate stringRedisTemplate;
    
    @Autowired
    public RefreshTokenInterceptor(StringRedisTemplate stringRedisTemplate) {
        this.stringRedisTemplate = stringRedisTemplate;
    }
    // 这实际上还是构造器注入
}
```


## 各种注入方式的对比

| 注入方式       | 优点                                                         | 缺点                                                         | 适用场景                     |
| -------------- | ------------------------------------------------------------ | ------------------------------------------------------------ | ---------------------------- |
| **构造器注入** | 1. 保证依赖不为null<br>2. 对象不可变<br>3. 便于测试<br>4. 符合单一职责 | 1. 构造器参数过多时复杂<br>2. 循环依赖问题                   | **推荐使用**，特别是必选依赖 |
| **字段注入**   | 1. 代码简洁<br>2. 使用简单                                   | 1. 依赖可能为null<br>2. 不利于单元测试<br>3. 隐藏了类的依赖关系<br>4. 对象状态可变 | 可选依赖，简单场景           |
| **Setter注入** | 1. 支持延迟注入<br>2. 可重新配置<br>3. 便于测试              | 1. 依赖可能为null<br>2. 对象状态可变                         | 可选依赖，需要重新配置的场景 |

## 在拦截器中的实际应用

由于拦截器通常通过配置类手动注册，所以**构造器注入**是最常用的方式：

```java
@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // 构造器注入
        registry.addInterceptor(new RefreshTokenInterceptor(stringRedisTemplate));
    }
}
```


如果使用字段注入，则需要将拦截器注册为 Spring Bean：

```java
@Component  // 注册为Spring Bean
public class RefreshTokenInterceptor implements HandlerInterceptor {
    @Autowired
    private StringRedisTemplate stringRedisTemplate;
    // ...
}

@Configuration
public class WebConfig implements WebMvcConfigurer {
    @Autowired
    private RefreshTokenInterceptor refreshTokenInterceptor;
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        // 直接使用Spring管理的Bean
        registry.addInterceptor(refreshTokenInterceptor);
    }
}
```

**总结**：在当前代码中使用构造器注入是最佳实践，因为它保证了依赖的强制性和可测试性。