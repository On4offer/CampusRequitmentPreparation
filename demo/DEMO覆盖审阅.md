# Demo 覆盖审阅：校招手撕与口述代码

> 对照 **技术栈文档**、**手撕代码题/知识点**、**面试试卷/模拟面试** 整理，便于查漏补缺。算法题（LeetCode）单独刷，不在此列。

---

## 一、手撕代码题（Java手撕代码题.md）覆盖情况

| 题目 | 对应 demo | 状态 |
|------|-----------|------|
| 单例（DCL/饿汉/静态内部类/枚举等） | singleton_demo | ✅ 已覆盖（7 种） |
| 生产者-消费者（BlockingQueue） | producer-consumer-blockingqueue-demo | ✅ 已覆盖 |
| 生产者-消费者（wait/notify） | producer-consumer-wait-notify-demo | ✅ 已覆盖 |
| LRU（LinkedHashMap + 手写链表+HashMap） | lru-cache-demo | ✅ 已覆盖 |
| 两线程交替打印 | alternate-print-demo | ✅ 已覆盖 |
| 三线程顺序打印 ABC | abc-order-print-demo | ✅ 已覆盖 |
| 手写 ArrayList | my-arraylist-demo | ✅ 已覆盖 |
| 手写 HashMap | my-hashmap-demo | ✅ 已覆盖 |
| 死锁示例 | deadlock-demo | ✅ 已覆盖 |
| 手写简单线程池 | simple-thread-pool-demo | ✅ 已覆盖 |
| 限流器（令牌桶/滑动窗口） | rate-limiter-demo | ✅ 已覆盖 |
| 带过期缓存 | expire-cache-demo | ✅ 已覆盖 |
| 公平锁 vs 非公平锁 | fair-lock-demo | ✅ 已覆盖 |
| **Callable + Future 取结果** | callable-future-demo | ✅ 已覆盖 |
| **手写简易 Future（阻塞队列存结果）** | simple-future-demo | ✅ 已覆盖 |
| 深拷贝 | copy_demo | ✅ 已覆盖 |
| **线程安全 LRU** | concurrent-lru-demo | ✅ 已覆盖 |
| **Redis 分布式锁（口述/伪代码）** | redis-distributed-lock-demo | ✅ 已覆盖（本地模拟 + Lua 说明） |

---

## 二、口述/原理类（Java手撕知识点 + 技术栈）覆盖情况

| 考点 | 对应 demo | 状态 |
|------|-----------|------|
| volatile、DCL、虚假唤醒、Condition | 单例 / 生产者-消费者 / 交替打印 | ✅ 已覆盖 |
| equals 与 hashCode、HashSet 行为 | equals-hashcode-demo | ✅ 已覆盖 |
| ThreadLocal 使用与 remove | threadlocal-demo | ✅ 已覆盖 |
| 反射 Class/构造/方法 | reflection-demo | ✅ 已覆盖 |
| 序列化创建对象 | serialization_obj_create_demo | ✅ 已覆盖 |
| 引用/浅拷贝/深拷贝 | copy_demo | ✅ 已覆盖 |
| **Comparable / Comparator 排序** | comparable-comparator-demo | ✅ 已补充 |
| **泛型类、泛型方法**（口述常写 Box\<T\>） | generic-demo | ✅ 已覆盖 |
| **自定义注解 + 运行时校验** | annotation-validation-demo | ✅ 已覆盖 |

---

## 三、技术栈「设计模式」与代码演示

| 技术栈文档 | 对应 demo | 状态 |
|------------|-----------|------|
| 创建型：单例、工厂方法 | singleton_demo、factory-pattern-demo | ✅ 已覆盖 |
| 结构型：代理（JDK/CGLib） | dynamic-proxy-private-field-demo | ✅ 已覆盖（偏 AOP/事务场景） |
| **行为型：观察者模式** | observer-pattern-demo | ✅ 已覆盖 |
| **行为型：策略模式** | strategy-pattern-demo | ✅ 已覆盖 |
| **创建型：简单工厂、工厂方法** | factory-pattern-demo | ✅ 已覆盖 |
| **行为型：责任链、模板方法** | chain-template-demo | ✅ 已覆盖 |

---

## 四、多线程与并发（技术栈 + 面试）

| 考点 | 对应 demo | 状态 |
|------|-----------|------|
| 线程顺序执行（join/Latch/Barrier/Semaphore/waitNotify） | thread_order_demo | ✅ 已覆盖 |
| 交替/轮流打印 | alternate-print-demo、abc-order-print-demo | ✅ 已覆盖 |
| 锁、可见性、可重入 | lock_demo | ✅ 已覆盖 |
| 并发工具使用 | concurrent_tools_demo | ✅ 已覆盖 |
| 线程池 7 参数与拒绝策略（口述） | simple-thread-pool-demo README 已补充 | ✅ 已覆盖 |

---

## 五、Java 后端 / Spring（技术栈 + 项目）

| 考点 | 对应 demo | 状态 |
|------|-----------|------|
| Java SE 系统学习（语法/OOP/异常与IO/泛型反射注解/并发/新特性/集合） | JavaSE（Maven 项目） | ✅ 已覆盖，与按题型手撕 demo 互补 |
| Spring 事务基础/传播/失效 | spring-transaction-*-demo | ✅ 已覆盖 |
| Spring Boot 启动、自动配置 | springboot-startup-demo、springboot-autoconfig-demo | ✅ 已覆盖 |
| Spring MVC vs Boot | springmvc-vs-springboot | ✅ 已覆盖 |
| AOP/动态代理与私有属性 | dynamic-proxy-private-field-demo | ✅ 已覆盖 |

---

## 六、未做独立 demo 的考点（建议口述 + 文档）

| 考点 | 说明 |
|------|------|
| 看门狗续期（Redisson） | redis-distributed-lock-demo README 已简述；完整实现依赖 Redisson 或自研定时续期。 |
| 其他行为型（状态、命令、迭代器等） | 技术栈笔记有；校招以观察者、策略、责任链、模板方法为主，其余口述意图即可。 |

---

## 七、小结

- **手撕题清单**：单例、LRU、生产者-消费者、交替/顺序打印、ArrayList/HashMap、死锁、线程池、限流、过期缓存、公平锁、**Callable+Future**、**手写 Future（阻塞队列）**、**线程安全 LRU**、**Redis 分布式锁**、深拷贝等均有对应 demo。
- **技术栈文档**：泛型、Comparable/Comparator、观察者、策略、**工厂**、**责任链/模板方法**、**自定义注解校验** 均已通过独立 demo 或 README 覆盖。
- **面试试卷/模拟面试**：线程安全阻塞队列、LRU（含并发版）、单例 DCL、生产者-消费者、深拷贝、线程池参数与拒绝策略、**自定义注解处理器**、**Redis 分布式锁** 均有对应 demo 或文档。

**维护建议**：新增校招遇到的手撕/口述题时，可先在本表「未做独立 demo」中登记，再决定是否新开 demo 或只更新手撕文档/八股。

---

## 文档与文件夹命名检查（简要）

- **文档**：本审阅表与 [demo/README.md](./README.md) 已与当前所有 demo 对齐（含 **JavaSE**）；[手撕代码/README.md](../手撕代码/README.md) 已增加对 demo 目录的引用。无需整体重写。
- **文件夹命名**：当前存在两种风格——**下划线**（如 `singleton_demo`、`copy_demo`）与 **连字符**（如 `lru-cache-demo`、`simple-future-demo`）。Java 包名一律为下划线。为减少批量重命名带来的链接与脚本影响，**建议保持现状**，已在 demo/README.md 中增加「命名说明」；新増 demo 若希望与包名完全一致，可采用**下划线**文件夹名。
