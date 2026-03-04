## apply 方法介绍

### 1. 基本概念
`apply` 是 Java 8 中函数式接口 `Function<T, R>` 的核心方法，用于将输入参数转换为输出结果。它不是特定工具类库的方法，而是 Java 标准库的一部分。

### 2. 所属体系
- **所属接口**：`java.util.function.Function<T, R>`
- **JDK 版本**：Java 8+
- **方法签名**：`R apply(T t)`

### 3. 功能作用
`apply` 方法用于：
1. **函数式编程**：作为函数式接口的核心方法实现函数式编程
2. **数据转换**：将一种类型的数据转换为另一种类型
3. **回调机制**：作为回调函数处理特定逻辑
4. **策略模式**：实现不同的业务处理策略

### 4. 接口定义

```java
@FunctionalInterface
public interface Function<T, R> {
    /**
     * 将输入参数 t 转换为输出结果 R
     */
    R apply(T t);
    
    // 其他默认方法...
}
```


### 5. 在代码中的使用

```java
// 在 queryWithPassThrough 方法中使用
// dbFallback 是一个 Function<ID, R> 类型的参数
R r = dbFallback.apply(id);

// 在 queryWithLogicalExpire 方法中使用
R newR = dbFallback.apply(id);

// 在 queryWithMutex 方法中使用
r = dbFallback.apply(id);
```


### 6. 使用示例

#### (1) Lambda 表达式形式
```java
// 定义 Function 函数
Function<Integer, String> converter = (Integer id) -> "User:" + id;

// 调用 apply 方法
String result = converter.apply(123); // 返回 "User:123"
```


#### (2) 方法引用形式
```java
// 使用方法引用
Function<String, Integer> parseInt = Integer::parseInt;
Integer number = parseInt.apply("123"); // 返回整数 123
```


#### (3) 自定义实现形式
```java
// 自定义 Function 实现
Function<Long, Shop> dbQuery = new Function<Long, Shop>() {
    @Override
    public Shop apply(Long id) {
        // 查询数据库逻辑
        return shopMapper.selectById(id);
    }
};

Shop shop = dbQuery.apply(1L);
```


### 7. 在缓存客户端中的作用

```java
public <R,ID> R queryWithPassThrough(
        String keyPrefix, ID id, Class<R> type, Function<ID, R> dbFallback, Long time, TimeUnit unit){
    
    // ...缓存查询逻辑
    
    // 当缓存未命中时，调用传入的函数查询数据库
    R r = dbFallback.apply(id);
    
    // ...
    return r;
}
```


在这个场景中，`dbFallback` 是一个函数式接口，允许调用者自定义数据库查询逻辑，实现了控制反转和依赖注入的思想。

### 8. 相关函数式接口对比

| 接口             | 方法签名            | 用途                       |
| ---------------- | ------------------- | -------------------------- |
| `Function<T, R>` | `R apply(T t)`      | 有输入有输出的函数         |
| `Consumer<T>`    | `void accept(T t)`  | 有输入无输出的消费函数     |
| `Supplier<T>`    | `T get()`           | 无输入有输出的供给函数     |
| `Predicate<T>`   | `boolean test(T t)` | 有输入返回布尔值的判断函数 |

### 9. 优势

1. **灵活性高**：允许调用方自定义具体实现逻辑
2. **解耦合**：将缓存逻辑与数据查询逻辑分离
3. **复用性强**：同一缓存框架可用于不同业务场景
4. **符合开闭原则**：对扩展开放，对修改关闭
5. **支持函数式编程**：可使用 Lambda 表达式简化代码

### 10. 与传统写法对比

```java
// 传统写法（硬编码）
public Shop queryShopWithCache(Long id) {
    String key = "shop:" + id;
    String json = redisTemplate.opsForValue().get(key);
    if (StrUtil.isNotBlank(json)) {
        return JSONUtil.toBean(json, Shop.class);
    }
    
    // 硬编码数据库查询逻辑
    Shop shop = shopMapper.selectById(id); 
    if (shop != null) {
        redisTemplate.opsForValue().set(key, JSONUtil.toJsonStr(shop));
    }
    return shop;
}

// 使用 Function 的写法（灵活解耦）
public <R,ID> R queryWithPassThrough(
        String keyPrefix, ID id, Class<R> type, Function<ID, R> dbFallback, Long time, TimeUnit unit) {
    
    String key = keyPrefix + id;
    String json = stringRedisTemplate.opsForValue().get(key);
    if (StrUtil.isNotBlank(json)) {
        return JSONUtil.toBean(json, type);
    }
    
    // 使用传入的函数进行数据库查询
    R r = dbFallback.apply(id);
    if (r != null) {
        this.set(key, r, time, unit);
    }
    return r;
}
```


### 11. 注意事项

```java
// 正确使用
R r = dbFallback.apply(id); // 调用传入的函数

// 异常处理
try {
    R r = dbFallback.apply(id);
} catch (Exception e) {
    // 处理数据库查询异常
}

// 空值检查
R r = dbFallback.apply(id);
if (r != null) {
    // 处理非空情况
}
```


`apply` 方法体现了 Java 8 函数式编程的强大能力，在缓存框架中通过依赖注入的方式实现了高度灵活和可复用的设计。