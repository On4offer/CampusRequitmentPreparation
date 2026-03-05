# SQL 手撕知识点（对应题目原理）

> 本文件整理 SQL 手撕题背后的**原理与考点**，便于理解「为什么这样写」、面试时能讲清。

---

## 一、SQL 执行顺序 → 对应「所有 SELECT 题」

### 1. 书写顺序 vs 执行顺序

**书写顺序**：
```
SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
```

**执行顺序**（MySQL 实际执行）：
```
FROM → JOIN → WHERE → GROUP BY → 聚合函数 → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT
```

### 2. 为什么 WHERE 不能写聚合函数

- `WHERE` 在 `GROUP BY` 之前执行，此时还没有分组。
- 聚合函数（SUM、AVG、COUNT 等）作用于分组后的结果。
- 要对聚合结果过滤，用 `HAVING`。

### 3. 为什么 HAVING 可以用聚合函数

- `HAVING` 在 `GROUP BY` 和聚合之后执行。
- 此时已有分组结果，可直接用 `SUM`、`COUNT` 等做条件。

---

## 二、JOIN 原理 → 对应「多表关联」题

### 1. 内连接 vs 左连接 vs 右连接

| 类型 | 结果 |
|------|------|
| INNER JOIN | 两表交集，只保留匹配行 |
| LEFT JOIN | 左表全保留，右表无匹配则补 NULL |
| RIGHT JOIN | 右表全保留，左表无匹配则补 NULL |
| FULL OUTER JOIN | 两表并集（MySQL 不直接支持，用 UNION 模拟） |

### 2. 驱动表选择

- 小表驱动大表：通常把数据量小的表放在前面，减少循环次数。
- MySQL 优化器会基于统计信息选择驱动表，但写 SQL 时注意索引和过滤条件。

### 3. 子查询 vs JOIN

- 子查询：可读性好，但有时会生成临时表，性能差。
- JOIN：适合多表关联，可利用索引。
- `IN` 子查询：若子查询结果集大，可能较慢；`EXISTS` 适合「存在性」判断，找到即返回。

---

## 三、窗口函数 → 对应「排名、累计、同环比、LAG/LEAD」

### 1. 窗口函数与聚合函数的区别

| 对比 | 聚合函数 | 窗口函数 |
|------|----------|----------|
| 结果行数 | 多行聚合为一行 | 每行保留，并附加一行计算结果 |
| 典型 | GROUP BY + SUM | OVER (PARTITION BY ... ORDER BY ...) |

### 2. 窗口函数语法

```sql
函数() OVER (
    PARTITION BY 列1, 列2 ...   -- 分区，类似 GROUP BY
    ORDER BY 列 [ASC|DESC]       -- 排序
    [ROWS/RANGE 窗口子句]        -- 窗口范围
)
```

### 3. ROW_NUMBER / RANK / DENSE_RANK

| 函数 | 同分处理 | 示例 |
|------|----------|------|
| ROW_NUMBER | 同分不同号 | 1,2,3,4 |
| RANK | 同分同名，下一名跳号 | 1,2,2,4 |
| DENSE_RANK | 同分同名，下一名不跳号 | 1,2,2,3 |

### 4. LAG / LEAD

- `LAG(col, n)`：当前行往前第 n 行的值。
- `LEAD(col, n)`：当前行往后第 n 行的值。
- 用于环比（n=1）、同比（n=12，按月）等。

### 5. 窗口范围：ROWS vs RANGE

- `ROWS`：按物理行数。
  - `ROWS UNBOUNDED PRECEDING`：从分区第一行到当前行。
  - `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`：前 2 行 + 当前行。
- `RANGE`：按值范围（如 ORDER BY 日期，RANGE 7 PRECEDING 表示 7 天内）。

---

## 四、GROUP BY 与 HAVING → 对应「聚合、分组」题

### 1. GROUP BY 规则

- SELECT 中的非聚合列，必须出现在 GROUP BY 中。
- 聚合列（SUM、AVG、COUNT 等）可以不在 GROUP BY 中。

### 2. WHERE vs HAVING

| 对比 | WHERE | HAVING |
|------|-------|--------|
| 执行时机 | 分组前 | 分组后 |
| 作用对象 | 单行 | 分组 |
| 聚合函数 | 不可用 | 可用 |

### 3. COUNT 的几种写法

- `COUNT(*)`：统计行数，含 NULL。
- `COUNT(列)`：统计该列非 NULL 的行数。
- `COUNT(DISTINCT 列)`：去重后统计。

---

## 五、子查询与 EXISTS → 对应「NOT IN、EXISTS」题

### 1. IN vs EXISTS

- `IN`：子查询先执行，结果集缓存，主查询用 IN 做匹配。
- `EXISTS`：子查询依赖主查询，找到一条匹配即返回 true，适合「存在性」判断。
- 当子查询结果集大，主表小：`EXISTS` 更合适；反之可考虑 `IN`。

### 2. NOT IN 的坑

- 若子查询返回 NULL，`NOT IN` 结果可能为 NULL（全假）。
- 写法：`WHERE col NOT IN (SELECT ... WHERE col IS NOT NULL)` 或改用 `NOT EXISTS`。

### 3. 标量子查询 vs 表子查询

- 标量子查询：返回单行单列，可放在 SELECT、WHERE 等位置。
- 表子查询：返回多行，用于 FROM、IN 等。

---

## 六、索引与性能 → 对应「复杂查询优化」

### 1. 为什么多表 JOIN 要关注索引

- JOIN 条件列应有索引，否则可能全表扫描。
- 驱动表过滤条件列有索引，可减少参与 JOIN 的行数。

### 2. 覆盖索引

- 查询的列都在索引中，无需回表。
- 如 `SELECT id FROM t WHERE a = 1`，若 (a, id) 有索引，则只走索引。

### 3. 最左前缀

- 联合索引 (a, b, c)：可用的查询条件为 a、(a,b)、(a,b,c)。
- 单独查 b 或 c 无法用该索引。

---

## 七、排名与 TopN → 对应「第二高、部门最高、每科前 N」题

### 1. 第二高的薪水为什么用 LIMIT 1 OFFSET 1

- `ORDER BY salary DESC` 后，第一行是最高，第二行是第二高。
- `OFFSET 1` 跳过第一行，`LIMIT 1` 取一行。

### 2. 为什么用 IFNULL 包一层

- 若没有第二高（如只有一条记录），子查询返回空，`IFNULL(..., NULL)` 保证返回 NULL 而不是空结果集。

### 3. 部门最高工资为什么用 (departmentId, salary) IN

- 子查询返回 `(部门, 最高工资)` 的元组。
- 主查询用 `(departmentId, salary)` 匹配，直接得到「该部门最高工资的员工」。

---

## 八、行转列 / 列转行 → 对应「CASE WHEN 行转列」题

### 1. 行转列：MAX + CASE WHEN

- `GROUP BY` 后，每行只保留一个分组。
- `MAX(CASE WHEN c_id='01' THEN s_score END)`：该分组内，c_id='01' 的那一行取 s_score，其余为 NULL，MAX 取非 NULL 值（若只有一个）。

### 2. 为什么用 MAX

- 同一分组内，每个 c_id 对应一行，`CASE WHEN` 只会在匹配时返回非 NULL。
- `MAX` 用于聚合掉 NULL，取唯一非 NULL 值；也可以用 `MIN`，效果相同。

### 3. 列转行：UNION ALL

- 每列拆成一行，用 `UNION ALL` 纵向拼接。
- 需加 `WHERE 列 IS NOT NULL` 避免无意义行。

---

## 九、连续类问题 → 对应「连续登录 N 天」题

### 1. 核心思路：分组标记

- 连续日期相减为常数：若 `login_date - 日期序号` 相同，则属于同一连续段。
- `ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date)` 得到序号。
- `login_date - 序号` 作为分组标记，同一连续段内该值相同。

### 2. 去重

- 同一用户同一天可能有多条记录，需先 `DISTINCT user_id, login_date`。

### 3. 为什么用 INTERVAL 做日期差

- `login_date - rn` 在 MySQL 中会按日期运算，`rn` 为整数时表示天数差。
- `login_date - INTERVAL rn DAY` 更明确。

---

## 十、留存与 LAG/LEAD → 对应「次日留存、同环比」题

### 1. 次日留存

- 今天活跃用户中，明天也活跃的占比。
- 用 `LEFT JOIN` 将 `today` 与 `today+1` 关联，`user_id` 匹配即表示次日留存。

### 2. 环比（LAG）

- `LAG(amount, 1)`：上一期（如上月）的值。
- 环比 = (本期 - 上期) / 上期。

### 3. 同比（LAG）

- `LAG(amount, 12)`：12 期前（如去年同月）的值。
- 同比 = (本期 - 去年同期) / 去年同期。

---

## 十一、中位数 → 对应「中位数」题

### 1. 为什么用 ROW_NUMBER + FLOOR/CEIL

- 中位数位置：奇数个为 `(n+1)/2`，偶数个为 `n/2` 和 `n/2+1` 的平均。
- `FLOOR((cnt+1)/2)` 和 `CEIL((cnt+1)/2)` 可统一处理奇偶。

### 2. 分组中位数

- 在 `PARTITION BY` 中按部门等分组。
- 每组内同样用 `ROW_NUMBER` 和 `cnt` 找中间位置。

---

## 十二、速查表（面试可脱口而出）

| 考点 | 一句话 |
|------|--------|
| SQL 执行顺序 | FROM → WHERE → GROUP BY → 聚合 → HAVING → SELECT → ORDER BY → LIMIT |
| WHERE vs HAVING | WHERE 分组前过滤行，HAVING 分组后过滤组 |
| ROW_NUMBER vs RANK | ROW_NUMBER 同分不同号，RANK 同分跳号 |
| LAG vs LEAD | LAG 往前取，LEAD 往后取 |
| 行转列 | GROUP BY + MAX(CASE WHEN ... THEN ... END) |
| 连续登录 | 日期 - ROW_NUMBER 作为分组，连续段内该值相同 |
| 次日留存 | 今天活跃用户 LEFT JOIN 明天活跃，匹配即留存 |
| 环比 | LAG(amount,1)，(本期-上期)/上期 |
| 同比 | LAG(amount,12)，(本期-去年同月)/去年同月 |
