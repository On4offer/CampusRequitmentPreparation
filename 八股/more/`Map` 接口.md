`Map` 是 Java 集合框架中用于**存储键值对（key-value）映射关系**的一个接口，位于 `java.util` 包下。

------

### 一、`Map` 接口的核心特性

- 每个键（Key）**唯一**，一个键只能映射一个值（Value）
- 可以存储 `null` 值，`HashMap` 允许 `null` 键和 `null` 值，`Hashtable` 不允许
- `Map` 并不继承 `Collection` 接口，是集合框架中一个独立的体系

------

### 二、常用方法

```java
V put(K key, V value);         // 添加键值对
V get(Object key);             // 获取指定键的值
V remove(Object key);          // 删除指定键
boolean containsKey(Object k); // 是否包含指定键
boolean containsValue(Object v); // 是否包含指定值
Set<K> keySet();               // 获取所有键
Collection<V> values();        // 获取所有值
Set<Map.Entry<K,V>> entrySet(); // 获取所有键值对
int size();                    // 获取元素个数
void clear();                  // 清空Map
```

------

### 三、常见实现类及区别

| 实现类              | 是否线程安全 | 是否有序   | 是否允许 null 键/值       | 特点                           |
| ------------------- | ------------ | ---------- | ------------------------- | ------------------------------ |
| `HashMap`           | 否           | 否         | 允许1个null键，多个null值 | 常用、效率高，基于哈希表       |
| `Hashtable`         | 是           | 否         | 不允许                    | 老旧同步实现，效率低           |
| `LinkedHashMap`     | 否           | 有插入顺序 | 允许                      | 保留插入顺序                   |
| `TreeMap`           | 否           | 有排序     | 不允许null键              | 键自动排序（基于红黑树）       |
| `ConcurrentHashMap` | 是（高效）   | 否         | 不允许null键/值           | 支持高并发，线程安全的替代方案 |
| `WeakHashMap`       | 否           | 否         | 允许                      | 键是弱引用，适用于缓存         |

------

### 四、Map 遍历的几种方式

#### 1. 遍历 `keySet`

```java
for (String key : map.keySet()) {
    System.out.println(key + " = " + map.get(key));
}
```

#### 2. 遍历 `entrySet`

```java
for (Map.Entry<String, String> entry : map.entrySet()) {
    System.out.println(entry.getKey() + " = " + entry.getValue());
}
```

#### 3. 使用 Lambda 表达式

```java
map.forEach((k, v) -> System.out.println(k + " = " + v));
```

------

### 五、总结

- `Map` 用于存储一一对应的关系，常用于配置、缓存、计数、索引等场景
- 选择哪种 `Map` 实现类要结合**线程安全、顺序要求、性能需求**等综合考虑

------

如果你有具体使用场景，我可以帮你推荐更合适的 `Map` 类型并给出使用示例。是否需要？