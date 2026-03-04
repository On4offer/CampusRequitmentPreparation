# 📌 MyBatis 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**日常开发中的 Mapper 写法、XML 标签与配置**，便于速查与上手。

---

## 一、Mapper 接口与 XML 对应

### 1.1 基本约定

- Mapper 接口方法名 = XML 中 **&lt;select&gt;/&lt;insert&gt;/&lt;update&gt;/&lt;delete&gt;** 的 **id**；**namespace** = Mapper 接口全限定名。
- 单参可直接写形参名或 **@Param("key")**；多参必须 **@Param**，XML 中用 **#{key}** 引用。

### 1.2 常用方法签名示例

```java
// 按 id 查
User selectById(@Param("id") Long id);
// 多条件查询
List<User> listByCondition(@Param("name") String name, @Param("status") Integer status);
// 分页（或交予 PageHelper）
List<User> listPage(@Param("offset") int offset, @Param("size") int size);
// 插入并回写主键
int insert(User user);  // useGeneratedKeys="true" keyProperty="id"
// 更新
int updateById(User user);
// 删除
int deleteById(@Param("id") Long id);
```

---

## 二、XML 常用标签速查

### 2.1 CRUD 标签

| 标签 | 说明 | 常用属性 |
|------|------|----------|
| **&lt;select&gt;** | 查询 | id、resultType/resultMap、parameterType（可省） |
| **&lt;insert&gt;** | 插入 | id、useGeneratedKeys、keyProperty（回写主键） |
| **&lt;update&gt;** | 更新 | id |
| **&lt;delete&gt;** | 删除 | id |

### 2.2 参数与结果

| 写法 | 说明 |
|------|------|
| **#{name}** | 预编译占位符，防注入，推荐 |
| **${name}** | 字符串替换，仅用于 order by 列名等，慎用 |
| **resultType="User"** | 单表实体，列名与属性一致或开启驼峰 |
| **resultMap="BaseResultMap"** | 自定义映射、嵌套、集合 |

### 2.3 动态 SQL 标签

| 标签 | 说明 | 示例 |
|------|------|------|
| **&lt;if test="name != null and name != ''"&gt;** | 条件成立才拼接 | 多条件查询 |
| **&lt;where&gt;** | 自动加 WHERE 并去掉首 AND/OR | 包住多个 &lt;if&gt; |
| **&lt;foreach collection="ids" item="id" open="(" separator="," close=")"&gt;** | 遍历集合 | IN (id1,id2) 或批量 insert |
| **&lt;choose&gt;/&lt;when&gt;/&lt;otherwise&gt;** | 多分支选一 | 类似 switch |
| **&lt;trim&gt;** | 去掉前后缀 | 替代 where/set 的精细控制 |
| **&lt;set&gt;** | 更新时去掉末尾逗号 | 动态 update |

---

## 三、常用 XML 片段示例

### 3.1 多条件查询（&lt;where&gt; + &lt;if&gt;）

```xml
<select id="listByCondition" resultType="User">
  SELECT * FROM user
  <where>
    <if test="name != null and name != ''"> AND name LIKE concat('%',#{name},'%')</if>
    <if test="status != null"> AND status = #{status}</if>
  </where>
  ORDER BY id DESC
</select>
```

### 3.2 主键回写（insert）

```xml
<insert id="insert" useGeneratedKeys="true" keyProperty="id">
  INSERT INTO user (name, status) VALUES (#{name}, #{status})
</insert>
```

### 3.3 IN 查询（&lt;foreach&gt;）

```xml
<select id="listByIds" resultType="User">
  SELECT * FROM user WHERE id IN
  <foreach collection="ids" item="id" open="(" separator="," close=")">
    #{id}
  </foreach>
</select>
```

### 3.4 动态更新（&lt;set&gt; + &lt;if&gt;）

```xml
<update id="updateById">
  UPDATE user
  <set>
    <if test="name != null"> name = #{name},</if>
    <if test="status != null"> status = #{status},</if>
  </set>
  WHERE id = #{id}
</update>
```

---

## 四、Spring Boot 配置要点（application.yml）

```yaml
mybatis:
  mapper-locations: classpath:mapper/**/*.xml
  type-aliases-package: com.example.entity
  configuration:
    map-underscore-to-camel-case: true
    cache-enabled: true
    log-impl: org.apache.ibatis.logging.slf4j.Slf4jImpl
```

- **mapper-locations**：XML 位置；**type-aliases-package**：实体包，XML 中可直接写类名；**map-underscore-to-camel-case**：列名下划线转驼峰；**log-impl**：打印 SQL 便于调试。

---

## 五、使用场景对照

| 场景 | 推荐做法 |
|------|----------|
| 单表 CRUD | 简单 SQL 写 XML 或注解；复杂条件用 &lt;where&gt;+&lt;if&gt;；也可用 MyBatis-Plus BaseMapper |
| 多条件列表 | &lt;where&gt; + &lt;if&gt;，参数用 @Param；避免 where 1=1，用 &lt;where&gt; 自动处理 |
| 主键回写 | &lt;insert&gt; 上 useGeneratedKeys="true" keyProperty="id" |
| IN 查询 | &lt;foreach&gt; 拼 (?,?,?)；collection 为 list/array 或 @Param 名 |
| 分页 | PageHelper 插件；或手写 LIMIT #{offset},#{size} + count 查询 |
| 批量插入 | &lt;foreach&gt; 拼多行 VALUES；或 ExecutorType.BATCH + 循环 insert |
| 多表关联 | resultMap + &lt;association&gt;/&lt;collection&gt;；或分两次查询避免 N+1 |
| 防注入 | 一律用 **#{}**；**${}** 仅用于 order by 列名等不可用 #{} 处并严格校验 |

---

## 六、与学习笔记的对应关系

- **架构与组件** → 第 2 章；**配置** → 第 3 章；**Mapper 与动态 SQL** → 第 4、6 章；**运行机制与缓存** → 第 5、7 章；**Spring 整合** → 第 8 章；**插件** → 第 9 章；**MyBatis-Plus** → 第 10 章；**实战与面试** → 第 11～13 章及附录。

> 更多原理与面试题见《学习笔记》相应章节。MyBatis-Plus 常用 API 见《MyBatis-Plus 学习笔记》及同系列速查文档。
