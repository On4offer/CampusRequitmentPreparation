# HashMap的遍历方式有哪些？各有什么特点？

## 一、HashMap 遍历方式总览

HashMap 提供了多种遍历方式，每种方式都有其特点和适用场景：

| 遍历方式 | 遍历对象 | 特点 | 性能 | 适用场景 |
|---------|---------|------|------|---------|
| KeySet 遍历 | Key | 只遍历键 | 一般 | 只需要键 |
| Values 遍历 | Value | 只遍历值 | 一般 | 只需要值 |
| EntrySet 遍历 | Entry | 遍历键值对 | 最优 | 需要键和值 |
| Lambda 遍历 | Entry/Key/Value | JDK8+，简洁 | 较优 | 简洁代码 |
| Iterator 遍历 | Entry | 可安全删除 | 较优 | 需要删除元素 |

## 二、KeySet 遍历

### 2.1 增强for循环遍历KeySet

```java
Map<String, Integer> map = new HashMap<>();
map.put("张三", 25);
map.put("李四", 30);
map.put("王五", 28);

for (String key : map.keySet()) {
    System.out.println("姓名：" + key + "，年龄：" + map.get(key));
}
```

**特点**：
- 代码简洁
- 每次需要调用 `map.get(key)` 获取值
- 遍历过程中删除元素会抛出 `ConcurrentModificationException`

### 2.2 Iterator 遍历KeySet

```java
Iterator<String> iterator = map.keySet().iterator();
while (iterator.hasNext()) {
    String key = iterator.next();
    System.out.println("姓名：" + key + "，年龄：" + map.get(key));
}
```

**特点**：
- 可以安全删除元素
- 仍然需要调用 `map.get(key)` 获取值

## 三、Values 遍历

### 3.1 增强for循环遍历Values

```java
for (Integer value : map.values()) {
    System.out.println("年龄：" + value);
}
```

**特点**：
- 只能遍历值，无法获取对应的键
- 代码简洁
- 适用于只需要值的场景

### 3.2 Iterator 遍历Values

```java
Iterator<Integer> iterator = map.values().iterator();
while (iterator.hasNext()) {
    Integer value = iterator.next();
    System.out.println("年龄：" + value);
    iterator.remove();  // 可以安全删除
}
```

**特点**：
- 可以安全删除元素
- 只能获取值，无法获取键

## 四、EntrySet 遍历（推荐）

### 4.1 增强for循环遍历EntrySet

```java
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    System.out.println("姓名：" + entry.getKey() + "，年龄：" + entry.getValue());
}
```

**特点**：
- **性能最优**：一次遍历同时获取键和值
- 代码简洁
- 遍历过程中删除元素会抛出异常

### 4.2 Iterator 遍历EntrySet

```java
Iterator<Map.Entry<String, Integer>> iterator = map.entrySet().iterator();
while (iterator.hasNext()) {
    Map.Entry<String, Integer> entry = iterator.next();
    System.out.println("姓名：" + entry.getKey() + "，年龄：" + entry.getValue());
    
    if (entry.getValue() > 28) {
        iterator.remove();  // 安全删除
    }
}
```

**特点**：
- 性能最优
- 可以安全删除元素
- 推荐在需要删除元素时使用

## 五、Lambda 遍历（JDK8+）

### 5.1 forEach 遍历

```java
map.forEach((key, value) -> {
    System.out.println("姓名：" + key + "，年龄：" + value);
});
```

**特点**：
- 代码最简洁
- 内部实现使用 EntrySet 遍历
- 性能与 EntrySet 相当
- 无法在遍历中删除元素

### 5.2 Stream 遍历

```java
map.entrySet().stream()
    .filter(entry -> entry.getValue() > 25)
    .forEach(entry -> {
        System.out.println("姓名：" + entry.getKey() + "，年龄：" + entry.getValue());
    });
```

**特点**：
- 支持过滤、映射等操作
- 适合复杂的数据处理
- 性能略低于直接遍历

## 六、性能对比

### 6.1 性能测试代码

```java
Map<String, Integer> map = new HashMap<>();
for (int i = 0; i < 100000; i++) {
    map.put("key" + i, i);
}

long start, end;

// KeySet 遍历
start = System.currentTimeMillis();
for (String key : map.keySet()) {
    int value = map.get(key);
}
end = System.currentTimeMillis();
System.out.println("KeySet: " + (end - start) + "ms");

// EntrySet 遍历
start = System.currentTimeMillis();
for (Map.Entry<String, Integer> entry : map.entrySet()) {
    String key = entry.getKey();
    int value = entry.getValue();
}
end = System.currentTimeMillis();
System.out.println("EntrySet: " + (end - start) + "ms");

// Lambda 遍历
start = System.currentTimeMillis();
map.forEach((key, value) -> {});
end = System.currentTimeMillis();
System.out.println("Lambda: " + (end - start) + "ms");
```

### 6.2 性能测试结果

| 遍历方式 | 10万条数据耗时 | 相对性能 |
|---------|---------------|---------|
| KeySet | ~15ms | 基准 |
| EntrySet | ~10ms | 最快 |
| Lambda | ~12ms | 接近EntrySet |

**结论**：EntrySet 性能最优，因为它一次遍历同时获取键和值，避免了额外的 `get()` 调用。

## 七、遍历过程中的删除操作

### 7.1 错误的删除方式

```java
for (String key : map.keySet()) {
    if (map.get(key) > 28) {
        map.remove(key);  // ConcurrentModificationException
    }
}
```

### 7.2 正确的删除方式

```java
// 方式1：使用 Iterator
Iterator<Map.Entry<String, Integer>> iterator = map.entrySet().iterator();
while (iterator.hasNext()) {
    Map.Entry<String, Integer> entry = iterator.next();
    if (entry.getValue() > 28) {
        iterator.remove();  // 安全删除
    }
}

// 方式2：使用 removeIf（JDK8+）
map.entrySet().removeIf(entry -> entry.getValue() > 28);

// 方式3：使用 Stream 过滤（创建新Map）
Map<String, Integer> filteredMap = map.entrySet().stream()
    .filter(entry -> entry.getValue() <= 28)
    .collect(Collectors.toMap(Map.Entry::getKey, Map.Entry::getValue));
```

## 八、医疗美容系统应用场景

### 8.1 场景1：遍历用户信息

```java
Map<String, UserInfo> userMap = userService.getAllUsers();

// 推荐：EntrySet 遍历
for (Map.Entry<String, UserInfo> entry : userMap.entrySet()) {
    String userId = entry.getKey();
    UserInfo user = entry.getValue();
    
    if (user.getAge() < 18) {
        System.out.println("未成年用户：" + user.getName());
    }
}
```

### 8.2 场景2：遍历并删除过期预约

```java
Map<String, Appointment> appointmentMap = appointmentService.getAllAppointments();

// 推荐：Iterator 遍历并删除
Iterator<Map.Entry<String, Appointment>> iterator = 
    appointmentMap.entrySet().iterator();
while (iterator.hasNext()) {
    Map.Entry<String, Appointment> entry = iterator.next();
    if (entry.getValue().getAppointmentTime().isBefore(LocalDateTime.now())) {
        iterator.remove();  // 删除过期预约
    }
}
```

### 8.3 场景3：统计美容项目数量

```java
Map<String, Integer> projectCount = new HashMap<>();
projectCount.put("面部护理", 120);
projectCount.put("身体护理", 80);
projectCount.put("美甲", 200);

// 推荐：Values 遍历
int totalCount = 0;
for (Integer count : projectCount.values()) {
    totalCount += count;
}
System.out.println("总项目数：" + totalCount);
```

## 九、面试标准回答（1分钟）

「HashMap 有多种遍历方式：KeySet 遍历键，Values 遍历值，EntrySet 遍历键值对。EntrySet 性能最优，因为它一次遍历同时获取键和值。JDK8+ 可以使用 Lambda 表达式遍历，代码更简洁。如果需要在遍历中删除元素，应该使用 Iterator 或 removeIf 方法。在医疗美容系统中，遍历用户信息用 EntrySet，统计项目数量用 Values，删除过期预约用 Iterator。」

## 十、常见追问

**Q1：为什么 EntrySet 比 KeySet 性能好？**

EntrySet 一次遍历获取键和值，KeySet 需要额外调用 `get()` 方法，增加了哈希查找开销。

**Q2：Lambda 遍历的性能如何？**

Lambda 内部使用 EntrySet 遍历，性能与 EntrySet 相当，但代码更简洁。

**Q3：遍历时删除元素为什么会抛出异常？**

HashMap 使用 `modCount` 记录修改次数，遍历时检查 `modCount` 是否变化，变化则抛出 `ConcurrentModificationException`。

**Q4：如何选择合适的遍历方式？**

- 需要键和值：EntrySet
- 只需要键：KeySet
- 只需要值：Values
- 需要删除：Iterator 或 removeIf
- 追求简洁：Lambda

## 十一、小结表

| 遍历方式 | 获取内容 | 性能 | 可删除 | 代码简洁度 |
|---------|---------|------|--------|-----------|
| KeySet | Key | 一般 | Iterator可 | 一般 |
| Values | Value | 一般 | Iterator可 | 一般 |
| EntrySet | Key+Value | 最优 | Iterator可 | 一般 |
| Lambda | Key+Value | 较优 | 不可 | 最简洁 |
| Stream | Key+Value | 较差 | 不可 | 简洁 |
