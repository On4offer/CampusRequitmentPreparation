# 工厂模式 Demo（简单工厂 + 工厂方法）

技术栈创建型：简单工厂（if/switch 创建）与工厂方法（子类决定创建谁）。校招口述或写小例子常用。

## 文件说明

| 文件 | 说明 |
|------|------|
| `SimpleFactoryDemo.java` | 简单工厂：一个类 create(type) 内 if/switch 返回不同产品；新增产品要改该类。 |
| `FactoryMethodDemo.java` | 工厂方法：抽象 Factory 有 createProduct()，FactoryA/FactoryB 分别创建 ProductA/ProductB；新增产品加新工厂子类即可。 |

## 考点速记

- **简单工厂 vs 工厂方法**：简单工厂创建逻辑集中在一处，改一处；工厂方法由子类决定创建谁，符合开闭原则。
- **工厂方法**：Spring BeanFactory、JDBC DriverManager、LoggerFactory 等都是「由子类/实现决定创建哪种对象」的思路。
- **与抽象工厂区别**：抽象工厂创建的是「一族」相关产品（如 UI 主题：按钮+文本框），工厂方法只创建一种产品。

## 运行方式

```bash
cd demo/factory-pattern-demo
javac -d . *.java
java factory_pattern_demo.SimpleFactoryDemo
java factory_pattern_demo.FactoryMethodDemo
```
