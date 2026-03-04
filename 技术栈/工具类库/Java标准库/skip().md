### 1. 基本定义

`skip()` 是 Java 8 Stream API 中 `Stream` 接口的中间操作方法，用于跳过流中的前 N 个元素，返回一个丢弃了前 N 个元素的新流。

### 2. 所属类和包路径

- **所属接口**: `java.util.stream.Stream`
- **包路径**: `java.util.stream`
- **框架**: Java 标准库 (Java 8+)

### 3. 方法签名

```java
Stream<T> skip(long n)
```


### 4. 功能作用

跳过流中的前 n 个元素，返回一个由剩余元素组成的新流。如果流中元素少于 n 个，则返回空流。

### 5. 参数说明

- **n**: 要跳过的元素数量，必须为非负数

### 6. 返回类型

- **Stream<T>**: 跳过指定元素后的新流

### 7. 在代码中的使用

```java
// 在 queryShopByType 方法中的使用
list.stream().skip(from).forEach(result -> {
    // 处理跳过前 from 个元素后的结果
    String shopIdStr = result.getContent().getName();
    ids.add(Long.valueOf(shopIdStr));
    Distance distance = result.getDistance();
    distanceMap.put(shopIdStr, distance);
});
```


在这段代码中的作用：

- 实现分页功能，跳过前面页的数据
- 处理当前页需要的数据
- 避免重复处理已显示的数据

### 8. 底层实现原理

```java
// Stream.skip() 的概念实现
public interface Stream<T> extends BaseStream<T, Stream<T>> {
    
    // 跳过前 n 个元素
    Stream<T> skip(long n);
}

// 具体实现（简化版）
final class ReferencePipeline<T> extends AbstractPipeline<T, T, Stream<T>> {
    
    public Stream<T> skip(long n) {
        if (n < 0) {
            throw new IllegalArgumentException("Skip count must be non-negative");
        }
        if (n == 0) {
            return this;  // 不跳过任何元素，返回原流
        }
        
        // 创建新的管道阶段
        return new StatelessOp<T, T>(this, StreamShape.REFERENCE) {
            Spliterator<T> spliterator;  // 用于遍历时跳过元素
            
            @Override
            Sink<T> opWrapSink(int flags, Sink<T> sink) {
                return new Sink.ChainedReference<T, T>(sink) {
                    long remaining = n;  // 剩余需要跳过的元素数
                    
                    @Override
                    public void accept(T t) {
                        if (remaining > 0) {
                            remaining--;  // 跳过元素
                            return;
                        }
                        downstream.accept(t);  // 处理不需要跳过的元素
                    }
                };
            }
        };
    }
}
```


### 9. 示例代码

```java
import java.util.List;
import java.util.stream.Collectors;
import java.util.stream.Stream;

// 示例：使用 skip 实现分页和数据处理
public class SkipExample {
    
    // 1. 基本分页使用
    public void basicPagination() {
        List<String> data = List.of("A", "B", "C", "D", "E", "F", "G", "H", "I", "J");
        
        int pageSize = 3;
        int currentPage = 2;
        int skipCount = (currentPage - 1) * pageSize;
        
        // 跳过前面页的数据，获取当前页数据
        List<String> pageData = data.stream()
            .skip(skipCount)      // 跳过前3个元素(A,B,C)
            .limit(pageSize)      // 限制当前页大小
            .collect(Collectors.toList());
        
        System.out.println("第" + currentPage + "页数据: " + pageData); // [D, E, F]
    }
    
    // 2. 结合 GEO 搜索结果使用
    public void geoResultsPagination() {
        // 模拟 GEO 搜索结果
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> geoResults = getMockGeoResults();
        
        int currentPage = 2;
        int pageSize = 5;
        int skipCount = (currentPage - 1) * pageSize;
        
        // 分页处理 GEO 结果
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> pageResults = 
            geoResults.stream()
                .skip(skipCount)
                .limit(pageSize)
                .collect(Collectors.toList());
        
        // 处理当前页数据
        pageResults.forEach(result -> {
            String memberId = result.getContent().getName();
            Distance distance = result.getDistance();
            System.out.println("成员: " + memberId + ", 距离: " + distance.getValue());
        });
    }
    
    // 3. 条件跳过
    public void conditionalSkip() {
        List<Integer> numbers = List.of(1, 2, 3, 4, 5, 6, 7, 8, 9, 10);
        
        // 跳过所有偶数之前的元素
        List<Integer> oddAndAfter = numbers.stream()
            .skip(numbers.stream().takeWhile(n -> n % 2 == 0).count())
            .collect(Collectors.toList());
    }
    
    private List<GeoResult<RedisGeoCommands.GeoLocation<String>>> getMockGeoResults() {
        // 模拟数据
        return List.of();
    }
}
```


### 10. 相关方法

| 方法                                          | 功能            |
| --------------------------------------------- | --------------- |
| `skip(long n)`                                | 跳过前 n 个元素 |
| `limit(long maxSize)`                         | 限制流的大小    |
| `filter(Predicate<? super T> predicate)`      | 过滤元素        |
| `map(Function<? super T,? extends R> mapper)` | 转换元素        |
| `forEach(Consumer<? super T> action)`         | 遍历处理元素    |

### 11. 在项目中的实际应用

```java
// queryShopByType 方法中使用 skip 实现分页
@Override
public Result queryShopByType(Integer typeId, Integer current, Double x, Double y) {
    // ...前面的搜索操作...
    
    // 2. 计算分页参数
    int from = (current - 1) * SystemConstants.DEFAULT_PAGE_SIZE;  // 要跳过的元素数
    int end = current * SystemConstants.DEFAULT_PAGE_SIZE;
    
    // ...搜索操作...
    
    // 4. 解析结果
    List<GeoResult<RedisGeoCommands.GeoLocation<String>>> list = results.getContent();
    
    if (list.size() <= from) {
        return Result.ok(Collections.emptyList());
    }
    
    // 4.1. 截取 from ~ end 的部分
    List<Long> ids = new ArrayList<>(list.size());
    Map<String, Distance> distanceMap = new HashMap<>(list.size());
    
    // 使用 skip 跳过前面的记录，处理当前页数据
    list.stream().skip(from).forEach(result -> {  // 关键操作：跳过前面 from 个元素
        // 4.2. 获取店铺id
        String shopIdStr = result.getContent().getName();
        ids.add(Long.valueOf(shopIdStr));
        
        // 4.3. 获取距离
        Distance distance = result.getDistance();
        distanceMap.put(shopIdStr, distance);
    });
    
    // ...后续处理...
}
```


### 12. 注意事项

1. **参数验证**: n 必须为非负数，否则抛出 `IllegalArgumentException`
2. **惰性求值**: skip 是中间操作，不会立即执行
3. **并行流**: 在并行流中 skip 的行为可能更复杂
4. **性能考虑**: 跳过大量元素时可能影响性能
5. **组合使用**: 通常与 `limit()` 组合实现完整的分页功能

### 13. 实际意义

在您的商铺查询系统中，`skip()` 方法确保了：

- 实现了搜索结果的分页功能
- 支持了跳过已处理数据的高效处理
- 提供了流式 API 的灵活数据处理能力
- 体现了现代 Java 开发中函数式编程的优势

这是 Java 8 Stream API 中重要的中间操作方法，体现了现代 Java 对数据流处理的强大支持。