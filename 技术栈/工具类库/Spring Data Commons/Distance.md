### 1. 基本定义

`Distance` 是 Spring Data Commons 中用于表示地理距离的类，包含距离值和距离单位（度量衡），用于地理空间计算和查询。

### 2. 所属类和包路径

- **所属类**: `org.springframework.data.geo.Distance`
- **包路径**: `org.springframework.data.geo`
- **框架**: Spring Data Commons

### 3. 类定义和构造函数

```java
public class Distance {
    private final double value;    // 距离值
    private final Metric metric;   // 距离单位（度量衡）
    
    // 构造函数
    public Distance(double value)  // 默认使用米作为单位
    public Distance(double value, Metric metric)  // 指定单位
}
```


### 4. 功能作用

表示地理空间中的距离信息，用于 GEO 搜索的半径定义、距离计算结果的表示，以及距离相关的比较操作。

### 5. 核心属性

- **value**: 距离的数值部分
- **metric**: 距离的度量单位（米、公里、英里等）

### 6. 在代码中的使用

```java
// 在 queryShopByType 方法中的使用
GeoResults<RedisGeoCommands.GeoLocation<String>> results = stringRedisTemplate.opsForGeo()
        .search(
                key,
                GeoReference.fromCoordinate(x, y),
                new Distance(5000),  // 5000米的搜索半径
                RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs().includeDistance().limit(end)
        );
```


在这段代码中的作用：

- 定义 GEO 搜索的半径范围
- 设置为 5000 米（5 公里）的搜索范围
- 作为搜索参数传递给 Redis GEO 命令

### 7. 底层实现原理

```java
// Distance 类的简化实现
public class Distance {
    private final double value;
    private final Metric metric;
    
    public Distance(double value) {
        this(value, Metrics.NEUTRAL);
    }
    
    public Distance(double value, Metric metric) {
        this.value = value;
        this.metric = metric;
    }
    
    // 获取距离值
    public double getValue() {
        return value;
    }
    
    // 获取度量单位
    public Metric getMetric() {
        return metric;
    }
    
    // 转换为指定单位的距离
    public Distance in(Metric metric) {
        if (this.metric.equals(metric)) {
            return this;
        }
        return new Distance((value * this.metric.getMultiplier()) / metric.getMultiplier(), metric);
    }
    
    // 比较操作
    public boolean isEqualTo(Distance other) { /* ... */ }
    public boolean isGreaterThan(Distance other) { /* ... */ }
    public boolean isLessThan(Distance other) { /* ... */ }
}
```


### 8. 示例代码

```java
import org.springframework.data.geo.Distance;
import org.springframework.data.geo.Metrics;

// 示例：创建和使用 Distance 对象
public class DistanceExample {
    
    // 1. 创建不同单位的距离
    public void createDistances() {
        // 默认使用米作为单位
        Distance distance1 = new Distance(5000);  // 5000米
        System.out.println("距离: " + distance1.getValue() + " " + distance1.getMetric());
        
        // 指定单位为公里
        Distance distance2 = new Distance(5, Metrics.KILOMETERS);  // 5公里
        System.out.println("距离: " + distance2.getValue() + " " + distance2.getMetric());
        
        // 指定单位为英里
        Distance distance3 = new Distance(3.1, Metrics.MILES);  // 3.1英里
        System.out.println("距离: " + distance3.getValue() + " " + distance3.getMetric());
    }
    
    // 2. 单位转换
    public void convertDistance() {
        Distance kmDistance = new Distance(5, Metrics.KILOMETERS);
        
        // 转换为米
        Distance meterDistance = kmDistance.in(Metrics.NEUTRAL);
        System.out.println("5公里 = " + meterDistance.getValue() + "米");
        
        // 转换为英里
        Distance mileDistance = kmDistance.in(Metrics.MILES);
        System.out.println("5公里 = " + mileDistance.getValue() + "英里");
    }
    
    // 3. 在 GEO 搜索中使用
    public void geoSearchWithDistance() {
        // 5公里搜索半径
        Distance searchRadius = new Distance(5, Metrics.KILOMETERS);
        
        GeoResults<RedisGeoCommands.GeoLocation<String>> results = 
            stringRedisTemplate.opsForGeo().search(
                "shops",
                GeoReference.fromCoordinate(116.4074, 39.9042),
                searchRadius,  // 使用 Distance 对象
                GeoSearchCommandArgs.newGeoSearchArgs().includeDistance().limit(10)
            );
    }
}
```


### 9. 常用度量单位 (Metrics)

| 度量单位             | 说明          | _multiplier_ |
| -------------------- | ------------- | ------------ |
| `Metrics.NEUTRAL`    | 米 (默认单位) | 1            |
| `Metrics.KILOMETERS` | 公里          | 1000         |
| `Metrics.MILES`      | 英里          | 1609.344     |
| `Metrics.FEET`       | 英尺          | 0.3048       |

### 10. 在项目中的实际应用

```java
// queryShopByType 方法中使用 Distance 定义搜索半径
@Override
public Result queryShopByType(Integer typeId, Integer current, Double x, Double y) {
    // 1. 判断是否需要根据坐标查询
    if (x == null || y == null) {
        // ...不使用坐标查询的逻辑...
    }
    
    // 2. 计算分页参数
    int from = (current - 1) * SystemConstants.DEFAULT_PAGE_SIZE;
    int end = current * SystemConstants.DEFAULT_PAGE_SIZE;
    
    // 3. 查询redis、按照距离排序、分页
    String key = SHOP_GEO_KEY + typeId;
    
    // 使用 Distance 定义 5000 米的搜索半径
    GeoResults<RedisGeoCommands.GeoLocation<String>> results = stringRedisTemplate.opsForGeo()
            .search(
                    key,                                    // GEO 数据键名
                    GeoReference.fromCoordinate(x, y),      // 搜索中心点
                    new Distance(5000),                     // 5000米搜索半径
                    RedisGeoCommands.GeoSearchCommandArgs   // 搜索参数
                        .newGeoSearchArgs()
                        .includeDistance()                  // 包含距离信息
                        .limit(end)                         // 限制结果数量
            );
    
    // 4. 处理搜索结果
    if (results != null) {
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> list = results.getContent();
        
        list.stream().skip(from).forEach(result -> {
            // 获取距离信息
            Distance distance = result.getDistance();
            
            // 可以对距离进行处理或转换
            if (distance.getValue() > 1000) {
                // 转换为公里显示
                Distance kmDistance = distance.in(Metrics.KILOMETERS);
                System.out.println("距离: " + kmDistance.getValue() + " 公里");
            }
        });
    }
    
    // ...后续处理...
}
```


### 11. 注意事项

1. **默认单位**: 无参构造函数默认使用米作为单位
2. **精度控制**: 距离值为 double 类型，注意精度问题
3. **单位转换**: 可以通过 `in()` 方法进行单位转换
4. **比较操作**: 提供了丰富的距离比较方法
5. **序列化**: Distance 对象可以被序列化和反序列化

### 12. 实际意义

在您的商铺查询系统中，`Distance` 类确保了：

- 实现了标准化的地理距离表示和处理
- 支持了多种距离单位的灵活使用
- 提供了距离计算和转换的便捷方法
- 利用了 Spring Data 的地理空间数据处理能力

这是 Spring Data Commons 中地理空间数据处理的核心类之一，体现了现代 Java 开发中对地理距离计算的标准化支持。