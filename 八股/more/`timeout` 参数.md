Spring 的 `@Transactional` 注解中的 `**timeout**` 参数用于**设置事务的超时时间（单位：秒）**，意思是：

> **如果事务在规定时间内没有完成，将自动回滚事务，避免长期占用资源，造成数据库死锁或性能问题。**

------

## 一、基本用法

```java
@Transactional(timeout = 5)
public void process() {
    // 如果方法在5秒内没执行完，事务将回滚
}
```

- 表示该事务最多只能运行 **5 秒**；
- 超过时间会抛出 `TransactionTimedOutException`；
- 默认值是 `-1`，表示 **永不超时**。

------

## 二、常见应用场景

| 场景                             | 原因                       |
| -------------------------------- | -------------------------- |
| 复杂 SQL 查询或批量更新          | 防止长事务阻塞数据库       |
| 与远程调用或慢服务交互           | 控制事务边界，避免等待过久 |
| 高并发系统，控制连接资源占用时间 | 避免连接池耗尽或死锁       |

------

## 三、事务超时的触发机制

Spring 会在开启事务时，**将超时参数传给底层事务管理器**（如 JDBC、JPA），由数据库连接或事务管理器负责监控。

如果在超时时间内未提交：

- 事务被标记为回滚状态；
- 在方法结束或异常时被强制回滚。

------

## 四、与数据库设置的区别

- `@Transactional(timeout = x)` 是**应用级别控制**；
- 数据库如 MySQL 的 `innodb_lock_wait_timeout` 是 **数据库内部锁等待超时设置**；
- 二者可同时配合使用，但作用层次不同。

------

## 五、注意事项

1. **timeout 不是强中断机制**，而是事务管理器**在超时后标记为“需回滚”**；
2. 如果事务中执行了 IO 阻塞或远程调用（如 `Thread.sleep`、网络请求），Spring 无法主动打断线程；
3. 不同事务管理器（如 JtaTransactionManager、DataSourceTransactionManager）支持程度略有差异。

------

## 六、配合其他参数使用示例：

```java
@Transactional(
    propagation = Propagation.REQUIRED,
    isolation = Isolation.READ_COMMITTED,
    timeout = 10,
    rollbackFor = Exception.class
)
public void doWork() {
    // 最多执行 10 秒，否则回滚
}
```

------

## 总结一句话：

> **`timeout` 是为了防止事务执行时间过长而设置的“保险机制”，它控制事务最多运行多长时间，超时会自动回滚，保护数据库资源不被长时间占用。**

如你需要，我可以为你绘制一张“事务超时处理流程图”，是否需要？