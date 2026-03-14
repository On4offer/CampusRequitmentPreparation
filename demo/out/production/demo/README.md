# equals 与 hashCode Demo（Java 基础/口述）

正确重写 equals 和 hashCode，并演示在 HashSet/HashMap 中的影响。校招常问“区别”与“为什么要一起重写”。

## 文件说明

| 文件 | 说明 |
|------|------|
| `Person.java` | 用 Objects.equals 与 Objects.hash 重写；main 演示 ==、equals、hashCode 及 Set 行为。 |

## 考点速记

- **==**：比较引用（地址）或基本类型值。
- **equals**：默认同 ==；重写后按业务语义比较。
- **hashCode 契约**：equals 相等则 hashCode 必相等；用于 HashMap 等，未重写会导致“相等对象”进不同桶，破坏语义。

## 运行方式

```bash
cd demo/equals-hashcode-demo
javac -d . *.java
java equals_hashcode_demo.Person
```
