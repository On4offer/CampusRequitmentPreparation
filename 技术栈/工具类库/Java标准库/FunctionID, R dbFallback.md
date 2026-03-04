## `Function<ID, R> dbFallback` 介绍

### 1. 基本概念
`Function<ID, R> dbFallback` 是 Java 8 引入的函数式接口，用于表示一个从 `ID` 类型到 `R` 类型的函数转换。

### 2. 所属体系
- **类型**：Java 标准库中的 `java.util.function.Function<T,R>` 接口
- **包路径**：`java.util.function`
- **类型**：函数式接口（@FunctionalInterface）

### 3. 功能作用
`Function<ID, R> dbFallback` 参数用于：
1. **回调函数**：当缓存未命中时，回调执行数据库查询
2. **延迟执行**：只在需要时才执行数据库查询
3. **类型安全**：确保输入输出类型的匹配

### 4. Function 接口定义

```java
@FunctionalInterface
public interface Function<T, R> {
    // 核心方法：接受 T 类型参数，返回 R 类型结果
    R apply(T t);
    
    // 默认方法：函数组合
    default <V> Function<V, R> compose(Function<? super V, ? extends T> before) { ... }
    default <V> Function<T, V> andThen(Function<? super R, ? extends V> after) { ... }
    static <T> Function<T, T> identity() { ... }
}
```


### 5. 在代码中的使用

```java
// 方法签名
public <R,ID> R queryWithPassThrough(
    String keyPrefix, 
    ID id, 
    Class<R> type, 
    Function<ID, R> dbFallback,  // 回调函数：ID -> R
    Long time, 
    TimeUnit unit
)

// 调用示例
Shop shop = cacheClient.queryWithPassThrough(
    CACHE_SHOP_KEY,    // keyPrefix
    1L,                // id: Long 类型
    Shop.class,        // type: Class<Shop>
    this::getById,     // dbFallback: Function<Long, Shop>
    CACHE_SHOP_TTL,    // time
    TimeUnit.MINUTES   // unit
);
```


### 6. 回调执行过程

```java
// 在方法内部执行回调
R r = dbFallback.apply(id);
//        ↑
//    调用传入的函数

// 等价于：
// 如果传入 this::getById，则执行：
// Shop shop = this.getById(1L);
```


### 7. 实际使用方式

#### (1) 方法引用
```java
// 使用方法引用
cacheClient.queryWithPassThrough(
    CACHE_SHOP_KEY,
    1L,
    Shop.class,
    this::getById,  // 等价于 (id) -> this.getById(id)
    CACHE_SHOP_TTL,
    TimeUnit.MINUTES
);
```


#### (2) Lambda 表达式
```java
// 使用 Lambda 表达式
cacheClient.queryWithPassThrough(
    CACHE_SHOP_KEY,
    1L,
    Shop.class,
    id -> shopMapper.selectById(id),  // Lambda 表达式
    CACHE_SHOP_TTL,
    TimeUnit.MINUTES
);
```


#### (3) 匿名内部类
```java
// 使用匿名内部类
cacheClient.queryWithPassThrough(
    CACHE_SHOP_KEY,
    1L,
    Shop.class,
    new Function<Long, Shop>() {
        @Override
        public Shop apply(Long id) {
            return shopMapper.selectById(id);
        }
    },
    CACHE_SHOP_TTL,
    TimeUnit.MINUTES
);
```


### 8. 在缓存方法中的作用

```java
public <R,ID> R queryWithPassThrough(...) {
    // 1. 先查缓存
    String json = stringRedisTemplate.opsForValue().get(key);
    if (StrUtil.isNotBlank(json)) {
        return JSONUtil.toBean(json, type);  // 缓存命中，直接返回
    }
    
    // 2. 缓存未命中，执行回调查询数据库
    R r = dbFallback.apply(id);  // 执行传入的查询函数
    //        ↑
    //    这里调用外部传入的查询方法
    
    // 3. 查询结果存入缓存
    if (r != null) {
        this.set(key, r, time, unit);
    }
    return r;
}
```


### 9. 优势

#### (1) 解耦合
```java
// 缓存工具不需要知道具体如何查询数据库
// 调用方提供查询逻辑
public <R,ID> R queryWithPassThrough(
    String keyPrefix, 
    ID id, 
    Class<R> type, 
    Function<ID, R> dbFallback,  // 调用方提供查询逻辑
    Long time, 
    TimeUnit unit
)
```


#### (2) 灵活性
```java
// 可以传入不同的查询逻辑
// 查询店铺
cacheClient.queryWithPassThrough(CACHE_SHOP_KEY, 1L, Shop.class, this::getById, ...);

// 查询用户
cacheClient.queryWithPassThrough(CACHE_USER_KEY, 1L, User.class, this::getUserById, ...);

// 自定义查询
cacheClient.queryWithPassThrough(CACHE_CUSTOM_KEY, 1L, Custom.class, 
    id -> customService.queryByCondition(id), ...);
```


#### (3) 类型安全
```java
// Function<ID, R> 确保输入输出类型匹配
Function<Long, Shop> fallback = this::getById;  // 类型匹配
// Function<String, Shop> fallback = this::getById;  // 编译错误！
```


### 10. 相关函数式接口

| 接口            | 功能        | 示例                   |
| --------------- | ----------- | ---------------------- |
| `Function<T,R>` | T → R       | `Function<Long, Shop>` |
| `Consumer<T>`   | T → void    | `Consumer<Shop>`       |
| `Supplier<T>`   | void → T    | `Supplier<Shop>`       |
| `Predicate<T>`  | T → boolean | `Predicate<Shop>`      |

这是 Java 8 函数式编程的核心特性，使得代码更加灵活和可复用。