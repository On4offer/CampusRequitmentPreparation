# BeanToMap 底层转换原理

## 核心调用链

```
public static Map<String, Object> beanToMap(Object bean, Map<String, Object> targetMap, CopyOptions copyOptions) {
    return null == bean ? null : (Map)BeanCopier.create(bean, targetMap, copyOptions).copy();
}
```

## BeanCopier 工作原理

BeanCopier 是 Hutool 工具库中的核心类，其工作流程如下：

### (1) 创建阶段 - create 方法

```
BeanCopier.create(bean, targetMap, copyOptions)
```

- 分析源对象（UserDTO）的类结构，获取所有 getter 方法
- 分析目标 Map 的结构
- 根据 CopyOptions 配置创建转换策略
- 构建属性映射关系（属性名 → getter方法）

### (2) 复制阶段 - copy 方法

```
.copy()
```

- 遍历源对象的所有属性
- 通过反射调用 getter 方法获取属性值
- 根据 CopyOptions 规则处理属性值
- 将属性名作为 key，属性值作为 value 放入目标 Map

## 具体转换过程

以 UserDTO 为例：

```
// UserDTO 对象
public class UserDTO {
    private Long id;        // getId() → 1L
    private String phone;   // getPhone() → "13812345678"
    private String nickName;// getNickName() → "user123"
    
    // getters and setters...
}
```

转换过程：

```
1. 反射获取 UserDTO.class 的所有方法
2. 筛选出 getter 方法：getId(), getPhone(), getNickName()
3. 通过方法名推导属性名：id, phone, nickName
4. 调用 getter 方法获取值：1L, "13812345678", "user123"
5. 应用 CopyOptions 规则处理值
6. 放入 Map：{"id" → "1", "phone" → "13812345678", "nickName" → "user123"}
```

## CopyOptions 的作用

在我的代码中：

```
CopyOptions.create()
    .setIgnoreNullValue(true)                    // 忽略 null 值
    .setFieldValueEditor((fieldName, fieldValue) -> fieldValue.toString())  // 转为字符串
```

处理规则：
- 忽略 null：如果某个属性值为 null，则不放入 Map
- 值转换：将所有属性值转换为字符串形式存储

性能优化

- Hutool 的 BeanCopier 采用了以下优化：
- 缓存机制：对相同类型的转换会缓存转换器，避免重复分析
- 反射优化：使用 MethodHandle 或缓存 Method 提高反射性能
- 直接赋值：避免不必要的包装和解包操作

这种设计使得 Bean 到 Map 的转换既灵活又高效，特别适合用于将 Java 对象序列化到 Redis 等键值存储系统中。