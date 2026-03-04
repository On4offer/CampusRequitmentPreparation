# 快速开始指南

## 文件说明

### 核心演示文件

1. **SynchronizedDemo.java** - synchronized 关键字的各种用法
   - 实例方法锁
   - 静态方法锁
   - 代码块锁
   - 可重入性
   - wait/notify 使用

2. **LockDemo.java** - Lock 接口的各种用法
   - ReentrantLock（可重入锁）
   - 可中断锁（lockInterruptibly）
   - 尝试获取锁（tryLock）
   - 公平锁
   - ReadWriteLock（读写锁）
   - Condition（条件变量）
   - StampedLock（邮戳锁）

3. **LockComparison.java** - synchronized 和 Lock 的对比
   - 功能对比
   - 性能对比
   - 使用场景建议

### 原理和进阶

4. **LockPrincipleDemo.java** - 底层原理演示
   - CAS 操作原理
   - AQS 队列机制
   - 可重入性实现
   - 锁状态查询
   - 锁竞争演示
   - synchronized 锁升级

5. **LockPracticalExamples.java** - 实际应用场景
   - 线程安全的计数器
   - 生产者-消费者模式
   - 读写分离的缓存
   - 限流器
   - 银行账户转账
   - StampedLock 乐观读

6. **LockComprehensiveTest.java** - 综合测试
   - 性能测试
   - 并发安全性测试
   - 可重入性测试
   - 公平锁 vs 非公平锁
   - tryLock 超时测试
   - 死锁检测
   - ReadWriteLock 性能测试

### 文档

7. **README.md** - 详细的原理说明和使用指南

## 运行示例

### 编译所有文件

```bash
cd lock_demo
javac *.java
```

### 运行各个演示

```bash
# synchronized 演示
java lock_demo.SynchronizedDemo

# Lock 演示
java lock_demo.LockDemo

# 对比演示
java lock_demo.LockComparison

# 原理演示
java lock_demo.LockPrincipleDemo

# 实际应用示例
java lock_demo.LockPracticalExamples

# 综合测试
java lock_demo.LockComprehensiveTest
```

## 学习路径建议

### 初学者路径

1. 先看 `SynchronizedDemo.java` - 了解 synchronized 的基本用法
2. 再看 `LockDemo.java` - 了解 Lock 的基本用法
3. 阅读 `LockComparison.java` - 理解两者的区别
4. 查看 `README.md` - 学习原理

### 进阶路径

1. 运行 `LockPrincipleDemo.java` - 理解底层原理
2. 研究 `LockPracticalExamples.java` - 学习实际应用
3. 运行 `LockComprehensiveTest.java` - 进行性能测试

## 关键知识点

### synchronized
- ✅ 自动获取和释放锁
- ✅ JVM 层面实现，性能优化好
- ✅ 简单易用
- ❌ 不可中断
- ❌ 无法尝试获取锁
- ❌ 非公平锁

### Lock
- ✅ 可中断（lockInterruptibly）
- ✅ 可尝试获取（tryLock）
- ✅ 可指定公平锁
- ✅ 多个条件变量（Condition）
- ❌ 必须手动释放锁
- ❌ 代码更复杂

## 常见问题

### Q: 什么时候用 synchronized，什么时候用 Lock？

**A:** 
- 简单场景用 `synchronized`
- 需要高级特性（可中断、tryLock、公平锁、多条件）时用 `Lock`

### Q: synchronized 和 Lock 哪个性能更好？

**A:** 
- 低竞争场景：`synchronized` 可能更好（JVM 优化）
- 高竞争场景：`ReentrantLock` 可能更好
- 实际差异不大，选择依据应该是功能需求

### Q: 如何避免死锁？

**A:**
1. 避免嵌套锁
2. 统一锁的获取顺序
3. 使用超时锁（tryLock）
4. 使用死锁检测工具（jstack）

## 参考资料

详细原理请参考 `README.md` 文件。

