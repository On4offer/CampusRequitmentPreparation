# Demo 总览（校招手撕 / 口述 / 项目代码演示）

本目录按 **一类问题一个文件夹** 组织 demo，用于：

- **校招手撕代码题**：单例、LRU（含并发版）、生产者-消费者、交替/顺序打印、手写 ArrayList/HashMap、死锁、线程池、限流、带过期缓存、手写 Future、Redis 分布式锁等。
- **口述代码题**：公平锁、equals/hashCode、ThreadLocal、反射、Comparable/Comparator、泛型、自定义注解校验等。
- **设计模式与后端**：观察者、策略、工厂、责任链/模板方法；拷贝、序列化、锁、事务、动态代理、Spring Boot、Spring MVC 等。

**算法题（LeetCode 风格）** 在仓库内单独刷，本目录不收录。

---

## 命名说明（文件夹与包名）

- **文件夹**：部分使用**下划线**（如 `singleton_demo`、`copy_demo`、`thread_order_demo`），与 Java 包名一致；部分使用**连字符**（如 `producer-consumer-blockingqueue-demo`），便于阅读。
- **包名**：所有 demo 的 Java 包名均为**下划线**（如 `producer_consumer_blockingqueue_demo`），因包名不能含连字符。
- **运行**：无论文件夹名如何，请进入对应目录后按该目录内 `README.md` 的说明执行（多数为 `javac` / `java`，主类为 `包名.类名`；**JavaSE** 为 Maven 项目，包名 `com.learning.`*，使用 `mvn compile` / `mvn exec:java`）。

---

## 一、手撕 / 并发与设计模式


| 文件夹                                                                             | 内容                                                               |
| ------------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| [singleton_demo](./singleton_demo/)                                             | 单例 7 种实现（饿汉、懒汉、DCL、静态内部类、枚举等）+ 面试问答                              |
| [producer-consumer-blockingqueue-demo](./producer-consumer-blockingqueue-demo/) | 生产者-消费者（Lock + Condition 手写阻塞队列）                                 |
| [producer-consumer-wait-notify-demo](./producer-consumer-wait-notify-demo/)     | 生产者-消费者（wait/notify）                                             |
| [alternate-print-demo](./alternate-print-demo/)                                 | 两线程交替打印（如 1~100）                                                 |
| [abc-order-print-demo](./abc-order-print-demo/)                                 | 三线程顺序打印 ABC 循环                                                   |
| [thread_order_demo](./thread_order_demo/)                                       | 多线程顺序执行（join、CountDownLatch、CyclicBarrier、Semaphore、wait/notify） |
| [deadlock-demo](./deadlock-demo/)                                               | 死锁示例与排查                                                          |
| [simple-thread-pool-demo](./simple-thread-pool-demo/)                           | 手写简单线程池                                                          |
| [rate-limiter-demo](./rate-limiter-demo/)                                       | 限流：令牌桶、固定窗口                                                      |
| [expire-cache-demo](./expire-cache-demo/)                                       | 带过期缓存（DelayQueue）                                                |
| [fair-lock-demo](./fair-lock-demo/)                                             | 公平锁 vs 非公平锁                                                      |
| [callable-future-demo](./callable-future-demo/)                                 | Callable + Future 取结果（手撕题其他高频）                                   |
| [simple-future-demo](./simple-future-demo/)                                     | 手写简易 Future（阻塞队列存结果，大厂手撕版）                                       |
| [redis-distributed-lock-demo](./redis-distributed-lock-demo/)                   | Redis 分布式锁（本地模拟 + 口述/Lua 对照）                                     |


## 二、手撕 / 数据结构实现


| 文件夹                                           | 内容                               |
| --------------------------------------------- | -------------------------------- |
| [my-arraylist-demo](./my-arraylist-demo/)     | 手写简易 ArrayList（扩容 1.5 倍）         |
| [my-hashmap-demo](./my-hashmap-demo/)         | 手写简易 HashMap（数组+链表、扩容）           |
| [lru-cache-demo](./lru-cache-demo/)           | LRU：LinkedHashMap + 手写链表+HashMap |
| [concurrent-lru-demo](./concurrent-lru-demo/) | 线程安全 LRU（读写锁，大厂并发版）              |


## 三、Java 基础（口述 / 原理）


| 文件夹                                                               | 内容                                |
| ----------------------------------------------------------------- | --------------------------------- |
| [copy_demo](./copy_demo/)                                         | 引用拷贝、浅拷贝、深拷贝                      |
| [equals-hashcode-demo](./equals-hashcode-demo/)                   | equals 与 hashCode、HashSet 行为      |
| [threadlocal-demo](./threadlocal-demo/)                           | ThreadLocal 使用与注意点                |
| [reflection-demo](./reflection-demo/)                             | 反射：Class、构造、方法调用                  |
| [serialization_obj_create_demo](./serialization_obj_create_demo/) | 序列化/反序列化创建对象                      |
| [comparable-comparator-demo](./comparable-comparator-demo/)       | Comparable / Comparator 排序（集合、口述） |
| [generic-demo](./generic-demo/)                                   | 泛型类、泛型方法（口述常写）                    |
| [annotation-validation-demo](./annotation-validation-demo/)       | 自定义注解 + 运行时校验（@NotNull、@Length）   |


## 四、设计模式（创建型 / 行为型）


| 文件夹                                               | 内容               |
| ------------------------------------------------- | ---------------- |
| [observer-pattern-demo](./observer-pattern-demo/) | 观察者模式（技术栈行为型高频）  |
| [strategy-pattern-demo](./strategy-pattern-demo/) | 策略模式（技术栈行为型+OCP） |
| [factory-pattern-demo](./factory-pattern-demo/)   | 简单工厂 + 工厂方法（创建型） |
| [chain-template-demo](./chain-template-demo/)     | 责任链 + 模板方法（行为型）  |


## 五、锁与并发工具


| 文件夹                                               | 内容                 |
| ------------------------------------------------- | ------------------ |
| [lock_demo](./lock_demo/)                         | 锁的实践（可见性、可重入、实战示例） |
| [concurrent_tools_demo](./concurrent_tools_demo/) | 并发工具使用演示           |


## 六、Java 后端 / Spring 相关


| 文件夹                                                                             | 内容                                                                                          |
| ------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| [JavaSE](./JavaSE/)                                                             | **Java SE 系统学习**（Maven 项目）：基础语法、OOP、异常与 IO、泛型/反射/注解、多线程与并发、新特性、集合与框架示例；与上方按题型的手撕/口述 demo 互补 |
| [dynamic-proxy-private-field-demo](./dynamic-proxy-private-field-demo/)         | 动态代理与私有属性（AOP/事务相关）                                                                         |
| [spring-transaction-basic-demo](./spring-transaction-basic-demo/)               | Spring 事务基础                                                                                 |
| [spring-transaction-propagation-demo](./spring-transaction-propagation-demo/)   | 事务传播行为                                                                                      |
| [spring-transaction-invalidation-demo](./spring-transaction-invalidation-demo/) | 事务失效场景                                                                                      |
| [springboot-startup-demo](./springboot-startup-demo/)                           | Spring Boot 启动流程（Runner、Listener、Processor）                                                 |
| [springboot-autoconfig-demo](./springboot-autoconfig-demo/)                     | 自动配置与自定义 Starter                                                                            |
| [springmvc-vs-springboot](./springmvc-vs-springboot/)                           | Spring MVC 与 Spring Boot Web 对比                                                             |


---

## 使用建议

1. **手撕重点**：单例 DCL、LRU（链表+HashMap）、生产者-消费者、交替打印建议能闭卷写；ArrayList/HashMap 能讲清扩容与流程。
2. **每个 demo**：进入对应文件夹看 `README.md`，按其中的命令编译运行（多数为 `javac -d . *.java` 后 `java 包名.主类`；**JavaSE** 为 Maven 项目，使用 `mvn compile` / `mvn exec:java`）。
3. **与手撕文档对应**：题目与原理可配合仓库内 [手撕代码/Java手撕代码题.md](../手撕代码/Java手撕代码题.md) 与 [Java手撕知识点.md](../手撕代码/Java手撕知识点.md) 一起复习。
4. **覆盖审阅**：校招手撕与口述、技术栈对应关系见 [DEMO覆盖审阅.md](./DEMO覆盖审阅.md)。

---

## 重复与差异说明

- **单例**：仅保留 [singleton_demo](./singleton_demo/)（7 种实现 + 详细面试问答），已删除与其它处重复的 singleton-demo 文件夹。
- **线程顺序 vs 交替打印**：  
  - [thread_order_demo](./thread_order_demo/)：多线程 **顺序执行**（A 执行完→B 执行完→C→D），用 join/Latch/Barrier 等。  
  - [alternate-print-demo](./alternate-print-demo/)：两线程 **交替打印** 同一序列（如 A 打 1、B 打 2、A 打 3…）。  
  - [abc-order-print-demo](./abc-order-print-demo/)：三线程 **轮流打印** A B C A B C…。  
  三者题型不同，无重复。

