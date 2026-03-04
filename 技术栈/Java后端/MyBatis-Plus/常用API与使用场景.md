# 📌 MyBatis-Plus 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**日常开发中的 BaseMapper、Wrapper、注解与配置**，便于速查与上手。

---

## 一、BaseMapper 常用方法

### 1.1 插入与删除

| 方法 | 说明 |
|------|------|
| **insert(T entity)** | 插入一条，主键回写（需实体 @TableId 配置 useId=true 或 IdType.ASSIGN_ID） |
| **deleteById(Serializable id)** | 按主键删除（逻辑删除时改为 update） |
| **deleteBatchIds(Collection ids)** | 按主键批量删除 |
| **delete(Wrapper&lt;T&gt; wrapper)** | 按条件删除 |

### 1.2 更新

| 方法 | 说明 |
|------|------|
| **updateById(T entity)** | 按主键更新，null 字段不更新（需配置字段策略） |
| **update(T entity, Wrapper&lt;T&gt; wrapper)** | 按条件更新，entity 中 set 要改的字段 |

### 1.3 查询

| 方法 | 说明 |
|------|------|
| **selectById(Serializable id)** | 按主键查一条 |
| **selectBatchIds(Collection ids)** | 按主键批量查 |
| **selectOne(Wrapper&lt;T&gt; wrapper)** | 按条件查一条，多条会抛异常 |
| **selectList(Wrapper&lt;T&gt; wrapper)** | 按条件查列表 |
| **selectPage(IPage&lt;T&gt; page, Wrapper&lt;T&gt; wrapper)** | 分页查询（需配置分页插件） |
| **selectCount(Wrapper&lt;T&gt; wrapper)** | 按条件统计总数 |

---

## 二、实体类常用注解

| 注解 | 说明 | 示例 |
|------|------|------|
| **@TableName("表名")** | 表名与类名不一致时 | @TableName("sys_user") |
| **@TableId(type = IdType.AUTO)** | 主键策略：AUTO 自增、ASSIGN_ID 雪花 | 主键字段 |
| **@TableField("列名")** | 列名与属性名不一致时 | @TableField("user_name") |
| **@TableField(exist = false)** | 非数据库字段 | 传输用 DTO 字段 |
| **@TableField(fill = FieldFill.INSERT)** | 插入时自动填充 | createTime |
| **@TableField(fill = FieldFill.INSERT_UPDATE)** | 插入与更新时填充 | updateTime |
| **@TableLogic** | 逻辑删除字段，查询自动加条件 | deleted |
| **@Version** | 乐观锁版本字段 | version |

---

## 三、条件构造器 Wrapper 常用方法

### 3.1 QueryWrapper / LambdaQueryWrapper

| 方法 | 说明 | 示例 |
|------|------|------|
| **eq(column, val)** | 等于 | wrapper.eq("status", 1) |
| **ne(column, val)** | 不等于 | wrapper.ne("deleted", 1) |
| **gt / ge / lt / le** | 大于 / 大于等于 / 小于 / 小于等于 | wrapper.gt("age", 18) |
| **like(column, val)** | 模糊 %val% | wrapper.like("name", "张") |
| **likeLeft / likeRight** | 左/右模糊 | likeLeft("code", "A") → like 'A%' |
| **in(column, coll)** | IN | wrapper.in("id", ids) |
| **between(column, v1, v2)** | BETWEEN | wrapper.between("age", 18, 30) |
| **isNull / isNotNull** | 空 / 非空 | wrapper.isNull("remark") |
| **orderByAsc / orderByDesc** | 排序 | wrapper.orderByDesc("create_time") |
| **last("limit 1")** | 拼接末尾（慎用，防注入） | 仅必要时用 |
| **select("id","name")** | 指定查询列 | 减少回表 |

Lambda 版避免列名字符串：**LambdaQueryWrapper&lt;User&gt;**. **eq(User::getStatus, 1)**、**like(User::getName, "张")** 等。

### 3.2 UpdateWrapper

- **set(column, val)** / **setSql("col = col + 1")** 设置更新值；**eq/ne/...** 同 QueryWrapper 作 WHERE；**update(entity, wrapper)** 时 entity 可只放主键，具体 set 在 wrapper 中。

---

## 四、分页

### 4.1 配置（Spring Boot）

```java
@Bean
public MybatisPlusInterceptor mybatisPlusInterceptor() {
    MybatisPlusInterceptor interceptor = new MybatisPlusInterceptor();
    interceptor.addInnerInterceptor(new PaginationInnerInterceptor(DbType.MYSQL));
    return interceptor;
}
```

### 4.2 使用

```java
Page<User> page = new Page<>(current, size);  // current 从 1 开始
page.setSearchCount(true);   // 是否查总数，大表可设 false
mapper.selectPage(page, wrapper);
List<User> list = page.getRecords();
long total = page.getTotal();
```

---

## 五、逻辑删除与乐观锁

### 5.1 逻辑删除

- 实体字段：**@TableLogic**（如 value="0" delval="1"）；配置 **global-config.db-config.logic-delete-field** 与 **logic-delete-value** / **logic-not-delete-value**。删除变 update，查询自动加 deleted=0。

### 5.2 乐观锁

- 实体加 **@Version**；配置 **OptimisticLockerInnerInterceptor**；更新时 WHERE 带 version，SET version=version+1，影响行数 0 表示冲突。

---

## 六、自动填充

- 实现 **MetaObjectHandler**，重写 **insertFill(MetaObject metaObject)**、**updateFill(MetaObject metaObject)**，根据 **metaObject.hasSetter("createTime")** 等判断并 **setValue**；实体字段 **@TableField(fill = FieldFill.INSERT)** 等；将 Handler 注册为 Bean。

---

## 七、使用场景对照

| 场景 | 推荐做法 |
|------|----------|
| 单表 CRUD | 继承 BaseMapper，直接 insert/selectById/updateById/deleteById |
| 多条件列表 | LambdaQueryWrapper 链式 eq/like/in/orderBy，mapper.selectList(wrapper) |
| 分页列表 | Page&lt;T&gt; + selectPage(page, wrapper)，配置分页插件 |
| 只查部分列 | wrapper.select(User::getId, User::getName) |
| 动态条件 | wrapper.eq(StrUtil.isNotBlank(name), User::getName, name) 等 |
| 批量 id 查 | selectBatchIds(ids) |
| 存在则更新 | insert 前 selectById，有则 updateById（或数据库 on duplicate key） |
| 逻辑删除 | 实体 @TableLogic，删除用 deleteById 即可 |
| 并发更新 | 实体 @Version + 乐观锁插件，更新失败重试或提示 |
| 创建/更新时间 | @TableField(fill) + MetaObjectHandler |
| 复杂 SQL / 多表 | Mapper 中自定义方法 + XML 或 @Select，与 Plus 混用 |

---

## 八、配置要点（application.yml）

```yaml
mybatis-plus:
  mapper-locations: classpath*:/mapper/**/*.xml
  type-aliases-package: com.example.entity
  global-config:
    db-config:
      id-type: auto
      logic-delete-field: deleted
      logic-delete-value: 1
      logic-not-delete-value: 0
  configuration:
    map-underscore-to-camel-case: true
```

---

## 九、与学习笔记的对应关系

- **概述与架构** → 第 1 章；**入门与实体** → 第 2 章；**Wrapper** → 第 3 章；**分页** → 第 4 章；**自动填充与乐观锁** → 第 5 章；**多表与自定义 SQL** → 第 6 章；**代码生成器** → 第 7 章；**插件** → 第 8 章；**Spring Boot 整合** → 第 9 章；**实战与面试** → 第 10～12 章及附录。

> 更多原理与面试题见《学习笔记》相应章节。MyBatis 原生 API 与 XML 见《MyBatis 学习笔记》及《MyBatis 常用API与使用场景》。
