# 两线程交替打印 Demo（1~100 或 ABAB）

校招常考：两线程交替打印数字或字母，使用 **Lock + Condition** 或 **synchronized + wait/notify**。

## 文件说明

| 文件 | 说明 |
|------|------|
| `AlternatePrint.java` | Lock + Condition，奇偶控制 A/B 谁打印。 |

## 考点

- 用 **while** 判断“是否轮到我”，防止虚假唤醒。
- 用共享变量（count 或 state）控制顺序，执行完更新并 signal 对方。

## 运行方式

```bash
cd demo/alternate-print-demo
javac -d . *.java
java alternate_print_demo.AlternatePrint
```

预期输出 A:1, B:2, A:3, B:4, ... 到 10。
