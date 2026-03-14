# 三线程顺序打印 ABC Demo

三线程按顺序循环打印 A、B、C 多轮。用 **state + 三个 Condition** 精确唤醒下一个线程。

## 文件说明

| 文件 | 说明 |
|------|------|
| `PrintABC.java` | state 0→A、1→B、2→C，每线程只在自己的 state 时打印并 signal 下一个。 |

## 考点

- 多 Condition 可精确唤醒对应线程，避免“唤醒所有人再竞争”。
- 用 while 判断 state，防止虚假唤醒。

## 运行方式

```bash
cd demo/abc-order-print-demo
javac -d . *.java
java abc_order_print_demo.PrintABC
```

预期输出：ABCABCABC（3 轮）。
