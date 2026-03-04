好的 ✅ 这道题考察 **MyBatis-Plus 的查询构造器 Wrapper**，很多面试官会追问其底层实现。我帮你整理一份八股文标准答题模板：

------

# 🎯 面试题

**MyBatis-Plus 中的 Wrapper 条件构造器是如何实现的？**

------

## 一、概念

- **Wrapper 条件构造器**：MyBatis-Plus 提供的一套 **链式条件构造器**，用于动态生成 SQL 条件，避免硬编码 SQL。
- 常见实现类：
  - `QueryWrapper<T>`：普通条件构造器。
  - `UpdateWrapper<T>`：更新条件构造器。
  - `LambdaQueryWrapper<T>`：基于 Lambda 表达式，避免硬编码字段名。
  - `LambdaUpdateWrapper<T>`：更新时的 Lambda 写法。

------

## 二、原理

1. **链式调用（Builder 模式）**
   - Wrapper 内部维护一个 `children` 条件列表（List），每次调用 `eq() / like() / in()` 等方法时，往集合中添加一个条件对象。
   - 通过 **链式调用** 组合多个条件，最后统一拼接成 SQL。
2. **条件封装（AbstractWrapper）**
   - `AbstractWrapper` 是核心父类，内部维护：
     - `entity`：实体对象。
     - `paramNameValuePairs`：参数映射。
     - `expression`：条件表达式对象。
   - 每次调用条件方法，都会往 `expression` 中追加 SQL 片段。
3. **Lambda 表达式实现**
   - `LambdaQueryWrapper` 使用 **序列化的 Lambda 表达式**，通过反射获取字段名，避免写字符串。
   - 底层通过 `SerializedLambda` 解析 `User::getName`，得到 `name` 字段。
4. **最终 SQL 拼接**
   - 执行 Mapper 方法时，Wrapper 会被传递给 **`SqlInjector`**。
   - `SqlInjector` 使用 `Wrapper.getSqlSegment()` 拼接动态 SQL。
   - 参数由 `Wrapper.getParamNameValuePairs()` 提供，交给 MyBatis `#{}` 占位符绑定。

------

## 三、案例

### 普通写法

```java
QueryWrapper<User> wrapper = new QueryWrapper<>();
wrapper.eq("age", 18).like("name", "Tom");
List<User> list = userMapper.selectList(wrapper);
```

生成 SQL：

```sql
SELECT * FROM user WHERE age = ? AND name LIKE ?
```

### Lambda 写法

```java
LambdaQueryWrapper<User> wrapper = new LambdaQueryWrapper<>();
wrapper.eq(User::getAge, 18).like(User::getName, "Tom");
List<User> list = userMapper.selectList(wrapper);
```

好处：**避免字段名硬编码**，更安全。

------

## 四、使用场景

- **黑马点评项目**：用户搜索点评时动态拼接条件（城市、评分、标签）。
- **苍穹外卖项目**：后台管理系统中按菜品分类、状态、价格范围动态查询。
- 动态条件拼接（用户可选条件 → 自动构造 SQL），避免写复杂 if 判断和拼接字符串。

------

## 五、面试模板（标准作答）

> MyBatis-Plus 的 Wrapper 条件构造器通过 **Builder 模式 + 表达式封装** 实现。
>
> 每次调用 `eq()`、`like()` 等方法，都会在内部的 `expression` 列表中追加一个 SQL 片段，最终由 `getSqlSegment()` 方法统一拼接成 SQL。
>
> `LambdaQueryWrapper` 通过 **序列化 Lambda 表达式解析字段名**，避免硬编码。
>
> 在实际项目中，它主要用于 **动态条件查询**，简化了 XML 编写和字符串拼接 SQL 的繁琐过程。

------

## 六、扩展追问

1. `QueryWrapper` 和 `LambdaQueryWrapper` 的区别？
    👉 前者用字符串表示字段名，后者用 Lambda，避免硬编码。
2. Wrapper 是在 Mapper 方法调用的哪个阶段生效的？
    👉 在 **SqlInjector 生成 SQL** 阶段，Wrapper 会被解析成 SQL 片段并拼接。
3. 如果我在 Wrapper 里拼接了 100 条条件，会不会影响性能？
    👉 解析时有一定开销，但影响不大，最终还是交由数据库优化。
4. Wrapper 如何避免 SQL 注入？
    👉 所有值都使用 `#{}` 预编译参数绑定，不做字符串拼接。

------

要不要我再帮你扩展一题 **“MyBatis-Plus 的分页插件底层原理”**？这个和 Wrapper 一起常常被问。