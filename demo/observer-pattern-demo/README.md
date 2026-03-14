# 观察者模式 Demo（行为型）

主题（Subject）维护观察者列表，状态变化时通知所有观察者。技术栈行为型模式高频；Spring 事件、前端响应式的基础。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ObserverPatternDemo.java` | Subject 提供 attach/detach/notify；Observer 提供 update；setState 时触发 notify。 |

## 考点速记

- **与发布/订阅区别**：观察者中主题**直接持有**观察者并调用；发布/订阅通过事件总线或 MQ 解耦，发布者与订阅者互不知。
- **注意**：notify 时遍历列表不要同时增删，可拷贝再遍历或使用 CopyOnWriteArrayList。

## 运行方式

```bash
cd demo/observer-pattern-demo
javac -d . *.java
java observer_pattern_demo.ObserverPatternDemo
```

预期：A、B 各打印两次（hello、world）。
