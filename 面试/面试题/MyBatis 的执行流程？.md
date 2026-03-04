好的 👍 我来给你整理一道标准的 **面试题答案**，按照“概念 ➝ 原理 ➝ 案例 ➝ 使用场景 ➝ 扩展追问”的答题模板来写：

------

# 🎯 面试题

**MyBatis 的核心组件有哪些？执行 SQL 的流程是怎样的？**

------

## 一、核心组件

1. **SqlSessionFactory**
   - **作用**：生成 `SqlSession`，是 MyBatis 的入口，类似数据库连接池的工厂。
   - **创建方式**：由 `SqlSessionFactoryBuilder` 读取 `mybatis-config.xml` 配置文件创建。
2. **SqlSession**
   - **作用**：核心对象，表示一次数据库会话，负责执行 SQL、获取映射器、管理事务。
   - **特点**：线程不安全，**每次使用必须获取新的对象**。
3. **Mapper 映射器**
   - **作用**：接口绑定 SQL 语句，通过代理模式让开发者直接调用接口方法。
   - **好处**：面向接口编程，不需要自己写 JDBC。
4. **Executor（执行器）**
   - **作用**：真正执行 SQL 的组件，支持一级缓存、二级缓存。
   - **类型**：
     - `SimpleExecutor`：每次执行都会创建新 Statement。
     - `ReuseExecutor`：复用 Statement。
     - `BatchExecutor`：批量执行。
5. **MappedStatement**
   - **作用**：封装 `<mapper.xml>` 中的一条 SQL 语句，包括 SQL、参数映射、返回结果映射等。
6. **Configuration**
   - **作用**：全局配置类，保存 MyBatis 所有配置信息。

------

## 二、SQL 执行流程

📌 **完整流程（以 Mapper 接口调用为例）：**

1. **加载配置**
   - 读取 `mybatis-config.xml`，解析数据库环境、映射文件，生成 `Configuration` 对象。
2. **构建 SqlSessionFactory**
   - 由 `SqlSessionFactoryBuilder` 创建 `SqlSessionFactory`。
3. **获取 SqlSession**
   - 调用 `openSession()`，返回 `SqlSession`。
4. **获取 Mapper 代理对象**
   - 通过 `SqlSession.getMapper(UserMapper.class)`，底层使用 **JDK 动态代理**。
5. **执行 SQL**
   - 调用 `mapper.selectUserById(1)`，MyBatis 会找到对应的 `MappedStatement`，交给 `Executor` 执行。
6. **执行 JDBC 操作**
   - `Executor` 调用 JDBC PreparedStatement，设置参数，发送 SQL 到数据库。
7. **结果映射**
   - `ResultSet` 结果集 → MyBatis 的 `ResultSetHandler` → 映射成 Java 对象返回。

------

## 三、案例

```java
// 1. 获取 SqlSession
SqlSession sqlSession = sqlSessionFactory.openSession();
// 2. 获取 Mapper
UserMapper mapper = sqlSession.getMapper(UserMapper.class);
// 3. 执行 SQL
User user = mapper.selectById(1);
System.out.println(user);
sqlSession.close();
```

------

## 四、使用场景

- 需要灵活 SQL、复杂条件查询的企业项目（如黑马点评、苍穹外卖）
- 避免 JDBC 重复造轮子，支持 ORM + 手写 SQL 的混合模式

------

## 五、扩展追问

1. 为什么 **SqlSession 线程不安全**？
2. MyBatis 的 **一级缓存**和 **二级缓存**分别存放在哪？
3. 为什么 Mapper 接口不用写实现类？代理对象是如何生成的？
4. Executor 的三种实现有何区别？适合什么场景？

------

要不要我帮你把 **扩展追问的参考答案**也写好？这样就能完整形成“标准面试回答 + 深挖问题”了。