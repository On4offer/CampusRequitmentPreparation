# MySQL 全体系学习与面试通关目录

## 一、MySQL 基础认知（入门必学，建立整体框架）

### 1.1 数据库基础概念

- 数据库 / 数据库管理系统 (DBMS) 的定义与分类（关系型 vs 非关系型）
- MySQL 的定位、版本差异（5.7 vs 8.0 核心区别）、应用场景
- 数据库核心概念：库、表、行、列、索引、主键 / 外键、约束（主键 / 唯一 / 非空 / 默认 / 外键）

### 1.2 MySQL 环境搭建与基础操作

- 本地 / 服务器安装 MySQL（Windows/Linux）、配置文件（my.cnf/my.ini）核心参数
- 客户端工具使用（Navicat/DBeaver/MySQL Workbench / 命令行）
- 基础命令：登录 / 退出、库操作（CREATE/DROP/USE）、表操作（查看表结构 DESC、修改表 ALTER）

## 二、MySQL 核心架构与底层原理（面试高频原理考点）

### 2.1 MySQL 整体架构分层（核心考点）

- 连接层：连接器（用户认证、连接管理）、线程池
- 服务层：查询缓存（8.0 已移除）、解析器（语法解析）、优化器（执行计划生成）、执行器
- 存储引擎层：插件式架构、与服务层的交互逻辑
- 存储层：文件系统、数据文件的存储方式

### 2.2 存储引擎（面试重中之重）

- 存储引擎的作用与选型依据
- InnoDB（默认）：核心特性（事务支持、行锁、MVCC、聚簇索引、缓冲池）、适用场景
- MyISAM：特性（表锁、不支持事务、全文索引）、适用场景
- 其他引擎：Memory（内存引擎）、Archive（归档引擎）、NDB（集群引擎）
- 不同引擎对比（锁粒度、事务、索引、崩溃恢复）、引擎切换方法

### 2.3 MySQL 数据存储原理

- 数据类型底层存储（int/varchar/date/blob 等）
- 表空间（系统表空间、独立表空间、临时表空间）
- 数据文件结构（.ibd/.frm/.MYD/.MYI）
- 页 / 区 / 段的存储逻辑（InnoDB 最小存储单元）

## 三、SQL 语法全掌握（基础 + 进阶，面试必测）

### 3.1 SQL 分类与基础语法

- DDL（数据定义）：CREATE/ALTER/DROP/TRUNCATE（重点：ALTER TABLE 各类修改）
- DML（数据操作）：INSERT/UPDATE/DELETE/REPLACE（批量插入、ON DUPLICATE KEY UPDATE）
- DQL（数据查询）：SELECT 基础（WHERE/GROUP BY/HAVING/ORDER BY/LIMIT）
- DCL（数据控制）：GRANT/REVOKE/COMMIT/ROLLBACK（权限管理、事务控制）
- TCL（事务控制）：START TRANSACTION/SAVEPOINT（事务基础）

### 3.2 高级查询语法（面试高频）

- 联表查询：INNER JOIN/LEFT JOIN/RIGHT JOIN/CROSS JOIN（笛卡尔积、NULL 值处理）
- 子查询：相关子查询 / 非相关子查询、EXISTS/IN（性能对比）
- 集合操作：UNION/UNION ALL/INTERSECT/EXCEPT
- 条件函数：IF/CASE WHEN/COALESCE/NULLIF（空值处理）
- 聚合函数：SUM/AVG/COUNT/MIN/MAX（COUNT (*) vs COUNT (1) vs COUNT (字段)）

### 3.3 窗口函数（面试核心难点）

- 窗口函数与聚合函数的区别（分组不聚合、保留原始行）

- 窗口函数语法：OVER () 子句（PARTITION BY/ORDER BY/ROWS/RANGE）

- 分类窗口函数：

  - 排序类：ROW_NUMBER ()/RANK ()/DENSE_RANK ()/NTILE ()（经典场景：TopN、排名）
  - 偏移类：LAG ()/LEAD ()/FIRST_VALUE ()/LAST_VALUE ()（经典场景：前后行数据对比）
  - 聚合类：SUM ()/AVG () OVER ()（累计求和 / 滑动窗口）

  

- 窗口函数实战场景（面试真题：连续登录、分组 Top3、同比环比）

### 3.4 其他高频 SQL 语法

- 正则表达式：REGEXP（模糊匹配）
- 公用表表达式（CTE）：WITH 子句（递归 CTE：层级查询，如部门树）
- 变量使用：@变量名（自定义变量实现复杂逻辑）
- 批量操作：LOAD DATA INFILE（大数据导入）

## 四、索引原理与优化（面试核心，占比最高）

### 4.1 索引基础

- 索引的定义、作用（加速查询、降低 IO）、代价（增删改变慢、占用空间）

- 索引分类：

  - 按数据结构：B + 树索引（核心）、哈希索引、全文索引、R 树索引
  - 按物理存储：聚簇索引（主键）、非聚簇索引（二级索引）
  - 按功能：主键索引 / 唯一索引 / 普通索引 / 组合索引 / 前缀索引

  

- 索引失效场景（面试必问）：like % xxx、函数操作字段、类型转换、OR 条件、不符合最左前缀

### 4.2 索引设计与优化

- 组合索引的最左前缀原则
- 索引设计原则（适合查询、避免冗余、控制数量）
- 慢查询优化：EXPLAIN 执行计划（type/key/rows/extra 字段解读）
- 覆盖索引、回表、索引下推（ICP）、MRR/BKA（优化器特性）

### 4.3 索引维护

- 索引创建 / 删除 / 修改（ALTER TABLE ADD INDEX）
- 索引碎片整理（OPTIMIZE TABLE）
- 索引分析（SHOW INDEX、ANALYZE TABLE）

## 五、事务与锁（面试核心原理）

### 5.1 事务基础

- 事务的 ACID 特性（原子性 / 一致性 / 隔离性 / 持久性）
- 事务的实现原理：redo log（重做日志）、undo log（回滚日志）
- 事务的提交与回滚机制

### 5.2 事务隔离级别（面试必问）

- 四种隔离级别：READ UNCOMMITTED/READ COMMITTED/REPEATABLE READ/SERIALIZABLE
- 不同隔离级别解决的问题：脏读 / 不可重复读 / 幻读
- InnoDB 默认隔离级别（REPEATABLE READ）的实现（MVCC 多版本并发控制）

### 5.3 锁机制

- 锁的分类：
  - 按粒度：行锁 / 表锁 / 页锁
  - 按类型：共享锁（S）/ 排他锁（X）
  - 特殊锁：意向锁（IS/IX）、间隙锁（Gap Lock）、临键锁（Next-Key Lock）
- 死锁的产生原因、检测与解决（SHOW ENGINE INNODB STATUS）
- 锁等待与超时配置（innodb_lock_wait_timeout）

## 六、MySQL 性能优化（工程实践 + 面试）

### 6.1 服务器参数优化

- 内存相关：innodb_buffer_pool_size（核心）、key_buffer_size、sort_buffer_size
- IO 相关：innodb_flush_log_at_trx_commit、sync_binlog
- 连接相关：max_connections、wait_timeout
- 8.0 新特性参数（如 innodb_dedicated_server）

### 6.2 SQL 语句优化

- 慢查询日志（slow_query_log）开启与分析
- 避免全表扫描、优化子查询、合理使用 JOIN
- 分页优化（超大分页：LIMIT 偏移量大的问题）
- 批量操作优化（减少事务次数、禁用自动提交）

### 6.3 架构层面优化

- 读写分离（主从复制）：主库写、从库读，复制原理（binlog/relay log/io_thread/sql_thread）
- 分库分表：垂直分表 / 水平分表、分库分表中间件（Sharding-JDBC）
- 缓存优化：Redis 缓存热点数据（缓存穿透 / 击穿 / 雪崩）
- 索引优化（复用四、4.2 内容）

## 七、MySQL 运维与故障处理（面试拓展）

### 7.1 备份与恢复

- 备份类型：物理备份（mysqldump）、逻辑备份（xtrabackup）
- 全量备份 / 增量备份 / 差异备份
- 数据恢复：基于时间点恢复（binlog）、基于备份文件恢复

### 7.2 故障排查

- 常见故障：连接数满、死锁、磁盘满、复制延迟
- 日志分析：error log/binlog/redo log/undo log/slow log
- 性能监控：SHOW STATUS/SHOW PROCESSLIST/INFORMATION_SCHEMA

### 7.3 高可用架构

- 主从复制（异步 / 半同步 / 全同步）
- MGR（MySQL Group Replication）
- 哨兵 / Proxy 中间件（ProxySQL/MaxScale）

## 八、面试高频专题（针对性复习）

### 8.1 原理类高频题

- MySQL 架构分层及各层作用
- InnoDB vs MyISAM 核心区别
- 事务 ACID 的实现原理
- MVCC 的实现机制（undo log + 事务 ID + Read View）
- 索引失效的场景及原因
- 间隙锁的作用及产生场景

### 8.2 SQL 实战类高频题

- 窗口函数实现分组 TopN
- 连续登录 / 连续打卡问题
- 行列转换（PIVOT/UNPIVOT）
- 层级查询（递归 CTE 实现部门树）
- 慢 SQL 优化案例分析

### 8.3 性能优化类高频题

- 一条慢 SQL 的优化思路（从 EXPLAIN 到索引调整）
- 主从复制延迟的原因及解决
- 分库分表的设计思路与痛点
- 大表优化方案（分区表 / 分表 / 索引优化）

------

### 总结

1. 学习核心逻辑：先掌握**基础架构与原理**（二、五），再吃透**SQL 语法（尤其是窗口函数）**（三），最后聚焦**索引与性能优化**（四、六），这三部分是面试考察的核心。
2. 重点突破方向：InnoDB 引擎特性、事务隔离级别 + MVCC、索引原理（B + 树）、窗口函数实战、慢 SQL 优化，这 5 个点是面试高频且易拉开差距的内容。
3. 学习方法：按目录逐层学习，每学完一个模块结合「理论 + SQL 实战 + 面试题」巩固，比如学完窗口函数立刻刷 TopN、连续登录等经典真题，避免 “只记不练”。