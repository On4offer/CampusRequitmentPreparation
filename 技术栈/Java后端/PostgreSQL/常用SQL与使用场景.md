# 📋 PostgreSQL 常用 SQL 与使用场景速查手册

> 本文档为《PostgreSQL 学习与实战手册》的配套速查文档，按使用场景分类整理常用 SQL，方便日常开发快速查阅。

---

## 📑 目录

1. [数据库与连接管理](#1️⃣-数据库与连接管理)
2. [表结构设计](#2️⃣-表结构设计)
3. [数据增删改查](#3️⃣-数据增删改查)
4. [索引优化](#4️⃣-索引优化)
5. [事务与并发](#5️⃣-事务与并发)
6. [性能分析](#6️⃣-性能分析)
7. [运维管理](#7️⃣-运维管理)
8. [常用函数速查](#8️⃣-常用函数速查)

---

## 1️⃣ 数据库与连接管理

### 连接数据库

```bash
# 命令行连接
psql -h localhost -p 5432 -U username -d database

# 使用连接字符串
psql "postgresql://user:password@host:port/database"

# JDBC 连接字符串
jdbc:postgresql://localhost:5432/mydb?user=admin&password=123456
```

### psql 常用命令

```sql
\l                          -- 列出所有数据库
\c database_name            -- 切换数据库
\dt                         -- 列出当前库所有表
\d table_name               -- 查看表结构
\di                         -- 列出所有索引
\df                         -- 列出所有函数
\du                         -- 列出所有用户
\dn                         -- 列出所有 schema
\timing on                  -- 开启执行时间显示
\i script.sql               -- 执行 SQL 文件
\o output.txt               -- 输出重定向到文件
\q                          -- 退出
```

### 数据库操作

```sql
-- 创建数据库
CREATE DATABASE mydb 
  WITH OWNER = admin 
  ENCODING = 'UTF8' 
  LC_COLLATE = 'zh_CN.UTF-8' 
  TEMPLATE = template0;

-- 删除数据库
DROP DATABASE IF EXISTS mydb;

-- 重命名数据库
ALTER DATABASE mydb RENAME TO newdb;
```

---

## 2️⃣ 表结构设计

### 创建表模板

```sql
-- 标准表结构模板
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT chk_username CHECK (LENGTH(username) >= 3),
    CONSTRAINT chk_email CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- 添加注释
COMMENT ON TABLE users IS '用户表';
COMMENT ON COLUMN users.username IS '用户名';
COMMENT ON COLUMN users.email IS '邮箱地址';
```

### 修改表结构

```sql
-- 添加列
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
ALTER TABLE users ADD COLUMN age INTEGER DEFAULT 0;

-- 删除列
ALTER TABLE users DROP COLUMN phone;

-- 修改列类型
ALTER TABLE users ALTER COLUMN age TYPE BIGINT;

-- 修改列约束
ALTER TABLE users ALTER COLUMN username SET NOT NULL;
ALTER TABLE users ALTER COLUMN age SET DEFAULT 18;

-- 重命名列
ALTER TABLE users RENAME COLUMN username TO name;

-- 重命名表
ALTER TABLE users RENAME TO customers;
```

### 约束管理

```sql
-- 添加主键
ALTER TABLE users ADD PRIMARY KEY (id);

-- 添加唯一约束
ALTER TABLE users ADD CONSTRAINT uk_email UNIQUE (email);

-- 添加外键
ALTER TABLE orders 
ADD CONSTRAINT fk_user_id 
FOREIGN KEY (user_id) 
REFERENCES users(id) 
ON DELETE CASCADE 
ON UPDATE CASCADE;

-- 添加检查约束
ALTER TABLE users ADD CONSTRAINT chk_age CHECK (age >= 0 AND age <= 150);

-- 删除约束
ALTER TABLE users DROP CONSTRAINT uk_email;
```

### 分区表

```sql
-- 创建范围分区表（按时间）
CREATE TABLE logs (
    id BIGSERIAL,
    user_id INTEGER,
    action VARCHAR(50),
    created_at TIMESTAMP NOT NULL
) PARTITION BY RANGE (created_at);

-- 创建分区
CREATE TABLE logs_2024_01 PARTITION OF logs
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE logs_2024_02 PARTITION OF logs
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- 查询分区信息
SELECT * FROM pg_partitions WHERE tablename = 'logs';
```

---

## 3️⃣ 数据增删改查

### 插入数据

```sql
-- 插入单条
INSERT INTO users (name, email, age) 
VALUES ('张三', 'zhangsan@example.com', 25);

-- 插入多条
INSERT INTO users (name, email, age) VALUES
    ('李四', 'lisi@example.com', 30),
    ('王五', 'wangwu@example.com', 28),
    ('赵六', 'zhaoliu@example.com', 35);

-- 插入或更新（UPSERT）
INSERT INTO users (id, name, email) 
VALUES (1, '张三', 'new@example.com')
ON CONFLICT (id) DO UPDATE SET 
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    updated_at = CURRENT_TIMESTAMP;

-- 插入或忽略
INSERT INTO users (id, name, email) 
VALUES (1, '张三', 'test@example.com')
ON CONFLICT (id) DO NOTHING;

-- 从查询结果插入
INSERT INTO users_backup (name, email, age)
SELECT name, email, age FROM users WHERE status = 'active';
```

### 更新数据

```sql
-- 基本更新
UPDATE users SET age = 26 WHERE name = '张三';

-- 多列更新
UPDATE users SET 
    age = 26,
    status = 'active',
    updated_at = CURRENT_TIMESTAMP
WHERE name = '张三';

-- 条件更新
UPDATE users SET status = 'inactive'
WHERE last_login < CURRENT_DATE - INTERVAL '90 days';

-- 从其他表更新
UPDATE orders o SET status = u.status
FROM users u
WHERE o.user_id = u.id AND u.status = 'inactive';

-- 返回更新的行
UPDATE users SET age = age + 1 
WHERE status = 'active'
RETURNING id, name, age;
```

### 删除数据

```sql
-- 条件删除
DELETE FROM users WHERE status = 'inactive';

-- 删除所有（慢，可回滚）
DELETE FROM users;

-- 截断表（快，不可回滚，重置自增）
TRUNCATE TABLE users;
TRUNCATE TABLE users RESTART IDENTITY CASCADE;

-- 删除并返回
DELETE FROM users WHERE status = 'inactive'
RETURNING id, name;

-- 使用 USING 删除
DELETE FROM orders o
USING users u
WHERE o.user_id = u.id AND u.status = 'deleted';
```

### 查询数据

```sql
-- 基础查询
SELECT * FROM users WHERE status = 'active';
SELECT name, email FROM users WHERE age > 18;

-- 排序与分页
SELECT * FROM users 
WHERE status = 'active'
ORDER BY created_at DESC
LIMIT 10 OFFSET 20;

-- 键集分页（高性能）
SELECT * FROM users 
WHERE id > 1000 AND status = 'active'
ORDER BY id
LIMIT 10;

-- 去重
SELECT DISTINCT status FROM users;
SELECT DISTINCT ON (status) * FROM users ORDER BY status, created_at DESC;

-- 聚合查询
SELECT 
    status,
    COUNT(*) as count,
    AVG(age) as avg_age,
    MAX(created_at) as last_created
FROM users
GROUP BY status;

-- 分组过滤
SELECT status, COUNT(*) as count
FROM users
GROUP BY status
HAVING COUNT(*) > 10;

-- 条件聚合
SELECT 
    COUNT(*) as total,
    COUNT(*) FILTER (WHERE status = 'active') as active_count,
    COUNT(*) FILTER (WHERE status = 'inactive') as inactive_count
FROM users;
```

### 关联查询

```sql
-- INNER JOIN
SELECT u.name, o.order_no, o.amount
FROM users u
INNER JOIN orders o ON u.id = o.user_id;

-- LEFT JOIN
SELECT u.name, COUNT(o.id) as order_count
FROM users u
LEFT JOIN orders o ON u.id = o.user_id
GROUP BY u.id, u.name;

-- 多表 JOIN
SELECT u.name, p.name as product_name, oi.quantity
FROM users u
JOIN orders o ON u.id = o.user_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id;

-- 自连接
SELECT e.name, m.name as manager_name
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;

-- 子查询
SELECT * FROM users 
WHERE id IN (SELECT user_id FROM orders WHERE amount > 1000);

-- EXISTS
SELECT * FROM users u
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

### CTE 与窗口函数

```sql
-- CTE（公用表表达式）
WITH active_users AS (
    SELECT * FROM users WHERE status = 'active'
),
user_orders AS (
    SELECT user_id, COUNT(*) as order_count 
    FROM orders 
    GROUP BY user_id
)
SELECT au.name, COALESCE(uo.order_count, 0) as orders
FROM active_users au
LEFT JOIN user_orders uo ON au.id = uo.user_id;

-- 递归 CTE
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id, 1 as level
    FROM employees WHERE id = 1
    
    UNION ALL
    
    SELECT e.id, e.name, e.manager_id, s.level + 1
    FROM employees e
    INNER JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates;

-- 窗口函数
SELECT 
    name,
    salary,
    RANK() OVER (ORDER BY salary DESC) as rank,
    DENSE_RANK() OVER (ORDER BY salary DESC) as dense_rank,
    ROW_NUMBER() OVER (ORDER BY salary DESC) as row_num,
    AVG(salary) OVER () as avg_salary,
    salary - AVG(salary) OVER () as diff_from_avg
FROM employees;

-- 分组窗口函数
SELECT 
    department,
    name,
    salary,
    RANK() OVER (PARTITION BY department ORDER BY salary DESC) as dept_rank,
    SUM(salary) OVER (PARTITION BY department) as dept_total
FROM employees;
```

---

## 4️⃣ 索引优化

### 创建索引

```sql
-- 单列索引
CREATE INDEX idx_users_name ON users(name);

-- 复合索引
CREATE INDEX idx_users_name_age ON users(name, age);

-- 唯一索引
CREATE UNIQUE INDEX idx_users_email ON users(email);

-- 条件索引（部分索引）
CREATE INDEX idx_users_active ON users(name) WHERE status = 'active';

-- 函数索引
CREATE INDEX idx_users_lower_email ON users(LOWER(email));

-- GIN 索引（JSONB、数组）
CREATE INDEX idx_users_settings ON users USING GIN (settings);
CREATE INDEX idx_posts_tags ON posts USING GIN (tags);

-- GiST 索引（范围类型）
CREATE INDEX idx_reservations_during ON reservations USING GIST (during);

-- BRIN 索引（大表、有序数据）
CREATE INDEX idx_logs_created_at ON logs USING BRIN (created_at);
```

### 索引维护

```sql
-- 查看表的所有索引
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'users';

-- 查看索引大小
SELECT pg_size_pretty(pg_relation_size('idx_users_name'));

-- 查看索引使用情况
SELECT 
    schemaname,
    tablename,
    indexrelname,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
WHERE tablename = 'users';

-- 删除索引
DROP INDEX idx_users_name;

-- 重建索引
REINDEX INDEX idx_users_name;
REINDEX TABLE users;

-- 分析表（更新统计信息）
ANALYZE users;

-- 清理表（回收空间）
VACUUM users;
VACUUM ANALYZE users;
VACUUM FULL users;  -- 完全回收，锁表慎用
```

---

## 5️⃣ 事务与并发

### 事务控制

```sql
-- 基本事务
BEGIN;
-- SQL 操作
COMMIT;

-- 回滚事务
BEGIN;
-- SQL 操作
ROLLBACK;

-- 保存点
BEGIN;
INSERT INTO orders VALUES (...);
SAVEPOINT sp1;
INSERT INTO order_items VALUES (...);
ROLLBACK TO SAVEPOINT sp1;  -- 回滚到保存点
COMMIT;

-- 设置隔离级别
BEGIN ISOLATION LEVEL READ COMMITTED;
BEGIN ISOLATION LEVEL REPEATABLE READ;
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

### 锁操作

```sql
-- 行级锁
SELECT * FROM users WHERE id = 1 FOR UPDATE;        -- 排他锁
SELECT * FROM users WHERE id = 1 FOR SHARE;         -- 共享锁
SELECT * FROM users WHERE id = 1 FOR UPDATE NOWAIT; -- 立即返回或报错
SELECT * FROM users WHERE id = 1 FOR UPDATE SKIP LOCKED; -- 跳过已锁定行

-- 表级锁
LOCK TABLE users IN ACCESS EXCLUSIVE MODE;

-- 查看锁信息
SELECT 
    l.locktype,
    l.relation::regclass,
    l.pid,
    l.mode,
    l.granted,
    a.query
FROM pg_locks l
LEFT JOIN pg_stat_activity a ON l.pid = a.pid
WHERE l.database IS NOT NULL;

-- 查看锁等待
SELECT 
    blocked_locks.pid AS blocked_pid,
    blocking_locks.pid AS blocking_pid
FROM pg_locks blocked_locks
JOIN pg_locks blocking_locks 
    ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
WHERE NOT blocked_locks.granted;

-- 终止进程
SELECT pg_terminate_backend(pid);
```

---

## 6️⃣ 性能分析

### 执行计划分析

```sql
-- 查看执行计划
EXPLAIN SELECT * FROM users WHERE name = '张三';

-- 实际执行并分析
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) 
SELECT * FROM users WHERE name = '张三';

-- 详细分析
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, COSTS, FORMAT JSON)
SELECT u.name, COUNT(o.id) 
FROM users u 
LEFT JOIN orders o ON u.id = o.user_id 
GROUP BY u.id, u.name;
```

### 慢查询排查

```sql
-- 查看当前活动查询
SELECT 
    pid,
    now() - query_start AS duration,
    state,
    query
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY duration DESC;

-- 查看长事务
SELECT 
    pid,
    now() - xact_start AS transaction_duration,
    query
FROM pg_stat_activity
WHERE xact_start IS NOT NULL
AND now() - xact_start > interval '5 minutes';

-- 重置统计信息
SELECT pg_stat_reset();
```

### 表统计信息

```sql
-- 查看表大小
SELECT pg_size_pretty(pg_total_relation_size('users'));
SELECT pg_size_pretty(pg_table_size('users'));
SELECT pg_size_pretty(pg_indexes_size('users'));

-- 查看表行数（估算）
SELECT reltuples::BIGINT AS estimate FROM pg_class WHERE relname = 'users';

-- 查看表统计信息
SELECT 
    schemaname,
    tablename,
    n_tup_ins,
    n_tup_upd,
    n_tup_del,
    n_live_tup,
    n_dead_tup,
    last_vacuum,
    last_autovacuum,
    last_analyze
FROM pg_stat_user_tables
WHERE tablename = 'users';
```

---

## 7️⃣ 运维管理

### 用户与权限

```sql
-- 创建用户
CREATE USER app_user WITH PASSWORD 'password';
CREATE ROLE readonly WITH LOGIN PASSWORD 'password';

-- 授权
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;

-- 只读权限
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO readonly;

-- 撤销权限
REVOKE DELETE ON users FROM app_user;

-- 查看权限
\du                         -- 列出用户
SELECT * FROM pg_roles;     -- 角色信息
```

### 备份与恢复

```bash
# 逻辑备份
pg_dump -h localhost -U admin -d mydb -Fc > mydb_backup.dump

# 逻辑恢复
pg_restore -h localhost -U admin -d mydb mydb_backup.dump

# 全库备份
pg_dumpall -h localhost -U postgres > all_databases.sql

# 基础备份
pg_basebackup -h localhost -U replicator -D /backup/base -Fp -Xs -P
```

### 配置参数

```sql
-- 查看配置
SHOW shared_buffers;
SHOW work_mem;
SHOW max_connections;

-- 修改配置（当前会话）
SET work_mem = '64MB';

-- 修改配置（永久）
ALTER SYSTEM SET work_mem = '64MB';
SELECT pg_reload_conf();

-- 常用配置参数
-- shared_buffers = 系统内存的 25%
-- work_mem = 4MB-64MB
-- maintenance_work_mem = 256MB-1GB
-- effective_cache_size = 系统内存的 50-75%
-- max_connections = 根据连接池配置
```

---

## 8️⃣ 常用函数速查

### 字符串函数

```sql
SELECT LENGTH('Hello');                    -- 5
SELECT UPPER('hello');                     -- HELLO
SELECT LOWER('HELLO');                     -- hello
SELECT SUBSTRING('Hello World', 1, 5);     -- Hello
SELECT REPLACE('Hello', 'l', 'L');         -- HeLLo
SELECT TRIM('  Hello  ');                  -- Hello
SELECT SPLIT_PART('a,b,c', ',', 2);        -- b
SELECT POSITION('World' IN 'Hello World'); -- 7
SELECT CONCAT('Hello', ' ', 'World');      -- Hello World
SELECT 'Hello' || ' ' || 'World';          -- Hello World
SELECT MD5('password');                    -- md5 hash
```

### 数值函数

```sql
SELECT ABS(-10);                           -- 10
SELECT ROUND(3.14159, 2);                  -- 3.14
SELECT CEIL(3.2);                          -- 4
SELECT FLOOR(3.8);                         -- 3
SELECT POWER(2, 3);                        -- 8
SELECT SQRT(16);                           -- 4
SELECT RANDOM();                           -- 0-1 随机数
SELECT TRUNC(3.14159, 2);                  -- 3.14
```

### 日期时间函数

```sql
SELECT CURRENT_DATE;                       -- 当前日期
SELECT CURRENT_TIME;                       -- 当前时间
SELECT CURRENT_TIMESTAMP;                  -- 当前时间戳
SELECT NOW();                              -- 当前时间戳

-- 日期计算
SELECT NOW() + INTERVAL '1 day';
SELECT NOW() - INTERVAL '2 hours';
SELECT NOW() + INTERVAL '1 month 2 days';

-- 日期提取
SELECT EXTRACT(YEAR FROM NOW());           -- 年
SELECT EXTRACT(MONTH FROM NOW());          -- 月
SELECT EXTRACT(DAY FROM NOW());            -- 日
SELECT EXTRACT(DOW FROM NOW());            -- 星期几 (0-6)
SELECT EXTRACT(WEEK FROM NOW());           -- 第几周

-- 日期格式化
SELECT TO_CHAR(NOW(), 'YYYY-MM-DD');
SELECT TO_CHAR(NOW(), 'YYYY-MM-DD HH24:MI:SS');
SELECT TO_CHAR(NOW(), 'YYYY年MM月DD日');

-- 日期转换
SELECT TO_DATE('2024-01-15', 'YYYY-MM-DD');
SELECT TO_TIMESTAMP('2024-01-15 10:30:00', 'YYYY-MM-DD HH24:MI:SS');

-- 日期差
SELECT AGE(TIMESTAMP '2024-12-31', TIMESTAMP '2024-01-01');
SELECT DATE_PART('day', NOW() - TIMESTAMP '2024-01-01');
```

### 聚合函数

```sql
SELECT COUNT(*) FROM users;
SELECT COUNT(DISTINCT status) FROM users;
SELECT SUM(amount) FROM orders;
SELECT AVG(age) FROM users;
SELECT MAX(salary) FROM employees;
SELECT MIN(salary) FROM employees;

-- 条件聚合
SELECT 
    COUNT(*) FILTER (WHERE status = 'active') as active_count,
    COUNT(*) FILTER (WHERE status = 'inactive') as inactive_count
FROM users;

-- 字符串聚合
SELECT STRING_AGG(name, ', ') FROM users;
SELECT ARRAY_AGG(name) FROM users;
```

### 类型转换

```sql
SELECT CAST('123' AS INTEGER);
SELECT '123'::INTEGER;
SELECT '2024-01-01'::DATE;
SELECT 123::TEXT;
SELECT '3.14'::NUMERIC;
```

### JSON/JSONB 函数

```sql
-- 创建 JSON
SELECT '{"name": "张三", "age": 25}'::JSONB;
SELECT JSONB_BUILD_OBJECT('name', '张三', 'age', 25);
SELECT JSONB_AGG(id, name) FROM users;

-- 查询 JSON
SELECT settings->>'theme' FROM users;
SELECT settings->'preferences'->>'notifications' FROM users;

-- 操作 JSON
SELECT settings || '{"theme": "dark"}'::JSONB;  -- 合并
SELECT settings - 'theme';                       -- 删除键
SELECT JSONB_PRETTY(settings);                   -- 格式化

-- 包含查询
SELECT * FROM users WHERE settings @> '{"theme": "dark"}';
SELECT * FROM users WHERE settings ? 'theme';
```

### 数组函数

```sql
-- 数组操作
SELECT ARRAY[1, 2, 3];
SELECT ARRAY_APPEND(ARRAY[1, 2], 3);      -- {1,2,3}
SELECT ARRAY_LENGTH(ARRAY[1, 2, 3], 1);   -- 3
SELECT ARRAY_POSITION(ARRAY[1, 2, 3], 2); -- 2
SELECT UNNEST(ARRAY[1, 2, 3]);            -- 展开为行

-- 数组包含
SELECT ARRAY[1, 2, 3] @> ARRAY[1, 2];    -- true
SELECT ARRAY[1, 2] && ARRAY[2, 3];        -- true (有交集)
```

### 条件函数

```sql
-- CASE WHEN
SELECT 
    name,
    CASE 
        WHEN age < 18 THEN '未成年'
        WHEN age < 60 THEN '成年'
        ELSE '老年'
    END as age_group
FROM users;

-- COALESCE（返回第一个非 NULL）
SELECT COALESCE(NULL, NULL, 'default');   -- default
SELECT COALESCE(phone, email, 'N/A') FROM users;

-- NULLIF（相等返回 NULL）
SELECT NULLIF(1, 1);                      -- NULL
SELECT NULLIF(1, 2);                      -- 1

-- GREATEST / LEAST
SELECT GREATEST(1, 5, 3);                 -- 5
SELECT LEAST(1, 5, 3);                    -- 1
```

### 窗口函数

```sql
-- 排名函数
SELECT 
    name,
    RANK() OVER (ORDER BY score DESC),           -- 排名，相同跳号
    DENSE_RANK() OVER (ORDER BY score DESC),     -- 排名，相同不跳号
    ROW_NUMBER() OVER (ORDER BY score DESC),     -- 行号
    NTILE(4) OVER (ORDER BY score DESC)          -- 分桶
FROM students;

-- 偏移函数
SELECT 
    name,
    salary,
    LAG(salary, 1) OVER (ORDER BY id),           -- 上一行
    LEAD(salary, 1) OVER (ORDER BY id),          -- 下一行
    FIRST_VALUE(salary) OVER (ORDER BY id),      -- 第一行
    LAST_VALUE(salary) OVER (ORDER BY id)        -- 最后一行
FROM employees;

-- 聚合窗口函数
SELECT 
    name,
    salary,
    SUM(salary) OVER (ORDER BY id) as running_total,
    AVG(salary) OVER () as avg_salary,
    SUM(salary) OVER (PARTITION BY dept) as dept_total
FROM employees;
```

---

## 📝 附录：常用查询模板

### 分页查询

```sql
-- 键集分页（推荐）
SELECT * FROM users 
WHERE id > :last_id 
ORDER BY id 
LIMIT 10;

-- OFFSET 分页（小数据量）
SELECT * FROM users 
ORDER BY id 
LIMIT 10 OFFSET 20;

-- 延迟关联分页（大数据量）
SELECT * FROM users u
JOIN (
    SELECT id FROM users 
    ORDER BY id 
    LIMIT 10 OFFSET 10000
) tmp ON u.id = tmp.id;
```

### 树形结构查询

```sql
-- 递归查询组织架构
WITH RECURSIVE org_tree AS (
    SELECT id, name, parent_id, 0 as level, name as path
    FROM departments WHERE parent_id IS NULL
    
    UNION ALL
    
    SELECT d.id, d.name, d.parent_id, ot.level + 1, 
           ot.path || ' > ' || d.name
    FROM departments d
    JOIN org_tree ot ON d.parent_id = ot.id
)
SELECT * FROM org_tree;
```

### 连续登录天数

```sql
-- 计算用户连续登录天数
WITH login_with_grp AS (
    SELECT 
        user_id,
        login_date,
        login_date - ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date)::INT as grp
    FROM user_login_log
)
SELECT user_id, grp, COUNT(*) as consecutive_days
FROM login_with_grp
GROUP BY user_id, grp
HAVING COUNT(*) >= 3;  -- 连续3天以上
```

### 数据去重

```sql
-- 删除重复数据（保留最新）
DELETE FROM users a
WHERE ctid NOT IN (
    SELECT MAX(ctid) 
    FROM users b 
    WHERE a.email = b.email
);

-- 或使用窗口函数
DELETE FROM users
WHERE ctid IN (
    SELECT ctid FROM (
        SELECT ctid, ROW_NUMBER() OVER (PARTITION BY email ORDER BY created_at DESC) as rn
        FROM users
    ) t WHERE rn > 1
);
```

---

> 💡 **提示**：本文档为速查手册，详细内容请参考《PostgreSQL 学习与实战手册》
