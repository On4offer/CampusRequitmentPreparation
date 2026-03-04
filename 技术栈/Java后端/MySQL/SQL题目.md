# SQL基础巩固练习题库（100题）

**目标**：熟练单表查询，建立肌肉记忆

1. 1.**基础查询与筛选** •SELECT, FROM, WHERE 基础组合 •比较运算符：=, <>, >, <, >=, <= •逻辑运算符：AND, OR, NOT •BETWEEN, IN, LIKE, IS NULL
2. 2.**结果排序与去重** •ORDER BY 多字段排序 •DISTINCT 去重 •LIMIT 分页

**推荐练习题量**：20-30题

 1. 基础查询与筛选（50题）

## 题目1-20：基础SELECT和WHERE

**表结构：employees（员工表）**

- •id (员工ID)
- •name (姓名)
- •age (年龄)
- •department (部门)
- •salary (薪资)
- •hire_date (入职日期)

**1. 查询所有员工信息**

```
SELECT * FROM employees;
```

**2. 查询所有员工的姓名和薪资**

```
SELECT name, salary FROM employees;
```

**3. 查询薪资大于50000的员工信息**

```
SELECT * FROM employees WHERE salary > 50000;
```

**4. 查询年龄等于30的员工姓名**

```
SELECT name FROM employees WHERE age = 30;
```

**5. 查询部门不是'技术部'的员工信息**

```
SELECT * FROM employees WHERE department <> '技术部';
```

**6. 查询年龄在25到35岁之间的员工信息**

```
SELECT * FROM employees WHERE age BETWEEN 25 AND 35;
```

**7. 查询薪资小于40000或大于60000的员工**

```
SELECT * FROM employees WHERE salary < 40000 OR salary > 60000;
```

**8. 查询部门为'销售部'或'市场部'的员工**

```
SELECT * FROM employees WHERE department IN ('销售部', '市场部');
```

**9. 查询姓名以'张'开头的员工**

```
SELECT * FROM employees WHERE name LIKE '张%';
```

**10. 查询姓名中包含'明'字的员工**

```
SELECT * FROM employees WHERE name LIKE '%明%';
```

**11. 查询邮箱为空的员工信息**

```
SELECT * FROM employees WHERE email IS NULL;
```

**12. 查询邮箱不为空的员工信息**

```
SELECT * FROM employees WHERE email IS NOT NULL;
```

**13. 查询年龄不等于30且薪资大于50000的员工**

```
SELECT * FROM employees WHERE age <> 30 AND salary > 50000;
```

**14. 查询部门为'技术部'且年龄小于35的员工**

```
SELECT * FROM employees WHERE department = '技术部' AND age < 35;
```

**15. 查询姓名以'李'开头且薪资在40000-60000之间的员工**

```
SELECT * FROM employees WHERE name LIKE '李%' AND salary BETWEEN 40000 AND 60000;
```

**16. 查询入职日期在2020年之后的员工**

```
SELECT * FROM employees WHERE hire_date > '2020-12-31';
```

**17. 查询部门不是'人事部'且不是'财务部'的员工**

```
SELECT * FROM employees WHERE department NOT IN ('人事部', '财务部');
```

**18. 查询年龄为25,30,35岁的员工**

```
SELECT * FROM employees WHERE age IN (25, 30, 35);
```

**19. 查询姓名第二个字是'小'的员工**

```
SELECT * FROM employees WHERE name LIKE '_小%';
```

**20. 查询姓名长度为2个字的员工**

```
SELECT * FROM employees WHERE name LIKE '__';
```

## 题目21-35：复杂WHERE条件组合

**表结构：products（产品表）**

- •product_id (产品ID)
- •product_name (产品名称)
- •category (类别)
- •price (价格)
- •stock (库存)
- •create_date (创建日期)

**21. 查询价格大于100且库存小于50的产品**

```
SELECT * FROM products WHERE price > 100 AND stock < 50;
```

**22. 查询类别为'电子产品'或'家电'且价格在500-2000之间的产品**

```
SELECT * FROM products WHERE category IN ('电子产品', '家电') AND price BETWEEN 500 AND 2000;
```

**23. 查询产品名称包含'手机'且库存不为0的产品**

```
SELECT * FROM products WHERE product_name LIKE '%手机%' AND stock <> 0;
```

**24. 查询创建日期在2023年且价格大于1000的产品**

```
SELECT * FROM products WHERE create_date BETWEEN '2023-01-01' AND '2023-12-31' AND price > 1000;
```

**25. 查询类别不是'食品'且不是'服装'的产品**

```
SELECT * FROM products WHERE category NOT IN ('食品', '服装');
```

**26. 查询价格小于50或大于2000的产品名称和价格**

```
SELECT product_name, price FROM products WHERE price < 50 OR price > 2000;
```

**27. 查询库存为0且创建日期在2022年之前的产品**

```
SELECT * FROM products WHERE stock = 0 AND create_date < '2022-01-01';
```

**28. 查询产品名称以'苹果'开头或以'三星'开头的产品**

```
SELECT * FROM products WHERE product_name LIKE '苹果%' OR product_name LIKE '三星%';
```

**29. 查询价格在100-500之间且库存大于100的产品**

```
SELECT * FROM products WHERE price BETWEEN 100 AND 500 AND stock > 100;
```

**30. 查询类别为'图书'且价格小于100的产品ID和名称**

```
SELECT product_id, product_name FROM products WHERE category = '图书' AND price < 100;
```

**31. 查询创建日期不为空且价格大于平均价格的产品**

```
SELECT * FROM products WHERE create_date IS NOT NULL AND price > (SELECT AVG(price) FROM products);
```

**32. 查询产品名称不包含'二手'且库存大于0的产品**

```
SELECT * FROM products WHERE product_name NOT LIKE '%二手%' AND stock > 0;
```

**33. 查询价格是99、199、299的产品**

```
SELECT * FROM products WHERE price IN (99, 199, 299);
```

**34. 查询类别为'家电'且(价格<1000或库存>50)的产品**

```
SELECT * FROM products WHERE category = '家电' AND (price < 1000 OR stock > 50);
```

**35. 查询产品名称长度为4-6个字符的产品**

```
SELECT * FROM products WHERE LENGTH(product_name) BETWEEN 4 AND 6;
```

## 题目36-50：NULL值处理

**表结构：students（学生表）**

- •student_id (学号)
- •name (姓名)
- •major (专业)
- •score (成绩)
- •birth_date (出生日期)
- •address (地址)

**36. 查询成绩为空的学生信息**

```
SELECT * FROM students WHERE score IS NULL;
```

**37. 查询地址不为空的学生姓名和专业**

```
SELECT name, major FROM students WHERE address IS NOT NULL;
```

**38. 查询成绩不为空且大于80的学生**

```
SELECT * FROM students WHERE score IS NOT NULL AND score > 80;
```

**39. 查询专业为'计算机'且成绩为空的学生**

```
SELECT * FROM students WHERE major = '计算机' AND score IS NULL;
```

**40. 查询出生日期为空或成绩为空的学生**

```
SELECT * FROM students WHERE birth_date IS NULL OR score IS NULL;
```

**41. 查询地址为空且专业不是'数学'的学生**

```
SELECT * FROM students WHERE address IS NULL AND major <> '数学';
```

**42. 查询成绩在60-100之间且不为空的学生**

```
SELECT * FROM students WHERE score BETWEEN 60 AND 100 AND score IS NOT NULL;
```

**43. 查询姓名以'王'开头且成绩不为空的学生**

```
SELECT * FROM students WHERE name LIKE '王%' AND score IS NOT NULL;
```

**44. 查询专业为空的学生的学号和姓名**

```
SELECT student_id, name FROM students WHERE major IS NULL;
```

**45. 查询所有信息都不为空的学生**

```
SELECT * FROM students WHERE name IS NOT NULL AND major IS NOT NULL 
AND score IS NOT NULL AND birth_date IS NOT NULL AND address IS NOT NULL;
```

**46. 查询成绩小于60或成绩为空的学生**

```
SELECT * FROM students WHERE score < 60 OR score IS NULL;
```

**47. 查询出生日期在2000年后且成绩不为空的学生**

```
SELECT * FROM students WHERE birth_date > '2000-12-31' AND score IS NOT NULL;
```

**48. 查询专业为'英语'且地址为空的学生**

```
SELECT * FROM students WHERE major = '英语' AND address IS NULL;
```

**49. 查询成绩大于90或专业为空的学生姓名**

```
SELECT name FROM students WHERE score > 90 OR major IS NULL;
```

**50. 查询所有有空值的学生信息（任一字段为空）**

```
SELECT * FROM students WHERE name IS NULL OR major IS NULL 
OR score IS NULL OR birth_date IS NULL OR address IS NULL;
```

 2. 结果排序与去重（50题）

## 题目51-70：ORDER BY排序

**表结构：sales（销售表）**

- •sale_id (销售ID)
- •product_name (产品名称)
- •salesperson (销售员)
- •amount (销售金额)
- •sale_date (销售日期)
- •region (区域)

**51. 按销售金额降序排列所有销售记录**

```
SELECT * FROM sales ORDER BY amount DESC;
```

**52. 按销售日期升序排列销售记录**

```
SELECT * FROM sales ORDER BY sale_date ASC;
```

**53. 按区域升序，同一区域内按金额降序排列**

```
SELECT * FROM sales ORDER BY region ASC, amount DESC;
```

**54. 查询销售金额前10名的记录**

```
SELECT * FROM sales ORDER BY amount DESC LIMIT 10;
```

**55. 按销售员姓名升序，再按销售日期降序排列**

```
SELECT * FROM sales ORDER BY salesperson ASC, sale_date DESC;
```

**56. 查询2023年的销售记录，按金额降序排列**

```
SELECT * FROM sales WHERE sale_date BETWEEN '2023-01-01' AND '2023-12-31' ORDER BY amount DESC;
```

**57. 按产品名称升序排列，相同产品按日期降序**

```
SELECT * FROM sales ORDER BY product_name ASC, sale_date DESC;
```

**58. 查询金额大于10000的记录，按区域和销售员排序**

```
SELECT * FROM sales WHERE amount > 10000 ORDER BY region, salesperson;
```

**59. 按销售日期升序排列，显示第11-20条记录**

```
SELECT * FROM sales ORDER BY sale_date ASC LIMIT 10 OFFSET 10;
```

**60. 查询每个销售员的最近一笔销售记录**

```
SELECT * FROM sales ORDER BY salesperson, sale_date DESC;
-- 注意：这需要结合GROUP BY，但基础阶段先理解排序
```

**61. 按金额降序排列，只显示前5条记录**

```
SELECT * FROM sales ORDER BY amount DESC LIMIT 5;
```

**62. 区域为'华东'的记录按金额降序排列**

```
SELECT * FROM sales WHERE region = '华东' ORDER BY amount DESC;
```

**63. 按产品名称升序，金额降序排列**

```
SELECT * FROM sales ORDER BY product_name ASC, amount DESC;
```

**64. 查询2023年第一季度的销售，按日期升序排列**

```
SELECT * FROM sales WHERE sale_date BETWEEN '2023-01-01' AND '2023-03-31' ORDER BY sale_date ASC;
```

**65. 按销售员升序，相同销售员按产品名称升序排列**

```
SELECT * FROM sales ORDER BY salesperson ASC, product_name ASC;
```

**66. 查询金额在5000-20000之间的记录，按日期降序排列**

```
SELECT * FROM sales WHERE amount BETWEEN 5000 AND 20000 ORDER BY sale_date DESC;
```

**67. 按区域升序，金额降序，显示前20条**

```
SELECT * FROM sales ORDER BY region ASC, amount DESC LIMIT 20;
```

**68. 查询特定销售员的记录，按日期降序排列**

```
SELECT * FROM sales WHERE salesperson = '张三' ORDER BY sale_date DESC;
```

**69. 按产品名称升序，相同产品按销售员升序排列**

```
SELECT * FROM sales ORDER BY product_name ASC, salesperson ASC;
```

**70. 查询最近30天的销售记录，按金额降序排列**

```
SELECT * FROM sales WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY) ORDER BY amount DESC;
```

## 题目71-85：DISTINCT去重

**表结构：customers（客户表）**

- •customer_id (客户ID)
- •name (姓名)
- •city (城市)
- •country (国家)
- •industry (行业)
- •contact_date (联系日期)

**71. 查询所有不重复的城市**

```
SELECT DISTINCT city FROM customers;
```

**72. 查询所有不重复的行业**

```
SELECT DISTINCT industry FROM customers;
```

**73. 查询不重复的城市和国家组合**

```
SELECT DISTINCT city, country FROM customers;
```

**74. 查询有客户的城市列表（去重）**

```
SELECT DISTINCT city FROM customers WHERE name IS NOT NULL;
```

**75. 查询不重复的国家和行业组合**

```
SELECT DISTINCT country, industry FROM customers;
```

**76. 查询有联系记录的不重复年份**

```
SELECT DISTINCT YEAR(contact_date) as year FROM customers WHERE contact_date IS NOT NULL;
```

**77. 查询不同城市的不同行业数量（去重组合）**

```
SELECT DISTINCT city, industry FROM customers ORDER BY city;
```

**78. 查询不重复的城市，按字母顺序排列**

```
SELECT DISTINCT city FROM customers ORDER BY city;
```

**79. 查询有客户的不同国家**

```
SELECT DISTINCT country FROM customers WHERE name IS NOT NULL;
```

**80. 查询不重复的行业，按行业名称排序**

```
SELECT DISTINCT industry FROM customers ORDER BY industry;
```

**81. 查询每个城市的不同行业（去重后计数）**

```
SELECT city, COUNT(DISTINCT industry) FROM customers GROUP BY city;
```

**82. 查询不重复的城市和国家，按国家、城市排序**

```
SELECT DISTINCT country, city FROM customers ORDER BY country, city;
```

**83. 查询有联系记录的不同月份**

```
SELECT DISTINCT MONTH(contact_date) as month FROM customers WHERE contact_date IS NOT NULL;
```

**84. 查询不重复的客户所在城市**

```
SELECT DISTINCT city FROM customers WHERE customer_id IS NOT NULL;
```

**85. 查询每个国家的不同城市数量（去重统计）**

```
SELECT country, COUNT(DISTINCT city) FROM customers GROUP BY country;
```

## 题目86-100：LIMIT分页和综合应用

**表结构：orders（订单表）**

- •order_id (订单ID)
- •customer_name (客户姓名)
- •product (产品)
- •quantity (数量)
- •price (单价)
- •order_date (订单日期)
- •status (状态)

**86. 查询最近的10个订单**

```
SELECT * FROM orders ORDER BY order_date DESC LIMIT 10;
```

**87. 查询第11-20条订单记录**

```
SELECT * FROM orders ORDER BY order_id LIMIT 10 OFFSET 10;
```

**88. 查询数量最多的前5个订单**

```
SELECT * FROM orders ORDER BY quantity DESC LIMIT 5;
```

**89. 按订单日期分页，每页10条，查询第3页**

```
SELECT * FROM orders ORDER BY order_date LIMIT 10 OFFSET 20;
```

**90. 查询状态为'已完成'的订单，按金额降序排列前10个**

```
SELECT * FROM orders WHERE status = '已完成' ORDER BY (quantity * price) DESC LIMIT 10;
```

**91. 查询不同状态下的订单数量**

```
SELECT status, COUNT(*) FROM orders GROUP BY status;
```

**92. 查询每个客户的不同产品订购数量**

```
SELECT customer_name, COUNT(DISTINCT product) FROM orders GROUP BY customer_name;
```

**93. 查询订单金额前10%的记录（近似）**

```
SELECT * FROM orders ORDER BY (quantity * price) DESC LIMIT (SELECT COUNT(*) / 10 FROM orders);
```

**94. 查询最近7天的订单，按时间倒序排列**

```
SELECT * FROM orders WHERE order_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) ORDER BY order_date DESC;
```

**95. 查询每个产品的不同客户数量**

```
SELECT product, COUNT(DISTINCT customer_name) FROM orders GROUP BY product;
```

**96. 分页查询：每页5条，按订单ID升序，查询第4页**

```
SELECT * FROM orders ORDER BY order_id LIMIT 5 OFFSET 15;
```

**97. 查询数量大于10且状态为'待发货'的订单，按日期排序**

```
SELECT * FROM orders WHERE quantity > 10 AND status = '待发货' ORDER BY order_date;
```

**98. 查询不重复的客户姓名和产品组合**

```
SELECT DISTINCT customer_name, product FROM orders;
```

**99. 查询订单金额最高的3个订单**

```
SELECT * FROM orders ORDER BY (quantity * price) DESC LIMIT 3;
```

**100. 综合查询：状态为'已完成'的不同客户的最新订单**

```
SELECT DISTINCT customer_name, order_date 
FROM orders 
WHERE status = '已完成' 
ORDER BY order_date DESC;
```

------

# 第二阶段：核心函数掌握（2-3周）

**目标**：掌握常用函数和分组统计

1. 1.**聚合函数** •COUNT, SUM, AVG, MAX, MIN •GROUP BY 分组统计 •HAVING 对分组结果筛选
2. 2.**日期与字符串函数** •DATE_FORMAT, DATEDIFF, NOW() •CONCAT, SUBSTRING, LENGTH •CASE WHEN 条件判断

**推荐练习题量**：30-40题

非常棒 👍——你已经完成了第一个阶段的“SQL 基础查询”练习（100题），接下来进入第二阶段的“函数与分组统计”。
 这一阶段的重点是 **函数操作 + 分组分析 + 条件聚合 + 字符串/日期处理**，
 我会为你整理出 **40 道覆盖全面的题目 + SQL 实现**，并尽量 **复用第一阶段表结构**（如 `employees`, `orders`, `products`, `customers`, `sales`, `students`），
 仅在必要时新增 `attendance`（考勤表）和 `departments`（部门表）两个轻量辅助表。

------

## 🏗️ 一、（若无则补充）辅助建表语句

```sql
-- 部门表（部门维度分析）
CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(50),
    manager VARCHAR(50),
    location VARCHAR(50)
);

-- 考勤表（日期函数练习）
CREATE TABLE attendance (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    work_date DATE,
    check_in TIME,
    check_out TIME,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);
```

------

## 🎯 二、40 道核心函数与分组统计练习题（分模块）

------

###  🌟 第一部分：聚合函数与分组统计（COUNT / SUM / AVG / MAX / MIN）

1️⃣ 统计公司员工总数

```sql
SELECT COUNT(*) AS total_employees FROM employees;
```

2️⃣ 查询技术部员工平均薪资

```sql
SELECT AVG(salary) AS avg_salary FROM employees WHERE department = '技术部';
```

3️⃣ 查询每个部门的员工数量

```sql
SELECT department, COUNT(*) AS emp_count FROM employees GROUP BY department;
```

 4️⃣ 查询每个部门的最高薪资

```sql
SELECT department, MAX(salary) AS max_salary FROM employees GROUP BY department;
```

 5️⃣ 查询每个部门的最低薪资与平均薪资

```sql
SELECT department, MIN(salary) AS min_salary, AVG(salary) AS avg_salary
FROM employees GROUP BY department;
```

 6️⃣ 查询每个部门薪资总和，并按总额降序

```sql
SELECT department, SUM(salary) AS total_salary
FROM employees GROUP BY department
ORDER BY total_salary DESC;
```

 7️⃣ 查询薪资总额超过 300000 的部门

```sql
SELECT department, SUM(salary) AS total_salary
FROM employees
GROUP BY department
HAVING total_salary > 300000;
```

 8️⃣ 查询平均薪资大于50000的部门

```sql
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING AVG(salary) > 50000;
```

 9️⃣ 查询各部门员工平均年龄

```sql
SELECT department, AVG(age) AS avg_age FROM employees GROUP BY department;
```

 🔟 查询各部门员工数量和最高薪资

```sql
SELECT department, COUNT(*) AS emp_count, MAX(salary) AS top_salary
FROM employees GROUP BY department;
```

------

### 🌟 第二部分：HAVING 进阶筛选 + 多表分组统计

 11️⃣ 查询下单次数超过 3 次的客户

```sql
SELECT customer_name, COUNT(*) AS order_count
FROM orders
GROUP BY customer_name
HAVING order_count > 3;
```

 12️⃣ 查询总购买金额超过 5000 的客户

```sql
SELECT customer_name, SUM(quantity * price) AS total_spent
FROM orders
GROUP BY customer_name
HAVING total_spent > 5000;
```

 13️⃣ 查询各产品的总销量（按数量求和）

```sql
SELECT product, SUM(quantity) AS total_qty
FROM orders
GROUP BY product
ORDER BY total_qty DESC;
```

 14️⃣ 查询每位销售员的平均销售额

```sql
SELECT salesperson, AVG(amount) AS avg_sales
FROM sales
GROUP BY salesperson;
```

 15️⃣ 查询各区域销售总额，筛选出销售额超过 100000 的区域

```sql
SELECT region, SUM(amount) AS total_sales
FROM sales
GROUP BY region
HAVING total_sales > 100000;
```

 16️⃣ 查询每位销售员的最高与最低销售额

```sql
SELECT salesperson, MAX(amount) AS max_sale, MIN(amount) AS min_sale
FROM sales
GROUP BY salesperson;
```

 17️⃣ 查询每位销售员的销售次数与总金额

```sql
SELECT salesperson, COUNT(*) AS sale_count, SUM(amount) AS total_amount
FROM sales
GROUP BY salesperson;zgliy
```

 18️⃣ 查询每个城市客户数量及平均联系次数

```sql
SELECT city, COUNT(DISTINCT customer_id) AS client_count, COUNT(contact_date) AS contact_times
FROM customers
GROUP BY city;
```

 19️⃣ 查询每个国家的城市数量（去重统计）

```sql
SELECT country, COUNT(DISTINCT city) AS city_count FROM customers GROUP BY country;
```

 20️⃣ 查询平均订单金额最高的客户（取前1）

```sql
SELECT customer_name, AVG(quantity * price) AS avg_spent
FROM orders
GROUP BY customer_name
ORDER BY avg_spent DESC
LIMIT 1;
```

------

### 🌟 第三部分：日期函数（DATE_FORMAT / DATEDIFF / NOW）

 21️⃣ 查询每个员工入职天数

```sql
SELECT name, DATEDIFF(NOW(), hire_date) AS days_worked FROM employees;
```

 22️⃣ 查询过去一年入职的员工

```sql
SELECT * FROM employees WHERE hire_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR);
```

 23️⃣ 查询每月入职的员工数量

```sql
SELECT DATE_FORMAT(hire_date, '%Y-%m') AS month, COUNT(*) AS emp_count
FROM employees
GROUP BY month
ORDER BY month;
```

 24️⃣ 查询每个月的销售额

```sql
SELECT DATE_FORMAT(sale_date, '%Y-%m') AS month, SUM(amount) AS total_sales
FROM sales
GROUP BY month;
```

 25️⃣ 查询下单距离现在超过 30 天的订单

```sql
SELECT * FROM orders WHERE DATEDIFF(NOW(), order_date) > 30;
```

 26️⃣ 查询客户联系时间距离上次超过 180 天的记录

```sql
SELECT * FROM customers
WHERE contact_date IS NOT NULL
AND DATEDIFF(NOW(), contact_date) > 180;
```

 27️⃣ 查询每个员工的打卡天数（考勤）

```sql
SELECT employee_id, COUNT(DISTINCT work_date) AS days_attended
FROM attendance
GROUP BY employee_id;
```

 28️⃣ 查询每天平均上班时长（使用 TIME_TO_SEC 计算小时数）

```sql
SELECT work_date, 
       AVG(TIME_TO_SEC(TIMEDIFF(check_out, check_in)) / 3600) AS avg_hours
FROM attendance
GROUP BY work_date;
```

------

### 🌟 第四部分：字符串函数（CONCAT / SUBSTRING / LENGTH）

 29️⃣ 拼接员工姓名与部门信息

```sql
SELECT CONCAT(name, ' - ', department) AS full_info FROM employees;
```

 30️⃣ 查询名字长度大于 3 的员工

```sql
SELECT name FROM employees WHERE LENGTH(name) > 3;
```

 31️⃣ 查询产品名前 3 个字符

```sql
SELECT product_name, SUBSTRING(product_name, 1, 3) AS short_name FROM products;
```

 32️⃣ 查询客户城市和国家拼接字段

```sql
SELECT CONCAT(city, ', ', country) AS location FROM customers;
```

 33️⃣ 查询销售员姓名后缀字母

```sql
SELECT salesperson, SUBSTRING(salesperson, -1) AS last_char FROM sales;
```

 34️⃣ 查询邮箱域名（假设 email 字段存在）

```sql
SELECT name, SUBSTRING_INDEX(email, '@', -1) AS domain FROM employees WHERE email IS NOT NULL;
```

------

### 🌟 第五部分：条件函数（CASE WHEN）

 35️⃣ 按薪资等级分类员工

```sql
SELECT name,
       CASE 
           WHEN salary >= 80000 THEN '高薪'
           WHEN salary >= 50000 THEN '中薪'
           ELSE '低薪'
       END AS salary_level
FROM employees;
```

 36️⃣ 统计各薪资等级的员工数量

```sql
SELECT 
    CASE 
        WHEN salary >= 80000 THEN '高薪'
        WHEN salary >= 50000 THEN '中薪'
        ELSE '低薪'
    END AS salary_level,
    COUNT(*) AS emp_count
FROM employees
GROUP BY salary_level;
```

 37️⃣ 按成绩等级分类学生

```sql
SELECT name,
       CASE
           WHEN score >= 90 THEN '优秀'
           WHEN score >= 75 THEN '良好'
           WHEN score >= 60 THEN '及格'
           ELSE '不及格'
       END AS level
FROM students;
```

 38️⃣ 按产品价格分类（高/中/低价）

```sql
SELECT product_name,
       CASE 
           WHEN price >= 2000 THEN '高价'
           WHEN price >= 500 THEN '中价'
           ELSE '低价'
       END AS price_level
FROM products;
```

 39️⃣ 查询每个客户的消费等级（基于总消费）

```sql
SELECT customer_name,
       CASE
           WHEN SUM(quantity * price) >= 10000 THEN 'VIP 客户'
           WHEN SUM(quantity * price) >= 5000 THEN '重点客户'
           ELSE '普通客户'
       END AS customer_level
FROM orders
GROUP BY customer_name;
```

 40️⃣ 按销售额等级统计销售员数量

```sql
SELECT 
    CASE 
        WHEN SUM(amount) >= 200000 THEN '顶级销售'
        WHEN SUM(amount) >= 100000 THEN '优秀销售'
        ELSE '普通销售'
    END AS sale_level,
    COUNT(*) AS person_count
FROM sales
GROUP BY sale_level;
```

------

## ✅ 三、阶段总结

| 模块             | 题数     | 覆盖内容                   |
| ---------------- | -------- | -------------------------- |
| 聚合函数基础     | 10       | COUNT, SUM, AVG, MAX, MIN  |
| 分组统计与HAVING | 10       | GROUP BY + HAVING          |
| 日期函数         | 8        | DATE_FORMAT, DATEDIFF, NOW |
| 字符串函数       | 6        | CONCAT, SUBSTRING, LENGTH  |
| 条件判断         | 6        | CASE WHEN 分类统计         |
| **合计**         | **40题** | 全面覆盖第二阶段核心知识   |

------

是否希望我帮你把这 **40 题导出成一份 `.sql 文件`（带题号注释 + 可直接导入 MySQL 运行）**？
 可自动生成练习数据并按章节注释清晰划分。

------

# 第三阶段：多表关联（3-4周）

**目标**：掌握各种JOIN和子查询

1. **表连接**
   - INNER JOIN
   - LEFT/RIGHT JOIN
   - 多表关联查询
   - 自连接场景
2. **子查询**
   - 标量子查询
   - EXISTS/NOT EXISTS
   - IN/NOT IN 子查询

### 🌟 第三阶段练习题（40-50题）

------

### 🏗️ 辅助建表语句及示例数据

 **1. `departments` 表（部门表）**

```sql
CREATE TABLE departments (
    dept_id INT PRIMARY KEY AUTO_INCREMENT,
    dept_name VARCHAR(50),
    manager VARCHAR(50),
    location VARCHAR(50)
);

-- 示例数据
INSERT INTO departments (dept_name, manager, location) 
VALUES ('技术部', '张经理', '北京'), 
       ('销售部', '李经理', '上海'),
       ('财务部', '王经理', '广州');
```

 **2. `attendance` 表（考勤表）**

```sql
CREATE TABLE attendance (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    employee_id INT,
    work_date DATE,
    check_in TIME,
    check_out TIME,
    FOREIGN KEY (employee_id) REFERENCES employees(id)
);

-- 示例数据
INSERT INTO attendance (employee_id, work_date, check_in, check_out) 
VALUES (1, '2023-10-01', '09:00:00', '18:00:00'),
       (2, '2023-10-01', '09:30:00', '18:30:00'),
       (1, '2023-10-02', '09:00:00', '18:00:00');
```

------

### 🌟 第一部分：表连接（JOIN）

 **1. 使用INNER JOIN查询每个员工的姓名和所在部门**

```sql
SELECT e.name, d.dept_name
FROM employees e
INNER JOIN departments d ON e.department = d.dept_name;
```

 **2. 查询所有员工与其所在部门的名称，如果没有部门，显示为'未知'（使用LEFT JOIN）**

```sql
SELECT e.name, COALESCE(d.dept_name, '未知') AS dept_name
FROM employees e
LEFT JOIN departments d ON e.department = d.dept_name;
```

 **3. 查询所有部门和负责该部门的经理**

```sql
SELECT dept_name, manager 
FROM departments;
```

 **4. 使用RIGHT JOIN查询所有部门及其对应的员工（包括没有员工的部门）**

```sql
SELECT d.dept_name, e.name 
FROM departments d
RIGHT JOIN employees e ON d.dept_name = e.department;
```

 **5. 使用INNER JOIN查询员工的姓名、入职日期以及部门的经理**

```sql
SELECT e.name, e.hire_date, d.manager
FROM employees e
INNER JOIN departments d ON e.department = d.dept_name;
```

 **6. 使用JOIN查询每个员工的工作日期与考勤信息（使用INNER JOIN）**

```sql
SELECT e.name, a.work_date, a.check_in, a.check_out
FROM employees e
INNER JOIN attendance a ON e.id = a.employee_id;
```

 **7. 查询每个员工所在部门的名称以及部门经理（使用JOIN连接多个表）**

```sql
SELECT e.name, d.dept_name, d.manager
FROM employees e
JOIN departments d ON e.department = d.dept_name;
```

 **8. 使用自连接查询每个员工与其上级经理的关系（假设employees表中有manager_id字段）**

```sql
SELECT e1.name AS employee_name, e2.name AS manager_name
FROM employees e1
JOIN employees e2 ON e1.manager_id = e2.id;
```

------

### 🌟 第二部分：子查询

 **9. 使用子查询查询薪资最高的员工姓名和薪资**

```sql
SELECT name, salary
FROM employees
WHERE salary = (SELECT MAX(salary) FROM employees);
```

 **10. 使用子查询查询每个部门的平均薪资**

```sql
SELECT department, AVG(salary)
FROM employees
GROUP BY department;
```

 **11. 使用IN子查询查询在销售部门的员工信息**

```sql
SELECT * 
FROM employees
WHERE department IN (SELECT dept_name FROM departments WHERE dept_name = '销售部');
```

 **12. 使用NOT IN子查询查询不在技术部和财务部的员工**

```sql
SELECT * 
FROM employees
WHERE department NOT IN (SELECT dept_name FROM departments WHERE dept_name IN ('技术部', '财务部'));
```

 **13. 使用EXISTS子查询查询哪些员工有考勤记录**

```sql
SELECT * 
FROM employees e
WHERE EXISTS (SELECT 1 FROM attendance a WHERE e.id = a.employee_id);
```

 **14. 使用EXISTS查询每个部门是否有员工**

```sql
SELECT dept_name
FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department = d.dept_name);
```

 **15. 查询那些入职日期在2022年之后的员工，使用标量子查询**

```sql
SELECT name, hire_date
FROM employees
WHERE hire_date > (SELECT '2022-01-01');
```

 **16. 查询所有薪资高于部门平均薪资的员工**

```sql
SELECT name, salary
FROM employees e
WHERE salary > (SELECT AVG(salary) FROM employees WHERE department = e.department);
```

 **17. 使用子查询查询每个部门薪资总额大于300000的部门**

```sql
SELECT department
FROM employees
GROUP BY department
HAVING SUM(salary) > (SELECT 300000);
```

 **18. 使用子查询查询员工中薪资高于所有销售部员工的人员**

```sql
SELECT name, salary
FROM employees
WHERE salary > (SELECT MAX(salary) FROM employees WHERE department = '销售部');
```

 **19. 使用NOT EXISTS查询没有考勤记录的员工**

```sql
SELECT name 
FROM employees e
WHERE NOT EXISTS (SELECT 1 FROM attendance a WHERE e.id = a.employee_id);
```

 **20. 使用IN子查询查询薪资高于50000且属于技术部的员工**

```sql
SELECT * 
FROM employees 
WHERE department IN (SELECT dept_name FROM departments WHERE dept_name = '技术部') AND salary > 50000;
```

------

### 🌟 第三部分：复杂多表关联

 **21. 查询每个部门的员工数量及薪资总额**

```sql
SELECT department, COUNT(*) AS emp_count, SUM(salary) AS total_salary
FROM employees
GROUP BY department;
```

 **22. 查询每个部门的员工数量和经理**

```sql
SELECT d.dept_name, COUNT(e.id) AS emp_count, d.manager
FROM departments d
LEFT JOIN employees e ON e.department = d.dept_name
GROUP BY d.dept_name;
```

 **23. 查询所有销售员的销售总金额，按金额排序**

```sql
SELECT salesperson, SUM(amount) AS total_sales
FROM sales
GROUP BY salesperson
ORDER BY total_sales DESC;
```

 **24. 查询每个部门的平均薪资大于50000的部门信息**

```sql
SELECT department, AVG(salary) AS avg_salary
FROM employees
GROUP BY department
HAVING avg_salary > 50000;
```

 **25. 查询所有有员工的部门信息**

```sql
SELECT dept_name, manager
FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department = d.dept_name);
```

------

### 🌟 第四部分：综合应用

 **26. 查询每个员工的姓名、部门及其工作天数（考勤信息）**

```sql
SELECT e.name, e.department, COUNT(a.work_date) AS work_days
FROM employees e
LEFT JOIN attendance a ON e.id = a.employee_id
GROUP BY e.id;
```

 **27. 查询每个部门的经理和其下属员工的姓名**

```sql
SELECT d.manager, e.name 
FROM departments d
LEFT JOIN employees e ON e.department = d.dept_name;
```

 **28. 查询各部门薪资总和超过100000的部门名称**

```sql
SELECT department
FROM employees
GROUP BY department
HAVING SUM(salary) > 100000;
```

 **29. 查询销售额大于平均销售额的销售员姓名**

```sql
SELECT salesperson
FROM sales
GROUP BY salesperson
HAVING SUM(amount) > (SELECT AVG(amount) FROM sales);
```

 **30. 查询薪资高于所有技术部员工的员工姓名**

```sql
SELECT name
FROM employees e
WHERE salary > (SELECT MAX(salary) FROM employees WHERE department = '技术部');
```

 **31. 查询每位销售员的销售总额及其所在区域**

```sql
SELECT salesperson, SUM(amount) AS total_sales, region
FROM sales
GROUP BY salesperson, region;
```

 **32. 查询没有任何销售记录的销售员**

```sql
SELECT name
FROM employees
WHERE NOT EXISTS (SELECT 1 FROM sales WHERE salesperson = employees.name);
```

 **33. 查询某个部门的最高薪资与最低薪资**

```sql
SELECT department, MAX(salary) AS max_salary, MIN(salary) AS min_salary
FROM employees
WHERE department = '技术部'
GROUP BY department;
```

 **34. 查询每个部门的薪资总额和员工数量**

```sql
SELECT department, SUM(salary) AS total_salary, COUNT(*) AS emp_count
FROM employees
GROUP BY department;
```

 **35. 查询每个销售员的销售额和销售记录数量**

```sql
SELECT salesperson, SUM(amount) AS total_sales, COUNT(*) AS sale_count
FROM sales
GROUP BY salesperson;
```

 **36. 查询每个客户的最大和最小订单金额**

```sql
SELECT customer_name, MAX(quantity * price) AS max_order, MIN(quantity * price) AS min_order
FROM orders
GROUP BY customer_name;
```

**37. 查询最近三个月内每个销售员的销售额**

```sql
SELECT salesperson, SUM(amount) AS total_sales
FROM sales
WHERE sale_date > DATE_SUB(CURDATE(), INTERVAL 3 MONTH)
GROUP BY salesperson;
```

**38. 查询每个产品的销售数量和销售金额**

```sql
SELECT product, SUM(quantity) AS total_qty, SUM(quantity * price) AS total_amount
FROM orders
GROUP BY product;
```

**39. 查询每个城市的客户数量及平均订单金额**

```sql
SELECT city, COUNT(DISTINCT customer_id) AS client_count, AVG(quantity * price) AS avg_order_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_name
GROUP BY city;
```

**40. 查询客户每月的总购买金额（按月统计）**

```sql
SELECT customer_name, DATE_FORMAT(order_date, '%Y-%m') AS month, SUM(quantity * price) AS total_spent
FROM orders
GROUP BY customer_name, month;
```

------

### 🏁 结束总结

此阶段通过 `JOIN` 和 `子查询` 涵盖了多表关联查询、数据整合、分组统计等基本技能，帮助理解如何在多个表之间建立联系和利用子查询进行数据筛选与处理。

------

# 第四阶段：高级应用（3-4周）

**目标**：解决复杂业务场景

1. 1.**窗口函数**（面试高频） •RANK, DENSE_RANK, ROW_NUMBER •LAG, LEAD 前后期对比 •累计计算等高级应用
2. 2.**常见业务场景** •连续登录、留存分析 •Top N问题、排名问题 •行列转换、数据透视

**推荐练习题量**：50-60题

## 推荐刷题平台

**新手友好**：

- •**牛客网** - 有SQL专项练习，题目分类清晰
- •**LeetCode** - Database专项，从易到难

**实战推荐**：

```
-- 示例：从最简单的开始
-- 题目：查询学生表中所有男生的姓名和年龄
SELECT name, age FROM students WHERE gender = '男';

-- 逐步增加难度
-- 题目：查询每个班级的平均成绩，按平均分降序排列
SELECT class_id, AVG(score) as avg_score
FROM scores 
GROUP BY class_id 
ORDER BY avg_score DESC;
```

## 学习建议

1. 1.**每日坚持**：每天至少做2-3题，保持手感
2. 2.**先思考后看答案**：给自己15分钟思考时间，实在不行再看解法
3. 3.**总结模板**：同类题目总结解题模式
4. 4.**模拟面试**：找朋友或录音模拟面试场景