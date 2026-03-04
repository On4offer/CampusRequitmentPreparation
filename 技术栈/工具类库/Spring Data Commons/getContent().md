### 1. 基本定义

`getContent()` 是 Spring Data Commons 中 `GeoResults` 类的实例方法，用于获取 GEO 搜索结果中的内容列表。

### 2. 所属类和包路径

- **所属类**: `org.springframework.data.geo.GeoResults`
- **包路径**: `org.springframework.data.geo`
- **框架**: Spring Data Commons

### 3. 方法签名

```java
public List<GeoResult<T>> getContent()
```


### 4. 功能作用

获取 GEO 搜索结果中的内容列表，返回包含所有匹配地理点的 `GeoResult` 对象列表，每个对象包含位置信息和相关元数据（如距离）。

### 5. 返回类型

- **List<GeoResult<T>>**: 包含 `GeoResult` 对象的列表，每个对象代表一个匹配的地理点

### 6. 在代码中的使用

```java
// 在 queryShopByType 方法中的使用
List<GeoResult<RedisGeoCommands.GeoLocation<String>>> list = results.getContent();
```


在这段代码中的作用：

- 获取 GEO 搜索返回的所有结果项
- 提供对搜索结果的遍历和处理能力
- 支持分页和数据提取操作

### 7. 底层实现原理

```java
// GeoResults 类的概念实现
public class GeoResults<T> implements Iterable<GeoResult<T>> {
    private final List<GeoResult<T>> content;  // 结果内容列表
    private final Distance averageDistance;    // 平均距离（可选）
    
    // 构造函数
    public GeoResults(List<GeoResult<T>> content) {
        this.content = content != null ? content : new ArrayList<>();
        this.averageDistance = calculateAverageDistance();
    }
    
    // 获取内容列表
    public List<GeoResult<T>> getContent() {
        return new ArrayList<>(content);  // 返回副本以保证不可变性
    }
    
    // 获取结果数量
    public int size() {
        return content.size();
    }
    
    // 检查是否为空
    public boolean isEmpty() {
        return content.isEmpty();
    }
    
    // 实现 Iterable 接口
    @Override
    public Iterator<GeoResult<T>> iterator() {
        return content.iterator();
    }
}
```


### 8. 示例代码

```java
import org.springframework.data.geo.GeoResults;
import org.springframework.data.geo.GeoResult;

// 示例：使用 getContent 处理 GEO 搜索结果
public class GetContentExample {
    
    // 1. 基本使用
    public void basicUsage() {
        // 执行 GEO 搜索
        GeoResults<RedisGeoCommands.GeoLocation<String>> results = 
            stringRedisTemplate.opsForGeo().search(/* ... */);
        
        // 获取结果内容列表
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> content = results.getContent();
        
        System.out.println("找到 " + content.size() + " 个结果");
        
        // 遍历处理每个结果
        for (GeoResult<RedisGeoCommands.GeoLocation<String>> result : content) {
            String memberId = result.getContent().getName();
            Distance distance = result.getDistance();
            System.out.println("成员: " + memberId + ", 距离: " + distance.getValue());
        }
    }
    
    // 2. 流式处理
    public void streamProcessing() {
        GeoResults<RedisGeoCommands.GeoLocation<String>> results = 
            stringRedisTemplate.opsForGeo().search(/* ... */);
        
        // 使用 Stream API 处理结果
        List<String> memberIds = results.getContent().stream()
            .map(result -> result.getContent().getName())
            .collect(Collectors.toList());
        
        // 过滤距离小于1000米的结果
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> nearbyResults = 
            results.getContent().stream()
                .filter(result -> result.getDistance().getValue() < 1000)
                .collect(Collectors.toList());
    }
    
    // 3. 分页处理
    public void paginationProcessing() {
        GeoResults<RedisGeoCommands.GeoLocation<String>> results = 
            stringRedisTemplate.opsForGeo().search(/* ... */);
        
        int pageSize = 10;
        int currentPage = 1;
        int fromIndex = (currentPage - 1) * pageSize;
        int toIndex = Math.min(fromIndex + pageSize, results.getContent().size());
        
        // 获取当前页的结果
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> pageContent = 
            results.getContent().subList(fromIndex, toIndex);
    }
}
```


### 9. 相关方法

| 方法                                                       | 功能                     |
| ---------------------------------------------------------- | ------------------------ |
| `getContent()`                                             | 获取结果内容列表         |
| [size()](file://cn\hutool\json\JSONObject.java#L29-L29)    | 获取结果数量             |
| [isEmpty()](file://cn\hutool\json\JSONObject.java#L30-L30) | 检查结果是否为空         |
| `iterator()`                                               | 获取迭代器               |
| `getAverageDistance()`                                     | 获取平均距离（如果可用） |

### 10. 在项目中的实际应用

```java
// queryShopByType 方法中使用 getContent 处理搜索结果
@Override
public Result queryShopByType(Integer typeId, Integer current, Double x, Double y) {
    // ...前面的搜索操作...
    
    // 4. 解析出id
    if (results == null) {
        return Result.ok(Collections.emptyList());
    }
    
    // 使用 getContent 获取搜索结果列表
    List<GeoResult<RedisGeoCommands.GeoLocation<String>>> list = results.getContent();
    
    // 检查结果数量是否足够分页
    if (list.size() <= from) {
        return Result.ok(Collections.emptyList());
    }
    
    // 4.1. 截取 from ~ end 的部分
    List<Long> ids = new ArrayList<>(list.size());
    Map<String, Distance> distanceMap = new HashMap<>(list.size());
    
    // 跳过前面的记录，处理当前页数据
    list.stream().skip(from).forEach(result -> {
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


### 11. 注意事项

1. **返回副本**: 通常返回内容列表的副本以保证不可变性
2. **空值处理**: 需要检查返回结果是否为 null 或空列表
3. **泛型支持**: 支持不同的内容类型泛型参数
4. **性能考虑**: 大结果集时注意内存使用
5. **线程安全**: 通常保证线程安全性

### 12. 实际意义

在您的商铺查询系统中，`getContent()` 方法确保了：

- 提供了对 GEO 搜索结果的统一访问接口
- 支持了结果的遍历、过滤和分页处理
- 实现了搜索结果与业务逻辑的解耦
- 体现了 Spring Data 对查询结果封装的一致性设计

这是 Spring Data Commons 中地理空间查询结果处理的核心方法，体现了现代 Java 框架对数据访问结果标准化封装的设计理念。