### 1. 基本定义

`includeDistance()` 是 Spring Data Redis 中 `RedisGeoCommands.GeoSearchCommandArgs` 类的实例方法，用于配置 GEO 搜索命令返回结果中包含距离信息。

### 2. 所属类和包路径

- **所属类**: `org.springframework.data.redis.connection.RedisGeoCommands.GeoSearchCommandArgs`
- **包路径**: `org.springframework.data.redis.connection`
- **框架**: Spring Data Redis

### 3. 方法签名

```java
public GeoSearchCommandArgs includeDistance()
```


### 4. 功能作用

配置 Redis GEO 搜索命令在返回结果中包含从搜索中心点到每个匹配成员的距离信息，使得可以在应用层获取和使用这些距离数据。

### 5. 返回类型

- **GeoSearchCommandArgs**: 返回当前配置对象本身，支持链式调用

### 6. 在代码中的使用

```java
// 在 queryShopByType 方法中的使用
GeoResults<RedisGeoCommands.GeoLocation<String>> results = stringRedisTemplate.opsForGeo()
        .search(
                key,
                GeoReference.fromCoordinate(x, y),
                new Distance(5000),
                RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs()
                    .includeDistance()   // 配置包含距离信息
                    .limit(end)
        );
```


在这段代码中的作用：

- 配置 GEO 搜索返回距离信息
- 使得后续可以获取每个商铺到用户位置的距离
- 支持距离显示和基于距离的业务逻辑处理

### 7. 底层实现原理

```java
// includeDistance 的概念实现
public class GeoSearchCommandArgs {
    private boolean withDistance = false;  // 距离信息标志
    private boolean withCoordinates = false;
    private boolean ascending = true;
    private int count = -1;
    
    // 配置包含距离信息
    public GeoSearchCommandArgs includeDistance() {
        this.withDistance = true;  // 设置标志位
        return this;  // 返回当前对象支持链式调用
    }
    
    // 转换为 Redis 命令参数
    public List<String> toArgs() {
        List<String> args = new ArrayList<>();
        
        if (withDistance) {
            args.add("WITHDIST");  // 添加 Redis 命令参数
        }
        if (withCoordinates) {
            args.add("WITHCOORD");
        }
        if (ascending) {
            args.add("ASC");
        } else {
            args.add("DESC");
        }
        if (count > 0) {
            args.add("COUNT");
            args.add(String.valueOf(count));
        }
        
        return args;
    }
    
    // 检查是否配置了距离信息
    public boolean isWithDistance() {
        return withDistance;
    }
}
```


### 8. 示例代码

```java
import org.springframework.data.redis.connection.RedisGeoCommands;

// 示例：使用 includeDistance 配置距离信息
public class IncludeDistanceExample {
    
    // 1. 基本使用
    public void basicUsage() {
        RedisGeoCommands.GeoSearchCommandArgs args = 
            RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs()
                .includeDistance();  // 配置包含距离信息
        
        // 执行搜索
        GeoResults<RedisGeoCommands.GeoLocation<String>> results = 
            stringRedisTemplate.opsForGeo().search(
                "shops",
                GeoReference.fromCoordinate(116.4074, 39.9042),
                new Distance(5000),
                args
            );
        
        // 处理结果时可以获取距离信息
        for (GeoResult<RedisGeoCommands.GeoLocation<String>> result : results) {
            Distance distance = result.getDistance();  // 获取距离
            System.out.println("距离: " + distance.getValue() + " 米");
        }
    }
    
    // 2. 链式调用
    public void chainedUsage() {
        RedisGeoCommands.GeoSearchCommandArgs args = 
            RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs()
                .includeDistance()      // 包含距离
                .includeCoordinates()   // 包含坐标
                .sortAscending()        // 升序排序
                .limit(10);             // 限制10个结果
    }
    
    // 3. 条件配置
    public void conditionalUsage() {
        boolean needDistance = true;
        
        RedisGeoCommands.GeoSearchCommandArgs args = 
            RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs();
        
        if (needDistance) {
            args.includeDistance();  // 根据条件配置距离信息
        }
    }
}
```


### 9. 相关方法

| 方法                   | 功能                   |
| ---------------------- | ---------------------- |
| `includeDistance()`    | 配置包含距离信息       |
| `includeCoordinates()` | 配置包含坐标信息       |
| `sortAscending()`      | 配置按距离升序排序     |
| `sortDescending()`     | 配置按距离降序排序     |
| `limit(int count)`     | 配置返回结果数量限制   |
| `isWithDistance()`     | 检查是否配置了距离信息 |

### 10. 在项目中的实际应用

```java
// queryShopByType 方法中使用 includeDistance 配置距离信息
@Override
public Result queryShopByType(Integer typeId, Integer current, Double x, Double y) {
    // ...前面的参数检查和计算...
    
    // 3. 查询redis、按照距离排序、分页
    String key = SHOP_GEO_KEY + typeId;
    
    // 配置搜索参数，包含距离信息
    GeoResults<RedisGeoCommands.GeoLocation<String>> results = stringRedisTemplate.opsForGeo()
            .search(
                    key,
                    GeoReference.fromCoordinate(x, y),
                    new Distance(5000),
                    RedisGeoCommands.GeoSearchCommandArgs
                        .newGeoSearchArgs()
                        .includeDistance()  // 关键配置：包含距离信息
                        .limit(end)
            );
    
    // 4. 处理搜索结果
    if (results != null) {
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> list = results.getContent();
        
        // 创建存储距离映射的 HashMap
        Map<String, Distance> distanceMap = new HashMap<>(list.size());
        
        list.stream().skip(from).forEach(result -> {
            String shopIdStr = result.getContent().getName();
            
            // 由于配置了 includeDistance()，这里可以安全获取距离信息
            Distance distance = result.getDistance();
            distanceMap.put(shopIdStr, distance);  // 存储距离映射
            
            System.out.println("商铺 " + shopIdStr + " 距离: " + distance.getValue() + " 米");
        });
        
        // 5. 根据id查询Shop
        String idStr = StrUtil.join(",", ids);
        List<Shop> shops = query().in("id", ids).last("ORDER BY FIELD(id," + idStr + ")").list();
        
        // 为每个商铺设置距离信息
        for (Shop shop : shops) {
            // 从距离映射中获取对应商铺的距离
            Distance storedDistance = distanceMap.get(shop.getId().toString());
            if (storedDistance != null) {
                shop.setDistance(storedDistance.getValue());  // 设置到商铺对象中
            }
        }
    }
    
    // ...后续处理...
}
```


### 11. 注意事项

1. **链式调用**: 返回当前对象，支持与其他配置方法链式调用
2. **Redis 命令映射**: 对应 Redis 的 `WITHDIST` 参数
3. **性能影响**: 包含距离信息会略微增加网络传输和处理开销
4. **结果访问**: 只有配置了此选项，才能从 `GeoResult` 中获取距离信息
5. **默认行为**: 默认不包含距离信息，需要显式配置

### 12. 实际意义

在您的商铺查询系统中，`includeDistance()` 方法确保了：

- 实现了距离信息的返回和使用
- 支持了商铺距离显示功能
- 提供了基于距离的业务逻辑处理能力
- 体现了配置化设计思想，按需获取所需信息

这是 Spring Data Redis GEO 功能中重要的配置方法，体现了现代 Java 框架对功能模块化和按需配置的设计理念。