好的 ✅ 这道题我帮你整理成标准的面试答题模板（概念 ➝ 功能 ➝ 区别 ➝ 案例 ➝ 使用场景 ➝ 扩展追问）：

------

# 🎯 面试题

**MyBatis-Plus 的常见功能有哪些？和 MyBatis 的区别是什么？**

------

## 一、MyBatis-Plus 概念

- **MyBatis-Plus（简称 MP）** 是基于 MyBatis 的增强工具，在 MyBatis 的基础上，只做增强不做改变，简化开发，提高效率。
- 核心思想：**少写代码，快速开发，避免重复造轮子**。

------

## 二、常见功能

1. **CRUD 封装**
   - 内置 `BaseMapper<T>`，单表的增删改查无需写 SQL。
   - 如 `selectById`、`insert`、`updateById`、`deleteById`。
2. **条件构造器**
   - 提供 `QueryWrapper`、`LambdaQueryWrapper`，支持链式调用，避免硬编码 SQL。
3. **分页插件**
   - 内置分页功能，只需配置插件，不需要额外写 `limit` 语句。
4. **自动填充**
   - 字段如 `create_time`、`update_time` 可自动填充。
5. **逻辑删除**
   - 支持逻辑删除，通过注解 `@TableLogic` 标识字段。
6. **多租户插件**
   - 内置多租户 SQL 解析器，自动拼接租户条件。
7. **性能分析 & 乐观锁**
   - 提供 SQL 性能分析插件，支持 `@Version` 乐观锁注解。
8. **代码生成器**
   - 支持一键生成 `Entity`、`Mapper`、`Service`、`Controller`，提高开发效率。

------

## 三、和 MyBatis 的区别

| 对比项    | MyBatis                          | MyBatis-Plus                           |
| --------- | -------------------------------- | -------------------------------------- |
| SQL 编写  | 需要手写 XML/注解                | 内置 CRUD，常见操作无需 SQL            |
| CRUD 操作 | `mapper.xml` 手动维护            | 继承 `BaseMapper` 即可                 |
| 分页支持  | 需要手写分页 SQL                 | 内置分页插件，配置即可                 |
| 插件体系  | 支持自定义插件                   | 内置丰富插件（分页、乐观锁、多租户等） |
| 上手成本  | 相对较高，灵活但繁琐             | 简单易用，适合快速开发                 |
| 适用场景  | 复杂 SQL、多表关联、灵活性要求高 | 单表 CRUD、多租户、多模块快速开发      |

------

## 四、案例示例

```java
// Mapper 接口
public interface UserMapper extends BaseMapper<User> {}

// Service 调用
@Autowired
private UserMapper userMapper;

@Test
public void testSelect() {
    // 1. 简单查询
    User user = userMapper.selectById(1);

    // 2. 条件查询
    List<User> users = userMapper.selectList(
        new QueryWrapper<User>().eq("age", 18)
    );

    // 3. Lambda 写法（避免硬编码字段）
    List<User> users2 = userMapper.selectList(
        new LambdaQueryWrapper<User>().eq(User::getAge, 18)
    );
}
```

------

## 五、使用场景

- **苍穹外卖、黑马点评**这类项目：
  - 用户、订单、菜品、商户等表的增删改查业务繁多 → 使用 MyBatis-Plus 提升效率。
  - 业务核心 SQL（复杂查询、统计分析）仍然使用手写 MyBatis。

------

## 六、扩展追问

1. 如果 MyBatis-Plus 已经封装了 CRUD，为什么还要自己写 SQL？
    👉 复杂业务 SQL（多表 join、聚合统计）仍然需要手写。
2. MyBatis-Plus 的分页插件底层是怎么实现的？
    👉 基于 **拦截器机制**，在执行 SQL 前修改原 SQL，自动拼接 `limit`。
3. 如何解决 MyBatis-Plus 与自定义 SQL 的冲突？
    👉 自定义 SQL 写在 `Mapper.xml`，优先级高于内置方法。

------

要不要我帮你把 **分页插件实现原理** 单独整理成一题？这是面试官经常会顺着追问的点。