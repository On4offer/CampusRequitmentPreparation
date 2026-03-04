Spring 的事务管理是其核心特性之一，核心目标是简化事务控制，支持**编程式事务**和**声明式事务**两种核心方式，其中声明式事务因低侵入性成为主流。以下从核心概念、两种实现方式、关键配置和注意事项展开说明：

### 一、核心基础概念

#### 1. 事务的核心属性（ACID）

- 原子性（Atomicity）：事务操作要么全成，要么全回滚；

- 一致性（Consistency）：事务前后数据状态合法；

- 隔离性（Isolation）：多事务并发时互不干扰（Spring 支持读未提交、读已提交、可重复读、串行化）；

- 持久性（Durability）：事务提交后数据永久生效。

#### 2. Spring 事务的核心接口

| 接口                       | 作用                                                         |
| -------------------------- | ------------------------------------------------------------ |
| PlatformTransactionManager | 事务管理器核心接口（不同数据源实现不同：如DataSourceTransactionManager用于 JDBC/MyBatis，JpaTransactionManager用于 JPA） |
| TransactionDefinition      | 定义事务属性（隔离级别、传播行为、超时时间、是否只读等）     |
| TransactionStatus          | 事务运行状态（是否新事务、是否回滚、是否完成等）             |

#### 3. 关键属性：事务传播行为（重点）

描述**嵌套调用方法时事务的传递规则**，常用值：

- REQUIRED（默认）：如果当前有事务则加入，无则新建；

- REQUIRES_NEW：无论当前是否有事务，都新建事务（原有事务挂起）；

- SUPPORTS：有事务则加入，无则以非事务执行；

- NOT_SUPPORTED：以非事务执行，原有事务挂起；

- NEVER：必须无事务，否则抛异常；

- NESTED：嵌套事务（基于保存点，外层回滚则内层也回滚，内层回滚不影响外层）。

### 二、方式 1：编程式事务（手动控制）

通过编码直接操作事务管理器，灵活性高但侵入性强，适合复杂事务场景。

#### 实现方式

##### （1）基础方式：直接使用TransactionTemplate（推荐）

```
@Service
public class UserService {
    @Autowired
    private TransactionTemplate transactionTemplate;
    @Autowired
    private UserMapper userMapper;

    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // 执行事务逻辑
        transactionTemplate.execute(status -> {
            try {
                // 扣减转出方余额
                userMapper.decreaseBalance(fromId, amount);
                // 增加转入方余额
                userMapper.increaseBalance(toId, amount);
                // 模拟异常：触发回滚
                if (amount.compareTo(new BigDecimal("1000")) > 0) {
                    throw new RuntimeException("金额超限，回滚");
                }
                return true;
            } catch (Exception e) {
                // 手动标记回滚
                status.setRollbackOnly();
                throw new RuntimeException("转账失败", e);
            }
        });
    }
}
```

##### （2）底层方式：手动获取 / 提交 / 回滚事务

```
@Service
public class UserService {
    @Autowired
    private PlatformTransactionManager transactionManager;
    @Autowired
    private TransactionDefinition transactionDefinition;
    @Autowired
    private UserMapper userMapper;

    public void transfer(Long fromId, Long toId, BigDecimal amount) {
        // 1. 获取事务状态
        TransactionStatus status = transactionManager.getTransaction(transactionDefinition);
        try {
            userMapper.decreaseBalance(fromId, amount);
            userMapper.increaseBalance(toId, amount);
            // 2. 提交事务
            transactionManager.commit(status);
        } catch (Exception e) {
            // 3. 回滚事务
            transactionManager.rollback(status);
            throw new RuntimeException("转账失败", e);
        }
    }
}
```

### 三、方式 2：声明式事务（主流）

基于 AOP 实现，通过注解 / XML 配置声明事务规则，无侵入、易维护，是 Spring 事务的首选方式。

#### 核心实现：@Transactional注解

##### （1）基础使用（注解标注在方法 / 类上）

```
@Service
// 类上标注：所有方法默认应用事务规则
@Transactional(rollbackFor = Exception.class)
public class UserService {
    @Autowired
    private UserMapper userMapper;

    // 方法上标注：覆盖类上的配置（细粒度控制）
    @Transactional(
        isolation = Isolation.REPEATABLE_READ, // 隔离级别
        propagation = Propagation.REQUIRED,    // 传播行为
        timeout = 30,                          // 超时时间（秒）
        readOnly = false,                      // 是否只读（查询建议设为true）
        rollbackFor = Exception.class,         // 触发回滚的异常（默认仅RuntimeException）
        noRollbackFor = NullPointerException.class // 不触发回滚的异常
    )
    public void transfer(Long fromId, Long toId, BigDecimal amount) throws Exception {
        userMapper.decreaseBalance(fromId, amount);
        // 任意异常触发回滚（因配置了rollbackFor = Exception.class）
        if (amount.compareTo(new BigDecimal("1000")) > 0) {
            throw new Exception("金额超限");
        }
        userMapper.increaseBalance(toId, amount);
    }

    // 查询方法：只读事务（优化性能）
    @Transactional(readOnly = true)
    public User getUserById(Long id) {
        return userMapper.selectById(id);
    }
}
```

##### （2）XML 配置方式（传统，较少用）

```
<!-- 配置事务管理器 -->
<bean id="transactionManager" class="org.springframework.jdbc.datasource.DataSourceTransactionManager">
    <property name="dataSource" ref="dataSource"/>
</bean>

<!-- 开启事务注解驱动（等同于@EnableTransactionManagement） -->
<tx:annotation-driven transaction-manager="transactionManager"/>

<!-- 或通过AOP配置事务规则（XML声明式） -->
<tx:advice id="txAdvice" transaction-manager="transactionManager">
    <tx:attributes>
        <tx:method name="transfer" propagation="REQUIRED" rollback-for="Exception"/>
        <tx:method name="get*" read-only="true"/>
    </tx:attributes>
</tx:advice>
<aop:config>
    <aop:pointcut id="txPointcut" expression="execution(* com.example.service.*.*(..))"/>
    <aop:advisor advice-ref="txAdvice" pointcut-ref="txPointcut"/>
</aop:config>
```

##### （3）开启注解驱动（核心配置）

Spring Boot 项目：自动开启（无需额外配置）；

Spring XML 项目：需配置<tx:annotation-driven/>；

Spring 注解项目：配置类上添加@EnableTransactionManagement：

```
@Configuration
@EnableTransactionManagement // 开启声明式事务
public class TransactionConfig {
    // 配置事务管理器
    @Bean
    public PlatformTransactionManager transactionManager(DataSource dataSource) {
        return new DataSourceTransactionManager(dataSource);
    }
}
```

### 四、声明式事务的关键注意事项（面试高频）

1. **注解生效条件**：

   - @Transactional 只能标注在**public 方法**上（AOP 基于动态代理，非 public 方法无法拦截）；

   - 避免**内部调用**（如 service 内方法 A 调用本类方法 B，B 的 @Transactional 不生效）：因动态代理仅拦截外部调用，内部调用不走代理；

​		→ 解决方案：注入自身代理对象 / 使用 AopContext.currentProxy () 获取代理。

1. **回滚规则**：

   - 默认仅对RuntimeException和Error回滚，检查型异常（如 Exception）不回滚；

   - 需回滚所有异常：显式配置rollbackFor = Exception.class。

1. **只读事务**：
   - 查询方法建议设readOnly = true：数据库优化（如 MySQL 禁止写操作，提升查询性能）。

1. **事务管理器匹配**：

   - JDBC/MyBatis：DataSourceTransactionManager；

   - JPA/Hibernate：JpaTransactionManager/HibernateTransactionManager；

   - 多数据源：需配置多个事务管理器，通过@Transactional(value = "txManager2")指定。

1. **嵌套事务**：

   - 传播行为NESTED需数据库支持保存点（如 MySQL）；

   - 外层事务回滚，内层也回滚；内层回滚（通过status.setRollbackOnly()），外层可继续提交。

### 五、总结

| 方式       | 优点                 | 缺点               | 适用场景                 |
| ---------- | -------------------- | ------------------ | ------------------------ |
| 编程式事务 | 灵活性高、可复杂控制 | 侵入性强、代码冗余 | 复杂事务（如多步骤判断） |
| 声明式事务 | 无侵入、易维护、简洁 | 灵活性稍弱         | 大部分常规业务场景       |

Spring 事务管理的核心是：**通过事务管理器统一管理事务，声明式事务基于 AOP 简化配置，是主流选择；编程式事务作为补充，应对复杂场景**。面试中需重点掌握@Transactional的使用、传播行为、隔离级别及注解不生效的常见原因。