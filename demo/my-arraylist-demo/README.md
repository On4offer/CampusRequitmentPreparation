# 手写简易 ArrayList Demo

实现 add/get/remove、扩容逻辑。校招口述“ArrayList 扩容机制”或手写核心方法。

## 文件说明

| 文件 | 说明 |
|------|------|
| `MyArrayList.java` | 默认容量 10，扩容 1.5 倍（oldCapacity + oldCapacity>>1），Arrays.copyOf。 |

## 考点速记

- **扩容**：newCapacity = oldCapacity + (oldCapacity >> 1)，即 1.5 倍。
- **删除**：System.arraycopy 前移，最后一位置 null。

## 运行方式

```bash
cd demo/my-arraylist-demo
javac -d . *.java
java my_arraylist_demo.MyArrayList
```
