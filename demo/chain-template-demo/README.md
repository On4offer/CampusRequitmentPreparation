# 责任链 + 模板方法 Demo（行为型）

技术栈行为型模式：责任链（请求沿链传递）、模板方法（骨架固定、步骤子类实现）。校招口述或写小例子常用。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ChainOfResponsibilityDemo.java` | Handler 抽象类含 next 与 handle；子类 doHandle 返回 true 则终止；Request 沿链传递。 |
| `TemplateMethodDemo.java` | 抽象类 execute() 为模板方法，内部调 step1/step2/step3；step2 抽象由子类实现。 |

## 考点速记

- **责任链**：Filter、Interceptor、审批流；每个节点处理或转交 next，避免 if-else 堆叠。
- **模板方法**：JdbcTemplate 的 query/update 骨架固定，子类或回调填具体 SQL/映射；Servlet service 调 doGet/doPost。

## 运行方式

```bash
cd demo/chain-template-demo
javac -d . *.java
java chain_template_demo.ChainOfResponsibilityDemo
java chain_template_demo.TemplateMethodDemo
```
