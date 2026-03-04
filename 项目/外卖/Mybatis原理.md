## MyBatis核心原理

### 1. MyBatis整体架构

MyBatis的工作流程可以分为以下几个核心步骤：

```
应用请求 → Mapper接口 → SqlSession → Executor → StatementHandler → ParameterHandler → ResultSetHandler → 数据库
```

### 2. 项目中的具体实现分析

#### 2.1 启动时配置加载

在<mcfile name="SkyApplication.java" path="d:\code\java\sky-take-out\sky-server\src\main\java\com\sky\SkyApplication.java"></mcfile>中：

```java
@SpringBootApplication
@EnableTransactionManagement
public class SkyApplication {
    public static void main(String[] args) {
        SpringApplication.run(SkyApplication.class, args);
    }
}
```

当Spring Boot启动时，MyBatis-Spring-Boot-Starter会自动：
1. 读取<mcfile name="application.yml" path="d:\code\java\sky-take-out\sky-server\src\main\resources\application.yml"></mcfile>中的配置
2. 创建DataSource（Druid连接池）
3. 创建SqlSessionFactory
4. 扫描带有`@Mapper`注解的接口，创建代理对象

#### 2.2 配置文件解析

```yaml
mybatis:
  mapper-locations: classpath:mapper/*.xml  # XML映射文件位置
  type-aliases-package: com.sky.entity      # 实体类别名包
  configuration:
    map-underscore-to-camel-case: true       # 开启驼峰命名转换
```

这些配置会被MyBatis的`Configuration`对象解析和保存。

### 3. SQL执行完整流程

#### 3.1 注解方式SQL执行

以<mcfile name="OrderMapper.java" path="d:\code\java\sky-take-out\sky-server\src\main\java\com\sky\mapper\OrderMapper.java"></mcfile>中的方法为例：

```java
@Select("select * from orders where status = #{status} and order_time < #{orderTime}")
List<Orders> getByStatusAndOrderTimeLT(Integer status, LocalDateTime orderTime);
```

**执行流程：**

1. **Mapper代理创建**
   ```java
   // Spring Boot自动为@Mapper接口创建代理对象
   @Autowired
   private OrderMapper orderMapper; // 实际上是代理对象
   ```

2. **方法调用拦截**
   ```java
   // 在OrderTask.java中调用
   List<Orders> ordersList = orderMapper.getByStatusAndOrderTimeLT(Orders.PENDING_PAYMENT, time);
   ```

3. **SQL解析**
   - MyBatis解析`@Select`注解中的SQL语句
   - 识别参数占位符`#{status}`和`#{orderTime}`

4. **参数绑定**
   - 创建`ParameterMapping`对象
   - 将方法参数映射到SQL占位符

5. **SQL执行**
   - 通过`PreparedStatement`执行SQL
   - 设置参数值

#### 3.2 XML方式SQL执行

以<mcfile name="EmployeeMapper.xml" path="d:\code\java\sky-take-out\sky-server\src\main\resources\mapper\EmployeeMapper.xml"></mcfile>为例：

```xml
<select id="pageQuery" resultType="com.sky.entity.Employee">
    select * from employee
    <where>
        <if test="name != null and name != ''">
            and name like concat('%',#{name},'%')
        </if>
    </where>
    order by create_time desc
</select>
```

**执行流程：**

1. **XML解析**
   - MyBatis启动时解析XML文件
   - 将SQL语句解析为`MappedStatement`对象

2. **动态SQL处理**
   - 解析`<if>`标签
   - 根据参数值动态构建SQL

3. **参数绑定详细过程**

### 4. 参数绑定机制详解

#### 4.1 简单参数绑定

```java
@Select("select * from orders where id = #{id}")
Orders getById(Long id);
```

**参数绑定过程：**
1. MyBatis创建`DefaultParameterHandler`
2. 遍历参数映射：`[{property: 'id', typeHandler: LongTypeHandler}]`
3. 调用`ps.setLong(1, id)`设置参数

#### 4.2 对象参数绑定

以<mcfile name="OrderMapper.xml" path="d:\code\java\sky-take-out\sky-server\src\main\resources\mapper\OrderMapper.xml"></mcfile>中的insert操作为例：

```xml
<insert id="insert" parameterType="Orders" useGeneratedKeys="true" keyProperty="id">
    insert into orders (number, status, user_id, order_time, amount)
    values (#{number}, #{status}, #{userId}, #{orderTime}, #{amount})
</insert>
```

**参数绑定过程：**

1. **参数对象解析**
   ```java
   Orders orders = Orders.builder()
       .number("ORD202312001")
       .status(1)
       .userId(100L)
       .orderTime(LocalDateTime.now())
       .amount(new BigDecimal("58.00"))
       .build();
   ```

2. **属性映射**
   - `#{number}` → `orders.getNumber()`
   - `#{status}` → `orders.getStatus()`
   - `#{userId}` → `orders.getUserId()`
   - `#{orderTime}` → `orders.getOrderTime()`
   - `#{amount}` → `orders.getAmount()`

3. **类型处理**
   - MyBatis根据属性类型选择合适的`TypeHandler`
   - `LocalDateTime` → `LocalDateTimeTypeHandler`
   - `BigDecimal` → `BigDecimalTypeHandler`
   - `Long` → `LongTypeHandler`

#### 4.3 复杂参数绑定

以<mcfile name="EmployeeMapper.xml" path="d:\code\java\sky-take-out\sky-server\src\main\resources\mapper\EmployeeMapper.xml"></mcfile>中的update为例：

```xml
<update id="update" parameterType="Employee">
    update employee
    <set>
        <if test="name != null">name = #{name},</if>
        <if test="username != null">username = #{username},</if>
        <if test="status != null">status = #{status},</if>
    </set>
    where id = #{id}
</update>
```

**动态SQL处理：**

1. **条件判断**
   ```java
   // OGNL表达式解析
   // test="name != null" → employee.getName() != null
   // test="username != null" → employee.getUsername() != null
   ```

2. **SQL动态构建**
   - 如果name不为null：添加`name = #{name},`
   - 如果username不为null：添加`username = #{username},`
   - 最终SQL可能是：`update employee set name = ?, status = ? where id = ?`

### 5. 结果集映射机制

#### 5.1 自动映射

```java
@Select("select id, username, name, phone from employee where id = #{id}")
Employee getById(Long id);
```

**映射过程：**
1. 数据库列名：`id, username, name, phone`
2. Java属性名：`id, username, name, phone`
3. 由于配置了`map-underscore-to-camel-case: true`，下划线会自动转驼峰

#### 5.2 ResultMap映射

以<mcfile name="SetmealMapper.xml" path="d:\code\java\sky-take-out\sky-server\src\main\resources\mapper\SetmealMapper.xml"></mcfile>为例：

```xml
<resultMap id="setmealAndDishMap" type="com.sky.vo.SetmealVO" autoMapping="true">
    <result column="id" property="id"/>
    <collection property="setmealDishes" ofType="SetmealDish">
        <result column="sd_id" property="id"/>
        <result column="setmeal_id" property="setmealId"/>
        <result column="dish_id" property="dishId"/>
    </collection>
</resultMap>
```

**映射过程：**
1. 主表数据映射到`SetmealVO`
2. 从表数据映射到`setmealDishes`集合
3. 列名到属性名的精确映射

### 6. 事务管理

在<mcfile name="SkyApplication.java" path="d:\code\java\sky-take-out\sky-server\src\main\java\com\sky\SkyApplication.java"></mcfile>中启用了事务管理：

```java
@EnableTransactionManagement //开启注解方式的事务管理
```

MyBatis与Spring事务的集成：
1. Spring管理事务边界
2. MyBatis的`SqlSession`与Spring事务同步
3. 事务提交时MyBatis执行缓存操作

### 7. 缓存机制

MyBatis有两级缓存：

#### 7.1 一级缓存（SqlSession级别）
```java
// 同一个SqlSession中，相同查询会从缓存获取
Employee emp1 = employeeMapper.getById(1L);
Employee emp2 = employeeMapper.getById(1L); // 从一级缓存获取
```

#### 7.2 二级缓存（Mapper级别）
需要在XML中配置：
```xml
<mapper namespace="com.sky.mapper.EmployeeMapper">
    <cache/>
</mapper>
```

### 8. 插件机制

项目中使用了PageHelper分页插件：

```xml
<dependency>
    <groupId>com.github.pagehelper</groupId>
    <artifactId>pagehelper-spring-boot-starter</artifactId>
</dependency>
```

**PageHelper工作原理：**
1. 拦截Executor的query方法
2. 修改原始SQL，添加LIMIT语句
3. 执行分页查询
4. 计算总记录数

## 完整的SQL执行时序图

```
1. Controller调用Service方法
   ↓
2. Service调用Mapper方法
   ↓
3. Mapper代理对象拦截方法调用
   ↓
4. SqlSession获取MappedStatement
   ↓
5. Executor执行SQL
   ↓
6. StatementHandler准备Statement
   ↓
7. ParameterHandler设置参数
   ↓
8. 执行SQL查询
   ↓
9. ResultSetHandler处理结果集
   ↓
10. 返回映射后的Java对象
```

## 总结

MyBatis的核心原理可以总结为：

1. **配置解析**：启动时解析XML和注解配置
2. **代理创建**：为Mapper接口创建代理对象
3. **SQL映射**：将方法调用映射到SQL语句
4. **参数绑定**：通过TypeHandler将Java参数转换为JDBC参数
5. **结果映射**：通过ResultMap将JDBC结果集转换为Java对象
6. **插件扩展**：通过拦截器机制提供扩展能力

这个项目很好地展示了MyBatis的各种特性，包括注解和XML混合使用、动态SQL、结果映射、分页插件等，是学习MyBatis原理的很好示例。