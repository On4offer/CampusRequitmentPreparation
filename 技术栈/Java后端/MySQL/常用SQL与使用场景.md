# 📌 MySQL 常用 SQL 与使用场景速查

> 配合《学习笔记》使用，侧重**日常开发/运维中的 SQL 模板、命令与场景**，便于速查与上手。

---

## 一、常用 SQL 模板

### 1.1 建表与字符集

```sql
-- 建库
CREATE DATABASE app_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE app_db;

-- 建表（InnoDB + utf8mb4，推荐）
CREATE TABLE user (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT PRIMARY KEY COMMENT '主键',
    username    VARCHAR(64) NOT NULL COMMENT '用户名',
    status      TINYINT NOT NULL DEFAULT 1 COMMENT '状态 0禁用 1正常',
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_username (username),
    KEY idx_status (status),
    KEY idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';
```

### 1.2 索引

```sql
-- 单列索引
CREATE INDEX idx_name ON user(username);
-- 联合索引（注意最左前缀）
CREATE INDEX idx_status_created ON user(status, created_at);
-- 唯一索引
CREATE UNIQUE INDEX uk_email ON user(email);
-- 删除索引
ALTER TABLE user DROP INDEX idx_name;
-- 查看表索引
SHOW INDEX FROM user;
```

### 1.3 分页（深分页优化）

```sql
-- 常规分页（深分页会变慢）
SELECT * FROM order_list ORDER BY id LIMIT 100000, 20;

-- 延迟关联优化（先查 id 再回表）
SELECT o.* FROM order_list o
INNER JOIN (SELECT id FROM order_list ORDER BY id LIMIT 100000, 20) t ON o.id = t.id
ORDER BY o.id;
```

### 1.4 统计与去重

```sql
-- 总数（尽量用索引或近似值）
SELECT COUNT(*) FROM user WHERE status = 1;
SELECT COUNT(1) FROM user;   -- 与 COUNT(*) 等价
-- 去重统计
SELECT COUNT(DISTINCT city) FROM user;
-- 分组聚合
SELECT status, COUNT(*) cnt FROM user GROUP BY status;
```

### 1.5 事务

```sql
START TRANSACTION;
-- 多条 DML
INSERT INTO order_main (...) VALUES (...);
UPDATE inventory SET stock = stock - 1 WHERE id = ?;
COMMIT;   -- 或 ROLLBACK;
```

### 1.6 用户与权限（DCL）

```sql
-- 创建用户（推荐限制 host）
CREATE USER 'app'@'%' IDENTIFIED BY 'StrongPass#123';
-- 授权（库级/表级）
GRANT SELECT, INSERT, UPDATE, DELETE ON app_db.* TO 'app'@'%';
FLUSH PRIVILEGES;
-- 查看权限
SHOW GRANTS FOR 'app'@'%';
-- 回收权限
REVOKE DELETE ON app_db.* FROM 'app'@'%';
```

---

## 二、常用命令速查

### 2.1 客户端连接

```bash
# 本地
mysql -u root -p
# 指定主机端口
mysql -h 127.0.0.1 -P 3306 -u root -p
# 执行单条 SQL 后退出
mysql -u root -p -e "SHOW DATABASES;"
```

### 2.2 备份与恢复

```bash
# 逻辑备份（单库）
mysqldump -u root -p --single-transaction --routines --triggers app_db > app_db.sql
# 全库（含建库语句）
mysqldump -u root -p --all-databases > all.sql
# 恢复
mysql -u root -p app_db < app_db.sql
```

### 2.3 状态与诊断

```sql
-- 当前连接与正在执行的 SQL
SHOW PROCESSLIST;
-- 查看锁/事务（InnoDB）
SHOW ENGINE INNODB STATUS\G
-- 慢查询是否开启及阈值
SHOW VARIABLES LIKE 'slow_query%';
SHOW VARIABLES LIKE 'long_query_time';
-- 执行计划
EXPLAIN SELECT ... ;
EXPLAIN FORMAT=TREE SELECT ... ;  -- 8.0 更直观
```

---

## 三、使用场景对照

| 场景             | 做法说明 |
|------------------|----------|
| 新项目建表       | 用 1.1 模板，统一 `utf8mb4`、主键、`created_at`/`updated_at`、必要索引 |
| 查询慢、要加索引 | 先 `EXPLAIN` 看是否走索引、是否回表；按 WHERE/ORDER BY 建单列或联合索引，注意最左前缀 |
| 深分页慢         | 用延迟关联（1.3）或业务上限制最大页码、改用游标/上次最大 id |
| 统计总数慢       | 避免 `SELECT COUNT(*)` 全表；可加 WHERE 用索引，或缓存/近似统计 |
| 备份             | 日常用 `mysqldump`（2.2）；大库或需 PITR 考虑 xtrabackup，见《学习笔记》第八章 |
| 主从是否延迟     | 从库执行 `SHOW SLAVE STATUS\G`，看 `Seconds_Behind_Master`、`Slave_IO_Running`/`Slave_SQL_Running` |
| 死锁排查         | `SHOW ENGINE INNODB STATUS\G` 中 LATEST DETECTED DEADLOCK 段；结合业务调整事务顺序或缩小锁范围 |
| 慢 SQL 分析      | 开启慢查询日志，用 pt-query-digest 或 MySQL 自带分析；EXPLAIN 看 type、rows、Extra |

---

## 四、常见问题排查

| 现象           | 可能原因           | 处理思路 |
|----------------|--------------------|----------|
| 连接失败       | 端口/防火墙、用户 host、密码 | 检查 `bind-address`、用户 `'root'@'%'`、防火墙 3306；`mysql_secure_installation` |
| 连接数满       | `max_connections` 过小或连接泄漏 | `SHOW STATUS LIKE 'Threads_connected';`；调大 `max_connections` 或排查应用连接未关闭 |
| 死锁           | 多事务加锁顺序不一致 | 见上「死锁排查」；缩短事务、按固定顺序访问表/行 |
| 慢查询/卡顿    | 缺索引、锁等待、大事务 | EXPLAIN、PROCESSLIST、INNODB STATUS；加索引、避免长事务 |
| 磁盘满          | 数据/日志/临时文件占满 | 查 `datadir`、`tmpdir`、binlog/redo 目录；清理 binlog、大表归档或扩容 |
| 主从复制中断   | 从库错误、网络、主库 binlog 缺失 | `SHOW SLAVE STATUS\G` 看 Last_Error；必要时重新做从库或跳过错误（谨慎） |

---

## 五、与学习笔记的对应关系

- **建表、索引、事务、权限** 详细语法与原理 → 《学习笔记》第二、三、四、十一章。
- **EXPLAIN、慢查询、性能调优** → 第三、九章及附录「EXPLAIN 字段解释」。
- **备份恢复、主从、日志** → 第六、七、八章。
- **命令速查表、my.cnf 模板** → 《学习笔记》附录一、二。

> 更多原理与面试题见《学习笔记》第十二章及附录。
