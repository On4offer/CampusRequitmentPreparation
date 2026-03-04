### `@Transactional` 注解

**`@Transactional`** 是 Spring 框架中用于声明式事务管理的注解。它是 Spring AOP（面向切面编程）的一部分，允许开发者通过简单的注解来为方法或类配置事务，而无需显式编写事务管理代码。它的**主要作用是将事务管理与业务逻辑分离**，使得代码更加简洁、可维护，并且方便地处理事务的提交、回滚等。

### 1. **`@Transactional` 的基本概念**

在 Spring 中，**事务管理** 主要分为两种方式：

- **[声明式事务管理](声明式事务管理)**：通过配置（如 `@Transactional` 注解）来管理事务，不需要显式写出事务的开始、提交或回滚操作。（还有基于 XML 的声明式事务管理；通过 AspectJ 声明式事务使用自定义注解 + AOP 实现声明式事务）
- **编程式事务管理**：通过编程代码手动控制事务的开始、提交或回滚。

`@Transactional` 注解属于声明式事务管理的一种方式。它通常用来标记需要事务管理的方法或类，在方法执行时自动进行事务的开启、提交或回滚。

### 2. **`@Transactional` 的基本用法**

#### 2.1 **作用范围**

- `@Transactional` 可以用于方法级别，也可以用于类级别。
  - **类级别**：如果 `@Transactional` 注解放在类级别，那么该类中的所有公共方法都会默认开启事务。
  - **方法级别**：如果 `@Transactional` 注解放在方法级别，那么只有该方法会被事务管理。

#### 2.2 **示例：方法级别的事务管理**

```java
@Service
public class UserService {

    @Transactional
    public void addUser(User user) {
        // 添加用户
        userRepository.save(user);
        // 模拟异常，事务会回滚
        if (true) {
            throw new RuntimeException("Simulating exception");
        }
    }
}
```

在这个示例中，`addUser` 方法被 `@Transactional` 注解标注，这表示该方法中的操作会在一个事务中执行。如果方法执行过程中抛出异常，事务会自动回滚。

#### 2.3 **示例：类级别的事务管理**

```java
@Service
@Transactional
public class UserService {

    public void addUser(User user) {
        // 添加用户
        userRepository.save(user);
    }

    public void updateUser(User user) {
        // 更新用户
        userRepository.update(user);
    }
}
```

在这个示例中，整个 `UserService` 类中的所有公共方法都会由 `@Transactional` 注解进行事务管理。

### 3. **`@Transactional` 注解的常用属性**

`@Transactional` 提供了一些常用的属性来定制事务的行为：

#### 3.1 **`propagation`**：事务传播行为

`propagation` 属性定义了一个事务方法如何参与已有事务的行为。常见的事务传播行为有：

- **`REQUIRED`**（默认值）：如果当前存在事务，则加入该事务；如果没有事务，则创建一个新的事务。
- **`SUPPORTS`**：如果当前存在事务，则加入该事务；如果没有事务，则以非事务方式执行。
- **`MANDATORY`**：如果当前没有事务，则抛出异常；如果有事务，则加入当前事务。
- **`REQUIRES_NEW`**：无论当前是否存在事务，都会创建一个新的事务，并挂起当前事务。
- **`NOT_SUPPORTED`**：如果当前存在事务，则挂起当前事务，以非事务方式执行方法。
- **`NEVER`**：如果当前存在事务，则抛出异常；如果没有事务，则以非事务方式执行。
- **`NESTED`**：如果当前存在事务，则创建一个事务嵌套在当前事务中。

**示例：使用 `propagation` 属性**

```java
@Transactional(propagation = Propagation.REQUIRES_NEW)
public void processNewTransaction() {
    // 该方法会创建一个新的事务，挂起当前事务
}
```

#### 3.2 **`isolation`**：事务隔离级别

`isolation` 属性定义了事务之间的隔离级别，控制一个事务对其他事务的可见性。常见的事务隔离级别有：

- **`READ_UNCOMMITTED`**：最低的隔离级别，事务可以读取未提交的数据（脏读）。
- **`READ_COMMITTED`**：只能读取已提交的数据，避免脏读。
- **`REPEATABLE_READ`**：确保事务读取的数据在事务内一直是一样的，避免了脏读和不可重复读。
- **`SERIALIZABLE`**：最高的隔离级别，强制事务串行执行，避免了脏读、不可重复读和幻读。

**示例：使用 `isolation` 属性**

```java
@Transactional(isolation = Isolation.SERIALIZABLE)
public void processTransaction() {
    // 事务隔离级别为 SERIALIZABLE
}
```

#### 3.3 **`timeout`**：事务超时

`timeout` 属性定义了事务的最大执行时间。如果事务执行超过指定时间，则会抛出异常并回滚事务。

**示例：使用 `timeout` 属性**

```java
@Transactional(timeout = 30)
public void processTransaction() {
    // 事务最多执行 30 秒
}
```

#### 3.4 **`readOnly`**：只读事务

`readOnly` 属性指示事务是否是只读事务。如果设置为 `true`，数据库可以进行优化，避免对数据库进行不必要的写操作。通常用于查询操作。

**示例：使用 `readOnly` 属性**

```java
@Transactional(readOnly = true)
public List<User> getUsers() {
    // 只读事务，适用于查询操作
    return userRepository.findAll();
}
```

#### 3.5 **`rollbackFor`** 和 **`noRollbackFor`**：回滚规则

`rollbackFor` 和 `noRollbackFor` 属性允许指定哪些异常类型会触发回滚。

- **`rollbackFor`**：指定哪些异常会导致事务回滚。
- **`noRollbackFor`**：指定哪些异常不会导致事务回滚。

**示例：使用 `rollbackFor` 和 `noRollbackFor` 属性**

```java
@Transactional(rollbackFor = Exception.class)
public void processTransaction() throws Exception {
    // 如果抛出 Exception 异常，事务将回滚
}
@Transactional(noRollbackFor = IllegalArgumentException.class)
public void processTransaction() throws IllegalArgumentException {
    // 如果抛出 IllegalArgumentException 异常，事务不会回滚
}
```

### 4. **`@Transactional` 的工作原理**

`@Transactional` 是通过 **Spring AOP**（面向切面编程）实现的。Spring AOP 会在目标方法执行时，在方法执行前后插入事务相关的逻辑，如开启、提交、回滚事务等。具体工作流程如下：

1. **代理创建**：Spring 在目标对象上创建代理对象，代理对象负责事务管理的工作。
2. **方法执行**：当调用 `@Transactional` 注解的方法时，代理会拦截方法的调用。
3. **事务开始**：如果当前没有事务，代理会创建一个新的事务。
4. **方法执行**：目标方法执行过程中，如果发生异常，事务会被回滚；如果没有异常，事务会提交。
5. **事务提交或回滚**：根据方法执行结果，Spring 会在事务完成时提交或回滚事务。

### 5. **`@Transactional` 的应用场景**

- **事务性操作**：例如在银行系统中进行转账操作时，确保两个数据库操作（扣款和存款）要么都成功，要么都失败。
- **批量更新或插入**：多个操作需要在同一个事务中执行，确保数据的一致性。
- **数据一致性保障**：在需要多个步骤保证一致性的场景下，例如订单支付、库存扣减等。

### 6. **总结**

- **`@Transactional`** 是 Spring 提供的声明式事务管理的注解，可以通过简单的配置来管理方法或类的事务。
- 通过配置 `propagation`、`isolation`、`timeout`、`readOnly` 等属性，可以控制事务的行为，如事务传播方式、隔离级别、超时设置等。
- **AOP 技术** 实现了 `@Transactional` 的事务管理逻辑，使得事务管理与业务逻辑解耦，提高了代码的清晰度和可维护性。
- `@Transactional` 是一个非常强大的工具，适用于涉及多步骤操作的场景，如金融交易、批量数据处理等。