# SQL 手撕题（校招常考）

> 以 MySQL 语法为主，掌握多表关联、窗口函数、排名、连续类、留存等题型。

---

## 一、所需建表语句（全部汇总）

> 以下为可重复执行的 MySQL 脚本，练习前复制到客户端执行即可。也可直接运行同目录下的 `init_tables.sql`。

```sql
-- ----------------------------------------
-- SQL 手撕题 建表脚本 (MySQL 5.7+)
-- 可重复执行：先 DROP 再 CREATE
-- ----------------------------------------

DROP TABLE IF EXISTS t_pivot;
DROP TABLE IF EXISTS t_median;
DROP TABLE IF EXISTS stats;
DROP TABLE IF EXISTS sales;
DROP TABLE IF EXISTS Logs;
DROP TABLE IF EXISTS login;
DROP TABLE IF EXISTS Department;
DROP TABLE IF EXISTS Employee;
DROP TABLE IF EXISTS score;
DROP TABLE IF EXISTS teacher;
DROP TABLE IF EXISTS course;
DROP TABLE IF EXISTS student;
DROP TABLE IF EXISTS products;

-- 商品表（基础题）
CREATE TABLE products (
    id       INT PRIMARY KEY,
    `name`   VARCHAR(50),
    price    DECIMAL(10,2),
    category VARCHAR(20)
);

-- 学生表
CREATE TABLE student (
    s_id    VARCHAR(10) PRIMARY KEY,
    s_name  VARCHAR(20),
    s_birth DATE,
    s_sex   VARCHAR(5)
);

-- 课程表
CREATE TABLE course (
    c_id   VARCHAR(10) PRIMARY KEY,
    c_name VARCHAR(20),
    t_id   VARCHAR(10)
);

-- 教师表
CREATE TABLE teacher (
    t_id   VARCHAR(10) PRIMARY KEY,
    t_name VARCHAR(20)
);

-- 成绩表
CREATE TABLE score (
    s_id    VARCHAR(10),
    c_id    VARCHAR(10),
    s_score DECIMAL(5,2),
    PRIMARY KEY (s_id, c_id)
);

-- 部门表
CREATE TABLE Department (
    id   INT PRIMARY KEY,
    `name` VARCHAR(50)
);

-- 员工表（LeetCode 176/184）
CREATE TABLE Employee (
    id           INT PRIMARY KEY,
    `name`       VARCHAR(50),
    salary       DECIMAL(10,2),
    departmentId INT
);

-- 登录表（连续登录、次日留存）
CREATE TABLE login (
    user_id    VARCHAR(20),
    login_date DATE,
    PRIMARY KEY (user_id, login_date)
);

-- 连续数字表（LeetCode 180）
CREATE TABLE Logs (
    id  INT PRIMARY KEY AUTO_INCREMENT,
    num INT
);

-- 数值表（中位数题）
CREATE TABLE t_median (
    id  INT PRIMARY KEY,
    val DECIMAL(10,2)
);

-- 销售表（累计求和）
CREATE TABLE sales (
    `year_month` DATE,
    gmv          DECIMAL(15,2)
);

-- 统计表（同环比）
CREATE TABLE stats (
    dt     DATE,
    amount DECIMAL(15,2)
);

-- 行转列结果表（列转行题，可由六(1)结果或手动插入）
CREATE TABLE t_pivot (
    s_id VARCHAR(10),
    `语文` DECIMAL(5,2),
    `数学` DECIMAL(5,2),
    `英语` DECIMAL(5,2)
);
```

> **说明**：`t_median` 用于中位数题，`t_pivot` 用于列转行题；中文列名已用反引号包裹，保证 MySQL 可正确解析。

---

## 二、基础题（覆盖简单考点）

> 面试可能从基础题开始，务必熟练。

### 1. 简单查询：SELECT、WHERE、ORDER BY、LIMIT

```sql
-- 查询所有学生
SELECT * FROM student;

-- 查询男生
SELECT * FROM student WHERE s_sex = '男';

-- 按姓名排序，取前 5 条
SELECT * FROM student ORDER BY s_name LIMIT 5;

-- 分页：第 2 页，每页 10 条（OFFSET 10, LIMIT 10）
SELECT * FROM student ORDER BY s_id LIMIT 10 OFFSET 10;
```

### 2. 去重 DISTINCT

```sql
-- 查询有选课的学生学号（去重）
SELECT DISTINCT s_id FROM score;

-- 查询选了几门不同课程
SELECT s_id, COUNT(DISTINCT c_id) AS cnt FROM score GROUP BY s_id;
```

### 3. 简单聚合（无分组）

```sql
-- 学生总数
SELECT COUNT(*) FROM student;

-- 成绩表总记录数、平均分、最高分
SELECT COUNT(*) AS cnt, AVG(s_score) AS avg_score, MAX(s_score) AS max_score
FROM score;
```

### 4. 条件：IN、BETWEEN、LIKE

```sql
-- 学号在指定列表中
SELECT * FROM student WHERE s_id IN ('01', '02', '03');

-- 成绩在 60～90 之间
SELECT * FROM score WHERE s_score BETWEEN 60 AND 90;

-- 姓名包含「张」
SELECT * FROM student WHERE s_name LIKE '%张%';

-- 姓「李」（一个字符用 _）
SELECT * FROM student WHERE s_name LIKE '李%';
```

### 5. NULL 处理

```sql
-- 成绩不为空
SELECT * FROM score WHERE s_score IS NOT NULL;

-- 成绩为空时显示 0
SELECT s_id, c_id, IFNULL(s_score, 0) AS score FROM score;

-- 统计非空成绩数量
SELECT COUNT(s_score) FROM score;  -- 不统计 NULL
```

### 6. 简单单表 JOIN

```sql
-- 查询学生姓名及成绩（两表关联）
SELECT st.s_name, sc.c_id, sc.s_score
FROM student st
JOIN score sc ON st.s_id = sc.s_id;
```

### 7. CASE WHEN 简单分支

```sql
-- 成绩等级：>=90 优，>=60 及格，否则不及格
SELECT s_id, c_id, s_score,
       CASE WHEN s_score >= 90 THEN '优'
            WHEN s_score >= 60 THEN '及格'
            ELSE '不及格' END AS level
FROM score;
```

### 8. 商品表基础题（products）

```sql
-- 价格在 100～500 的商品
SELECT * FROM products WHERE price BETWEEN 100 AND 500;

-- 分类为「电子产品」的商品，按价格降序
SELECT * FROM products WHERE category = '电子产品' ORDER BY price DESC;

-- 商品名以「手机」开头
SELECT * FROM products WHERE name LIKE '手机%';

-- 每个分类的商品数量
SELECT category, COUNT(*) AS cnt FROM products GROUP BY category;
```

### 9. 日期条件

```sql
-- 本月出生的学生
SELECT * FROM student
WHERE DATE_FORMAT(s_birth, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m');

-- 最近 7 天登录的用户（login 表）
SELECT DISTINCT user_id FROM login
WHERE login_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
```

### 10. 简单子查询

```sql
-- 查询高于平均成绩的记录
SELECT * FROM score WHERE s_score > (SELECT AVG(s_score) FROM score);

-- 查询成绩最高的学生学号
SELECT s_id FROM score WHERE s_score = (SELECT MAX(s_score) FROM score);
```

---

## 三、排名与 TopN（进阶）

### 1. 第二高的薪水（LeetCode 176）

```sql
-- 表: Employee (id, salary)
SELECT IFNULL(
    (SELECT DISTINCT salary
     FROM Employee
     ORDER BY salary DESC
     LIMIT 1 OFFSET 1),
    NULL
) AS SecondHighestSalary;
```

### 2. 部门工资最高的员工（LeetCode 184）

```sql
-- Employee: id, name, salary, departmentId
-- Department: id, name
SELECT d.name AS Department, e.name AS Employee, e.salary AS Salary
FROM Employee e
JOIN Department d ON e.departmentId = d.id
WHERE (e.departmentId, e.salary) IN (
    SELECT departmentId, MAX(salary)
    FROM Employee
    GROUP BY departmentId
);
```

### 3. 各科成绩排名（row_number / rank / dense_rank）

```sql
-- 每门课程的成绩排名，同分不同名
SELECT s_id, c_id, s_score,
       ROW_NUMBER() OVER (PARTITION BY c_id ORDER BY s_score DESC) AS rn
FROM score;

-- 同分同名，下一名跳号（如 1,2,2,4）
SELECT s_id, c_id, s_score,
       RANK() OVER (PARTITION BY c_id ORDER BY s_score DESC) AS rk
FROM score;

-- 同分同名，下一名不跳号（如 1,2,2,3）
SELECT s_id, c_id, s_score,
       DENSE_RANK() OVER (PARTITION BY c_id ORDER BY s_score DESC) AS dr
FROM score;
```

### 4. 每门课程前两名

```sql
SELECT * FROM (
    SELECT s_id, c_id, s_score,
           DENSE_RANK() OVER (PARTITION BY c_id ORDER BY s_score DESC) AS rk
    FROM score
) t
WHERE t.rk <= 2;
```

---

## 四、聚合与分组

### 1. 平均成绩大于 60 的学生及平均成绩

```sql
SELECT s_id, AVG(s_score) AS avg_score
FROM score
GROUP BY s_id
HAVING AVG(s_score) > 60;
```

### 2. 所有学生选课数、总成绩（含 0 门课）

```sql
SELECT st.s_id, st.s_name,
       COUNT(sc.c_id) AS course_cnt,
       IFNULL(SUM(sc.s_score), 0) AS total_score
FROM student st
LEFT JOIN score sc ON st.s_id = sc.s_id
GROUP BY st.s_id, st.s_name;
```

### 3. 每门课程的平均分、最高分、最低分

```sql
SELECT c_id,
       AVG(s_score) AS avg_score,
       MAX(s_score) AS max_score,
       MIN(s_score) AS min_score
FROM score
GROUP BY c_id;
```

---

## 五、多表关联

### 1. 查询选了「张三」老师课程的学生

```sql
SELECT DISTINCT st.s_id, st.s_name
FROM student st
JOIN score sc ON st.s_id = sc.s_id
JOIN course c  ON sc.c_id = c.c_id
JOIN teacher t ON c.t_id = t.t_id
WHERE t.t_name = '张三';
```

### 2. 查询没选「张三」老师课程的学生

```sql
SELECT s_id, s_name FROM student
WHERE s_id NOT IN (
    SELECT sc.s_id
    FROM score sc
    JOIN course c ON sc.c_id = c.c_id
    JOIN teacher t ON c.t_id = t.t_id
    WHERE t.t_name = '张三'
);
```

### 3. 查询至少选了两门课的学生

```sql
SELECT s_id
FROM score
GROUP BY s_id
HAVING COUNT(c_id) >= 2;
```

---

## 六、行转列 / 列转行

### 1. 行转列：每个学生每门课成绩一列

```sql
-- 假设只有语文、数学、英语 三科
SELECT s_id,
       MAX(CASE WHEN c_id = '01' THEN s_score END) AS 语文,
       MAX(CASE WHEN c_id = '02' THEN s_score END) AS 数学,
       MAX(CASE WHEN c_id = '03' THEN s_score END) AS 英语
FROM score
GROUP BY s_id;
```

### 2. 列转行（UNION ALL）

```sql
-- 表 t_pivot(s_id, 语文, 数学, 英语)，转为 (s_id, subject, score)
SELECT s_id, '语文' AS subject, 语文 AS score FROM t_pivot WHERE 语文 IS NOT NULL
UNION ALL
SELECT s_id, '数学', 数学 FROM t_pivot WHERE 数学 IS NOT NULL
UNION ALL
SELECT s_id, '英语', 英语 FROM t_pivot WHERE 英语 IS NOT NULL;
```

---

## 七、连续类问题

### 1. 连续登录 N 天的用户（如 3 天）

```sql
-- 表 login: user_id, login_date (日期，每人每天一条)
SELECT DISTINCT user_id
FROM (
    SELECT user_id, login_date,
           login_date - INTERVAL ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date) DAY AS grp
    FROM (SELECT DISTINCT user_id, login_date FROM login) t
) t2
GROUP BY user_id, grp
HAVING COUNT(1) >= 3;
```

### 2. 连续出现 3 次的数字（LeetCode 180）

```sql
-- 表 Logs: id, num
SELECT DISTINCT a.num AS ConsecutiveNums
FROM Logs a
JOIN Logs b ON a.id = b.id - 1 AND a.num = b.num
JOIN Logs c ON b.id = c.id - 1 AND b.num = c.num;
```

---

## 八、留存 / 次日留存

```sql
-- 表 login(user_id, login_date)，次日留存：今天活跃且明天也活跃
SELECT
    a.login_date,
    COUNT(DISTINCT a.user_id) AS dau,
    COUNT(DISTINCT b.user_id) AS next_day_users,
    ROUND(COUNT(DISTINCT b.user_id) / COUNT(DISTINCT a.user_id), 2) AS retention
FROM login a
LEFT JOIN login b ON a.user_id = b.user_id AND b.login_date = DATE_ADD(a.login_date, INTERVAL 1 DAY)
GROUP BY a.login_date;
```

---

## 九、子查询与 EXISTS

### 1. 查询没有成绩的学生

```sql
SELECT * FROM student
WHERE s_id NOT IN (SELECT s_id FROM score WHERE s_id IS NOT NULL);
-- 或
SELECT * FROM student st
WHERE NOT EXISTS (SELECT 1 FROM score sc WHERE sc.s_id = st.s_id);
```

### 2. 查询比某门课平均分高的学生（该课程）

```sql
SELECT sc.s_id, sc.c_id, sc.s_score
FROM score sc
WHERE sc.s_score > (
    SELECT AVG(s_score) FROM score WHERE c_id = sc.c_id
);
```

---

## 十、日期与区间

### 1. 本月、本周、今日

```sql
WHERE DATE_FORMAT(date_col, '%Y-%m') = DATE_FORMAT(CURDATE(), '%Y-%m')
WHERE YEARWEEK(date_col) = YEARWEEK(CURDATE())
WHERE DATE(date_col) = CURDATE();
```

### 2. 最近 7 天

```sql
WHERE date_col >= DATE_SUB(CURDATE(), INTERVAL 7 DAY);
```

---

## 十一、综合题示例

### 1. 各科成绩都大于该科平均分的学生

```sql
SELECT st.s_id, st.s_name
FROM student st
JOIN score sc ON st.s_id = sc.s_id
JOIN (
    SELECT c_id, AVG(s_score) AS avg_score
    FROM score
    GROUP BY c_id
) avg_t ON sc.c_id = avg_t.c_id AND sc.s_score > avg_t.avg_score
GROUP BY st.s_id, st.s_name
HAVING COUNT(DISTINCT sc.c_id) = (SELECT COUNT(DISTINCT c_id) FROM score WHERE s_id = st.s_id);
```

### 2. 成绩有重复时查第二高（同分算同一名次）

```sql
SELECT MAX(salary) AS SecondHighestSalary
FROM Employee
WHERE salary < (SELECT MAX(salary) FROM Employee);
```

---

## 十二、中位数

### 1. 有序中位数（MySQL 无 MEDIAN，用排序+序号）

```sql
-- 表 t_median(id, val)，求 val 的中位数（奇数取中间，偶数取中间两个平均）
SELECT AVG(val) AS median
FROM (
    SELECT val,
           ROW_NUMBER() OVER (ORDER BY val) AS rn,
           COUNT(*) OVER () AS cnt
    FROM t_median
) x
WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2));
```

### 2. 分组中位数（如每个部门工资中位数）

```sql
SELECT departmentId, AVG(salary) AS median_salary
FROM (
    SELECT departmentId, salary,
           ROW_NUMBER() OVER (PARTITION BY departmentId ORDER BY salary) AS rn,
           COUNT(*) OVER (PARTITION BY departmentId) AS cnt
    FROM Employee
) t
WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2))
GROUP BY departmentId;
```

---

## 十三、累计求和（如每月 GMV 累计）

```sql
-- 表 sales(year_month, gmv)，求每月 GMV 及当年累计 GMV
SELECT `year_month`, gmv,
       SUM(gmv) OVER (PARTITION BY YEAR(`year_month`) ORDER BY `year_month`
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_gmv
FROM sales;

-- 或使用 RANGE（按月份累加）
SELECT `year_month`, gmv,
       SUM(gmv) OVER (ORDER BY `year_month` RANGE UNBOUNDED PRECEDING) AS cum_gmv
FROM sales;
```

---

## 十四、同环比

### 1. 环比：与上一期比（如本月 vs 上月）

```sql
-- 表 stats(dt, amount)，dt 为月度日期
SELECT dt, amount,
       LAG(amount, 1) OVER (ORDER BY dt) AS last_amount,
       amount - LAG(amount, 1) OVER (ORDER BY dt) AS mom_diff,
       ROUND((amount - LAG(amount, 1) OVER (ORDER BY dt)) * 100.0
             / NULLIF(LAG(amount, 1) OVER (ORDER BY dt), 0), 2) AS mom_pct
FROM (SELECT DATE_FORMAT(dt, '%Y-%m-01') AS dt, SUM(amount) AS amount FROM stats GROUP BY 1) t;
```

### 2. 同比：与去年同期比（今年本月 vs 去年本月）

```sql
SELECT dt, amount,
       LAG(amount, 12) OVER (ORDER BY dt) AS same_month_last_year,
       ROUND((amount - LAG(amount, 12) OVER (ORDER BY dt)) * 100.0
             / NULLIF(LAG(amount, 12) OVER (ORDER BY dt), 0), 2) AS yoy_pct
FROM (SELECT DATE_FORMAT(dt, '%Y-%m-01') AS dt, SUM(amount) AS amount FROM stats GROUP BY 1) t;
```

---

## 十五、常考函数速记


| 类别  | 函数/语法                                        |
| --- | -------------------------------------------- |
| 窗口  | ROW_NUMBER(), RANK(), DENSE_RANK(), LAG/LEAD |
| 聚合  | COUNT, SUM, AVG, MAX, MIN；GROUP BY, HAVING   |
| 判空  | IFNULL(expr, val), COALESCE(a, b, ...)       |
| 条件  | CASE WHEN ... THEN ... ELSE ... END          |
| 去重  | DISTINCT；COUNT(DISTINCT col)                 |
| 分页  | LIMIT n OFFSET m（或 LIMIT m, n）               |
| 日期  | DATE_FORMAT, DATE_ADD, DATEDIFF, CURDATE()   |


**建议**：多表 JOIN、GROUP BY + HAVING、窗口排名、行转列、连续/留存至少各练一两道；冲数仓/数据分析岗可加练中位数、累计、同环比。