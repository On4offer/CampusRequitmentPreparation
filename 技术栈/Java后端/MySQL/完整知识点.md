# SQL 完整指南：从基础到专家级

## 一、SQL 语言分类体系

### 1. 数据定义语言 (DDL)

```sql
-- 数据库操作
CREATE DATABASE dbname [CHARACTER SET charset] [COLLATE collation];
ALTER DATABASE dbname [options];
DROP DATABASE [IF EXISTS] dbname;

-- 表操作
CREATE [TEMPORARY] TABLE [IF NOT EXISTS] table_name (
    column1 datatype [constraints] [DEFAULT value] [AUTO_INCREMENT],
    column2 datatype [constraints],
    ...
    [PRIMARY KEY (column1, column2, ...)],
    [FOREIGN KEY (column) REFERENCES other_table(column)],
    [UNIQUE (column)],
    [CHECK (condition)]
) [ENGINE=engine_type] [CHARSET=charset];

ALTER TABLE table_name 
    ADD [COLUMN] column_definition [FIRST|AFTER existing_column],
    MODIFY [COLUMN] column_definition,
    CHANGE [COLUMN] old_name new_name column_definition,
    DROP [COLUMN] column_name,
    ADD CONSTRAINT constraint_name constraint_definition,
    DROP CONSTRAINT constraint_name;

DROP TABLE [IF EXISTS] table_name [CASCADE|RESTRICT];
TRUNCATE [TABLE] table_name;
RENAME TABLE old_name TO new_name;
```

------

### 1. CREATE DATABASE - 创建数据库

这条语句用于创建一个全新的、空的数据库。

#### 完整语法（以MySQL为例，其他数据库类似）：

```sql
CREATE DATABASE [IF NOT EXISTS] db_name
    [[DEFAULT] CHARACTER SET charset_name]
    [[DEFAULT] COLLATE collation_name]
    [ENCRYPTION [=] {'Y' | 'N'}];
```

#### 详细参数解释：

1. 1.**`CREATE DATABASE db_name`** 这是最核心的部分。`db_name`是你要创建的数据库的名称。 **命名规则**：通常只能使用字母、数字、下划线和美元符号（`$`），且不能以数字开头。建议使用有意义的英文名称，如 `online_store`, `hr_management`。

2. 2.

   **`[IF NOT EXISTS]`（可选）**

   - **作用**：安全检查。如果指定了这个子句，当要创建的数据库已经存在时，系统不会报错，只会发出一个警告，并且不会执行创建操作。

   - **使用场景**：在脚本中非常有用，可以确保脚本可重复执行而不会因为数据库已存在而中断。

     **示例对比**：

     ```
     -- 不安全的方式：如果 `my_db` 已存在，会报错：ERROR 1007 (HY000): Can't create database 'my_db'; database exists
     CREATE DATABASE my_db;
     
     -- 安全的方式：如果 `my_db` 已存在，只会警告，不会报错，脚本继续执行
     CREATE DATABASE IF NOT EXISTS my_db;
     ```

3. 3.

   **`[DEFAULT] CHARACTER SET charset_name`（可选）**

   - **作用**：指定数据库默认的字符集。字符集定义了数据库可以存储哪些字符（如字母、数字、中文、表情符号等）以及如何用二进制表示这些字符。

   - **常见字符集**： `utf8mb4`（**现代首选**）：真正的UTF-8编码，支持所有Unicode字符，包括表情符号（如👍）。这是MySQL 8.0的默认字符集，也是当前的实际标准。 `utf8`（**过时，不推荐**）：MySQL中一个残缺的UTF-8实现，最多只支持3字节字符，不支持表情符号（4字节字符）。 `latin1`：西欧字符集，不支持中文等非西欧字符。

   - 

     **示例**：

     ```
     CREATE DATABASE my_blog CHARACTER SET utf8mb4;
     ```

4. 4.

   **`[DEFAULT] COLLATE collation_name`（可选）**

   - **作用**：指定数据库默认的排序规则。排序规则定义了字符串比较和排序的规则，比如是否区分大小写、是否区分重音等。

   - **常见排序规则**（通常与字符集配套使用）： 对于 `utf8mb4`： `utf8mb4_0900_ai_ci`（MySQL 8.0默认）：基于Unicode 9.0标准，不区分大小写（ai），不区分重音（as）。 `utf8mb4_unicode_ci`：基于旧的Unicode标准，不区分大小写。 `utf8mb4_bin`：纯粹的二进制比较，**区分大小写**。

   - 

     **示例**：创建一个区分大小写排序规则的数据库。

     ```
     CREATE DATABASE my_app CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
     -- 在这个数据库中，'Apple' 和 'apple' 会被认为是两个不同的词。
     ```

#### 综合示例：

```
-- 创建一个支持多语言和表情符号的博客数据库，使用不区分大小写的现代排序规则
CREATE DATABASE IF NOT EXISTS my_blog
CHARACTER SET utf8mb4
COLLATE utf8mb4_0900_ai_ci;
```

------

### 2. ALTER DATABASE - 修改数据库

这条语句用于修改一个已存在数据库的全局属性，主要是修改其默认的字符集和排序规则。

#### 重要提示：

- `ALTER DATABASE`**通常只影响之后在该数据库中新创建的表**。对于已经存在的表，它们会保留自己创建时的字符集和排序规则，除非你显式地去修改它们。

#### 语法：

```
ALTER DATABASE db_name
    [[DEFAULT] CHARACTER SET charset_name]
    [[DEFAULT] COLLATE collation_name];
```

#### 示例：

```
-- 将数据库 `my_blog` 的字符集修改为 `utf8mb4`，排序规则修改为 `utf8mb4_unicode_ci`
ALTER DATABASE my_blog
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;
```

------

### 3. DROP DATABASE - 删除数据库

**这是一条极其危险的语句！** 它会永久删除整个数据库及其中的所有数据（表、视图、存储过程等），且通常不可恢复。

#### 语法：

```
DROP DATABASE [IF EXISTS] db_name;
```

#### 详细参数解释：

1. 1.**`DROP DATABASE db_name`** 直接删除名为 `db_name`的数据库。

2. 2.

   **`[IF EXISTS]`（强烈建议使用！）**

   - **作用**：安全检查。如果指定了这个子句，当要删除的数据库不存在时，系统不会报错，只会发出一个警告。

   - **为什么重要**：防止在脚本中因为数据库不存在而导致的执行中断。

   - 

     **示例对比**：

     ```
     -- 危险的方式：如果 `old_db` 不存在，会报错：ERROR 1008 (HY000): Can't drop database 'old_db'; database doesn't exist
     DROP DATABASE old_db;
     
     -- 安全的方式：如果 `old_db` 不存在，只会警告，不会报错
     DROP DATABASE IF EXISTS old_db;
     ```

#### 操作前的重要检查：

在执行 `DROP DATABASE`之前，务必：

1. 1.**确认数据库名**：再三检查 `db_name`是否拼写正确。
2. 2.**备份数据**：如果数据库中有任何重要数据，请务必先进行备份。
3. 3.**确认当前连接**：确保你当前没有连接到要删除的数据库，否则操作可能会失败。

------

### 总结与最佳实践

| 语句                  | 用途                         | 危险程度 | 最佳实践                                                     |
| --------------------- | ---------------------------- | -------- | ------------------------------------------------------------ |
| **`CREATE DATABASE`** | 创建新数据库                 | 低       | 总是使用 `IF NOT EXISTS`防止重复创建报错。明确指定 `CHARACTER SET utf8mb4`。 |
| **`ALTER DATABASE`**  | 修改数据库属性               | 中       | 主要用来修改字符集和排序规则。注意它不影响已存在的表。       |
| **`DROP DATABASE`**   | **永久删除数据库及所有数据** | **极高** | **1. 备份！2. 使用 `IF EXISTS`。3. 执行前双重确认数据库名。** |

这些操作是数据库管理的基石，理解其每个选项的含义对于构建健壮、可维护的应用程序至关重要。

------

## 一、CREATE TABLE - 创建表

这是最复杂的DDL语句之一，用于定义新表的结构。

### 完整语法深度解析：

```sql
CREATE [TEMPORARY] TABLE [IF NOT EXISTS] table_name (
    -- 列定义部分
    column1 datatype [constraints] [DEFAULT value] [AUTO_INCREMENT],
    column2 datatype [constraints],
    ...
    
    -- 表级约束部分
    [PRIMARY KEY (column1, column2, ...)],
    [FOREIGN KEY (column) REFERENCES other_table(column)],
    [UNIQUE (column1, column2, ...)],
    [CHECK (condition)],
    [INDEX index_name (column1, column2, ...)]
) [ENGINE=engine_type] [CHARSET=charset] [AUTO_INCREMENT=start_value];
```

### 1. 表级选项详解

#### **`[TEMPORARY]`- 临时表**

```
CREATE TEMPORARY TABLE temp_sessions (
    session_id VARCHAR(32),
    user_data TEXT
);
```

- **作用**：创建临时表，只在当前数据库连接会话中存在，连接关闭时自动删除。
- **用途**：中间结果存储、会话特定数据。
- **特点**：不与其它会话共享，允许与永久表重名。

#### **`[IF NOT EXISTS]`- 安全创建**

```
CREATE TABLE IF NOT EXISTS users (id INT);
```

- 防止表已存在时报错，特别适用于可重复执行的部署脚本。

### 2. 列定义详解

每列的定义包含多个部分：

#### **数据类型 (datatype)**

```
CREATE TABLE example (
    id INT,                          -- 整数
    name VARCHAR(100),              -- 变长字符串
    price DECIMAL(10,2),            -- 精确小数(总位数10,小数位2)
    created_at DATETIME,             -- 日期时间
    is_active BOOLEAN,              -- 布尔值
    metadata JSON                   -- JSON数据(MySQL 5.7+)
);
```

#### **约束 (Constraints)**

**列级约束：**

```
CREATE TABLE users (
    id INT NOT NULL,                    -- 非空约束
    email VARCHAR(255) UNIQUE,          -- 唯一约束
    age INT CHECK (age >= 0),          -- 检查约束
    country VARCHAR(50) DEFAULT 'CN',   -- 默认值
    status ENUM('active','inactive')   -- 枚举约束
);
```

#### **`AUTO_INCREMENT`- 自增字段**

```
CREATE TABLE products (
    id INT PRIMARY KEY AUTO_INCREMENT,  -- 自动生成唯一ID
    name VARCHAR(100)
);
```

- **用途**：主键的自动生成，每次插入自动+1。
- **注意**：通常与PRIMARY KEY一起使用。

### 3. 表级约束详解

#### **PRIMARY KEY - 主键**

```
-- 单字段主键
CREATE TABLE users (
    id INT PRIMARY KEY,
    name VARCHAR(100)
);

-- 复合主键（多个字段共同作为主键）
CREATE TABLE order_items (
    order_id INT,
    product_id INT,
    quantity INT,
    PRIMARY KEY (order_id, product_id)  -- 订单+产品唯一确定一条记录
);
```

#### **FOREIGN KEY - 外键约束**

```
CREATE TABLE orders (
    order_id INT PRIMARY KEY,
    user_id INT,
    order_date DATETIME,
    -- 这里 orders表的 user_id字段引用 users表的 id字段
    FOREIGN KEY (user_id) REFERENCES users(id) 
        ON DELETE CASCADE          -- 用户删除时，订单自动删除
        ON UPDATE NO ACTION        -- 用户ID更新时，不操作
);

-- 外键动作选项：
-- ON DELETE: CASCADE, SET NULL, NO ACTION, RESTRICT
-- ON UPDATE: CASCADE, SET NULL, NO ACTION, RESTRICT
```

#### **UNIQUE - 唯一约束**

```
CREATE TABLE employees (
    id INT PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE,  -- 员工编号必须唯一
    email VARCHAR(255) UNIQUE         -- 邮箱必须唯一
);

-- 复合唯一约束
CREATE TABLE class_schedule (
    class_id INT,
    time_slot VARCHAR(10),
    UNIQUE KEY (class_id, time_slot)  -- 同一班级同一时间段只能有一条记录
);
```

#### **CHECK - 检查约束**

```
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10,2) CHECK (price > 0),		  -- 价格必须大于0
    stock_quantity INT CHECK (stock_quantity >= 0) -- 库存不能为负
);
```

### 4. 表选项详解

#### **`ENGINE=engine_type`- 存储引擎**

```
CREATE TABLE log_entries (
    id INT PRIMARY KEY,
    log_text TEXT
) ENGINE=InnoDB;  -- 默认，支持事务、外键

-- 其他常用引擎：
-- ENGINE=MyISAM    (不支持事务，读性能好)
-- ENGINE=MEMORY    (内存表，重启数据丢失)
-- ENGINE=ARCHIVE   (高压缩，只支持插入查询)
```

#### **`CHARSET=charset`- 字符集**

```
CREATE TABLE multilingual_content (
    id INT PRIMARY KEY,
    chinese_text TEXT,
    emoji_text VARCHAR(500)
) CHARSET=utf8mb4;  -- 支持中文、表情符号等所有Unicode字符
```

#### **完整创建表示例：**

```
CREATE TABLE IF NOT EXISTS employees (
    emp_id INT PRIMARY KEY AUTO_INCREMENT,
    emp_code VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(255) UNIQUE,
    salary DECIMAL(10,2) CHECK (salary >= 0),
    dept_id INT,
    hire_date DATE DEFAULT (CURRENT_DATE),
    status ENUM('active','on_leave','terminated') DEFAULT 'active',
    
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) 
        ON DELETE SET NULL ON UPDATE CASCADE,
        
    INDEX idx_name (first_name, last_name),
    INDEX idx_email (email)
) ENGINE=InnoDB CHARSET=utf8mb4 AUTO_INCREMENT=1001;
```

------

## 二、ALTER TABLE - 修改表结构

用于修改已存在表的结构，是数据库演进的关键操作。

### 语法详细解析：

```
ALTER TABLE table_name 
    ADD [COLUMN] column_definition [FIRST|AFTER existing_column],
    | MODIFY [COLUMN] column_definition,
    | CHANGE [COLUMN] old_name new_name column_definition,
    | DROP [COLUMN] column_name,
    | ADD CONSTRAINT constraint_name constraint_definition,
    | DROP CONSTRAINT constraint_name,
    | RENAME TO new_table_name,
    | ADD INDEX index_name (column_list);
```

### 1. **ADD COLUMN - 添加列**

```
-- 添加单列
ALTER TABLE users ADD COLUMN phone VARCHAR(20);

-- 指定位置添加
ALTER TABLE users ADD COLUMN middle_name VARCHAR(50) AFTER first_name;
ALTER TABLE users ADD COLUMN seq_num INT FIRST;  -- 作为第一列

-- 添加多列
ALTER TABLE products 
    ADD COLUMN weight DECIMAL(8,2),
    ADD COLUMN dimensions VARCHAR(50);
```

### 2. **MODIFY COLUMN - 修改列定义**

```
-- 修改数据类型
ALTER TABLE users MODIFY COLUMN phone VARCHAR(30);  -- 扩大长度

-- 修改约束
ALTER TABLE products MODIFY COLUMN price DECIMAL(10,2) NOT NULL;

-- 复杂修改
ALTER TABLE employees MODIFY COLUMN salary DECIMAL(12,2) 
    DEFAULT 0.00 
    CHECK (salary >= 0);
```

### 3. **CHANGE COLUMN - 重命名列**

```
-- 重命名并修改定义
ALTER TABLE users CHANGE COLUMN phone mobile_phone VARCHAR(20);

-- 只重命名（保持其他定义不变需要在定义中重复）
ALTER TABLE users CHANGE COLUMN name full_name VARCHAR(100);
```

### 4. **DROP COLUMN - 删除列**

```
ALTER TABLE users DROP COLUMN middle_name;
-- ⚠️危险操作：数据将永久丢失！
```

### 5. **约束管理**

```
-- 添加主键
ALTER TABLE orders ADD CONSTRAINT pk_orders PRIMARY KEY (order_id);

-- 添加外键
ALTER TABLE order_items 
    ADD CONSTRAINT fk_order_items_orders 
    FOREIGN KEY (order_id) REFERENCES orders(order_id);

-- 添加唯一约束
ALTER TABLE users ADD CONSTRAINT uk_users_email UNIQUE (email);

-- 删除约束
ALTER TABLE users DROP CONSTRAINT uk_users_email;
ALTER TABLE orders DROP PRIMARY KEY;  -- 删除主键
```

### 6. **索引操作**

```
-- 添加索引
ALTER TABLE products ADD INDEX idx_product_name (product_name);
ALTER TABLE logs ADD INDEX idx_timestamp (created_at DESC);

-- 删除索引
ALTER TABLE products DROP INDEX idx_product_name;
```

### 实际应用场景示例：

```
-- 为现有表添加审计字段
ALTER TABLE customers 
    ADD COLUMN created_by INT,
    ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    ADD INDEX idx_created_at (created_at);

-- 修改表结构以适应业务变化
ALTER TABLE orders 
    MODIFY COLUMN order_amount DECIMAL(12,2),  -- 扩大金额字段
    ADD COLUMN currency VARCHAR(3) DEFAULT 'USD',
    ADD COLUMN payment_method VARCHAR(20),
    ADD INDEX idx_order_date (order_date);
```

------

## 三、其他表操作语句

### 1. **DROP TABLE - 删除表**

```
-- 安全删除
DROP TABLE IF EXISTS temporary_data;

-- 级联删除（PostgreSQL等）
DROP TABLE orders CASCADE;  -- 同时删除依赖此表的外键约束

-- 限制删除（如果有依赖则拒绝删除）
DROP TABLE departments RESTRICT;
```

**⚠️ 极度危险操作**：

- 永久删除表结构和所有数据
- 操作前务必备份重要数据
- 生产环境强烈建议使用 `IF EXISTS`

### 2. **TRUNCATE TABLE - 清空表**

```
TRUNCATE TABLE log_entries;
TRUNCATE TABLE temporary_results;

-- 等效但更高效的写法
TRUNCATE temporary_results;
```

**TRUNCATE vs DELETE vs DROP**：

| 操作                   | 作用            | 是否可回滚 | 性能 | 自增ID重置 |
| ---------------------- | --------------- | ---------- | ---- | ---------- |
| `DELETE FROM table`    | 删除数据        | ✅ 可回滚   | 慢   | 不重置     |
| `TRUNCATE TABLE table` | 清空表          | ❌ 不可回滚 | 快   | 重置       |
| `DROP TABLE table`     | 删除表结构+数据 | ❌ 不可回滚 | 最快 | -          |

### 3. **RENAME TABLE - 重命名表**

```
-- 重命名单个表
RENAME TABLE old_users TO users;

-- 重命名多个表（原子操作）
RENAME TABLE 
    current_products TO products,
    product_archive TO archived_products;

-- 使用ALTER TABLE重命名（MySQL）
ALTER TABLE users RENAME TO system_users;
```

------

## 四、最佳实践总结

### 创建表时：

1. 1.**明确主键**：每个表都应该有主键
2. 2.**合适的数据类型**：避免过度分配存储空间
3. 3.**必要的约束**：NOT NULL, UNIQUE, CHECK等保证数据完整性
4. 4.**一致的命名规范**：表名、列名使用统一风格
5. 5.**考虑索引**：为常用查询字段添加索引

### 修改表时：

1. 1.**测试环境先行**：在生产环境执行前充分测试
2. 2.**数据备份**：ALTER TABLE前备份重要数据
3. 3.**低峰期操作**：大表修改在业务低峰期进行
4. 4.**使用IF EXISTS**：防止因对象不存在导致的错误

### 危险操作防护：

```
-- 安全操作示例
DROP TABLE IF EXISTS temp_backup;
TRUNCATE TABLE audit_log;  -- 确认无需回滚时使用
ALTER TABLE large_table ADD INDEX idx_query (query_field); -- 低峰期执行
```

这些表操作语句是数据库设计和维护的基础，熟练掌握对于任何数据库开发和管理人员都至关重要。

------

### 2. 数据操作语言 (DML)

```sql
-- 查询
SELECT [ALL|DISTINCT|DISTINCTROW] 
    column1 [AS alias], 
    expression [AS alias],
    ...
FROM table1 [AS alias]
[WHERE conditions]
[GROUP BY column1, column2 [WITH ROLLUP]]
[HAVING group_conditions]
[ORDER BY column1 [ASC|DESC], column2 [ASC|DESC]]
[LIMIT [offset,] row_count | OFFSET offset]
[FOR UPDATE | LOCK IN SHARE MODE];

-- 插入
INSERT [INTO] table_name [(column1, column2, ...)]
VALUES (value1, value2, ...),
       (value1, value2, ...),
       ...;
       
INSERT INTO table_name 
SELECT ... FROM ...;  -- 插入查询结果

INSERT INTO table_name SET column1=value1, column2=value2, ...;

-- 更新
UPDATE [LOW_PRIORITY] [IGNORE] table_name 
SET column1=value1, column2=value2, ...
[WHERE conditions]
[ORDER BY ...]
[LIMIT row_count];

-- 删除
DELETE [LOW_PRIORITY] [QUICK] [IGNORE] FROM table_name 
[WHERE conditions]
[ORDER BY ...]
[LIMIT row_count];
```

------

## 一、SELECT 语句完整架构

### SELECT 执行顺序（重要理解）

虽然书写顺序如下，但数据库的实际执行顺序不同：

**书写顺序**：SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT

**执行顺序**：FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT

```
SELECT [ALL|DISTINCT|DISTINCTROW] 
    column1 [AS alias], 
    expression [AS alias],
    ...
FROM table1 [AS alias]
[WHERE conditions]
[GROUP BY column1, column2 [WITH ROLLUP]]
[HAVING group_conditions]
[ORDER BY column1 [ASC|DESC], column2 [ASC|DESC]]
[LIMIT [offset,] row_count | OFFSET offset]
[FOR UPDATE | LOCK IN SHARE MODE];
```

------

## 二、SELECT 子句详解

### 1. 选择列和表达式

**基本列选择**：

```
-- 选择特定列
SELECT id, name, email FROM users;

-- 选择所有列（生产环境谨慎使用）
SELECT * FROM products;

-- 使用表前缀（多表查询时有用）
SELECT users.id, users.name, orders.amount 
FROM users, orders 
WHERE users.id = orders.user_id;
```

**使用表达式和函数**：

```
-- 算术表达式
SELECT product_name, price, quantity, price * quantity AS total_value 
FROM order_items;

-- 字符串函数
SELECT 
    first_name,
    last_name,
    CONCAT(first_name, ' ', last_name) AS full_name,
    UPPER(email) AS email_upper,
    LENGTH(address) AS addr_length
FROM customers;

-- 日期函数
SELECT 
    order_id,
    order_date,
    YEAR(order_date) AS order_year,
    DATE_ADD(order_date, INTERVAL 7 DAY) AS expected_delivery
FROM orders;

-- CASE 条件表达式
SELECT 
    product_name,
    price,
    CASE 
        WHEN price > 1000 THEN '高价'
        WHEN price > 100 THEN '中价' 
        ELSE '低价'
    END AS price_category
FROM products;
```

### 2. 列别名 (AS)

```
SELECT 
    employee_id AS id,
    monthly_salary * 12 AS annual_salary,
    department_id AS dept,
    CONCAT(last_name, ', ', first_name) AS full_name
FROM employees;
-- AS 关键字可选，但建议保留以提高可读性
```

### 3. 去重选项

**`DISTINCT`- 去除重复行**：

```
-- 基本的去重
SELECT DISTINCT department FROM employees;

-- 多列去重（所有指定列的组合唯一）
SELECT DISTINCT department, job_title FROM employees;

-- 与表达式结合
SELECT DISTINCT YEAR(hire_date) AS hire_year FROM employees;
```

**`DISTINCT`vs `ALL`**：

```
-- 默认是 ALL，显示所有行（包括重复）
SELECT ALL department FROM employees;     -- 显示所有部门，包括重复
SELECT DISTINCT department FROM employees; -- 每个部门只显示一次

-- 计算不重复值的数量
SELECT COUNT(DISTINCT department) FROM employees;
```

------

## 三、FROM 子句详解

### 1. 单表查询

```
SELECT * FROM products;
SELECT name, price FROM products WHERE price > 100;
```

### 2. 表别名

```
-- 简化书写，提高可读性
SELECT e.emp_id, e.name, d.dept_name 
FROM employees AS e 
INNER JOIN departments AS d ON e.dept_id = d.dept_id;

-- AS 可选
SELECT p.name, p.price, c.category_name 
FROM products p, categories c 
WHERE p.category_id = c.id;
```

### 3. 多表连接（详见后面章节）

```
-- 内连接
SELECT o.order_id, c.customer_name, o.order_date
FROM orders o
INNER JOIN customers c ON o.customer_id = c.customer_id;

-- 左外连接
SELECT e.name, d.dept_name
FROM employees e
LEFT JOIN departments d ON e.dept_id = d.dept_id;
```

### 4. 子查询作为表（派生表）

```
-- 子查询结果作为临时表
SELECT dept_stats.dept_name, dept_stats.avg_salary
FROM (
    SELECT d.dept_name, AVG(e.salary) AS avg_salary
    FROM departments d
    JOIN employees e ON d.dept_id = e.dept_id
    GROUP BY d.dept_name
) AS dept_stats
WHERE dept_stats.avg_salary > 50000;
```

------

## 四、WHERE 子句详解

### 1. 比较运算符

```
SELECT * FROM products WHERE price = 100;           -- 等于
SELECT * FROM products WHERE price <> 100;         -- 不等于
SELECT * FROM products WHERE price > 50;           -- 大于
SELECT * FROM products WHERE price >= 50;          -- 大于等于
SELECT * FROM products WHERE price < 200;          -- 小于
SELECT * FROM products WHERE price <= 200;         -- 小于等于

-- 范围检查
SELECT * FROM products WHERE price BETWEEN 50 AND 200;     -- 50 <= price <= 200
SELECT * FROM employees WHERE hire_date BETWEEN '2020-01-01' AND '2023-12-31';
```

### 2. 逻辑运算符

```
-- AND: 同时满足多个条件
SELECT * FROM employees 
WHERE department = 'Sales' AND salary > 50000;

-- OR: 满足任意一个条件
SELECT * FROM products 
WHERE category = 'Electronics' OR category = 'Books';

-- NOT: 取反
SELECT * FROM customers 
WHERE NOT country = 'USA';

-- 复杂逻辑组合
SELECT * FROM orders 
WHERE (status = 'Shipped' OR status = 'Delivered') 
  AND order_date >= '2024-01-01'
  AND NOT customer_id IN (1001, 1002, 1003);
```

### 3. 模糊匹配 (LIKE)

```
-- % 匹配任意字符（包括空字符）
SELECT * FROM products WHERE name LIKE 'Apple%';    -- 以Apple开头
SELECT * FROM products WHERE name LIKE '%Phone';    -- 以Phone结尾
SELECT * FROM products WHERE name LIKE '%Pro%';     -- 包含Pro

-- _ 匹配单个字符
SELECT * FROM users WHERE username LIKE 'john_';    -- john后跟一个字符
SELECT * FROM products WHERE code LIKE 'A__B';      -- A开头，B结尾，中间两个字符

-- 转义特殊字符
SELECT * FROM files WHERE name LIKE '100\% complete';  -- 匹配 "100% complete"
```

### 4. 集合操作

```
-- IN: 在指定值列表中
SELECT * FROM products WHERE category IN ('Electronics', 'Books', 'Clothing');
SELECT * FROM employees WHERE department_id IN (SELECT dept_id FROM departments WHERE active = 1);

-- NOT IN: 不在指定值列表中
SELECT * FROM customers WHERE country NOT IN ('USA', 'UK', 'CN');
```

### 5. 空值检查

```
-- IS NULL: 是空值
SELECT * FROM employees WHERE manager_id IS NULL;      -- 没有经理的员工

-- IS NOT NULL: 不是空值  
SELECT * FROM customers WHERE phone IS NOT NULL;       -- 有电话号码的客户

-- 常见错误：不要用 = NULL
SELECT * FROM users WHERE email = NULL;               -- ❌ 错误！总是返回空集
SELECT * FROM users WHERE email IS NULL;              -- ✅ 正确
```

------

## 五、GROUP BY 和聚合函数

### 1. 基本分组

```
-- 按部门分组，计算每个部门的统计信息
SELECT 
    department,
    COUNT(*) AS employee_count,      -- 员工数量
    AVG(salary) AS avg_salary,      -- 平均工资
    MAX(salary) AS max_salary,      -- 最高工资
    MIN(salary) AS min_salary,       -- 最低工资
    SUM(salary) AS total_salary      -- 工资总额
FROM employees
GROUP BY department;
```

### 2. 多列分组

```
-- 按部门和职位分组
SELECT 
    department,
    job_title,
    COUNT(*) AS count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department, job_title;      -- 先按部门分，再按职位分
```

### 3. 聚合函数详解

```
SELECT 
    COUNT(*) AS total_rows,              -- 总行数
    COUNT(DISTINCT department) AS dept_count, -- 不重复部门数
    AVG(salary) AS average_salary,       -- 平均值（忽略NULL）
    SUM(salary) AS total_salary,         -- 总和
    MAX(hire_date) AS latest_hire,      -- 最晚入职日期
    MIN(hire_date) AS earliest_hire,    -- 最早入职日期
    GROUP_CONCAT(name SEPARATOR ', ') AS employee_names  -- 连接所有名字
FROM employees
WHERE salary > 30000;
```

### 4. WITH ROLLUP - 小计和总计（组内汇总）

```
-- 生成分层小计
SELECT 
    department,
    job_title, 
    COUNT(*) AS employee_count,
    AVG(salary) AS avg_salary
FROM employees
GROUP BY department, job_title WITH ROLLUP;

-- 结果示例：
-- IT, Developer, 5, 75000    -- IT部门Developer职位
-- IT, Manager, 2, 90000      -- IT部门Manager职位  
-- IT, NULL, 7, 80000         -- IT部门小计（job_title为NULL）
-- Sales, Developer, 3, 70000 -- Sales部门Developer职位
-- Sales, NULL, 3, 70000      -- Sales部门小计
-- NULL, NULL, 10, 77000      -- 总计（department和job_title都为NULL）
```

------

## 六、HAVING 子句详解

### HAVING vs WHERE 的区别：

- **WHERE**：在分组前过滤**行**，不能使用聚合函数
- **HAVING**：在分组后过滤**组**，可以使用聚合函数

```
-- 查找员工数量超过10人的部门
SELECT department, COUNT(*) AS employee_count
FROM employees
GROUP BY department
HAVING COUNT(*) > 10;

-- 查找平均工资超过5万且员工数量大于5的部门
SELECT department, AVG(salary) AS avg_salary, COUNT(*) AS emp_count
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000 AND COUNT(*) > 5;

-- 复杂的HAVING条件
SELECT 
    YEAR(hire_date) AS hire_year,
    department,
    AVG(salary) AS avg_salary
FROM employees
WHERE salary > 30000  -- 先过滤掉低工资员工
GROUP BY hire_year, department
HAVING AVG(salary) > 50000 AND COUNT(*) >= 3  -- 再过滤分组结果
ORDER BY hire_year DESC, avg_salary DESC;
```

------

## 七、ORDER BY 排序详解

### 1. 基本排序

```
-- 单列排序
SELECT name, salary FROM employees ORDER BY salary DESC;     -- 降序
SELECT name, hire_date FROM employees ORDER BY hire_date;    -- 升序（默认）

-- 多列排序：先按部门升序，同部门内按工资降序
SELECT department, name, salary 
FROM employees 
ORDER BY department ASC, salary DESC;

-- 按表达式排序
SELECT name, salary, salary * 12 AS annual_salary
FROM employees
ORDER BY salary * 12 DESC;

-- 按选择列表中的位置排序（不推荐，可读性差）
SELECT name, department, salary 
FROM employees 
ORDER BY 2, 3 DESC;  -- 按第2列(department)，第3列(salary)排序
```

### 2. 高级排序技巧

```
-- 自定义排序顺序
SELECT product_name, category, price
FROM products
ORDER BY 
    CASE category
        WHEN 'Electronics' THEN 1
        WHEN 'Books' THEN 2
        WHEN 'Clothing' THEN 3
        ELSE 4
    END,
    price DESC;

-- NULL值排序控制
SELECT name, commission_pct
FROM employees
ORDER BY 
    CASE WHEN commission_pct IS NULL THEN 1 ELSE 0 END,  -- NULL值放最后
    commission_pct DESC;
```

------

## 八、LIMIT 和分页查询

### 1. 基本限制

```
-- 限制返回行数
SELECT * FROM products ORDER BY price DESC LIMIT 10;      -- 前10条
SELECT * FROM products LIMIT 5;                          -- 前5条

-- 分页查询：LIMIT offset, count
SELECT * FROM products ORDER BY product_id LIMIT 0, 10;  -- 第1页：0-9条
SELECT * FROM products ORDER BY product_id LIMIT 10, 10; -- 第2页：10-19条
SELECT * FROM products ORDER BY product_id LIMIT 20, 10; -- 第3页：20-29条

-- 使用OFFSET语法（更清晰）
SELECT * FROM products ORDER BY product_id LIMIT 10 OFFSET 0;   -- 第1页
SELECT * FROM products ORDER BY product_id LIMIT 10 OFFSET 10;  -- 第2页
SELECT * FROM products ORDER BY product_id LIMIT 10 OFFSET 20;  -- 第3页
```

### 2. 分页最佳实践

```
-- 高效的分页查询（使用索引列排序）
SELECT product_id, name, price
FROM products
WHERE status = 'active'
ORDER BY product_id          -- 使用有索引的列提高性能
LIMIT 20 OFFSET 40;

-- 获取分页元信息
SELECT 
    COUNT(*) AS total_items,
    CEIL(COUNT(*) / 20.0) AS total_pages  -- 每页20条，计算总页数
FROM products
WHERE status = 'active';
```

------

## 九、锁定查询（事务控制）

### 1. FOR UPDATE - 行级排他锁

```
-- 在事务中锁定选中的行，防止其他事务修改
START TRANSACTION;

SELECT * FROM accounts 
WHERE account_id = 1001 
FOR UPDATE;  -- 锁定该账户记录

-- 执行更新操作（其他事务无法修改锁定的行）
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1001;

COMMIT;  -- 提交后释放锁
```

### 2. LOCK IN SHARE MODE - 共享锁

```
-- 允许其他事务读，但不允许修改锁定的行
START TRANSACTION;

SELECT * FROM products 
WHERE stock_quantity < 10 
LOCK IN SHARE MODE;  -- 其他事务可以读但不能修改

-- 执行一些检查逻辑...
COMMIT;
```

### 3. 锁定使用场景

```
-- 库存扣减（防止超卖）
START TRANSACTION;
SELECT stock_quantity FROM products WHERE product_id = 123 FOR UPDATE;
-- 检查库存是否充足，然后扣减
UPDATE products SET stock_quantity = stock_quantity - 1 WHERE product_id = 123;
COMMIT;

-- 资金转账（保证一致性）
START TRANSACTION;
SELECT * FROM accounts WHERE account_id IN (1001, 1002) FOR UPDATE;
-- 执行转账逻辑
UPDATE accounts SET balance = balance - 100 WHERE account_id = 1001;
UPDATE accounts SET balance = balance + 100 WHERE account_id = 1002;
COMMIT;
```

------

## 十、完整综合示例

```
-- 复杂的业务查询：获取2023年每个部门销售前3名的员工
SELECT 
    d.dept_name AS department,
    e.employee_name,
    e.job_title,
    SUM(s.sale_amount) AS total_sales,
    RANK() OVER (PARTITION BY d.dept_id ORDER BY SUM(s.sale_amount) DESC) AS sales_rank
FROM departments d
INNER JOIN employees e ON d.dept_id = e.dept_id
INNER JOIN sales s ON e.employee_id = s.employee_id
WHERE s.sale_date BETWEEN '2023-01-01' AND '2023-12-31'
  AND e.status = 'active'
  AND s.sale_status = 'completed'
GROUP BY d.dept_id, e.employee_id, e.employee_name, e.job_title
HAVING SUM(s.sale_amount) > 100000  -- 只显示销售额超过10万的
ORDER BY d.dept_name, total_sales DESC
LIMIT 10;  -- 限制返回结果数量
```

------

## 十一、性能优化建议

1. 1.**避免 SELECT***：只选择需要的列
2. 2.**使用 WHERE 过滤**：尽早减少处理的数据量
3. 3.**合理使用索引**：为WHERE、JOIN、ORDER BY的列创建索引
4. 4.**LIMIT 分页**：避免返回大量数据
5. 5.**EXPLAIN 分析**：使用EXPLAIN查看执行计划

```
-- 查看查询执行计划
EXPLAIN SELECT * FROM employees WHERE department = 'Sales' ORDER BY salary DESC;

-- 优化后的查询
EXPLAIN SELECT employee_id, name, salary 
FROM employees 
WHERE department = 'Sales' 
ORDER BY salary DESC 
LIMIT 100;
```

这个详细的SELECT指南涵盖了从基础到高级的所有方面，是SQL查询的核心知识。

------

## 一、INSERT 语句完整架构

### 三种主要语法形式：

```
-- 1. 标准VALUES插入（单行或多行）
INSERT [INTO] table_name [(column1, column2, ...)]
VALUES (value1, value2, ...),
       (value1, value2, ...),
       ...;

-- 2. 插入查询结果（从其他表复制数据）
INSERT INTO table_name [(column1, column2, ...)]
SELECT column1, column2, ... 
FROM source_table 
[WHERE conditions];

-- 3. SET语法插入（MySQL扩展）
INSERT INTO table_name 
SET column1 = value1, 
    column2 = value2,
    ...;
```

------

## 二、标准 VALUES 插入详解

### 1. 基本单行插入

**指定列名插入（推荐）**：

```
-- 明确指定列名和值（顺序对应）
INSERT INTO employees (first_name, last_name, email, hire_date, salary, department_id)
VALUES ('张', '三', 'zhangsan@company.com', '2024-01-15', 75000.00, 3);
```

**不指定列名插入（需谨慎）**：

```
-- 必须提供所有列的值，且顺序必须与表定义完全一致
INSERT INTO employees 
VALUES (NULL, '张', '三', 'zhangsan@company.com', '2024-01-15', 75000.00, 3, NULL);
-- ⚠️ 危险：如果表结构变更，此语句可能失败
```

### 2. 多行批量插入（高性能）

```
-- 一次性插入多行数据（大幅提高性能）
INSERT INTO products (product_name, category, price, stock_quantity)
VALUES 
    ('iPhone 15', 'Electronics', 999.99, 100),
    ('MacBook Pro', 'Electronics', 1999.99, 50),
    ('AirPods', 'Electronics', 179.99, 200),
    ('SQL指南', 'Books', 49.99, 300);
```

**批量插入的优势**：

- 减少网络往返次数
- 减少事务开销
- 提高插入速度（通常快5-10倍）

### 3. 处理默认值和NULL

```
-- 使用DEFAULT关键字
INSERT INTO orders (order_date, customer_id, status, total_amount)
VALUES (CURRENT_DATE(), 1001, DEFAULT, 299.99);  -- status使用默认值

-- 显式使用NULL
INSERT INTO customers (name, email, phone, address)
VALUES ('李四', 'lisi@email.com', NULL, '北京市朝阳区');  -- phone允许为NULL

-- 省略有默认值的列
INSERT INTO products (product_name, price)  -- stock_quantity有默认值0
VALUES ('新商品', 89.99);

-- 使用表达式和函数作为值
INSERT INTO employees (first_name, last_name, email, hire_date, salary)
VALUES (
    '王', 
    '五', 
    LOWER(CONCAT('wang', 'wu', '@company.com')),  -- 表达式生成邮箱
    CURDATE(),                                    -- 当前日期
    ROUND(50000 * 1.1, 2)                        -- 计算后的薪资
);
```

### 4. 自增字段处理

```
-- 表结构：id INT AUTO_INCREMENT PRIMARY KEY
INSERT INTO users (username, email, created_at)  -- 省略id，自动生成
VALUES ('john_doe', 'john@example.com', NOW());

-- 获取自增ID（在应用程序中）
INSERT INTO orders (customer_id, order_date, total_amount)
VALUES (1001, NOW(), 299.99);

-- 在MySQL中获取最后插入的ID
SELECT LAST_INSERT_ID();  -- 返回刚刚插入的自增ID

-- 显式指定自增ID（通常不推荐）
INSERT INTO products (product_id, product_name, price)  -- 覆盖自增
VALUES (1000, '特殊商品', 199.99);  -- 后续自增从1001开始
```

------

## 三、INSERT...SELECT 插入查询结果

### 1. 从其他表复制数据

**基本数据迁移**：

```
-- 从旧表复制数据到新表
INSERT INTO new_employees (emp_name, emp_email, hire_date, salary)
SELECT name, email, start_date, monthly_salary 
FROM old_employees 
WHERE status = 'active';

-- 包含计算和转换
INSERT INTO financial_reports (report_date, department, revenue, expenses)
SELECT 
    report_date,
    department_name,
    total_income,
    operating_costs + salary_costs AS total_expenses
FROM raw_financial_data 
WHERE report_date >= '2024-01-01';
```

### 2. 数据聚合后插入

```
-- 插入聚合统计结果
INSERT INTO sales_summary (sale_date, product_category, total_sales, avg_price)
SELECT 
    DATE(sale_time) AS sale_date,
    product_category,
    COUNT(*) AS total_sales,
    AVG(unit_price) AS avg_price
FROM sales_transactions 
WHERE sale_time BETWEEN '2024-01-01' AND '2024-01-31'
GROUP BY DATE(sale_time), product_category;
```

### 3. 数据归档和备份

```
-- 归档旧数据
INSERT INTO orders_archive 
SELECT * FROM orders 
WHERE order_date < '2023-01-01';

-- 备份特定条件的数据
INSERT INTO important_customers_backup
SELECT c.* 
FROM customers c
WHERE c.total_orders > 10 
   OR c.total_spent > 10000;
```

### 4. 复杂数据转换

```
-- 数据清洗和转换后插入
INSERT INTO clean_customer_data (customer_id, full_name, clean_phone, region)
SELECT 
    customer_id,
    TRIM(CONCAT(first_name, ' ', last_name)) AS full_name,
    CASE 
        WHEN phone LIKE '+86%' THEN REPLACE(phone, '+86', '')
        WHEN phone LIKE '86%' THEN SUBSTRING(phone, 3)
        ELSE phone 
    END AS clean_phone,
    CASE 
        WHEN province IN ('北京','天津','上海','重庆') THEN '直辖市'
        WHEN province IN ('江苏','浙江','广东') THEN '沿海省份'
        ELSE '其他地区'
    END AS region
FROM raw_customer_data 
WHERE email LIKE '%@%';  -- 基本邮箱格式验证
```

------

## 四、INSERT...SET 语法（MySQL扩展）

### 1. 基本用法

```
-- 类似于UPDATE语法，可读性更好
INSERT INTO employees 
SET 
    first_name = '赵',
    last_name = '六',
    email = 'zhaoliu@company.com',
    hire_date = '2024-02-01',
    salary = 68000.00,
    department_id = 2;
```

### 2. 复杂表达式和函数

```
INSERT INTO website_stats 
SET 
    stat_date = CURDATE(),
    page_views = (SELECT COUNT(*) FROM page_visits WHERE visit_date = CURDATE()),
    unique_visitors = (SELECT COUNT(DISTINCT visitor_id) FROM page_visits WHERE visit_date = CURDATE()),
    avg_session_duration = ROUND(
        (SELECT AVG(duration_seconds) FROM sessions WHERE DATE(start_time) = CURDATE()), 
        2
    );
```

### 3. 与VALUES语法对比

| 特性     | VALUES语法 | SET语法     |
| -------- | ---------- | ----------- |
| 多行插入 | ✅ 支持     | ❌ 不支持    |
| 标准SQL  | ✅ 是       | ❌ MySQL扩展 |
| 可读性   | 中等       | ✅ 更好      |
| 列顺序   | 必须一致   | 🔄 任意顺序  |

------

## 五、高级插入技巧

### 1. 条件插入（避免重复）

**使用IGNORE忽略错误**：

```
-- 如果遇到重复键错误，忽略并继续插入其他行
INSERT IGNORE INTO unique_products (product_code, product_name, price)
VALUES 
    ('P1001', 'iPhone 15', 999.99),
    ('P1002', 'MacBook Pro', 1999.99),  -- 如果P1002已存在，跳过此行
    ('P1003', 'AirPods', 179.99);
```

**ON DUPLICATE KEY UPDATE（重复时更新）**：

```
-- 如果记录已存在，则更新；不存在，则插入
INSERT INTO product_stock (product_id, product_name, stock_quantity)
VALUES (1001, 'iPhone 15', 50)
ON DUPLICATE KEY UPDATE 
    stock_quantity = stock_quantity + VALUES(stock_quantity),
    last_updated = NOW();

-- 批量upsert操作
INSERT INTO user_scores (user_id, game_type, score, play_count)
VALUES 
    (1001, 'puzzle', 1500, 1),
    (1002, 'puzzle', 1800, 1),
    (1003, 'puzzle', 1200, 1)
ON DUPLICATE KEY UPDATE 
    score = GREATEST(score, VALUES(score)),  -- 保留最高分
    play_count = play_count + 1,
    last_played = NOW();
```

**REPLACE INTO（删除后插入）**：

```
-- 如果记录存在，先删除再插入（注意：会删除整行，包括未指定的列）
REPLACE INTO configuration (config_key, config_value, updated_by)
VALUES ('max_login_attempts', '5', 'system');
```

### 2. 插入大量数据的性能优化

**分批插入**：

```
-- 不好的做法：一次性插入10万条
-- INSERT INTO log_entries (...) VALUES (1,...), (2,...), ..., (100000,...);

-- 好的做法：分批插入，每批1000条
INSERT INTO log_entries (entry_data, created_at) VALUES (...);  -- 第1批1000条
INSERT INTO log_entries (entry_data, created_at) VALUES (...);  -- 第2批1000条
-- ... 共100批完成10万条插入
```

**禁用索引和约束（大数据量时）**：

```
-- 大数据量导入时临时优化
ALTER TABLE large_table DISABLE KEYS;  -- 禁用非唯一索引

-- 执行批量插入...
INSERT INTO large_table (...) VALUES (...), (...), ...;

ALTER TABLE large_table ENABLE KEYS;   -- 重新启用索引（会重建索引）
```

### 3. 插入时的数据验证

**使用CHECK约束**：

```
-- 表定义时添加约束
CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE,
    salary DECIMAL(10,2) CHECK (salary >= 0),
    hire_date DATE CHECK (hire_date <= CURDATE())
);

-- 插入时会自动验证
INSERT INTO employees (name, email, salary, hire_date)
VALUES ('测试', 'test@company.com', -1000, '2025-01-01');  -- ❌ 会失败
```

**使用BEFORE INSERT触发器验证**：

```
DELIMITER //
CREATE TRIGGER validate_employee_data 
BEFORE INSERT ON employees
FOR EACH ROW
BEGIN
    -- 验证邮箱格式
    IF NEW.email NOT LIKE '%@%.%' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '无效的邮箱格式';
    END IF;
    
    -- 验证未来入职日期
    IF NEW.hire_date > CURDATE() THEN
        SET NEW.hire_date = CURDATE();  -- 自动修正为今天
    END IF;
END//
DELIMITER ;
```

------

## 六、实际应用场景示例

### 1. 用户注册系统

```
-- 新用户注册（带默认值）
INSERT INTO users (username, email, password_hash, registration_date, status)
VALUES (
    'new_user_123', 
    'user@example.com', 
    SHA2('secure_password', 256),  -- 密码加密
    NOW(), 
    'active'  -- 默认状态
);

-- 获取新用户的ID
SET @new_user_id = LAST_INSERT_ID();

-- 插入用户配置档案
INSERT INTO user_profiles (user_id, display_name, bio, avatar_url)
VALUES (@new_user_id, '新用户', NULL, '/images/default-avatar.png');
```

### 2. 电商订单系统

```
-- 1. 创建订单
INSERT INTO orders (order_number, customer_id, order_date, total_amount, status)
VALUES (
    CONCAT('ORD', DATE_FORMAT(NOW(), '%Y%m%d'), LPAD(FLOOR(RAND()*10000), 4, '0')),
    1001,
    NOW(),
    299.99,
    'pending'
);

SET @order_id = LAST_INSERT_ID();

-- 2. 插入订单项
INSERT INTO order_items (order_id, product_id, product_name, quantity, unit_price, subtotal)
VALUES 
    (@order_id, 2001, 'iPhone 15', 1, 999.99, 999.99),
    (@order_id, 2002, 'AirPods', 2, 179.99, 359.98);

-- 3. 更新库存
INSERT INTO inventory_changes (product_id, change_type, quantity, reference_id, change_date)
SELECT 
    product_id, 
    'sale', 
    -quantity,  -- 负数表示减少库存
    @order_id,
    NOW()
FROM order_items 
WHERE order_id = @order_id
ON DUPLICATE KEY UPDATE quantity = quantity + VALUES(quantity);
```

### 3. 日志和审计系统

```
-- 批量插入系统日志
INSERT INTO system_logs (log_level, component, message, user_id, ip_address, created_at)
VALUES 
    ('INFO', 'Authentication', '用户登录成功', 1001, '192.168.1.100', NOW()),
    ('WARN', 'Payment', '支付处理时间过长', NULL, '10.0.1.50', NOW()),
    ('ERROR', 'Database', '连接超时', NULL, '10.0.2.100', NOW()),
    ('INFO', 'Order', '订单创建成功', 1002, '192.168.1.101', NOW());

-- 从临时表归档日志
INSERT INTO archived_logs_2024 
SELECT * FROM system_logs 
WHERE created_at < '2024-01-01' 
  AND log_level != 'DEBUG';
```

### 4. 数据同步和ETL

```
-- 从外部数据源同步
INSERT INTO product_catalog (external_id, product_name, category, price, source_system)
SELECT 
    p.id,
    p.name,
    COALESCE(p.category, 'Uncategorized'),
    ROUND(p.price * 1.1, 2),  -- 增加10%作为利润
    'ERP_SYSTEM'
FROM external_products p
WHERE p.status = 'active'
  AND p.last_updated >= DATE_SUB(NOW(), INTERVAL 1 DAY)
ON DUPLICATE KEY UPDATE 
    product_name = VALUES(product_name),
    price = VALUES(price),
    last_synced = NOW();
```

------

## 七、错误处理和最佳实践

### 1. 错误处理示例

```
-- 在存储过程中处理插入错误
DELIMITER //
CREATE PROCEDURE SafeInsertCustomer(
    IN p_name VARCHAR(100),
    IN p_email VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        -- 记录错误信息
        INSERT INTO error_logs (procedure_name, error_message, error_time)
        VALUES ('SafeInsertCustomer', '插入客户数据失败', NOW());
        
        -- 返回错误标识
        SELECT -1 AS result_id, '插入失败' AS message;
    END;
    
    -- 尝试插入
    INSERT INTO customers (name, email, created_at)
    VALUES (p_name, p_email, NOW());
    
    -- 成功返回
    SELECT LAST_INSERT_ID() AS result_id, '插入成功' AS message;
END//
DELIMITER ;
```

### 2. 性能最佳实践

**批量插入大小优化**：

```
-- 合适的批量大小（通常100-1000条/批）
INSERT INTO large_table (data) VALUES (...);  -- 100条/批

-- 使用事务包装批量插入
START TRANSACTION;
INSERT INTO table1 (...) VALUES (...), (...), ...;
INSERT INTO table2 (...) VALUES (...), (...), ...;
COMMIT;
```

**预处理语句（在应用程序中）**：

```
# Python示例 - 使用预处理语句
import mysql.connector

sql = "INSERT INTO users (name, email, created_at) VALUES (%s, %s, %s)"
data = [
    ('User1', 'user1@email.com', '2024-01-01'),
    ('User2', 'user2@email.com', '2024-01-02'),
    # ... 更多数据
]

cursor.executemany(sql, data)  # 批量执行
connection.commit()
```

### 3. 安全最佳实践

**防止SQL注入**：

```
-- ❌ 危险：直接拼接字符串
INSERT INTO users (name) VALUES ('$user_input');  -- 可能被注入

-- ✅ 安全：使用参数化查询
INSERT INTO users (name) VALUES (?);  -- 应用程序中使用预处理语句
```

**数据验证和清理**：

```
-- 在插入前清理数据
INSERT INTO comments (post_id, author, content, created_at)
VALUES 
    (1001, 
     TRIM(REPLACE(@author_name, '<script>', '')),  -- 清理作者名
     REPLACE(REPLACE(@content, '<script>', ''), '\r\n', '<br>'),  -- 清理内容
     NOW()
    );
```

这个全面的INSERT指南涵盖了从基础语法到高级技巧的所有方面，是数据库操作的核心知识。

------

## 一、UPDATE 语句完整架构

### 基本语法和扩展：

```
UPDATE [LOW_PRIORITY] [IGNORE] table_name 
SET column1 = value1, 
    column2 = value2,
    ...
[WHERE conditions]
[ORDER BY column1 [ASC|DESC], ...]
[LIMIT row_count]
[RETURNING column1, column2, ...];  -- PostgreSQL、SQL Server等支持
```

------

## 二、UPDATE 子句详解

### 1. 表选项修饰符

#### **`LOW_PRIORITY`（MySQL）**

```
-- 低优先级更新，等待其他读操作完成后再执行
UPDATE LOW_PRIORITY large_table 
SET status = 'processed' 
WHERE processed = 0;
```

- **适用场景**：后台批量处理，不紧急的数据更新
- **效果**：降低对正常查询性能的影响

#### **`IGNORE`- 忽略错误**

```
-- 忽略更新过程中的错误（如重复键、约束违反等）
UPDATE IGNORE products 
SET product_code = 'NEW-CODE' 
WHERE category = 'Electronics';
```

- **忽略的错误类型**： 重复唯一键冲突 数据截断警告 外键约束违反
- **风险**：可能导致数据不一致，谨慎使用

### 2. 多表更新语法

```
-- 标准多表更新（基于关联条件）
UPDATE employees e, departments d 
SET e.salary = e.salary * 1.1,
    d.budget = d.budget * 1.05
WHERE e.dept_id = d.dept_id 
  AND d.location = '上海';

-- 使用JOIN语法（更清晰）
UPDATE employees e
JOIN departments d ON e.dept_id = d.dept_id
SET e.salary = e.salary * 1.1,
    e.updated_at = NOW()
WHERE d.budget > 1000000;
```

------

## 三、SET 子句详解

### 1. 基本赋值操作

```
-- 单字段更新
UPDATE users SET last_login = NOW() WHERE user_id = 1001;

-- 多字段同时更新
UPDATE products 
SET price = 99.99,
    stock = stock - 1,
    last_updated = NOW()
WHERE product_id = 2001;

-- 基于表达式的更新
UPDATE employees 
SET salary = salary * 1.1,  -- 涨薪10%
    vacation_days = vacation_days + 5  -- 增加年假
WHERE hire_date < '2020-01-01';
```

### 2. 条件更新（CASE WHEN）

```
-- 根据不同条件进行不同更新
UPDATE employees 
SET salary = CASE 
    WHEN performance_rating = 'A' THEN salary * 1.15  -- 优秀员工加薪15%
    WHEN performance_rating = 'B' THEN salary * 1.10  -- 良好员工加薪10%
    WHEN performance_rating = 'C' THEN salary * 1.05  -- 合格员工加薪5%
    ELSE salary  -- 其他情况不变
END,
bonus = CASE 
    WHEN department = 'Sales' THEN salary * 0.1  -- 销售部门10%奖金
    ELSE salary * 0.05  -- 其他部门5%奖金
END
WHERE status = 'active';
```

### 3. 基于其他列的更新

```
-- 列间数据转移或计算
UPDATE orders 
SET total_amount = subtotal + tax_amount - discount_amount,
    net_amount = total_amount - handling_fee;

-- 字符串操作
UPDATE customers 
SET full_name = CONCAT(first_name, ' ', last_name),
    email = LOWER(CONCAT(first_name, '.', last_name, '@company.com'))
WHERE full_name IS NULL;
```

### 4. JSON字段更新（MySQL 5.7+）

```
-- 更新JSON对象的特定属性
UPDATE products 
SET specifications = JSON_SET(
    specifications, 
    '$.weight', '2.5kg',
    '$.dimensions.length', '30cm'
)
WHERE product_id = 3001;

-- 向JSON数组添加元素
UPDATE user_profiles 
SET preferences = JSON_ARRAY_APPEND(
    preferences,
    '$.recent_searches', 
    JSON_QUOTE('新搜索词')
)
WHERE user_id = 1001;
```

------

## 四、WHERE 子句详解（极其重要！）

### 1. 基本条件过滤

```
-- 单条件更新
UPDATE products SET price = price * 0.9 WHERE category = '清仓商品';

-- 多条件组合
UPDATE employees 
SET status = 'on_leave'
WHERE department = 'HR' 
  AND hire_date > '2020-01-01'
  AND vacation_days > 20;
```

### 2. 子查询条件

```
-- 基于子查询结果更新
UPDATE products p
SET p.discount_price = p.price * 0.8
WHERE p.product_id IN (
    SELECT product_id 
    FROM low_sales_products 
    WHERE sales_quantity < 10
);

-- 关联子查询更新
UPDATE employees e
SET e.salary = e.salary * 1.1
WHERE e.salary < (
    SELECT AVG(salary) 
    FROM employees 
    WHERE department = e.department
);
```

### 3. EXISTS/NOT EXISTS 条件

```
-- 更新有订单的客户
UPDATE customers c
SET c.last_purchase_date = (
    SELECT MAX(order_date) 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
)
WHERE EXISTS (
    SELECT 1 
    FROM orders o 
    WHERE o.customer_id = c.customer_id
);

-- 更新30天内无活动的用户
UPDATE users u
SET u.status = 'inactive',
    u.inactive_since = NOW()
WHERE u.status = 'active'
  AND NOT EXISTS (
    SELECT 1 
    FROM user_sessions s 
    WHERE s.user_id = u.user_id 
      AND s.login_time > DATE_SUB(NOW(), INTERVAL 30 DAY)
);
```

------

## 五、ORDER BY 和 LIMIT 子句

### 1. 有序更新

```
-- 按优先级顺序更新（先处理重要的记录）
UPDATE task_queue 
SET status = 'processing',
    assigned_at = NOW()
WHERE status = 'pending'
ORDER BY priority DESC, created_at ASC  -- 先高优先级，先创建的
LIMIT 10;  -- 每次只处理10条

-- 避免死锁的排序更新
UPDATE bank_accounts 
SET balance = balance - 100 
WHERE account_id IN (1001, 1002)
ORDER BY account_id;  -- 按固定顺序更新，避免死锁
```

### 2. 分批次更新（大数据量）

```
-- 大批量数据分批次更新，避免锁表时间过长
UPDATE large_table 
SET processed = 1,
    processed_at = NOW()
WHERE processed = 0
ORDER BY id  -- 按主键顺序，提高性能
LIMIT 1000;  -- 每次更新1000条

-- 在应用程序中循环执行，直到所有数据更新完成
```

### 3. 顶部记录更新

```sql
-- 更新前N条记录
UPDATE products 
SET featured = 1
WHERE category = 'Electronics'
ORDER BY sales_volume DESC  -- 按销量降序
LIMIT 5;  -- 只更新销量前5的产品

-- 跳过前M条，更新接下来的N条（模拟OFFSET）
UPDATE user_notifications 
SET status = 'read'
WHERE user_id = 1001 
  AND status = 'unread'
ORDER BY created_at DESC
LIMIT 10;  -- 只标记最新的10条未读通知为已读
```

------

## 六、高级更新技巧

### 1. 基于关联表的更新

```sql
-- 使用JOIN进行关联更新
UPDATE employees e
JOIN departments d ON e.dept_id = d.dept_id
JOIN company_budget cb ON d.company_id = cb.company_id
SET e.salary = e.salary * (1 + cb.salary_increase_rate),
    e.updated_at = NOW()
WHERE cb.fiscal_year = 2024
  AND e.performance_rating >= 'B';

-- 使用多表SET语法
UPDATE orders o, customers c, products p
SET o.total_amount = o.quantity * p.price,
    c.total_orders = c.total_orders + 1,
    p.total_sold = p.total_sold + o.quantity
WHERE o.customer_id = c.customer_id
  AND o.product_id = p.product_id
  AND o.status = 'completed';
```

### 2. 增量更新和计数器

```
-- 页面浏览量统计
UPDATE article_stats 
SET view_count = view_count + 1,
    daily_views = daily_views + 1,
    last_viewed = NOW()
WHERE article_id = 5001;

-- 库存管理
UPDATE product_inventory 
SET stock_quantity = stock_quantity - 1,
    reserved_quantity = reserved_quantity - 1,
    last_updated = NOW()
WHERE product_id = 3001 
  AND stock_quantity > 0;

-- 并发安全的计数器更新
UPDATE user_scores 
SET score = score + 100,
    games_played = games_played + 1,
    streak_count = CASE 
        WHEN last_game_won = 1 THEN streak_count + 1 
        ELSE 1 
    END,
    last_game_won = 1
WHERE user_id = 1001;
```

### 3. 数据修复和清理

```
-- 修复异常数据
UPDATE financial_records 
SET amount = ABS(amount),  -- 确保金额为正数
    status = 'corrected'
WHERE amount < 0;

-- 数据去重，保留最新记录
DELETE FROM duplicate_products 
WHERE product_id NOT IN (
    SELECT MAX(product_id) 
    FROM duplicate_products 
    GROUP BY product_code, product_name
);

-- 批量NULL值处理
UPDATE customer_contacts 
SET phone = '未知',
    email = COALESCE(email, '无邮箱'),
    updated_by = 'system_cleanup'
WHERE phone IS NULL 
   OR email IS NULL;
```

### 4. 递归更新和层次数据处理

```
-- 更新组织结构的路径字段
UPDATE organization_tree ot
SET full_path = CONCAT(
    (SELECT full_path FROM organization_tree WHERE node_id = ot.parent_id),
    '/', 
    ot.node_name
)
WHERE ot.parent_id IS NOT NULL;

-- 使用CTE进行递归更新（PostgreSQL、SQL Server）
WITH RECURSIVE employee_tree AS (
    -- 锚点：顶级经理
    SELECT employee_id, manager_id, 1 as level
    FROM employees 
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 递归：下属员工
    SELECT e.employee_id, e.manager_id, et.level + 1
    FROM employees e
    INNER JOIN employee_tree et ON e.manager_id = et.employee_id
)
UPDATE employees e
JOIN employee_tree et ON e.employee_id = et.employee_id
SET e.management_level = et.level;
```

------

## 七、RETURNING 子句（PostgreSQL等）

### 1. 返回更新后的数据

```
-- 返回更新后的记录（PostgreSQL）
UPDATE products 
SET price = price * 0.8,
    last_discount_date = CURRENT_DATE
WHERE category = '清仓商品'
RETURNING product_id, product_name, price, last_discount_date;

-- 返回受影响的行数信息
UPDATE employees 
SET salary = salary * 1.1
WHERE department = 'Engineering'
RETURNING 
    employee_id,
    name,
    salary AS old_salary,
    salary * 1.1 AS new_salary,
    (salary * 0.1) AS increase_amount;
```

### 2. 基于返回结果继续操作

```
-- 更新并记录审计日志
WITH updated_employees AS (
    UPDATE employees 
    SET status = 'terminated',
        termination_date = CURRENT_DATE
    WHERE termination_date IS NOT NULL
    RETURNING employee_id, name, termination_date
)
INSERT INTO termination_audit (employee_id, employee_name, terminated_at)
SELECT employee_id, name, termination_date 
FROM updated_employees;
```

------

## 八、安全注意事项和最佳实践

### 1. ⚠️ **永远不要忘记WHERE子句！**

**灾难性错误示例**：

```
-- ❌ 危险！会更新表中所有记录！
UPDATE users SET password = 'invalid';

-- ✅ 安全：明确指定条件
UPDATE users SET password = 'new_secure_hash' WHERE user_id = 1001;
```

**防护措施**：

```
-- 1. 先SELECT验证要更新的记录
SELECT COUNT(*) FROM products WHERE price > 1000;  -- 确认有10条记录

-- 2. 然后执行更新（使用相同的WHERE条件）
UPDATE products SET discount = 0.2 WHERE price > 1000;  -- 确认更新10条记录

-- 3. 启用安全更新模式（MySQL）
SET SQL_SAFE_UPDATES = 1;  -- 要求UPDATE必须包含WHERE或LIMIT
```

### 2. 事务控制保证数据一致性

```
-- 使用事务确保相关更新要么全部成功，要么全部失败
START TRANSACTION;

-- 减少库存
UPDATE products 
SET stock_quantity = stock_quantity - 1 
WHERE product_id = 2001 AND stock_quantity > 0;

-- 如果库存不足，回滚事务
IF ROW_COUNT() = 0 THEN
    ROLLBACK;
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '库存不足';
END IF;

-- 创建订单
INSERT INTO orders (product_id, quantity, order_date) 
VALUES (2001, 1, NOW());

COMMIT;
```

### 3. 性能优化技巧

**批量更新优化**：

```
-- ❌ 低效：逐条更新（N次数据库往返）
UPDATE products SET price = 100 WHERE product_id = 1;
UPDATE products SET price = 200 WHERE product_id = 2;
-- ...

-- ✅ 高效：批量更新（1次数据库往返）
UPDATE products 
SET price = CASE product_id
    WHEN 1 THEN 100
    WHEN 2 THEN 200
    WHEN 3 THEN 150
    ELSE price
END
WHERE product_id IN (1, 2, 3);
```

**索引优化**：

```
-- 确保WHERE条件的列有索引
CREATE INDEX idx_employee_dept ON employees(department);
CREATE INDEX idx_product_category ON products(category);

-- 现在这些更新会很快
UPDATE employees SET salary = salary * 1.1 WHERE department = 'Engineering';
UPDATE products SET status = 'active' WHERE category = 'Electronics';
```

**分时段大批量更新**：

```
-- 低峰期执行大批量更新
UPDATE large_audit_table 
SET archived = 1,
    archive_date = NOW()
WHERE created_date < '2023-01-01'
  AND archived = 0
LIMIT 10000;  -- 每次只处理1万条

-- 在应用程序中循环调用，直到所有数据处理完成
```

### 4. 备份和验证策略

**更新前备份**：

```
-- 创建临时备份表
CREATE TABLE products_backup_20240115 AS 
SELECT * FROM products WHERE category = 'Electronics';

-- 执行更新
UPDATE products SET price = price * 0.9 WHERE category = 'Electronics';

-- 验证更新结果
SELECT COUNT(*) AS updated_count FROM products WHERE category = 'Electronics';
SELECT AVG(price) AS new_avg_price FROM products WHERE category = 'Electronics';

-- 如果需要回滚
-- TRUNCATE TABLE products;
-- INSERT INTO products SELECT * FROM products_backup_20240115;
```

------

## 九、实际业务场景示例

### 1. 电商库存管理

```
-- 订单支付成功后扣减库存
START TRANSACTION;

UPDATE products 
SET stock_quantity = stock_quantity - 1,
    reserved_quantity = reserved_quantity - 1,
    last_updated = NOW()
WHERE product_id = 3001 
  AND stock_quantity >= 1;

-- 记录库存变更
INSERT INTO inventory_logs (product_id, change_type, change_amount, reference_id)
VALUES (3001, 'sale', -1, LAST_INSERT_ID());

COMMIT;
```

### 2. 用户积分系统

```
-- 用户完成活动奖励积分
UPDATE users 
SET points = points + 100,
    total_activities = total_activities + 1,
    last_activity_date = NOW()
WHERE user_id = 1001;

-- 积分等级自动调整
UPDATE users 
SET membership_level = CASE 
    WHEN points >= 5000 THEN '黄金'
    WHEN points >= 2000 THEN '白银' 
    WHEN points >= 500 THEN '青铜'
    ELSE '普通'
END
WHERE last_activity_date > DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### 3. 数据迁移和ETL

```
-- 数据清洗和标准化
UPDATE customer_data 
SET 
    email = LOWER(TRIM(email)),
    phone = REGEXP_REPLACE(phone, '[^0-9]', ''),  -- 只保留数字
    full_name = CONCAT(
        UPPER(SUBSTRING(first_name, 1, 1)), 
        LOWER(SUBSTRING(first_name, 2)),
        ' ',
        UPPER(last_name)
    ),
    data_quality = 'cleaned'
WHERE email LIKE '%@%' 
  AND LENGTH(phone) >= 10;
```

### 4. 系统维护任务

```
-- 定期归档过期数据
UPDATE user_sessions 
SET status = 'expired',
    expired_at = NOW()
WHERE last_activity < DATE_SUB(NOW(), INTERVAL 7 DAY)
  AND status = 'active'
LIMIT 1000;  -- 每次处理1000条，避免长时间锁表

-- 更新统计信息
UPDATE product_statistics ps
SET 
    average_rating = (
        SELECT AVG(rating) 
        FROM product_reviews pr 
        WHERE pr.product_id = ps.product_id
    ),
    review_count = (
        SELECT COUNT(*) 
        FROM product_reviews pr 
        WHERE pr.product_id = ps.product_id
    ),
    last_updated = NOW()
WHERE ps.product_id IN (
    SELECT DISTINCT product_id 
    FROM product_reviews 
    WHERE created_date > DATE_SUB(NOW(), INTERVAL 1 DAY)
);
```

------

## 十、错误处理和监控

### 1. 更新结果验证

```
-- 检查更新是否成功
UPDATE products SET price = 99.99 WHERE product_id = 2001;

-- 获取受影响的行数
SELECT ROW_COUNT() AS affected_rows;  -- MySQL

-- 在PostgreSQL中
UPDATE products SET price = 99.99 WHERE product_id = 2001;
GET DIAGNOSTICS update_count = ROW_COUNT;
```

### 2. 存储过程中的安全更新

```
DELIMITER //
CREATE PROCEDURE SafeProductUpdate(
    IN p_product_id INT,
    IN p_new_price DECIMAL(10,2)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        RESIGNAL;
    END;

    START TRANSACTION;
    
    -- 记录更新前的值
    INSERT INTO price_change_audit (product_id, old_price, new_price, changed_by, change_time)
    SELECT product_id, price, p_new_price, USER(), NOW()
    FROM products 
    WHERE product_id = p_product_id;
    
    -- 执行更新
    UPDATE products 
    SET price = p_new_price,
        last_updated = NOW()
    WHERE product_id = p_product_id;
    
    -- 验证是否更新了记录
    IF ROW_COUNT() = 0 THEN
        ROLLBACK;
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '产品不存在';
    END IF;
    
    COMMIT;
END//
DELIMITER ;
```

这个全面的UPDATE指南涵盖了从基础语法到高级技巧的所有方面，强调了安全性和性能优化，是数据库操作中至关重要的知识。

------

## 一、DELETE 语句完整架构

### 基本语法和扩展：

```sql
DELETE [LOW_PRIORITY] [QUICK] [IGNORE] FROM table_name 
[WHERE conditions]
[ORDER BY column1 [ASC|DESC], ...]
[LIMIT row_count]
[RETURNING column1, column2, ...];  -- PostgreSQL等支持
```

------

## 二、DELETE 子句详解

### 1. 表选项修饰符

#### **`LOW_PRIORITY`（MySQL）**

```
-- 低优先级删除，等待其他操作完成后再执行
DELETE LOW_PRIORITY FROM audit_logs 
WHERE created_date < '2023-01-01';
```

- **适用场景**：后台清理任务，不紧急的数据删除
- **效果**：降低对正常业务操作的影响

#### **`QUICK`（MySQL - MyISAM表）**

```
-- 快速删除，不合并索引叶节点（仅MyISAM有效）
DELETE QUICK FROM large_myisam_table 
WHERE status = 'obsolete';
```

- **适用场景**：MyISAM表的大批量删除
- **效果**：提高删除速度，但可能降低后续查询性能
- **注意**：InnoDB表忽略此修饰符

#### **`IGNORE`- 忽略错误**

```
-- 忽略删除过程中的外键约束错误等
DELETE IGNORE FROM products 
WHERE category_id = 5;  -- 如果有关联订单，忽略错误继续删除其他记录
```

- **忽略的错误类型**： 外键约束违反 触发器执行错误
- **风险**：可能导致数据不一致，谨慎使用

------

## 三、WHERE 子句详解（极其重要！）

### 1. 基本条件删除

```sql
-- 删除特定记录
DELETE FROM users WHERE user_id = 1001;

-- 基于时间条件删除
DELETE FROM session_logs 
WHERE last_activity < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- 多条件组合删除
DELETE FROM orders 
WHERE status = 'cancelled' 
  AND order_date < '2023-01-01'
  AND total_amount < 100;
```

### 2. 子查询条件删除

```sql
-- 删除没有订单的客户
DELETE FROM customers 
WHERE customer_id NOT IN (
    SELECT DISTINCT customer_id 
    FROM orders 
    WHERE order_date > '2022-01-01'
);

-- 删除重复记录（保留最新的一条）
DELETE FROM duplicate_products 
WHERE product_id NOT IN (
    SELECT MAX(product_id) 
    FROM duplicate_products 
    GROUP BY product_code, product_name
);
```

### 3. EXISTS/NOT EXISTS 条件删除

```sql
-- 删除30天内无活动的用户
DELETE FROM users u
WHERE u.status = 'inactive'
  AND NOT EXISTS (
    SELECT 1 
    FROM user_activities ua 
    WHERE ua.user_id = u.user_id 
      AND ua.activity_date > DATE_SUB(NOW(), INTERVAL 30 DAY)
);

-- 删除没有下属的部门
DELETE FROM departments d
WHERE NOT EXISTS (
    SELECT 1 
    FROM employees e 
    WHERE e.department_id = d.department_id
);
```

### 4. 关联删除（多表删除）

```
-- MySQL多表删除语法
DELETE o, oi
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_date < '2020-01-01';

-- 使用子查询的关联删除
DELETE FROM products
WHERE category_id IN (
    SELECT category_id 
    FROM categories 
    WHERE status = 'inactive'
);
```

------

## 四、ORDER BY 和 LIMIT 子句

### 1. 有序删除

```
-- 按时间顺序删除旧记录（先删最早的）
DELETE FROM audit_trail 
WHERE log_date < '2023-01-01'
ORDER BY log_date ASC  -- 从最早开始删除
LIMIT 1000;

-- 按优先级删除（先删不重要的）
DELETE FROM task_queue 
WHERE status = 'failed'
ORDER BY priority ASC, created_at ASC  -- 先删低优先级、早创建的
LIMIT 500;
```

### 2. 分批次删除（大数据量关键技巧）

```
-- 大批量数据分批次删除，避免锁表时间过长
DELETE FROM large_log_table 
WHERE created_date < '2022-01-01'
ORDER BY id  -- 按主键顺序，提高性能
LIMIT 10000;  -- 每次删除1万条

-- 在存储过程中循环执行
DELIMITER //
CREATE PROCEDURE BatchDeleteOldData()
BEGIN
    DECLARE done INT DEFAULT 0;
    DECLARE rows_affected INT;
    
    WHILE NOT done DO
        -- 每次删除1000条
        DELETE FROM large_log_table 
        WHERE created_date < '2022-01-01'
        LIMIT 1000;
        
        SET rows_affected = ROW_COUNT();
        
        -- 如果没有更多数据可删，退出循环
        IF rows_affected = 0 THEN
            SET done = 1;
        END IF;
        
        -- 短暂暂停，减少对系统的影响
        DO SLEEP(1);
    END WHILE;
END//
DELIMITER ;
```

### 3. 顶部记录删除

```
-- 删除最旧的N条记录
DELETE FROM user_notifications 
WHERE user_id = 1001
ORDER BY created_at ASC  -- 从最旧的开始
LIMIT 50;  -- 只删除50条最旧的通知

-- 删除测试数据（保留最新的）
DELETE FROM test_records 
WHERE environment = 'test'
ORDER BY created_at DESC 
LIMIT 100 OFFSET 1000;  -- 删除第1000条之后的数据
```

------

## 五、高级删除技巧

### 1. 级联删除和关联数据清理

```
-- 手动级联删除（当外键约束不存在时）
START TRANSACTION;

-- 1. 先删除子表记录
DELETE FROM order_items 
WHERE order_id IN (
    SELECT order_id 
    FROM orders 
    WHERE order_date < '2020-01-01'
);

-- 2. 再删除父表记录
DELETE FROM orders 
WHERE order_date < '2020-01-01';

COMMIT;

-- 使用外键约束自动级联删除
-- 建表时设置：FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
```

### 2. 存档后删除模式

```
-- 1. 先存档重要数据
INSERT INTO orders_archive 
SELECT * FROM orders 
WHERE order_date < '2022-01-01';

-- 2. 验证存档成功
SELECT COUNT(*) FROM orders_archive 
WHERE order_date < '2022-01-01';

-- 3. 然后删除原表数据
DELETE FROM orders 
WHERE order_date < '2022-01-01';

-- 4. 记录操作日志
INSERT INTO cleanup_logs (operation, table_name, records_affected, executed_by)
VALUES ('archive_and_delete', 'orders', ROW_COUNT(), CURRENT_USER);
```

### 3. 软删除模式（推荐替代物理删除）

```
-- 添加软删除标志字段
ALTER TABLE products ADD COLUMN is_deleted TINYINT DEFAULT 0;
ALTER TABLE products ADD COLUMN deleted_at DATETIME NULL;

-- 软删除：更新标志而非真正删除
UPDATE products 
SET is_deleted = 1,
    deleted_at = NOW(),
    deleted_by = CURRENT_USER
WHERE product_id = 1001;

-- 查询时排除已删除的记录
SELECT * FROM products WHERE is_deleted = 0;

-- 真正的物理删除（定期清理）
DELETE FROM products 
WHERE is_deleted = 1 
  AND deleted_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

### 4. 分区表删除优化

```
-- 对于分区表，直接删除整个分区（极快）
ALTER TABLE sales_data DROP PARTITION p2020;

-- 比传统DELETE快得多
-- DELETE FROM sales_data WHERE sale_date BETWEEN '2020-01-01' AND '2020-12-31';
```

------

## 六、RETURNING 子句（PostgreSQL等）

### 1. 返回被删除的数据

```
-- 返回被删除的记录信息（PostgreSQL）
DELETE FROM temporary_sessions 
WHERE expires_at < NOW()
RETURNING session_id, user_id, created_at;

-- 记录删除审计信息
WITH deleted_records AS (
    DELETE FROM user_sessions 
    WHERE last_activity < DATE_SUB(NOW(), INTERVAL 7 DAY)
    RETURNING session_id, user_id, last_activity
)
INSERT INTO deletion_audit (table_name, deleted_data, deleted_by, deleted_at)
SELECT 
    'user_sessions',
    JSON_OBJECT('session_id', session_id, 'user_id', user_id),
    CURRENT_USER,
    NOW()
FROM deleted_records;
```

------

## 七、安全注意事项和最佳实践

### 1. ⚠️ **永远不要忘记WHERE子句！**

**灾难性错误示例**：

```
-- ❌ 危险！会删除表中所有记录！
DELETE FROM users;

-- ❌ 仍然危险！条件可能匹配所有记录
DELETE FROM products WHERE price > 0;  -- 如果所有产品价格都>0

-- ✅ 安全：明确指定条件，先SELECT验证
SELECT COUNT(*) FROM users WHERE last_login < '2020-01-01';  -- 先确认
DELETE FROM users WHERE last_login < '2020-01-01';  -- 再执行
```

**防护措施**：

```
-- 1. 启用安全模式（MySQL）
SET SQL_SAFE_UPDATES = 1;  -- 要求DELETE必须包含WHERE或LIMIT

-- 2. 使用事务进行测试
START TRANSACTION;
DELETE FROM table_name WHERE conditions;  -- 先测试
SELECT ROW_COUNT();  -- 查看影响行数
ROLLBACK;  -- 回滚，不实际执行

-- 3. 备份重要数据
CREATE TABLE backup_20240115 AS SELECT * FROM table_name WHERE conditions;
```

### 2. 事务控制保证数据一致性

```
-- 关联数据删除的事务保护
START TRANSACTION;

-- 记录删除审计信息
INSERT INTO deletion_audit (table_name, deleted_ids, deleted_by)
SELECT 'orders', GROUP_CONCAT(order_id), CURRENT_USER()
FROM orders 
WHERE order_date < '2020-01-01';

-- 删除子表记录
DELETE FROM order_items 
WHERE order_id IN (
    SELECT order_id 
    FROM orders 
    WHERE order_date < '2020-01-01'
);

-- 删除主表记录
DELETE FROM orders 
WHERE order_date < '2020-01-01';

-- 验证删除结果
IF ROW_COUNT() = (SELECT COUNT(*) FROM deletion_audit ...) THEN
    COMMIT;
    SELECT '删除成功' AS result;
ELSE
    ROLLBACK;
    SELECT '删除失败，已回滚' AS result;
END IF;
```

### 3. 性能优化技巧

**大批量删除优化**：

```
-- ❌ 低效：单条大数据量删除
DELETE FROM huge_log_table WHERE created_date < '2020-01-01';  -- 可能锁表很久

-- ✅ 高效：分批次删除
DELIMITER //
CREATE PROCEDURE BatchDeleteLargeData()
BEGIN
    DECLARE finished INT DEFAULT 0;
    
    WHILE finished = 0 DO
        DELETE FROM huge_log_table 
        WHERE created_date < '2020-01-01'
        LIMIT 1000;  -- 每次1000条
        
        IF ROW_COUNT() = 0 THEN
            SET finished = 1;
        END IF;
        
        -- 给其他操作机会
        DO SLEEP(0.1);
    END WHILE;
END//
DELIMITER ;
```

**索引优化**：

```
-- 确保WHERE条件的列有索引
CREATE INDEX idx_users_last_login ON users(last_login);
CREATE INDEX idx_orders_date_status ON orders(order_date, status);

-- 现在这些删除会很快
DELETE FROM users WHERE last_login < '2020-01-01';
DELETE FROM orders WHERE order_date < '2021-01-01' AND status = 'cancelled';
```

**低峰期执行**：

```
-- 在业务低峰期执行大批量删除
-- 例如：凌晨2-4点执行数据清理任务
DELETE FROM audit_logs 
WHERE created_date < DATE_SUB(CURDATE(), INTERVAL 90 DAY)
AND created_time BETWEEN '02:00:00' AND '04:00:00';  -- 只在低峰期执行
```

### 4. 备份和验证策略

**删除前备份**：

```
-- 创建备份表
CREATE TABLE customers_backup_20240115 AS 
SELECT * FROM customers 
WHERE last_purchase_date < '2020-01-01';

-- 验证备份
SELECT COUNT(*) FROM customers_backup_20240115;

-- 执行删除
DELETE FROM customers 
WHERE last_purchase_date < '2020-01-01';

-- 记录操作
INSERT INTO cleanup_logs (operation, table_name, records_deleted, backup_table)
VALUES ('delete_old_customers', 'customers', ROW_COUNT(), 'customers_backup_20240115');

-- 如果需要恢复
-- INSERT INTO customers SELECT * FROM customers_backup_20240115;
```

------

## 八、实际业务场景示例

### 1. 数据归档和清理系统

```
-- 自动化数据清理存储过程
DELIMITER //
CREATE PROCEDURE CleanupOldData()
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        INSERT INTO error_logs (procedure_name, error_message) 
        VALUES ('CleanupOldData', '数据清理失败');
    END;

    START TRANSACTION;
    
    -- 1. 备份即将删除的数据
    CREATE TABLE IF NOT EXISTS user_sessions_archive_20240115 AS 
    SELECT * FROM user_sessions 
    WHERE last_activity < DATE_SUB(NOW(), INTERVAL 180 DAY);
    
    -- 2. 执行删除
    DELETE FROM user_sessions 
    WHERE last_activity < DATE_SUB(NOW(), INTERVAL 180 DAY);
    
    -- 3. 记录操作日志
    INSERT INTO cleanup_audit (
        table_name, 
        records_deleted, 
        cleanup_criteria, 
        executed_by
    ) VALUES (
        'user_sessions', 
        ROW_COUNT(), 
        '180天前的不活跃会话', 
        CURRENT_USER()
    );
    
    COMMIT;
    
    -- 4. 优化表空间
    OPTIMIZE TABLE user_sessions;
END//
DELIMITER ;
```

### 2. 用户数据管理（GDPR合规）

```
-- 用户账号注销和数据删除
START TRANSACTION;

-- 1. 记录注销审计
INSERT INTO account_deletion_audit (user_id, reason, requested_by, requested_at)
VALUES (1001, '用户主动注销', 'user_request', NOW());

-- 2. 匿名化敏感数据（保留审计需要的信息）
UPDATE users 
SET 
    email = CONCAT('deleted_', user_id, '@example.com'),
    phone = NULL,
    real_name = '已注销用户',
    id_card = NULL,
    is_deleted = 1,
    deleted_at = NOW()
WHERE user_id = 1001;

-- 3. 删除敏感日志数据
DELETE FROM user_activity_logs 
WHERE user_id = 1001 
  AND activity_type IN ('login', 'password_change', 'profile_update');

-- 4. 保留必要的业务数据（订单等），但解除个人信息关联
UPDATE orders 
SET user_info = '已注销用户'
WHERE user_id = 1001;

COMMIT;
```

### 3. 电商库存清理

```
-- 清理无效的购物车数据
DELETE FROM shopping_carts 
WHERE user_id IN (
    SELECT user_id 
    FROM users 
    WHERE status = 'inactive'
) OR last_updated < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- 清理过期促销活动数据
DELETE FROM promotion_codes 
WHERE expiration_date < NOW() 
  AND times_used = 0;  -- 未使用过的过期优惠码
```

### 4. 系统维护和监控

```
-- 监控大表删除操作
SET @start_time = NOW();
SET @start_size = (SELECT DATA_LENGTH FROM information_schema.TABLES 
                  WHERE TABLE_NAME = 'large_audit_table');

-- 执行删除
DELETE FROM large_audit_table 
WHERE created_date < DATE_SUB(NOW(), INTERVAL 365 DAY)
LIMIT 100000;

-- 记录性能指标
INSERT TABLE maintenance_logs (
    table_name,
    operation,
    records_affected,
    duration_seconds,
    size_reduction_mb,
    executed_by
)
SELECT 
    'large_audit_table',
    'delete_old_records',
    ROW_COUNT(),
    TIMESTAMPDIFF(SECOND, @start_time, NOW()),
    (@start_size - (SELECT DATA_LENGTH FROM information_schema.TABLES 
                   WHERE TABLE_NAME = 'large_audit_table')) / 1024 / 1024,
    CURRENT_USER();
```

------

## 九、错误处理和监控

### 1. 删除结果验证

```
-- 检查删除是否成功
DELETE FROM temp_sessions WHERE expires_at < NOW();

-- 获取受影响的行数
SELECT ROW_COUNT() AS deleted_rows;

-- 验证删除结果
SELECT COUNT(*) AS remaining_count 
FROM temp_sessions 
WHERE expires_at < NOW();  -- 应该返回0
```

### 2. 外键约束处理

```
-- 检查外键约束
SELECT 
    TABLE_NAME,
    COLUMN_NAME,
    CONSTRAINT_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_NAME = 'products';

-- 处理有外键关联的数据
-- 方案1：先删除子表记录
DELETE FROM order_items WHERE product_id = 1001;
DELETE FROM product_reviews WHERE product_id = 1001;
DELETE FROM products WHERE product_id = 1001;

-- 方案2：设置NULL（如果外键允许）
UPDATE order_items SET product_id = NULL WHERE product_id = 1001;
DELETE FROM products WHERE product_id = 1001;
```

### 3. 存储过程中的安全删除

```
DELIMITER //
CREATE PROCEDURE SafeDataDeletion(
    IN p_table_name VARCHAR(64),
    IN p_where_condition VARCHAR(1000),
    IN p_max_deletions INT
)
BEGIN
    DECLARE v_sql VARCHAR(2000);
    DECLARE v_continue INT DEFAULT 1;
    DECLARE v_total_deleted INT DEFAULT 0;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        INSERT INTO error_logs (procedure_name, error_message) 
        VALUES ('SafeDataDeletion', CONCAT('表:', p_table_name, ' 条件:', p_where_condition));
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '删除操作失败';
    END;

    -- 验证表名和条件的安全性
    IF p_where_condition NOT REGEXP '^[a-zA-Z0-9_ =<>''%()]+$' THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = '无效的删除条件';
    END IF;

    WHILE v_continue = 1 AND v_total_deleted < p_max_deletions DO
        START TRANSACTION;
        
        SET @sql = CONCAT(
            'DELETE FROM ', p_table_name,
            ' WHERE ', p_where_condition,
            ' LIMIT 1000'
        );
        
        PREPARE stmt FROM @sql;
        EXECUTE stmt;
        DEALLOCATE PREPARE stmt;
        
        SET v_total_deleted = v_total_deleted + ROW_COUNT();
        
        IF ROW_COUNT() = 0 THEN
            SET v_continue = 0;
        END IF;
        
        COMMIT;
        
        -- 短暂暂停
        DO SLEEP(0.5);
    END WHILE;
    
    SELECT CONCAT('成功删除 ', v_total_deleted, ' 条记录') AS result;
END//
DELIMITER ;
```

------

## 十、DELETE vs TRUNCATE vs DROP

### 对比总结：

| 操作         | 作用     | 是否可回滚 | 性能 | 自增ID | 日志记录   | 使用场景           |
| ------------ | -------- | ---------- | ---- | ------ | ---------- | ------------------ |
| **DELETE**   | 删除数据 | ✅ 可回滚   | 慢   | 不重置 | 详细日志   | 条件删除、部分删除 |
| **TRUNCATE** | 清空表   | ❌ 不可回滚 | 快   | 重置   | 最小日志   | 快速清空整个表     |
| **DROP**     | 删除表   | ❌ 不可回滚 | 最快 | -      | 无数据日志 | 删除整个表结构     |

### 使用建议：

```
-- 需要条件删除时用DELETE
DELETE FROM users WHERE status = 'inactive';

-- 需要快速清空整个表用TRUNCATE
TRUNCATE TABLE temporary_data;

-- 需要删除表结构用DROP
DROP TABLE obsolete_table;
```

这个全面的DELETE指南强调了安全性和性能优化，是数据库管理中必须谨慎操作但非常重要的部分。

### 3. 数据控制语言 (DCL)

```sql
-- 权限管理
GRANT 
    privilege1 [(column_list)], 
    privilege2, 
    ...
ON [object_type] privilege_level 
TO user1 [IDENTIFIED BY 'password'], user2, ...
[WITH GRANT OPTION]
[WITH ADMIN OPTION];

REVOKE 
    privilege1, privilege2, ...
ON object_name 
FROM user1, user2, ...;

-- 权限类型：SELECT, INSERT, UPDATE, DELETE, REFERENCES, USAGE, ALL PRIVILEGES

-- 事务控制
START TRANSACTION | BEGIN [WORK]
COMMIT [WORK] [AND [NO] CHAIN] [[NO] RELEASE]
ROLLBACK [WORK] [AND [NO] CHAIN] [[NO] RELEASE]
SAVEPOINT savepoint_name
ROLLBACK [WORK] TO [SAVEPOINT] savepoint_name
RELEASE SAVEPOINT savepoint_name
```

### 4. 事务控制语言 (TCL)

```sql
SET TRANSACTION 
    [ISOLATION LEVEL {READ UNCOMMITTED | READ COMMITTED | REPEATABLE READ | SERIALIZABLE}]
    [READ WRITE | READ ONLY];

SET autocommit = 0|1;  -- 关闭/开启自动提交
```

## 二、完整的数据类型体系

### 1. 数值类型

```sql
-- 整数
TINYINT[(M)] [UNSIGNED] [ZEROFILL]      -- 1字节，-128~127 或 0~255
SMALLINT[(M)] [UNSIGNED] [ZEROFILL]     -- 2字节，-32768~32767
MEDIUMINT[(M)] [UNSIGNED] [ZEROFILL]    -- 3字节
INT/INTEGER[(M)] [UNSIGNED] [ZEROFILL]  -- 4字节
BIGINT[(M)] [UNSIGNED] [ZEROFILL]       -- 8字节

-- 浮点数
FLOAT[(M,D)] [UNSIGNED] [ZEROFILL]      -- 4字节，单精度
DOUBLE[(M,D)] [UNSIGNED] [ZEROFILL]     -- 8字节，双精度
DECIMAL(M,D) [UNSIGNED] [ZEROFILL]      -- 精确小数，M是总位数，D是小数位

-- 位值类型
BIT[(M)]  -- 位字段，M表示位数(1-64)
```

### 2. 字符串类型

```SQL
-- 定长字符串
CHAR(M) [CHARACTER SET charset] [COLLATE collation]  -- M: 0-255

-- 变长字符串  
VARCHAR(M) [CHARACTER SET charset] [COLLATE collation]  -- M: 0-65535

-- 文本类型
TINYTEXT   -- 最大255字节
TEXT       -- 最大65,535字节
MEDIUMTEXT -- 最大16,777,215字节  
LONGTEXT   -- 最大4,294,967,295字节

-- 二进制数据
BINARY(M)  -- 定长二进制
VARBINARY(M) -- 变长二进制
BLOB, LONGBLOB  -- 二进制大对象

-- 枚举和集合
ENUM('value1','value2',...)  -- 枚举，最多65535个值
SET('value1','value2',...)   -- 集合，最多64个成员
```

### 3. 日期时间类型

```sql
DATE        -- 'YYYY-MM-DD'，1000-01-01 到 9999-12-31
TIME[(fsp)] -- 'HH:MM:SS[.fraction]'，-838:59:59 到 838:59:59
DATETIME[(fsp)] -- 'YYYY-MM-DD HH:MM:SS[.fraction]'
TIMESTAMP[(fsp)] -- 时间戳，1970-01-01 到 2038-01-19
YEAR[(4)]   -- 年份，1901 到 2155
```

### 4. 空间数据类型 (GIS)

```sql
GEOMETRY
POINT, LINESTRING, POLYGON
MULTIPOINT, MULTILINESTRING, MULTIPOLYGON
GEOMETRYCOLLECTION
```

### 5. JSON 类型

```sql
JSON  -- MySQL 5.7+，PostgreSQL 9.2+
```

## 三、完整的函数体系

### 1. 聚合函数

```sql
COUNT([DISTINCT] expr)    -- 计数
SUM([DISTINCT] expr)      -- 求和
AVG([DISTINCT] expr)      -- 平均值
MIN([DISTINCT] expr)      -- 最小值  
MAX([DISTINCT] expr)      -- 最大值

-- 统计函数
STDDEV_POP(expr)          -- 总体标准差
STDDEV_SAMP(expr)         -- 样本标准差
VAR_POP(expr)             -- 总体方差
VAR_SAMP(expr)            -- 样本方差

-- 高级聚合
GROUP_CONCAT(expr)        -- 连接组内值
JSON_ARRAYAGG(expr)       -- 聚合为JSON数组
JSON_OBJECTAGG(key, value) -- 聚合为JSON对象
BIT_AND(expr), BIT_OR(expr), BIT_XOR(expr)  -- 位运算
```

### 2. 窗口函数 (分析函数)

```sql
-- 排名函数
ROW_NUMBER() OVER ([PARTITION BY expr] ORDER BY expr)     -- 行号
RANK() OVER ([PARTITION BY expr] ORDER BY expr)           -- 排名，允许并列
DENSE_RANK() OVER ([PARTITION BY expr] ORDER BY expr)     -- 密集排名
NTILE(n) OVER ([PARTITION BY expr] ORDER BY expr)         -- 分桶

-- 取值函数
LAG(expr [, offset[, default]]) OVER (PARTITION BY ... ORDER BY ...)
LEAD(expr [, offset[, default]]) OVER (PARTITION BY ... ORDER BY ...)
FIRST_VALUE(expr) OVER (PARTITION BY ... ORDER BY ... RANGE/ROWS ...)
LAST_VALUE(expr) OVER (PARTITION BY ... ORDER BY ... RANGE/ROWS ...)
NTH_VALUE(expr, n) OVER (PARTITION BY ... ORDER BY ...)

-- 聚合窗口函数
SUM(salary) OVER (PARTITION BY dept ORDER BY hire_date ROWS UNBOUNDED PRECEDING)
AVG(salary) OVER (PARTITION BY dept ORDER BY hire_date RANGE BETWEEN INTERVAL '7' DAY PRECEDING AND CURRENT ROW)
```

### 3. 字符串函数

```sql
-- 基础操作
CONCAT(str1, str2, ...)                    -- 连接字符串
CONCAT_WS(separator, str1, str2, ...)     -- 带分隔符连接
LENGTH(str), CHAR_LENGTH(str)              -- 长度计算
UPPER(str), LOWER(str)                     -- 大小写转换

-- 子串操作
SUBSTRING(str, start[, length])            -- 提取子串
LEFT(str, length), RIGHT(str, length)      -- 左/右子串
SUBSTRING_INDEX(str, delim, count)         -- 按分隔符提取

-- 搜索替换
LOCATE(substr, str[, start])               -- 查找位置
REPLACE(str, from_str, to_str)             -- 替换
INSERT(str, pos, len, newstr)              -- 插入替换

-- 格式化
TRIM([{BOTH|LEADING|TRAILING} [remstr] FROM] str)  -- 去除空格
LPAD(str, len, padstr), RPAD(str, len, padstr)      -- 填充
REPEAT(str, count)                         -- 重复
REVERSE(str)                               -- 反转

-- 正则表达式 (MySQL 8.0+, PostgreSQL)
REGEXP_LIKE(str, pattern)                  -- 正则匹配
REGEXP_REPLACE(str, pattern, replacement)  -- 正则替换
REGEXP_SUBSTR(str, pattern)                -- 正则提取
```

### 4. 数值函数

```sql
-- 基础数学
ABS(x), SIGN(x)                            -- 绝对值，符号
CEILING(x), FLOOR(x), ROUND(x[, d])        -- 取整
MOD(n, m)                                  -- 取模

-- 指数对数
POW(x, y), SQRT(x)                         -- 幂，平方根
EXP(x), LN(x), LOG(b, x)                   -- 指数，对数

-- 三角函数
SIN(x), COS(x), TAN(x)                     -- 三角函数
ASIN(x), ACOS(x), ATAN(x)                  -- 反三角函数
RADIANS(x), DEGREES(x)                     -- 弧度角度转换

-- 随机数
RAND([seed])                               -- 随机数
```

### 5. 日期时间函数

```sql
-- 当前时间
NOW([fsp]), SYSDATE()                      -- 当前日期时间
CURDATE(), CURTIME()                       -- 当前日期，时间
UTC_DATE(), UTC_TIME()                     -- UTC时间

-- 提取部分
YEAR(date), MONTH(date), DAY(date)         -- 年，月，日
HOUR(time), MINUTE(time), SECOND(time)     -- 时，分，秒
DAYOFWEEK(date), DAYOFYEAR(date)           -- 周几，年中第几天
WEEK(date[, mode]), QUARTER(date)          -- 周，季度

-- 日期计算
DATE_ADD(date, INTERVAL expr unit)         -- 日期加法
DATE_SUB(date, INTERVAL expr unit)         -- 日期减法
DATEDIFF(date1, date2)                     -- 日期差
TIMESTAMPDIFF(unit, datetime1, datetime2)  -- 时间戳差

-- 格式化
DATE_FORMAT(date, format)                  -- 日期格式化
STR_TO_DATE(str, format)                   -- 字符串转日期
FROM_UNIXTIME(unix_timestamp[, format])    -- 时间戳转日期
UNIX_TIMESTAMP([date])                     -- 日期转时间戳
```

### 6. JSON 函数 (MySQL 5.7+, PostgreSQL 9.2+)

```sql
-- 创建JSON
JSON_OBJECT(key, val[, key, val]...)       -- 创建JSON对象
JSON_ARRAY(val1, val2, ...)                -- 创建JSON数组

-- 提取查询
JSON_EXTRACT(json_doc, path)               -- 提取值
json_doc->'$.path'                         -- 简化提取
json_doc->>'$.path'                        -- 提取并转为字符串

-- 搜索验证
JSON_SEARCH(json_doc, one_or_all, search_str)  -- 搜索
JSON_CONTAINS(json_doc, val[, path])       -- 是否包含
JSON_VALID(val)                            -- 是否有效JSON

-- 修改操作
JSON_SET(json_doc, path, val[, path, val]...)  -- 设置值
JSON_INSERT(json_doc, path, val)           -- 插入值
JSON_REPLACE(json_doc, path, val)          -- 替换值
JSON_REMOVE(json_doc, path[, path]...)     -- 删除值
```

## 四、高级查询技术

### 1. 多表连接详解

```sql
-- 内连接
SELECT * FROM table1 
[INNER] JOIN table2 ON table1.id = table2.table1_id;

-- 外连接
SELECT * FROM table1 
LEFT [OUTER] JOIN table2 ON table1.id = table2.table1_id;

SELECT * FROM table1 
RIGHT [OUTER] JOIN table2 ON table1.id = table2.table1_id;

SELECT * FROM table1 
FULL [OUTER] JOIN table2 ON table1.id = table2.table1_id;

-- 交叉连接
SELECT * FROM table1 CROSS JOIN table2;

-- 自然连接（不推荐）
SELECT * FROM table1 NATURAL JOIN table2;

-- 自连接
SELECT e1.name, e2.name as manager 
FROM employees e1 
LEFT JOIN employees e2 ON e1.manager_id = e2.id;
```

### 2. 子查询全面语法

```sql
-- 标量子查询（返回单个值）
SELECT name, (SELECT COUNT(*) FROM orders WHERE orders.customer_id = customers.id) as order_count
FROM customers;

-- 列子查询（返回一列）
SELECT * FROM products 
WHERE category_id IN (SELECT id FROM categories WHERE active = 1);

-- 行子查询（返回一行）
SELECT * FROM employees 
WHERE (department, salary) = (SELECT department, MAX(salary) FROM employees GROUP BY department);

-- 表子查询（返回表）
SELECT * FROM (SELECT id, name FROM customers WHERE country = 'US') AS us_customers;

-- EXISTS/NOT EXISTS
SELECT * FROM customers c 
WHERE EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id AND o.total > 1000);

-- 相关子查询
UPDATE products p 
SET price = (SELECT AVG(price) FROM products p2 WHERE p2.category = p.category);
```

### 3. 公共表表达式 (CTE)

```sql
-- 普通CTE
WITH department_stats AS (
    SELECT department, AVG(salary) as avg_salary, COUNT(*) as emp_count
    FROM employees 
    GROUP BY department
)
SELECT * FROM department_stats WHERE avg_salary > 50000;

-- 递归CTE（处理层次数据）
WITH RECURSIVE org_chart AS (
    -- 锚点查询
    SELECT id, name, manager_id, 1 as level
    FROM employees 
    WHERE manager_id IS NULL
    
    UNION ALL
    
    -- 递归查询
    SELECT e.id, e.name, e.manager_id, oc.level + 1
    FROM employees e
    INNER JOIN org_chart oc ON e.manager_id = oc.id
)
SELECT * FROM org_chart ORDER BY level, id;

-- 多CTE
WITH 
    sales2019 AS (SELECT * FROM sales WHERE year = 2019),
    sales2020 AS (SELECT * FROM sales WHERE year = 2020),
    growth AS (
        SELECT s2020.product_id, 
               (s2020.amount - s2019.amount) / s2019.amount as growth_rate
        FROM sales2020 s2020 
        JOIN sales2019 s2019 ON s2020.product_id = s2019.product_id
    )
SELECT * FROM growth WHERE growth_rate > 0.1;
```

### 4. 高级分组和过滤

```sql
-- GROUPING SETS
SELECT department, job_title, COUNT(*), AVG(salary)
FROM employees 
GROUP BY GROUPING SETS ((department), (job_title), (department, job_title), ());

-- CUBE (所有可能的组合)
SELECT department, job_title, COUNT(*)
FROM employees 
GROUP BY CUBE (department, job_title);

-- ROLLUP (层次聚合)
SELECT year, quarter, month, SUM(sales)
FROM sales_data 
GROUP BY ROLLUP (year, quarter, month);

-- FILTER 子句 (PostgreSQL)
SELECT department,
       COUNT(*) AS total,
       COUNT(*) FILTER (WHERE salary > 50000) AS high_earners,
       AVG(salary) FILTER (WHERE active = true) AS avg_active_salary
FROM employees 
GROUP BY department;
```

## 五、性能优化和高级特性

### 1. 索引详解

```sql
-- 创建索引
CREATE [UNIQUE|FULLTEXT|SPATIAL] INDEX index_name 
ON table_name (column1 [ASC|DESC], ...) 
[USING BTREE|HASH|RTREE]  -- 索引类型
[WITH (storage_parameter = value)];

-- 复合索引
CREATE INDEX idx_name ON users (last_name, first_name);

-- 函数索引
CREATE INDEX idx_lower_name ON users (LOWER(name));

-- 部分索引（条件索引）
CREATE INDEX idx_active_users ON users (id) WHERE active = true;

-- 覆盖索引
CREATE INDEX idx_covering ON orders (customer_id, order_date) INCLUDE (total_amount);

-- 查看索引使用
EXPLAIN [FORMAT=JSON] SELECT * FROM users WHERE name = 'John';
```

### 2. 分区表

```sql
-- 范围分区
CREATE TABLE sales (
    id INT,
    sale_date DATE,
    amount DECIMAL(10,2)
) PARTITION BY RANGE (YEAR(sale_date)) (
    PARTITION p2019 VALUES LESS THAN (2020),
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p_max VALUES LESS THAN MAXVALUE
);

-- 列表分区
PARTITION BY LIST (region_id) (
    PARTITION p_north VALUES IN (1, 2, 3),
    PARTITION p_south VALUES IN (4, 5, 6)
);

-- 哈希分区
PARTITION BY HASH (YEAR(sale_date)) PARTITIONS 4;

-- 分区管理
ALTER TABLE sales ADD PARTITION (PARTITION p2022 VALUES LESS THAN (2023));
ALTER TABLE sales DROP PARTITION p2019;
ALTER TABLE sales REORGANIZE PARTITION p_max INTO (
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p_max VALUES LESS THAN MAXVALUE
);
```

### 3. 全文搜索

```sql
-- 创建全文索引
CREATE FULLTEXT INDEX idx_content ON articles (title, content);

-- 自然语言搜索
SELECT * FROM articles 
WHERE MATCH(title, content) AGAINST('database performance' IN NATURAL LANGUAGE MODE);

-- 布尔模式搜索
SELECT * FROM articles 
WHERE MATCH(title, content) AGAINST('+MySQL -Oracle' IN BOOLEAN MODE);

-- 查询扩展
SELECT * FROM articles 
WHERE MATCH(title, content) AGAINST('database' WITH QUERY EXPANSION);
```

## 六、存储过程、函数和触发器

### 1. 存储过程

```sql
DELIMITER //

CREATE PROCEDURE GetEmployeeStatistics(
    IN dept_id INT, 
    OUT total_count INT,
    OUT avg_salary DECIMAL(10,2)
)
BEGIN
    -- 变量声明
    DECLARE min_salary DECIMAL(10,2) DEFAULT 0;
    
    -- 业务逻辑
    SELECT COUNT(*), AVG(salary) 
    INTO total_count, avg_salary
    FROM employees 
    WHERE department_id = dept_id AND salary > min_salary;
    
    -- 条件判断
    IF total_count = 0 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No employees found';
    END IF;
    
    -- 循环示例
    WHILE min_salary < 100000 DO
        SET min_salary = min_salary + 10000;
    END WHILE;
    
END //

DELIMITER ;

-- 调用存储过程
CALL GetEmployeeStatistics(1, @count, @avg_salary);
SELECT @count, @avg_salary;
```

### 2. 自定义函数

```sql
DELIMITER //

CREATE FUNCTION CalculateBonus(
    base_salary DECIMAL(10,2), 
    performance_rating INT
) 
RETURNS DECIMAL(10,2)
READS SQL DATA
DETERMINISTIC
BEGIN
    DECLARE bonus DECIMAL(10,2);
    
    CASE performance_rating
        WHEN 1 THEN SET bonus = base_salary * 0.1;
        WHEN 2 THEN SET bonus = base_salary * 0.15;
        WHEN 3 THEN SET bonus = base_salary * 0.2;
        ELSE SET bonus = base_salary * 0.05;
    END CASE;
    
    RETURN bonus;
END //

DELIMITER ;

-- 使用函数
SELECT name, salary, CalculateBonus(salary, performance) as bonus FROM employees;
```

### 3. 触发器

```sql
-- BEFORE INSERT 触发器
CREATE TRIGGER before_employee_insert 
BEFORE INSERT ON employees
FOR EACH ROW
BEGIN
    IF NEW.salary < 0 THEN
        SET NEW.salary = 0;
    END IF;
    
    SET NEW.created_at = NOW();
    SET NEW.updated_at = NOW();
END;

-- AFTER UPDATE 触发器
CREATE TRIGGER after_salary_update 
AFTER UPDATE ON employees
FOR EACH ROW
BEGIN
    IF OLD.salary != NEW.salary THEN
        INSERT INTO salary_history (employee_id, old_salary, new_salary, change_date)
        VALUES (NEW.id, OLD.salary, NEW.salary, NOW());
    END IF;
END;

-- INSTEAD OF 触发器 (SQL Server, PostgreSQL)
CREATE TRIGGER instead_of_delete_view
INSTEAD OF DELETE ON employee_view
FOR EACH ROW
BEGIN
    UPDATE employees SET active = 0 WHERE id = OLD.id;
END;
```

## 七、高级事务和锁机制

### 1. 事务隔离级别

```sql
-- 设置隔离级别
SET TRANSACTION ISOLATION LEVEL 
    READ UNCOMMITTED |    -- 读未提交
    READ COMMITTED |      -- 读已提交  
    REPEATABLE READ |     -- 可重复读
    SERIALIZABLE;         -- 序列化

-- 死锁处理示例
START TRANSACTION;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- 获取锁

-- 死锁检测和重试逻辑
DECLARE EXIT HANDLER FOR SQLEXCEPTION
BEGIN
    IF @@ERROR = 1213 THEN  -- 死锁错误码
        ROLLBACK;
        -- 重试逻辑
    END IF;
END;
```

### 2. 锁机制

```sql
-- 行级锁
SELECT * FROM table WHERE id = 1 FOR UPDATE;        -- 排他锁
SELECT * FROM table WHERE id = 1 LOCK IN SHARE MODE; -- 共享锁

-- 表级锁
LOCK TABLES table_name [READ|WRITE];
UNLOCK TABLES;

-- 间隙锁 (防止幻读)
SELECT * FROM employees 
WHERE salary BETWEEN 3000 AND 5000 FOR UPDATE;
```

## 八、数据库管理和维护

### 1. 用户和权限管理

```sql
-- 创建用户
CREATE USER 'username'@'host' IDENTIFIED BY 'password';

-- 权限授予
GRANT SELECT, INSERT, UPDATE ON database.* TO 'username'@'host';
GRANT ALL PRIVILEGES ON database.* TO 'username'@'host' WITH GRANT OPTION;

-- 角色管理 (MySQL 8.0+)
CREATE ROLE 'read_only', 'read_write';
GRANT SELECT ON *.* TO 'read_only';
GRANT SELECT, INSERT, UPDATE, DELETE ON database.* TO 'read_write';
GRANT 'read_only' TO 'username'@'host';
SET DEFAULT ROLE 'read_only' TO 'username'@'host';
```

### 2. 备份和恢复

```sql
-- 逻辑备份
mysqldump -u username -p database_name > backup.sql

-- 物理备份
-- 使用文件系统快照或企业备份工具

-- 时间点恢复
mysqlbinlog binlog.000001 --start-datetime="2024-01-01 00:00:00" | mysql -u root -p
```

## 九、SQL 标准和方言差异

### 主要数据库系统特性对比

| 特性     | MySQL         | PostgreSQL | SQL Server | Oracle   |
| -------- | ------------- | ---------- | ---------- | -------- |
| 窗口函数 | 8.0+ 完整支持 | 优秀支持   | 优秀支持   | 优秀支持 |
| CTE      | 8.0+          | 优秀支持   | 优秀支持   | 优秀支持 |
| JSON支持 | 5.7+          | 优秀支持   | 2016+      | 12.1+    |
| 分区表   | 支持          | 优秀支持   | 优秀支持   | 优秀支持 |
| 存储过程 | 有限          | PL/pgSQL   | T-SQL      | PL/SQL   |

这个指南涵盖了SQL的绝大部分核心概念和高级特性。要完全掌握，建议在实际项目中逐步应用这些技术，并根据具体使用的数据库系统深入学习其特有功能。