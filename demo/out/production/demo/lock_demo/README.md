# synchronized 和 Lock 详解

本目录包含 `synchronized` 关键字和 `Lock` 接口的完整演示，包括常用用法、对比分析和底层原理。

## 目录结构

```
lock_demo/
├── README.md                    # 本文档：原理和说明
├── SynchronizedDemo.java        # synchronized 各种用法演示
├── LockDemo.java                # Lock 接口各种用法演示
├── LockComparison.java          # synchronized 和 Lock 对比
├── LockPrincipleDemo.java       # 底层原理演示
├── LockPracticalExamples.java   # 实际应用场景示例
└── LockComprehensiveTest.java   # 综合测试
```

## 一、synchronized 原理

### 1.1 基本概念

`synchronized` 是 Java 内置的同步机制，基于 **JVM 的监视器锁（Monitor Lock）** 实现。

### 1.2 实现原理

#### JVM 层面的实现

`synchronized` 在 JVM 中的实现依赖于对象头中的 **Mark Word**：

```
对象头结构（64位JVM）：
┌─────────────────────────────────────────────────────────┐
│ Mark Word (64 bits)                                     │
├─────────────────────────────────────────────────────────┤
│ 锁状态   │ 25 bits      │ 31 bits      │ 1 bit │ 4 bits │
├──────────┼──────────────┼──────────────┼───────┼────────┤
│ 无锁     │ unused       │ hashcode     │ 0     │ 01     │
│ 偏向锁   │ threadId     │ epoch        │ 1     │ 01     │
│ 轻量级锁 │ ptr_to_lock  │              │       │ 00     │
│ 重量级锁 │ ptr_to_monitor│             │       │ 10     │
│ GC标记   │              │              │       │ 11     │
└─────────────────────────────────────────────────────────┘
```

#### 锁升级过程

1. **无锁状态**：对象刚创建时
2. **偏向锁**：第一个线程访问时，将线程ID写入 Mark Word
   - 优点：同一线程再次访问时无需加锁，性能最优
   - 适用：单线程访问场景
3. **轻量级锁（自旋锁）**：多线程竞争时，通过 CAS 操作获取锁
   - 优点：避免线程阻塞，减少系统调用开销
   - 适用：锁竞争不激烈，线程持有锁时间短
4. **重量级锁（互斥锁）**：竞争激烈时，线程进入阻塞状态
   - 实现：通过操作系统的 Mutex 实现
   - 适用：锁竞争激烈，线程持有锁时间长

#### 字节码层面

`synchronized` 在字节码中通过以下指令实现：

- `monitorenter`：进入监视器（获取锁）
- `monitorexit`：退出监视器（释放锁）

```java
// 源代码
synchronized (obj) {
    // 代码块
}

// 字节码（简化）
monitorenter
try {
    // 代码块
} finally {
    monitorexit
}
```

### 1.3 可重入性

`synchronized` 是可重入锁，同一线程可以多次获取同一个锁：

```java
public synchronized void method1() {
    method2(); // 可以调用，不会死锁
}

public synchronized void method2() {
    // 同一线程已经持有锁，可以直接进入
}
```

**实现原理**：JVM 在对象头中记录锁的持有线程和重入次数。

## 二、Lock 接口原理

### 2.1 基本概念

`Lock` 是 Java 5 引入的显式锁接口，提供了比 `synchronized` 更灵活的锁机制。

### 2.2 核心实现类

#### ReentrantLock（可重入锁）

**实现原理**：
- 基于 **AQS（AbstractQueuedSynchronizer）** 实现
- 使用 **CAS（Compare-And-Swap）** 操作保证原子性
- 维护一个 **CLH 队列**（虚拟的双向链表）来管理等待线程

**AQS 核心组件**：
```
┌─────────────────────────────────────┐
│ AbstractQueuedSynchronizer (AQS)   │
├─────────────────────────────────────┤
│ state: volatile int                 │ ← 锁状态（0=未锁定，1=已锁定）
│ head: Node                          │ ← 队列头节点
│ tail: Node                          │ ← 队列尾节点
└─────────────────────────────────────┘
```

**CLH 队列结构**：
```
head → [Node1] → [Node2] → [Node3] → tail
        ↑          ↑          ↑
      Thread1   Thread2   Thread3
```

**加锁流程**：
1. 尝试通过 CAS 将 state 从 0 改为 1
2. 成功：获取锁，设置当前线程为持有者
3. 失败：将当前线程封装成 Node 加入 CLH 队列，并阻塞

**解锁流程**：
1. 将 state 从 1 改为 0
2. 唤醒队列中下一个等待的线程

#### ReadWriteLock（读写锁）

**实现原理**：
- 内部维护两个锁：读锁（共享锁）和写锁（独占锁）
- 读锁：多个线程可以同时持有
- 写锁：独占，与其他读锁和写锁互斥

**状态管理**：
- 使用 AQS 的 state 字段：
  - 高 16 位：读锁持有数量
  - 低 16 位：写锁持有数量

#### StampedLock（邮戳锁）

**实现原理**：
- 提供三种模式：写锁、悲观读锁、乐观读
- 乐观读：不阻塞，通过版本号（stamp）验证数据一致性
- 性能优于 ReadWriteLock

### 2.3 CAS 原理

**CAS（Compare-And-Swap）** 是 Lock 实现的基础：

```java
// CAS 操作伪代码
boolean compareAndSet(int expect, int update) {
    if (value == expect) {
        value = update;
        return true;
    }
    return false;
}
```

**底层实现**：
- 在 x86 架构上，通过 `LOCK CMPXCHG` 指令实现
- 保证操作的原子性

## 三、synchronized vs Lock 对比

### 3.1 功能对比

| 特性 | synchronized | Lock |
|------|-------------|------|
| **锁的获取** | 自动获取和释放 | 手动获取和释放 |
| **可中断性** | 不可中断 | 可中断（lockInterruptibly） |
| **尝试获取** | 不支持 | 支持（tryLock） |
| **公平锁** | 非公平（无法指定） | 可指定公平/非公平 |
| **条件变量** | 单一条件（wait/notify） | 多个条件（Condition） |
| **锁的范围** | 方法或代码块 | 更灵活的控制 |

### 3.2 性能对比

**低竞争场景**：
- `synchronized` 性能更好（JVM 优化，偏向锁、轻量级锁）

**高竞争场景**：
- `ReentrantLock` 可能性能更好（可配置公平锁、更细粒度控制）

**实际测试**：
- 在大多数场景下，两者性能差异不大
- 选择依据应该是功能需求，而非性能

### 3.3 使用场景

#### 优先使用 synchronized：
- ✅ 简单的同步需求
- ✅ 不需要高级特性
- ✅ 代码简洁性优先
- ✅ 自动释放锁，避免忘记释放

#### 优先使用 Lock：
- ✅ 需要可中断的锁
- ✅ 需要尝试获取锁（tryLock）
- ✅ 需要公平锁
- ✅ 需要多个条件变量
- ✅ 需要更细粒度的控制
- ✅ 需要读写锁（ReadWriteLock）

## 四、常见问题

### 4.1 死锁问题

**死锁产生的四个必要条件**：
1. 互斥条件
2. 请求与保持条件
3. 不剥夺条件
4. 循环等待条件

**预防死锁**：
- 避免嵌套锁
- 使用超时锁（tryLock）
- 统一锁的获取顺序

### 4.2 锁优化建议

1. **减小锁的粒度**：只锁必要的代码块
2. **减少锁的持有时间**：尽快释放锁
3. **读写分离**：使用 ReadWriteLock
4. **无锁编程**：使用 CAS 或原子类
5. **避免锁嵌套**：防止死锁

## 五、参考资料

- [Java 并发编程实战](https://book.douban.com/subject/10484692/)
- [深入理解 Java 虚拟机](https://book.douban.com/subject/34907497/)
- [Java 并发编程的艺术](https://book.douban.com/subject/26591326/)

## 六、运行示例

```bash
# 编译所有文件
javac lock_demo/*.java

# 运行 synchronized 演示
java lock_demo.SynchronizedDemo

# 运行 Lock 演示
java lock_demo.LockDemo

# 运行对比测试
java lock_demo.LockComparison
```

