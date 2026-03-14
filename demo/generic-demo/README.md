# 泛型类与泛型方法 Demo（口述常写）

技术栈《泛型、反射与注解》中的基础示例：泛型类 Box\<T\>、泛型方法。口述或白板常要求写。

## 文件说明

| 文件 | 说明 |
|------|------|
| `GenericDemo.java` | 泛型类 Box\<T\>；静态泛型方法 printArray(T[] arr)。 |

## 考点速记

- **类型擦除**：运行时泛型信息被擦除，JVM 只看原始类型。
- **泛型方法**：修饰符与返回类型之间写 \<T\>，可与类上的泛型不同；调用时可显式指定或由参数推断。

## 运行方式

```bash
cd demo/generic-demo
javac -d . *.java
java generic_demo.GenericDemo
```
