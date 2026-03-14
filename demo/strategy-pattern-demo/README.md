# 策略模式 Demo（行为型）

算法族可互换，与使用解耦；符合开闭原则（新增策略只加实现类）。技术栈行为型+创建型均提到；支付方式、Comparator 常用。

## 文件说明

| 文件 | 说明 |
|------|------|
| `StrategyPatternDemo.java` | Context 持有 Strategy，setStrategy 注入，doSomething 调用 strategy.execute()。 |

## 考点速记

- **与状态模式区别**：策略由**外部/客户端**在运行时注入或选择；状态由**对象内部**根据当前状态切换。
- **应用**：支付方式切换、排序 Comparator、资源加载策略等。

## 运行方式

```bash
cd demo/strategy-pattern-demo
javac -d . *.java
java strategy_pattern_demo.StrategyPatternDemo
```
