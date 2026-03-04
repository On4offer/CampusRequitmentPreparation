## [isNotBlank()](file://cn\hutool\core\text\CharSequenceUtil.java#L19-L19) 方法介绍

### 1. 基本概念
[isNotBlank()](file://cn\hutool\core\text\CharSequenceUtil.java#L19-L19) 是 Hutool 工具库提供的字符串工具方法，用于判断字符串是否不为空且不全为空白字符。

### 2. 所属体系
- **工具库**：Hutool（Java 增强工具包）
- **类**：[cn.hutool.core.util.StrUtil](file://cn\hutool\core\util\StrUtil.java#L11-L43)（实际上是 [CharSequenceUtil](file://cn\hutool\core\text\CharSequenceUtil.java#L13-L231) 的别名）
- **方法签名**：`public static boolean isNotBlank(CharSequence str)`

### 3. 功能作用
[isNotBlank()](file://cn\hutool\core\text\CharSequenceUtil.java#L19-L19) 方法用于：
1. **判断字符串非空**：检查字符串不为 `null`
2. **判断非空字符串**：检查字符串长度大于 0
3. **判断非空白字符**：检查字符串不全为空白字符（空格、制表符、换行符等）

### 4. 方法定义

```java
// StrUtil 类中的实际实现
public static boolean isNotBlank(CharSequence str) {
    return !isBlank(str);
}

// isBlank 的实现
public static boolean isBlank(CharSequence str) {
    int length;
    if (str != null && (length = str.length()) != 0) {
        for(int i = 0; i < length; ++i) {
            // 如果发现任何一个非空白字符，就不是 blank
            if (!Character.isWhitespace(str.charAt(i))) {
                return false;
            }
        }
        return true; // 全是空白字符
    } else {
        return true; // null 或空字符串
    }
}
```


### 5. 在代码中的使用

```java
// 在 queryWithPassThrough 方法中使用
String json = stringRedisTemplate.opsForValue().get(key);

// 判断缓存值是否存在且不为空白
if (StrUtil.isNotBlank(json)) {
    // json 不为 null、不为空字符串、不全为空白字符
    return JSONUtil.toBean(json, type);
}
```


### 6. 判断结果对照表

| 输入值     | [isNotBlank()](file://cn\hutool\core\text\CharSequenceUtil.java#L19-L19) 结果 | 说明           |
| ---------- | ------------------------------------------------------------ | -------------- |
| `null`     | `false`                                                      | null 值        |
| `""`       | `false`                                                      | 空字符串       |
| `" "`      | `false`                                                      | 空格字符       |
| `"\t"`     | `false`                                                      | 制表符         |
| `"\n"`     | `false`                                                      | 换行符         |
| `" \t\n "` | `false`                                                      | 多个空白字符   |
| `"a"`      | `true`                                                       | 非空白字符     |
| `" a "`    | `true`                                                       | 包含非空白字符 |
| `"hello"`  | `true`                                                       | 普通字符串     |
| `"123"`    | `true`                                                       | 数字字符串     |

### 7. 与相关方法对比

| 方法                                                         | null  | ""    | " "   | "abc" | 用途           |
| ------------------------------------------------------------ | ----- | ----- | ----- | ----- | -------------- |
| [isEmpty()](file://cn\hutool\core\text\CharSequenceUtil.java#L23-L23) | true  | true  | false | false | 判断是否为空   |
| [isBlank()](file://cn\hutool\core\text\CharSequenceUtil.java#L19-L19) | true  | true  | true  | false | 判断是否为空白 |
| [isNotEmpty()](file://cn\hutool\core\text\CharSequenceUtil.java#L25-L25) | false | false | true  | true  | 判断是否非空   |
| [isNotBlank()](file://cn\hutool\core\text\CharSequenceUtil.java#L19-L19) | false | false | false | true  | 判断是否非空白 |

### 8. 在缓存逻辑中的作用

```java
public <R,ID> R queryWithPassThrough(...) {
    String json = stringRedisTemplate.opsForValue().get(key);
    
    // 使用 isNotBlank 判断缓存是否有效
    if (StrUtil.isNotBlank(json)) {
        // 只有当 json 真正包含有效数据时才进行反序列化
        return JSONUtil.toBean(json, type);
    }
    
    // 如果 json 为 null、空字符串或全空白字符，则认为缓存未命中
    // 继续执行数据库查询逻辑...
}
```


### 9. 实际应用场景

#### (1) 缓存验证
```java
String cacheData = redisTemplate.opsForValue().get("user:123");
if (StrUtil.isNotBlank(cacheData)) {
    // 缓存有效，直接使用
    User user = JSONUtil.toBean(cacheData, User.class);
}
```


#### (2) 表单验证
```java
String username = request.getParameter("username");
if (StrUtil.isNotBlank(username)) {
    // 用户名有效，继续处理
}
```


#### (3) 配置检查
```java
String configValue = getConfig("api.url");
if (StrUtil.isNotBlank(configValue)) {
    // 配置有效，使用配置值
}
```


### 10. 优势

1. **功能全面**：同时检查 null、空字符串和空白字符
2. **性能优秀**：实现经过优化
3. **使用简单**：一个方法调用解决多种情况
4. **避免异常**：安全处理 null 值
5. **语义清晰**：方法名明确表达意图

### 11. 与传统写法对比

```java
// 传统写法（繁琐且容易出错）
if (json != null && json.length() > 0 && !json.trim().isEmpty()) {
    // 处理逻辑
}

// Hutool 写法（简洁明了）
if (StrUtil.isNotBlank(json)) {
    // 处理逻辑
}
```


### 12. 注意事项

```java
// 正确使用
if (StrUtil.isNotBlank(json)) {
    // json 包含有效数据
}

// 错误理解
if (json != null && StrUtil.isNotBlank(json)) {
    // 多余的 null 检查，isNotBlank 已经包含了 null 检查
}
```


这是 Hutool 工具库中最常用的字符串验证方法之一，在实际开发中能大大提高代码的健壮性和可读性。