### 1. 基本定义

[emptyList()](file://java\util\Collections.java#L4494-L4494) 方法是 Java 标准库中用于创建空的不可变列表的工具方法。

### 2. 所属类和包路径

- **所属类**: `java.util.Collections`
- **包路径**: `java.util`
- **Java 版本**: 自 Java 1.5 起可用

### 3. 方法签名

```java
public static final <T> List<T> emptyList()
```


### 4. 功能作用

返回一个空的、不可变的列表实例。该列表不能被修改（添加、删除、替换元素等操作都会抛出异常）。

### 5. 返回值

- 返回 `List<T>` 类型的空列表实例
- 该列表是不可变的（immutable）

### 6. 在代码中的使用

```java
Long result = stringRedisTemplate.execute(
        SECKILL_SCRIPT,
        Collections.emptyList(),  // 传递空的键列表
        voucherId.toString(), userId.toString(), String.valueOf(orderId)
);
```


在这段代码中的作用：
- 传递一个空的键列表给 Redis 脚本执行方法
- 表示该 Lua 脚本不需要使用 Redis 的键参数
- 所有需要的参数都通过 args 参数传递（voucherId、userId、orderId）

### 7. 底层实现原理

```java
// Java Collections.empty_list 的简化实现
@SuppressWarnings("unchecked")
public static final <T> List<T> emptyList() {
    return (List<T>) EMPTY_LIST;
}

// EMPTY_LIST 是一个静态不可变实例
private static class EmptyList<E> extends AbstractList<E> implements RandomAccess, Serializable {
    private static final long serialVersionUID = 8842843931221139166L;

    public Iterator<E> iterator() {
        return emptyIterator();
    }

    public ListIterator<E> listIterator() {
        return emptyListIterator();
    }

    public int size() {return 0;}

    public boolean isEmpty() {return true;}

    public boolean contains(Object obj) {return false;}

    public E get(int index) {
        throw new IndexOutOfBoundsException("Index: "+index);
    }
    
    // 所有修改操作都会抛出 UnsupportedOperationException
    public E set(int index, E element) {
        throw new UnsupportedOperationException();
    }
    
    public void add(int index, E element) {
        throw new UnsupportedOperationException();
    }
    
    public E remove(int index) {
        throw new UnsupportedOperationException();
    }
}
```


### 8. 示例代码

```java
import java.util.*;

// 基本使用
List<String> emptyList = Collections.emptyList();
System.out.println("Size: " + emptyList.size()); // 输出: Size: 0

// 类型安全的空列表
List<Integer> emptyIntList = Collections.emptyList();
List<String> emptyStringList = Collections.emptyList();

// 尝试修改会抛出异常
try {
    emptyList.add("item"); // 抛出 UnsupportedOperationException
} catch (UnsupportedOperationException e) {
    System.out.println("Cannot modify empty list");
}

// 在方法参数中的使用
public void processData(List<String> data) {
    if (data == null) {
        data = Collections.emptyList(); // 避免 null 值
    }
    // 处理数据...
}

// 作为默认返回值
public List<String> getItems() {
    // 当没有数据时返回空列表而不是 null
    return Collections.emptyList();
}
```


### 9. 相关方法

| 方法                                                         | 功能                           |
| ------------------------------------------------------------ | ------------------------------ |
| [emptyList()](file://java\util\Collections.java#L4494-L4494) | 返回空的不可变列表             |
| `emptyMap()`                                                 | 返回空的不可变映射             |
| `emptySet()`                                                 | 返回空的不可变集合             |
| `singletonList(T o)`                                         | 返回只包含一个元素的不可变列表 |
| `unmodifiableList(List<? extends T> list)`                   | 返回指定列表的不可变视图       |

### 10. 与 Java 9+ 的 List.of() 对比

```java
// Java 8 及之前
List<String> empty = Collections.emptyList();

// Java 9+
List<String> empty = List.of(); // 更简洁的语法
```


### 11. 注意事项

1. **不可变性**: 返回的列表不能被修改
2. **内存效率**: 所有调用返回同一个实例，节省内存
3. **类型安全**: 支持泛型，编译期类型检查
4. **线程安全**: 由于不可变性，是线程安全的
5. **避免 null**: 用空列表代替 null 值，避免 NullPointerException

### 12. 实际意义

在您的秒杀系统中，[emptyList()](file://java\util\Collections.java#L4494-L4494) 方法确保了：

- 提供了一个安全的空键列表参数传递给 Redis 脚本
- 避免了传递 null 值可能导致的 NullPointerException
- 节省内存，因为所有调用都返回同一个实例
- 保持了代码的简洁性和可读性

这是 Java 编程中的最佳实践之一，体现了防御性编程的思想。