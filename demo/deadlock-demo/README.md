# 死锁示例 Demo（口述/手写）

演示典型死锁：T1 先拿 A 再等 B，T2 先拿 B 再等 A。用于面试口述“死锁条件与避免”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `DeadlockDemo.java` | 两线程交叉获取 A、B，形成循环等待。 |

## 考点速记

- **四条件**：互斥、占有且等待、不可抢占、循环等待。
- **避免**：统一加锁顺序（都先 A 后 B）、tryLock(timeout)、死锁检测。
- **排查**：jstack \<pid\> 查 deadlock。

## 运行方式

```bash
cd demo/deadlock-demo
javac -d . *.java
java deadlock_demo.DeadlockDemo
```

会卡住（死锁）。用 jstack 可看到死锁报告。
