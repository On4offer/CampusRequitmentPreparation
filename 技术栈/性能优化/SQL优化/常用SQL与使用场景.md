# 📋 SQL优化 - 常用SQL与使用场景速查

> 日常开发SQL优化、问题排查常用SQL语句与场景速查，配合《学习笔记.md》系统学习使用。

---

## 🚀 快速开始

### 连接MySQL

```bash
# 命令行连接
mysql -u root -p
mysql -u root -p -h localhost -P 3306 database_name

# 常用参数
mysql -u root -p --default-character-set=utf8mb4
mysql -u root -p --execute="SELECT * FROM user LIMIT 5"
mysql -u root -p database_name < script.sql
```

---

## 📊 性能分析SQL速查

### 查看执行计划

```sql
-- 基本执行计划
EXPLAIN SELECT * FROM user WHERE id = 1;

-- 详细执行计划（MySQL 8.0+）
EXPLAIN ANALYZE SELECT * FROM user WHERE id = 1;

-- 格式化输出
EXPLAIN FORMAT=JSON SELECT * FROM user WHERE id = 1;
EXPLAIN FORMAT=TREE SELECT * FROM user WHERE id = 1;
```

### 关键字段解读

| 字段 | 含义 | 优化建议 |
|------|------|----------|
| **type** | 访问类型 | 至少达到`ref`，最好达到`const`或`eq_ref` |
| **possible_keys** | 可能使用的索引 | 为空说明没有可用索引 |
| **key** | 实际使用的索引 | 为空说明索引未使用 |
| **rows** | 扫描行数 | 越小越好 |
| **Extra** | 额外信息 | 避免`Using filesort`和`Using temporary` |

### type字段值（从好到差）

```
system > const > eq_ref > ref > range > index > ALL

system    -- 系统表，只有一行数据
const     -- 主键或唯一索引，最多返回一行
eq_ref    -- 唯一索引扫描，每个索引对应一条记录
ref       -- 非唯一索引扫描，返回匹配的多行
range     -- 范围查询
index     -- 索引全扫描
ALL       -- 全表扫描（最差）
```

---

## 🔍 慢查询分析

### 开启慢查询日志

```sql
-- 查看慢查询配置
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';

-- 开启慢查询日志（临时）
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
SET GLOBAL log_queries_not_using_indexes = 'ON';

-- 查看慢查询日志位置
SHOW VARIABLES LIKE 'slow_query_log_file';
```

### 分析慢查询日志

```bash
# 使用mysqldumpslow分析
mysqldumpslow -s t -t 10 /var/lib/mysql/slow.log

# 参数说明
-s t  # 按查询时间排序
-s l  # 按锁定时间排序
-s r  # 按返回记录数排序
-s c  # 按访问次数排序
-t 10 # 显示前10条

# 使用pt-query-digest分析（Percona Toolkit）
pt-query-digest /var/lib/mysql/slow.log
```

### 查看当前正在执行的慢查询

```sql
-- 查看当前执行的查询
SHOW PROCESSLIST;
SELECT * FROM information_schema.PROCESSLIST WHERE TIME > 10;

-- 查看正在执行的查询（MySQL 5.7+）
SELECT * FROM performance_schema.threads WHERE NAME LIKE '%sql%';
```

---

## 🔧 索引相关SQL

### 查看索引

```sql
-- 查看表的所有索引
SHOW INDEX FROM table_name;
SHOW INDEX FROM table_name FROM database_name;

-- 从information_schema查看
SELECT * FROM information_schema.STATISTICS 
WHERE TABLE_NAME = 'table_name' AND TABLE_SCHEMA = 'database_name';
```

### 创建索引

```sql
-- 创建普通索引
CREATE INDEX idx_name ON table_name(column_name);

-- 创建唯一索引
CREATE UNIQUE INDEX idx_unique_name ON table_name(column_name);

-- 创建联合索引
CREATE INDEX idx_composite ON table_name(col1, col2, col3);

-- 创建前缀索引（字符串列）
CREATE INDEX idx_prefix ON table_name(column_name(10));

-- 创建函数索引（MySQL 8.0.13+）
CREATE INDEX idx_func ON table_name((UPPER(column_name)));

-- 创建降序索引（MySQL 8.0+）
CREATE INDEX idx_desc ON table_name(column_name DESC);
```

### 删除索引

```sql
-- 删除索引
DROP INDEX idx_name ON table_name;
ALTER TABLE table_name DROP INDEX idx_name;

-- 查看索引使用情况（MySQL 5.7+）
SELECT 
    OBJECT_SCHEMA AS database_name,
    OBJECT_NAME AS table_name,
    INDEX_NAME,
    COUNT_STAR AS times_used
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE INDEX_NAME IS NOT NULL
AND OBJECT_SCHEMA = 'database_name'
ORDER BY COUNT_STAR DESC;

-- 查看未使用的索引
SELECT 
    OBJECT_SCHEMA AS database_name,
    OBJECT_NAME AS table_name,
    INDEX_NAME
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE INDEX_NAME IS NOT NULL
AND COUNT_STAR = 0
AND OBJECT_SCHEMA = 'database_name';
```

### 索引维护

```sql
-- 分析表（更新统计信息）
ANALYZE TABLE table_name;

-- 优化表（整理碎片）
OPTIMIZE TABLE table_name;

-- 查看表碎片
SELECT 
    table_name,
    data_free / 1024 / 1024 AS fragment_size_mb
FROM information_schema.tables
WHERE table_schema = 'database_name'
AND data_free > 0;
```

---

## 📈 性能监控SQL

### 查看数据库状态

```sql
-- 查看数据库状态变量
SHOW STATUS;
SHOW GLOBAL STATUS;

-- 查看特定状态变量
SHOW STATUS LIKE 'Com_%';        -- 各种SQL执行次数
SHOW STATUS LIKE 'Innodb_%';     -- InnoDB相关状态
SHOW STATUS LIKE 'Threads_%';    -- 线程相关状态
SHOW STATUS LIKE 'Connections';  -- 连接数
SHOW STATUS LIKE 'Slow_queries'; -- 慢查询次数
```

### 关键性能指标

```sql
-- QPS（每秒查询数）
SHOW GLOBAL STATUS LIKE 'Queries';

-- TPS（每秒事务数）
-- TPS = (Com_commit + Com_rollback) / 时间

-- 连接数
SHOW GLOBAL STATUS LIKE 'Threads_connected';
SHOW GLOBAL STATUS LIKE 'Max_used_connections';

-- 缓存命中率
-- 查询缓存命中率（MySQL 8.0已移除查询缓存）
-- InnoDB缓冲池命中率
SHOW GLOBAL STATUS LIKE 'Innodb_buffer_pool_read%';
-- 命中率 = (1 - Innodb_buffer_pool_reads / Innodb_buffer_pool_read_requests) * 100%

-- 临时表使用情况
SHOW GLOBAL STATUS LIKE 'Created_tmp%';
```

### 查看表状态

```sql
-- 查看表状态
SHOW TABLE STATUS;
SHOW TABLE STATUS LIKE 'table_name';
SHOW TABLE STATUS FROM database_name;

-- 查看表大小
SELECT 
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_size_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_size_mb,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS total_size_mb,
    table_rows
FROM information_schema.tables
WHERE table_schema = 'database_name'
ORDER BY total_size_mb DESC;
```

---

## 🔒 锁相关SQL

### 查看锁信息

```sql
-- 查看InnoDB状态（包含锁信息）
SHOW ENGINE INNODB STATUS;

-- 查看锁等待（MySQL 5.7+）
SELECT * FROM information_schema.INNODB_LOCK_WAITS;
SELECT * FROM information_schema.INNODB_LOCKS;
SELECT * FROM information_schema.INNODB_TRX;

-- 查看锁等待详情（MySQL 8.0+）
SELECT 
    r.trx_id waiting_trx_id,
    r.trx_mysql_thread_id waiting_thread,
    r.trx_query waiting_query,
    b.trx_id blocking_trx_id,
    b.trx_mysql_thread_id blocking_thread,
    b.trx_query blocking_query
FROM performance_schema.data_lock_waits w
INNER JOIN information_schema.innodb_trx b ON b.trx_id = w.blocking_engine_transaction_id
INNER JOIN information_schema.innodb_trx r ON r.trx_id = w.requesting_engine_transaction_id;
```

### 查看元数据锁

```sql
-- 查看元数据锁（MySQL 5.7+）
SELECT * FROM performance_schema.metadata_locks;

-- 查看被阻塞的DDL
SELECT 
    OBJECT_NAME, 
    OBJECT_TYPE, 
    LOCK_TYPE, 
    LOCK_STATUS, 
    PROCESSLIST_ID, 
    PROCESSLIST_INFO
FROM performance_schema.metadata_locks m
JOIN performance_schema.threads t ON m.OWNER_THREAD_ID = t.THREAD_ID
WHERE OBJECT_TYPE = 'TABLE';
```

---

## 🛠️ 常用优化SQL

### 分页优化

```sql
-- 传统分页（大偏移量性能差）
SELECT * FROM orders ORDER BY id LIMIT 1000000, 10;

-- 优化1：使用延迟关联
SELECT * FROM orders o
JOIN (SELECT id FROM orders ORDER BY id LIMIT 1000000, 10) tmp
ON o.id = tmp.id;

-- 优化2：使用游标（基于上一页最后ID）
SELECT * FROM orders WHERE id > last_id ORDER BY id LIMIT 10;

-- 优化3：使用覆盖索引
SELECT * FROM orders o
JOIN (SELECT id FROM orders ORDER BY create_time LIMIT 1000000, 10) tmp
ON o.id = tmp.id;
```

### 批量操作优化

```sql
-- 批量插入（推荐）
INSERT INTO user (name, age) VALUES 
('张三', 20),
('李四', 21),
('王五', 22);

-- 批量更新（使用CASE WHEN）
UPDATE user SET status = CASE id
    WHEN 1 THEN 1
    WHEN 2 THEN 1
    WHEN 3 THEN 1
END
WHERE id IN (1, 2, 3);

-- 批量更新（使用JOIN）
UPDATE user u
JOIN (SELECT id, 1 AS new_status FROM user WHERE id IN (1, 2, 3)) tmp
ON u.id = tmp.id
SET u.status = tmp.new_status;

-- 批量删除
DELETE FROM user WHERE id IN (1, 2, 3);

-- 分批删除（避免锁表）
DELETE FROM user WHERE status = 0 LIMIT 1000;
```

### 统计优化

```sql
-- 避免COUNT(*)
-- 如果只需要知道是否有数据，使用LIMIT 1
SELECT 1 FROM user WHERE status = 1 LIMIT 1;

-- 估算行数（快速但不精确）
EXPLAIN SELECT * FROM user;
-- 查看rows字段

-- 从information_schema获取近似行数
SELECT table_rows FROM information_schema.tables 
WHERE table_name = 'user' AND table_schema = 'database_name';
```

---

## 🚨 常见问题排查SQL

### 排查慢查询

```sql
-- 1. 查看执行计划
EXPLAIN SELECT * FROM user WHERE name = '张三';

-- 2. 查看是否使用索引
-- 关注key字段，如果为NULL说明未使用索引

-- 3. 查看扫描行数
-- 关注rows字段，如果过大需要优化

-- 4. 查看额外操作
-- 关注Extra字段，避免Using filesort和Using temporary
```

### 排查锁问题

```sql
-- 1. 查看当前锁
SHOW ENGINE INNODB STATUS;

-- 2. 查看锁等待
SELECT * FROM information_schema.INNODB_LOCK_WAITS;

-- 3. 查看事务
SELECT * FROM information_schema.INNODB_TRX;

-- 4. 终止长时间运行的事务
KILL trx_mysql_thread_id;
```

### 排查连接问题

```sql
-- 1. 查看当前连接
SHOW PROCESSLIST;

-- 2. 查看连接数
SHOW STATUS LIKE 'Threads_connected';
SHOW STATUS LIKE 'Max_used_connections';
SHOW VARIABLES LIKE 'max_connections';

-- 3. 查看连接详情
SELECT 
    ID, USER, HOST, DB, COMMAND, TIME, STATE, INFO
FROM information_schema.PROCESSLIST
WHERE COMMAND != 'Sleep'
ORDER BY TIME DESC;

-- 4. 终止连接
KILL connection_id;
```

### 排查死锁

```sql
-- 1. 查看死锁日志
SHOW ENGINE INNODB STATUS;
-- 查看LATEST DETECTED DEADLOCK部分

-- 2. 开启死锁监控（MySQL 5.7+）
SET GLOBAL innodb_print_all_deadlocks = ON;

-- 3. 查看死锁信息（MySQL 8.0+）
SELECT * FROM performance_schema.data_lock_waits;
```

---

## 📝 常用配置参数

### 查看配置参数

```sql
-- 查看所有配置
SHOW VARIABLES;
SHOW GLOBAL VARIABLES;

-- 查看特定配置
SHOW VARIABLES LIKE 'innodb%';
SHOW VARIABLES LIKE 'max_connections';
SHOW VARIABLES LIKE 'query_cache%';

-- 查看运行时配置
SELECT @@variable_name;
SELECT @@max_connections;
SELECT @@innodb_buffer_pool_size;
```

### 常用配置参数

```ini
# my.cnf 常用配置

[mysqld]
# 连接数
max_connections = 500
max_user_connections = 400

# InnoDB缓冲池（通常设置为物理内存的50-75%）
innodb_buffer_pool_size = 4G
innodb_buffer_pool_instances = 4

# 日志文件大小
innodb_log_file_size = 512M
innodb_log_files_in_group = 2

# 刷新日志策略
innodb_flush_log_at_trx_commit = 2

# 每次提交刷新binlog
sync_binlog = 1

# 临时表大小
tmp_table_size = 64M
max_heap_table_size = 64M

# 排序缓冲区
sort_buffer_size = 2M

# 连接缓冲区
join_buffer_size = 2M

# 查询缓存（MySQL 8.0已移除）
# query_cache_type = 1
# query_cache_size = 64M
```

---

## 🎯 使用场景速查

### 场景1：查询变慢了

```sql
-- 1. 查看执行计划
EXPLAIN SELECT * FROM table WHERE condition;

-- 2. 检查是否使用索引
-- 关注key字段

-- 3. 检查扫描行数
-- 关注rows字段

-- 4. 检查是否有额外操作
-- 关注Extra字段

-- 5. 查看表统计信息是否过期
SHOW TABLE STATUS LIKE 'table_name';

-- 6. 更新统计信息
ANALYZE TABLE table_name;
```

### 场景2：CPU使用率过高

```sql
-- 1. 查看当前执行的查询
SHOW PROCESSLIST;

-- 2. 找出执行时间长的查询
SELECT * FROM information_schema.PROCESSLIST WHERE TIME > 10;

-- 3. 查看慢查询日志
-- 分析slow.log

-- 4. 查看QPS
SHOW GLOBAL STATUS LIKE 'Queries';
```

### 场景3：内存使用率过高

```sql
-- 1. 查看InnoDB缓冲池使用情况
SHOW STATUS LIKE 'Innodb_buffer_pool%';

-- 2. 查看临时表使用情况
SHOW STATUS LIKE 'Created_tmp%';

-- 3. 查看连接数
SHOW STATUS LIKE 'Threads_connected';

-- 4. 查看表缓存
SHOW STATUS LIKE 'Open_tables';
SHOW STATUS LIKE 'Opened_tables';
```

### 场景4：磁盘IO过高

```sql
-- 1. 查看InnoDB IO情况
SHOW STATUS LIKE 'Innodb_data%';
SHOW STATUS LIKE 'Innodb_log%';

-- 2. 查看临时表是否写入磁盘
SHOW STATUS LIKE 'Created_tmp_disk_tables';

-- 3. 查看排序是否使用磁盘
SHOW STATUS LIKE 'Sort_merge_passes';
```

### 场景5：出现死锁

```sql
-- 1. 查看死锁日志
SHOW ENGINE INNODB STATUS;

-- 2. 开启死锁监控
SET GLOBAL innodb_print_all_deadlocks = ON;

-- 3. 查看当前事务
SELECT * FROM information_schema.INNODB_TRX;

-- 4. 终止事务
KILL trx_mysql_thread_id;
```

### 场景6：主从延迟

```sql
-- 在从库执行
-- 1. 查看从库状态
SHOW SLAVE STATUS;

-- 2. 关注Seconds_Behind_Master字段

-- 3. 查看复制线程状态
SHOW PROCESSLIST;

-- 4. 查看中继日志应用情况
SHOW STATUS LIKE 'Slave_retried_transactions';
```

---

## 🛠️ 常用工具命令

### mysqldump备份

```bash
# 备份单个数据库
mysqldump -u root -p database_name > backup.sql

# 备份多个数据库
mysqldump -u root -p --databases db1 db2 > backup.sql

# 备份所有数据库
mysqldump -u root -p --all-databases > backup.sql

# 仅备份表结构
mysqldump -u root -p --no-data database_name > schema.sql

# 仅备份数据
mysqldump -u root -p --no-create-info database_name > data.sql

# 压缩备份
mysqldump -u root -p database_name | gzip > backup.sql.gz
```

### mysqlbinlog分析

```bash
# 查看binlog文件
mysqlbinlog mysql-bin.000001

# 查看特定时间段的binlog
mysqlbinlog --start-datetime="2024-01-01 00:00:00" --stop-datetime="2024-01-02 00:00:00" mysql-bin.000001

# 查看特定位置的binlog
mysqlbinlog --start-position=1234 --stop-position=5678 mysql-bin.000001

# 导出binlog为SQL
mysqlbinlog mysql-bin.000001 > binlog.sql
```

### pt-query-digest分析

```bash
# 安装Percona Toolkit
# 分析慢查询日志
pt-query-digest /var/lib/mysql/slow.log

# 分析binlog
pt-query-digest --type=binlog mysql-bin.000001

# 分析PROCESSLIST
pt-query-digest --type=processlist --processlist h=localhost,u=root,p=password

# 分析TCPDUMP
pt-query-digest --type=tcpdump tcpdump.txt
```

### pt-online-schema-change在线DDL

```bash
# 在线添加索引（避免锁表）
pt-online-schema-change --alter "ADD INDEX idx_name(column_name)" \
    D=database_name,t=table_name,u=root,p=password --execute

# 在线修改列类型
pt-online-schema-change --alter "MODIFY COLUMN column_name VARCHAR(255)" \
    D=database_name,t=table_name,u=root,p=password --execute
```

---

## 📚 常用查询模板

### 查看表大小排名

```sql
SELECT 
    table_name,
    ROUND(data_length / 1024 / 1024, 2) AS data_size_mb,
    ROUND(index_length / 1024 / 1024, 2) AS index_size_mb,
    ROUND((data_length + index_length) / 1024 / 1024, 2) AS total_size_mb,
    table_rows
FROM information_schema.tables
WHERE table_schema = 'database_name'
ORDER BY total_size_mb DESC
LIMIT 20;
```

### 查看重复索引

```sql
SELECT 
    t.table_name,
    t.index_name,
    GROUP_CONCAT(t.column_name ORDER BY t.seq_in_index) AS columns
FROM information_schema.statistics t
WHERE t.table_schema = 'database_name'
GROUP BY t.table_name, t.index_name
HAVING COUNT(*) > 1;
```

### 查看没有主键的表

```sql
SELECT 
    t.table_schema,
    t.table_name
FROM information_schema.tables t
LEFT JOIN information_schema.key_column_usage k
    ON t.table_schema = k.table_schema
    AND t.table_name = k.table_name
    AND k.constraint_name = 'PRIMARY'
WHERE t.table_schema = 'database_name'
AND t.table_type = 'BASE TABLE'
AND k.constraint_name IS NULL;
```

### 查看长时间运行的事务

```sql
SELECT 
    trx_id,
    trx_mysql_thread_id,
    trx_state,
    trx_started,
    TIMESTAMPDIFF(SECOND, trx_started, NOW()) AS trx_seconds,
    trx_tables_locked,
    trx_rows_locked,
    LEFT(trx_query, 100) AS query_preview
FROM information_schema.innodb_trx
ORDER BY trx_started
LIMIT 10;
```

---

## ✅ 检查清单

### SQL优化检查清单

```
□ 是否使用了SELECT *？
  → 只查询需要的列

□ WHERE条件是否有索引？
  → 为查询条件添加索引

□ 是否使用了函数？
  → 避免在WHERE条件中使用函数

□ 是否使用了LIKE '%xxx%'？
  → 前缀模糊查询无法使用索引

□ 是否使用了OR？
  → 考虑使用UNION ALL替代

□ 是否使用了子查询？
  → 考虑使用JOIN替代

□ 是否使用了ORDER BY？
  → 为排序字段添加索引

□ 是否使用了GROUP BY？
  → 为分组字段添加索引

□ 是否使用了LIMIT大偏移量？
  → 使用延迟关联或游标

□ 是否有多表JOIN？
  → 确保JOIN字段有索引
```

### 索引优化检查清单

```
□ 表是否有主键？
  → 每个表都应该有主键

□ 查询条件是否有索引？
  → 为WHERE条件添加索引

□ 排序字段是否有索引？
  → 为ORDER BY字段添加索引

□ 分组字段是否有索引？
  → 为GROUP BY字段添加索引

□ JOIN字段是否有索引？
  → 为JOIN条件添加索引

□ 是否有冗余索引？
  → 删除冗余索引

□ 是否有未使用的索引？
  → 删除未使用的索引

□ 索引选择性是否足够？
  → 选择性低的列不适合建索引
```

---

> 💡 **提示**：本文档为速查手册，详细知识点请参考《学习笔记.md》
