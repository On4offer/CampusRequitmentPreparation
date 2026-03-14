# ThreadLocal Demo（Java 基础/项目相关）

每线程独立变量，典型用法：用户上下文、数据库连接、请求 ID。校招常问“项目中用过吗”“原理”“为什么要 remove”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ThreadLocalDemo.java` | 两个线程各 set/get 自己的值，演示隔离性；使用后 remove 防止线程池复用时泄漏。 |

## 考点速记

- **原理**：Thread 内有 threadLocals（ThreadLocalMap），key 为 ThreadLocal，value 为副本。
- **key 弱引用**：ThreadLocal 无强引用时 key 可被 GC，避免 Thread 不回收导致 value 泄漏；但 value 仍可能泄漏，故要 remove。
- **使用场景**：请求链路传用户信息、SimpleDateFormat 等非线程安全对象的线程局部持有。

## 运行方式

```bash
cd demo/threadlocal-demo
javac -d . *.java
java threadlocal_demo.ThreadLocalDemo
```

预期：T1 打印 user-A/100，T2 打印 user-B/200。
