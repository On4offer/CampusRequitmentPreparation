# 反射 Demo（Java 基础/口述）

Class.forName、构造实例、调用方法。校招常问“反射是什么”“应用场景”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `ReflectionDemo.java` | 通过 Class 获取无参/有参构造并创建对象，通过 Method 调用 setName/getName。 |

## 考点速记

- **反射**：运行时获取类信息并操作类（构造、方法、字段）。
- **应用**：框架（Spring 创建 Bean）、序列化、注解处理、动态代理等。
- **getDeclaredConstructor/Method**：获取声明的构造/方法；setAccessible(true) 可访问私有。

## 运行方式

```bash
cd demo/reflection-demo
javac -d . *.java
java reflection_demo.ReflectionDemo
```
