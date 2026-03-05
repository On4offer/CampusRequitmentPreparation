# SQL 手撕题（校招常考）

> 以 MySQL 语法为主，掌握多表关联、窗口函数、排名、连续类、留存等题型。

---

## 一、建表与数据（经典四表）

```sql
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
```

---

## 二、排名与 TopN

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

## 三、聚合与分组

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

## 四、多表关联

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

## 五、行转列 / 列转行

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
-- 若表为 (s_id, 语文, 数学, 英语)，转为 (s_id, subject, score)
SELECT s_id, '语文' AS subject, 语文 AS score FROM t WHERE 语文 IS NOT NULL
UNION ALL
SELECT s_id, '数学', 数学 FROM t WHERE 数学 IS NOT NULL
UNION ALL
SELECT s_id, '英语', 英语 FROM t WHERE 英语 IS NOT NULL;
```

---

## 六、连续类问题

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

## 七、留存 / 次日留存

```sql
-- 表: user_id, date（每天一条）
-- 次日留存：今天活跃且明天也活跃
SELECT
    a.date,
    COUNT(DISTINCT a.user_id) AS dau,
    COUNT(DISTINCT b.user_id) AS next_day_users,
    ROUND(COUNT(DISTINCT b.user_id) / COUNT(DISTINCT a.user_id), 2) AS retention
FROM login a
LEFT JOIN login b ON a.user_id = b.user_id AND b.date = DATE_ADD(a.date, INTERVAL 1 DAY)
GROUP BY a.date;
```

---

## 八、子查询与 EXISTS

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

## 九、日期与区间

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

## 十、综合题示例

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

## 十一、中位数

### 1. 有序中位数（MySQL 无 MEDIAN，用排序+序号）

```sql
-- 表 t(id, val)，求 val 的中位数（奇数取中间，偶数取中间两个平均）
SELECT AVG(val) AS median
FROM (
    SELECT val,
           ROW_NUMBER() OVER (ORDER BY val) AS rn,
           COUNT(*) OVER () AS cnt
    FROM t
) x
WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2));
```

### 2. 分组中位数（如每个部门工资中位数）

```sql
SELECT department_id, AVG(salary) AS median_salary
FROM (
    SELECT department_id, salary,
           ROW_NUMBER() OVER (PARTITION BY department_id ORDER BY salary) AS rn,
           COUNT(*) OVER (PARTITION BY department_id) AS cnt
    FROM Employee
) t
WHERE rn IN (FLOOR((cnt + 1) / 2), CEIL((cnt + 1) / 2))
GROUP BY department_id;
```

---

## 十二、累计求和（如每月 GMV 累计）

```sql
-- 表 sales(year_month, gmv)，求每月 GMV 及当年累计 GMV
SELECT year_month, gmv,
       SUM(gmv) OVER (PARTITION BY YEAR(year_month) ORDER BY year_month
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cum_gmv
FROM sales;

-- 或使用 RANGE（按月份累加）
SELECT year_month, gmv,
       SUM(gmv) OVER (ORDER BY year_month RANGE UNBOUNDED PRECEDING) AS cum_gmv
FROM sales;
```

---

## 十三、同环比

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

## 十四、常考函数速记

| 类别     | 函数/语法 |
|----------|-----------|
| 窗口     | ROW_NUMBER(), RANK(), DENSE_RANK(), LAG/LEAD |
| 聚合     | COUNT, SUM, AVG, MAX, MIN；GROUP BY, HAVING |
| 判空     | IFNULL(expr, val), COALESCE(a, b, ...) |
| 条件     | CASE WHEN ... THEN ... ELSE ... END |
| 去重     | DISTINCT；COUNT(DISTINCT col) |
| 分页     | LIMIT n OFFSET m（或 LIMIT m, n） |
| 日期     | DATE_FORMAT, DATE_ADD, DATEDIFF, CURDATE() |

**建议**：多表 JOIN、GROUP BY + HAVING、窗口排名、行转列、连续/留存至少各练一两道；冲数仓/数据分析岗可加练中位数、累计、同环比。
