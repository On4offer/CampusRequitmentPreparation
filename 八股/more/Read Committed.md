**`READ COMMITTED`（读已提交）** 是数据库事务的常见隔离级别之一，**只允许读取其他事务已经提交的数据**，可以防止**脏读（Dirty Read）**，但仍然可能出现**不可重复读（Non-Repeatable Read）\**和\**幻读（Phantom Read）**。

------

### 一、核心特性

| 特性           | 是否允许     |
| -------------- | ------------ |
| **脏读**       | 否           |
| **不可重复读** | 是           |
| **幻读**       | 是           |
| **并发性能**   | 较好（适中） |

------

### 二、行为描述

- 每次 `SELECT` 查询，**都会看到当前已提交的最新数据**；
- 不会读取正在修改但尚未提交的行；
- 但由于其他事务可能在你两次查询之间提交修改，导致结果不一致（即不可重复读）。

------

### 三、不可重复读示例

```sql
-- 事务 A
START TRANSACTION;
SELECT balance FROM accounts WHERE id = 1;  -- 第一次查询，返回 100

-- 事务 B
START TRANSACTION;
UPDATE accounts SET balance = 200 WHERE id = 1;
COMMIT;

-- 事务 A
SELECT balance FROM accounts WHERE id = 1;  -- 第二次查询，返回 200（值变了）
```

→ 同一行在事务 A 中两次读取结果不同，这就是不可重复读。

------

### 四、设置方式（MySQL）

```sql
SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
```

注意：**MySQL 默认不是这个，而是 `REPEATABLE READ`。**
 但在 **Oracle、SQL Server 中，`READ COMMITTED` 是默认隔离级别**。

------

### 五、对比其他隔离级别

| 隔离级别           | 能否脏读 | 能否不可重复读 | 能否幻读                |
| ------------------ | -------- | -------------- | ----------------------- |
| READ UNCOMMITTED   | 是       | 是             | 是                      |
| **READ COMMITTED** | **否**   | 是             | 是                      |
| REPEATABLE READ    | 否       | 否             | **可能（MySQL中解决）** |
| SERIALIZABLE       | 否       | 否             | 否                      |

------

### 六、适用场景

- 追求一定并发性能，同时避免读取到未提交的数据；
- 业务对“同一条记录在一个事务中读多次是否一致”要求不高；
- 适用于大多数业务系统（特别是 Oracle）。

------

### 七、小结一句话：

> `READ COMMITTED` 可以避免脏读，但不能保证同一事务内两次读到的数据一致，适合性能与一致性平衡要求不高的场景。

------

是否需要我演示 InnoDB 在 `READ COMMITTED` 下如何使用 MVCC 来读取最新已提交数据？