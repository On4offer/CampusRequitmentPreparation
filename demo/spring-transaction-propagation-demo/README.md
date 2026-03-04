# Spring 事务传播机制演示项目

[![Java](https://img.shields.io/badge/Java-17-orange.svg)](https://www.oracle.com/java/)
[![Spring Boot](https://img.shields.io/badge/Spring%20Boot-3.1.10-brightgreen.svg)](https://spring.io/projects/spring-boot)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

一个完整的 Spring 事务传播机制学习和演示项目，通过实际的电商订单业务场景，深入理解 Spring 中 7 种事务传播机制的行为特性、使用场景和最佳实践。

## 📋 目录

- [项目简介](#项目简介)
- [技术栈](#技术栈)
- [核心特性](#核心特性)
- [项目结构](#项目结构)
- [快速开始](#快速开始)
- [事务传播机制详解](#事务传播机制详解)
- [API 文档](#api-文档)
- [测试指南](#测试指南)
- [常见问题](#常见问题)
- [最佳实践](#最佳实践)
- [参考资料](#参考资料)

## 🎯 项目简介

本项目是一个 Spring Boot 3.x 事务传播机制演示项目，通过模拟电商订单创建流程（扣库存、减余额、创建订单、记录日志），全面展示 Spring 中 7 种事务传播机制的实际应用场景和区别。

### 为什么需要了解事务传播机制？

在实际开发中，我们经常遇到以下场景：
- 订单创建失败时，需要保证库存和余额都能回滚
- 日志记录需要独立提交，即使主业务失败也要记录
- 某些操作必须在事务中执行，否则应该报错
- 复杂业务中，部分操作失败不应该影响整体流程

事务传播机制正是解决这些问题的关键。

## 🛠 技术栈

| 技术 | 版本 | 说明 |
|------|------|------|
| Java | 17 | JDK 版本 |
| Spring Boot | 3.1.10 | 应用框架 |
| Spring Data JPA | 3.1.10 | 数据持久化 |
| H2 Database | 2.1.214 | 内存数据库（用于演示） |
| Lombok | 1.18.36 | 代码简化工具 |
| Maven | 3.6+ | 项目构建工具 |

## ✨ 核心特性

- ✅ **7 种事务传播机制完整演示**：REQUIRED、REQUIRES_NEW、SUPPORTS、NOT_SUPPORTED、MANDATORY、NEVER、NESTED
- ✅ **真实业务场景**：基于电商订单流程，贴近实际开发
- ✅ **RESTful API**：提供完整的 HTTP 接口，方便测试和演示
- ✅ **单元测试**：包含完整的 JUnit 5 测试用例
- ✅ **详细注释**：代码中包含详细的中文注释和说明
- ✅ **H2 控制台**：内置数据库控制台，方便查看数据变化

## 📁 项目结构

```
spring-transaction-propagation-demo/
├── src/
│   ├── main/
│   │   ├── java/com/example/
│   │   │   ├── TransactionPropagationDemoApplication.java  # 应用启动类
│   │   │   ├── config/
│   │   │   │   └── DataInitializer.java                      # 数据初始化配置
│   │   │   ├── controller/
│   │   │   │   └── TransactionPropagationController.java   # REST API 控制器
│   │   │   ├── entity/
│   │   │   │   ├── User.java                                # 用户实体
│   │   │   │   ├── Product.java                             # 商品实体
│   │   │   │   ├── Order.java                               # 订单实体
│   │   │   │   └── Log.java                                 # 日志实体
│   │   │   ├── repository/
│   │   │   │   ├── UserRepository.java                      # 用户数据访问
│   │   │   │   ├── ProductRepository.java                   # 商品数据访问
│   │   │   │   ├── OrderRepository.java                     # 订单数据访问
│   │   │   │   └── LogRepository.java                       # 日志数据访问
│   │   │   └── service/
│   │   │       ├── OrderService.java                        # 订单服务接口
│   │   │       ├── PaymentService.java                      # 支付服务接口
│   │   │       ├── StockService.java                        # 库存服务接口
│   │   │       ├── LogService.java                          # 日志服务接口
│   │   │       └── impl/
│   │   │           ├── OrderServiceImpl.java                 # 订单服务实现
│   │   │           ├── PaymentServiceImpl.java              # 支付服务实现
│   │   │           ├── StockServiceImpl.java                # 库存服务实现
│   │   │           └── LogServiceImpl.java                  # 日志服务实现
│   │   └── resources/
│   │       └── application.properties                       # 应用配置文件
│   └── test/
│       └── java/com/example/
│           └── TransactionPropagationTests.java            # 单元测试
├── pom.xml                                                   # Maven 配置文件
├── lombok.config                                             # Lombok 配置
└── README.md                                                 # 项目说明文档
```

## 🚀 快速开始

### 环境要求

- **JDK**: 17 或更高版本
- **Maven**: 3.6 或更高版本
- **IDE**: IntelliJ IDEA（推荐）或 Eclipse

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/yourusername/spring-transaction-propagation-demo.git
cd spring-transaction-propagation-demo
```

2. **构建项目**

```bash
mvn clean install
```

3. **运行项目**

```bash
mvn spring-boot:run
```

或者直接在 IDE 中运行 `TransactionPropagationDemoApplication` 类的 `main` 方法。

4. **验证启动**

应用启动成功后，访问以下地址：

- **应用首页**: http://localhost:8080
- **H2 数据库控制台**: http://localhost:8080/h2-console
  - JDBC URL: `jdbc:h2:mem:transactiondemo`
  - 用户名: `sa`
  - 密码: (留空)

### IDEA 配置（重要）

如果使用 IntelliJ IDEA，需要配置 Lombok 插件：

1. **安装 Lombok 插件**
   - `File` → `Settings` → `Plugins`
   - 搜索 "Lombok" 并安装

2. **启用注解处理器**
   - `File` → `Settings` → `Build, Execution, Deployment` → `Compiler` → `Annotation Processors`
   - 勾选 `Enable annotation processing`

3. **重新导入 Maven 项目**
   - 右键 `pom.xml` → `Maven` → `Reload Project`

## 📚 事务传播机制详解

### 1. REQUIRED（默认）

**行为特性**：
- 如果当前存在事务，则加入该事务
- 如果当前没有事务，则创建一个新事务

**使用场景**：
- 大多数业务操作的标准选择
- 需要保证数据一致性的场景

**示例代码**：
```java
@Transactional(propagation = Propagation.REQUIRED)
public String createOrderWithRequired(Long userId, Long productId, Integer quantity) {
    // 扣库存、减余额、创建订单都在同一事务中
    stockService.deductStockWithRequired(productId, quantity);
    paymentService.deductBalance(userId, totalAmount);
    orderRepository.save(order);
    // 任一操作失败，全部回滚
}
```

**回滚特性**：整体回滚，任一操作失败全部回滚

---

### 2. REQUIRES_NEW

**行为特性**：
- 无论是否存在事务，都创建一个新事务
- 如果存在事务，则挂起当前事务

**使用场景**：
- 日志记录（必须独立提交）
- 消息发送（避免主事务回滚影响）
- 审计操作（需要记录所有尝试）

**示例代码**：
```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void recordLog(Long userId, String operation, String content) {
    // 即使主事务回滚，日志也会独立提交
    logRepository.save(log);
}
```

**回滚特性**：内外部事务完全独立，互不影响

---

### 3. SUPPORTS

**行为特性**：
- 如果当前存在事务，则加入该事务
- 如果当前没有事务，则以非事务方式执行

**使用场景**：
- 可选的查询操作
- 可以参与事务但不强制的事务操作

**示例代码**：
```java
@Transactional(propagation = Propagation.SUPPORTS)
public void deductStockWithSupports(Long productId, Integer quantity) {
    // 如果有事务就参与，没有事务就直接执行
    productRepository.decreaseStock(productId, quantity);
}
```

**回滚特性**：跟随外部事务，如果没有事务则不会回滚

---

### 4. NOT_SUPPORTED

**行为特性**：
- 总是以非事务方式执行
- 如果存在事务，则挂起当前事务

**使用场景**：
- 大查询操作（避免长时间占用事务）
- 报表生成（不需要事务保证）
- 性能敏感的操作

**示例代码**：
```java
@Transactional(propagation = Propagation.NOT_SUPPORTED)
public void generateReport() {
    // 即使外层有事务，这里也会以非事务方式执行
    // 避免长时间占用事务资源
}
```

**回滚特性**：不会回滚，即使外层事务回滚也不影响

---

### 5. MANDATORY

**行为特性**：
- 必须在事务中运行
- 如果当前没有事务，则抛出异常

**使用场景**：
- 财务系统中的关键操作
- 必须保证事务一致性的操作
- 强制要求事务环境的业务逻辑

**示例代码**：
```java
@Transactional(propagation = Propagation.MANDATORY)
public boolean deductBalanceWithMandatory(Long userId, BigDecimal amount) {
    // 必须在事务中调用，否则抛出异常
    return userRepository.decreaseBalance(userId, amount) > 0;
}
```

**回滚特性**：跟随外部事务，如果没有事务则抛出异常

---

### 6. NEVER

**行为特性**：
- 必须在非事务状态下运行
- 如果存在事务，则抛出异常

**使用场景**：
- 高频读取操作（避免事务开销）
- 禁止在事务中执行的操作
- 性能优化的场景

**示例代码**：
```java
@Transactional(propagation = Propagation.NEVER)
public void deductStockWithNever(Long productId, Integer quantity) {
    // 禁止在事务中执行，否则抛出异常
    productRepository.decreaseStock(productId, quantity);
}
```

**回滚特性**：不会回滚，如果在事务中调用则抛出异常

---

### 7. NESTED

**行为特性**：
- 如果当前存在事务，则创建一个嵌套事务（基于保存点）
- 如果当前没有事务，则创建一个新事务
- 嵌套事务可以独立回滚，不影响外层事务
- 外层事务回滚会导致嵌套事务也回滚

**使用场景**：
- 复杂业务中，部分操作失败不应该影响整体
- 优惠券扣减失败时，不影响主订单
- 需要局部回滚的场景

**示例代码**：
```java
@Transactional(propagation = Propagation.REQUIRED)
public String createOrder(Long userId, Long productId, Integer quantity) {
    // 主事务
    stockService.deductStockWithNested(productId, quantity); // 嵌套事务
    // 如果嵌套事务失败，可以只回滚嵌套事务，主事务继续
}
```

**回滚特性**：
- 内层事务回滚不影响外层事务
- 外层事务回滚会导致内层事务也回滚

---

## 📊 事务传播机制对比表

| 传播机制 | 有事务环境 | 无事务环境 | 主要应用场景 | 回滚特性 | 异常处理 |
|---------|-----------|-----------|------------|----------|----------|
| **REQUIRED** | 加入当前事务 | 新建事务 | 大多数业务操作 | 整体回滚 | 全部回滚 |
| **REQUIRES_NEW** | 新建事务，挂起原事务 | 新建事务 | 日志、消息发送 | 独立回滚 | 互不影响 |
| **SUPPORTS** | 加入当前事务 | 非事务执行 | 可选查询操作 | 随外部事务 | 跟随外部 |
| **NOT_SUPPORTED** | 非事务执行，挂起原事务 | 非事务执行 | 大查询、报表 | 不回滚 | 不回滚 |
| **MANDATORY** | 加入当前事务 | **抛出异常** | 强制事务操作 | 随外部事务 | 无事务则异常 |
| **NEVER** | **抛出异常** | 非事务执行 | 禁止事务操作 | 不回滚 | 有事务则异常 |
| **NESTED** | 嵌套事务（保存点） | 新建事务 | 局部可回滚操作 | 内层可独立回滚 | 内层不影响外层 |

## 🔌 API 文档

### 基础信息

- **Base URL**: `http://localhost:8080`
- **Content-Type**: `application/json`

### REQUIRED 传播机制

#### 测试 REQUIRED（成功场景）
```http
GET /api/transaction/required
```

**响应示例**：
```json
{
  "message": "REQUIRED 测试成功：订单创建成功，事务提交"
}
```

#### 测试 REQUIRED（回滚场景）
```http
GET /api/transaction/required-rollback
```

**说明**：演示主事务回滚时，所有操作都会回滚

---

### REQUIRES_NEW 传播机制

#### 测试 REQUIRES_NEW
```http
GET /api/transaction/requires-new
```

#### 测试 REQUIRES_NEW（主事务回滚）
```http
GET /api/transaction/requires-new-rollback
```

**说明**：演示主事务回滚时，REQUIRES_NEW 的事务（如日志）会独立提交

---

### SUPPORTS 传播机制

```http
GET /api/transaction/supports
```

---

### NOT_SUPPORTED 传播机制

```http
GET /api/transaction/not-supported
```

---

### MANDATORY 传播机制

#### 测试 MANDATORY（非事务环境 - 预期失败）
```http
GET /api/transaction/mandatory
```

**说明**：直接调用会失败，因为没有事务上下文

#### 测试 MANDATORY（事务环境 - 成功）
```http
GET /api/transaction/mandatory-with-transaction
```

---

### NEVER 传播机制

#### 测试 NEVER（非事务环境 - 成功）
```http
GET /api/transaction/never
```

#### 测试 NEVER（事务环境 - 预期失败）
```http
GET /api/transaction/never-with-transaction
```

**说明**：在事务中调用会失败，因为 NEVER 禁止在事务中执行

---

### NESTED 传播机制

#### 测试 NESTED
```http
GET /api/transaction/nested
```

#### 测试 NESTED（内部回滚）
```http
GET /api/transaction/nested-inner-rollback
```

**说明**：演示内部嵌套事务回滚，不影响外层事务

#### 测试 NESTED（外部回滚）
```http
GET /api/transaction/nested-outer-rollback
```

**说明**：演示外部事务回滚，会导致嵌套事务也回滚

---

### 其他测试

#### 测试事务自调用问题
```http
GET /api/transaction/self-invocation
```

**说明**：演示同一类中调用事务方法，传播机制可能失效的问题

---

## 🧪 测试指南

### 运行所有测试

```bash
mvn test
```

### 运行特定测试类

```bash
mvn test -Dtest=TransactionPropagationTests
```

### 测试用例说明

项目包含完整的 JUnit 5 测试用例，覆盖所有事务传播机制：

| 测试方法 | 测试内容 |
|---------|---------|
| `testRequired()` | 验证 REQUIRED 传播机制的基本行为 |
| `testRequiredWithRollback()` | 验证 REQUIRED 的回滚行为 |
| `testRequiresNew()` | 验证 REQUIRES_NEW 的独立性 |
| `testMandatory()` | 验证 MANDATORY 的强制事务性 |
| `testNever()` | 验证 NEVER 的非事务性 |
| `testNested()` | 验证 NESTED 的嵌套事务行为 |
| `testSupports()` | 验证 SUPPORTS 的灵活性 |
| `testNotSupported()` | 验证 NOT_SUPPORTED 的非事务性 |
| `testSelfInvocation()` | 验证事务自调用问题 |

### 测试数据

测试前会自动初始化：
- **用户**: ID=1, 余额=1000
- **商品**: ID=1, 价格=500, 库存=100

## ❓ 常见问题

### Q1: 为什么事务传播机制在同一个类中调用不生效？

**A**: Spring 的事务管理是通过 AOP 代理实现的。当在同一个类中调用事务方法时，调用是直接通过 `this` 引用进行的，不会经过代理，所以事务注解不会被触发。

**解决方案**：
1. 将方法拆分到不同的类中（推荐）
2. 通过 `AopContext.currentProxy()` 获取代理对象后调用
3. 使用 `@Async` 等注解强制走代理

### Q2: REQUIRES_NEW 和 NESTED 有什么区别？

**A**: 

| 特性 | REQUIRES_NEW | NESTED |
|------|-------------|--------|
| 事务关系 | 完全独立的新事务 | 嵌套事务（基于保存点） |
| 提交顺序 | 内层先提交，外层后提交 | 外层提交时内层一起提交 |
| 回滚影响 | 互不影响 | 外层回滚影响内层，内层回滚不影响外层 |
| 使用场景 | 日志、消息等必须独立提交 | 局部可回滚的复杂业务 |

### Q3: 如何选择合适的事务传播机制？

**A**: 根据业务需求选择：

- **数据一致性要求高** → `REQUIRED`
- **操作必须独立提交** → `REQUIRES_NEW`
- **可选事务操作** → `SUPPORTS`
- **性能优先、大查询** → `NOT_SUPPORTED`
- **强制事务环境** → `MANDATORY`
- **禁止事务环境** → `NEVER`
- **局部回滚需求** → `NESTED`

### Q4: 什么情况下会发生 "UnexpectedRollbackException"？

**A**: 当内层事务设置了 `rollbackFor` 属性导致回滚，但外层事务没有捕获异常继续提交时，Spring 会抛出此异常，因为实际事务已经被内层标记为回滚了。

**解决方案**：在外层捕获异常并处理，或者调整事务传播机制。

### Q5: NESTED 传播机制在哪些数据库上支持？

**A**: NESTED 基于保存点（Savepoint）机制，需要数据库支持保存点功能。大多数主流数据库都支持：
- ✅ MySQL（InnoDB）
- ✅ PostgreSQL
- ✅ Oracle
- ✅ SQL Server
- ❌ H2（部分版本可能不支持，本项目使用 H2 仅用于演示）

## 💡 最佳实践

### 1. 默认使用 REQUIRED

对于大多数业务操作，使用 `REQUIRED` 是最安全的选择，可以保证数据一致性。

### 2. 日志记录使用 REQUIRES_NEW

日志记录应该使用 `REQUIRES_NEW`，确保即使主业务失败，操作日志也能被记录。

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void recordLog(String operation) {
    // 日志记录逻辑
}
```

### 3. 避免在同一个类中调用事务方法

将事务方法拆分到不同的服务类中，避免事务失效问题。

### 4. 合理使用 NESTED

对于复杂业务，使用 `NESTED` 可以实现局部回滚，但要注意数据库支持情况。

### 5. 明确事务边界

在方法上明确标注事务传播机制，避免使用默认值导致理解困难。

### 6. 异常处理

在事务方法中正确处理异常，避免意外的回滚或提交。

## 📖 参考资料

- [Spring 官方文档 - 事务管理](https://docs.spring.io/spring-framework/docs/current/reference/html/data-access.html#transaction)
- [Spring @Transactional 注解详解](https://docs.spring.io/spring-framework/docs/current/javadoc-api/org/springframework/transaction/annotation/Transactional.html)
- [Spring 事务传播机制深入解析](https://spring.io/guides/gs/managing-transactions/)
- [Spring Boot 官方文档](https://docs.spring.io/spring-boot/docs/current/reference/htmlsingle/)

## 📝 许可证

本项目采用 MIT 许可证，详情请参阅 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## ⭐ 致谢

感谢 Spring 团队提供的优秀框架，让事务管理变得如此简单。

---

**如果这个项目对你有帮助，请给一个 ⭐ Star！**
