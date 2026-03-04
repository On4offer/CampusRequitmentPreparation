### 1. 基本定义

`newGeoSearchArgs()` 是 Spring Data Redis 中 `RedisGeoCommands.GeoSearchCommandArgs` 类的静态工厂方法，用于创建 GEO 搜索命令参数配置对象。

### 2. 所属类和包路径

- **所属类**: `org.springframework.data.redis.connection.RedisGeoCommands.GeoSearchCommandArgs`
- **包路径**: `org.springframework.data.redis.connection`
- **框架**: Spring Data Redis

### 3. 方法签名

```java
public static GeoSearchCommandArgs newGeoSearchArgs()
```


### 4. 功能作用

创建一个新的 `GeoSearchCommandArgs` 对象实例，用于配置 Redis GEO 搜索命令的各种参数选项，如是否包含距离、坐标、排序方式、结果数量限制等。

### 5. 返回类型

- **GeoSearchCommandArgs**: GEO 搜索命令参数配置对象

### 6. 在代码中的使用

```java
// 在 queryShopByType 方法中的使用
GeoResults<RedisGeoCommands.GeoLocation<String>> results = stringRedisTemplate.opsForGeo()
        .search(
                key,
                GeoReference.fromCoordinate(x, y),
                new Distance(5000),
                RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs()  // 创建参数配置对象
                    .includeDistance()   // 配置：包含距离信息
                    .limit(end)         // 配置：限制结果数量
        );
```


在这段代码中的作用：

- 创建 GEO 搜索参数配置对象
- 通过链式调用配置搜索选项
- 为 GEO 搜索提供灵活的参数设置

### 7. 底层实现原理

```java
// newGeoSearchArgs 的概念实现
public static GeoSearchCommandArgs newGeoSearchArgs() {
    // 1. 创建新的 GeoSearchCommandArgs 实例
    return new GeoSearchCommandArgs();
}

// GeoSearchCommandArgs 类的简化实现
public class GeoSearchCommandArgs {
    private boolean withDistance = false;
    private boolean withCoordinates = false;
    private boolean ascending = true;
    private int count = -1;
    
    // 私有构造函数
    private GeoSearchCommandArgs() {
        // 初始化默认值
    }
    
    // 链式配置方法
    public GeoSearchCommandArgs includeDistance() {
        this.withDistance = true;
        return this;  // 返回当前对象以支持链式调用
    }
    
    public GeoSearchCommandArgs includeCoordinates() {
        this.withCoordinates = true;
        return this;
    }
    
    public GeoSearchCommandArgs sortAscending() {
        this.ascending = true;
        return this;
    }
    
    public GeoSearchCommandArgs limit(int count) {
        this.count = count;
        return this;
    }
    
    // 转换为 Redis 命令参数
    public List<String> toArgs() {
        List<String> args = new ArrayList<>();
        if (withDistance) args.add("WITHDIST");
        if (withCoordinates) args.add("WITHCOORD");
        if (ascending) args.add("ASC"); else args.add("DESC");
        if (count > 0) {
            args.add("COUNT");
            args.add(String.valueOf(count));
        }
        return args;
    }
}
```


### 8. 示例代码

```java
import org.springframework.data.redis.connection.RedisGeoCommands;

// 示例：使用 newGeoSearchArgs 创建和配置搜索参数
public class NewGeoSearchArgsExample {
    
    // 1. 基本使用
    public void basicUsage() {
        // 使用静态工厂方法创建参数对象
        RedisGeoCommands.GeoSearchCommandArgs args = 
            RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs();
        
        System.out.println("参数对象创建成功");
    }
    
    // 2. 链式配置
    public void chainedConfiguration() {
        // 创建并链式配置参数
        RedisGeoCommands.GeoSearchCommandArgs args = 
            RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs()
                .includeDistance()      // 包含距离信息
                .includeCoordinates()   // 包含坐标信息
                .sortAscending()        // 按距离升序排序
                .limit(10);             // 限制返回10个结果
        
        // 使用配置好的参数进行搜索
        GeoResults<RedisGeoCommands.GeoLocation<String>> results = 
            stringRedisTemplate.opsForGeo().search(
                "shops",
                GeoReference.fromCoordinate(116.4074, 39.9042),
                new Distance(5000),
                args
            );
    }
    
    // 3. 不同配置组合
    public void differentConfigurations() {
        // 只包含距离信息
        RedisGeoCommands.GeoSearchCommandArgs args1 = 
            RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs()
                .includeDistance()
                .limit(5);
        
        // 包含距离和坐标信息，降序排序
        RedisGeoCommands.GeoSearchCommandArgs args2 = 
            RedisGeoCommands.GeoSearchCommandArgs.newGeoSearchArgs()
                .includeDistance()
                .includeCoordinates()
                .sortDescending()
                .limit(20);
    }
}
```


### 9. 相关方法

| 方法                   | 功能                                 |
| ---------------------- | ------------------------------------ |
| `newGeoSearchArgs()`   | 创建新的参数配置对象（静态工厂方法） |
| `includeDistance()`    | 配置包含距离信息                     |
| `includeCoordinates()` | 配置包含坐标信息                     |
| `sortAscending()`      | 配置按距离升序排序                   |
| `sortDescending()`     | 配置按距离降序排序                   |
| `limit(int count)`     | 配置返回结果数量限制                 |

### 10. 在项目中的实际应用

```java
// queryShopByType 方法中使用 newGeoSearchArgs 创建搜索参数
@Override
public Result queryShopByType(Integer typeId, Integer current, Double x, Double y) {
    // ...前面的参数检查和计算...
    
    // 2. 计算分页参数
    int from = (current - 1) * SystemConstants.DEFAULT_PAGE_SIZE;
    int end = current * SystemConstants.DEFAULT_PAGE_SIZE;
    
    // 3. 查询redis、按照距离排序、分页
    String key = SHOP_GEO_KEY + typeId;
    
    // 使用 newGeoSearchArgs 创建并配置搜索参数
    GeoResults<RedisGeoCommands.GeoLocation<String>> results = stringRedisTemplate.opsForGeo()
            .search(
                    key,                                    // GEO 数据键名
                    GeoReference.fromCoordinate(x, y),      // 搜索中心点
                    new Distance(5000),                     // 5000米搜索半径
                    RedisGeoCommands.GeoSearchCommandArgs   // 参数配置
                        .newGeoSearchArgs()                 // 静态工厂方法创建对象
                        .includeDistance()                  // 配置：包含距离信息
                        .limit(end)                         // 配置：限制结果数量
            );
    
    // 4. 处理搜索结果
    if (results != null) {
        List<GeoResult<RedisGeoCommands.GeoLocation<String>>> list = results.getContent();
        
        list.stream().skip(from).forEach(result -> {
            // 由于配置了 includeDistance()，可以获取距离信息
            Distance distance = result.getDistance();
            String shopIdStr = result.getContent().getName();
            distanceMap.put(shopIdStr, distance);
        });
    }
    
    // ...后续处理...
}
```


### 11. 注意事项

1. **静态工厂方法**: 使用静态方法创建对象，而非直接使用构造函数
2. **链式调用**: 支持链式调用多个配置方法
3. **默认值**: 创建的对象包含合理的默认配置
4. **不可变性**: 配置完成后对象状态相对稳定
5. **内存效率**: 避免重复创建相同配置的对象

### 12. 实际意义

在您的商铺查询系统中，`newGeoSearchArgs()` 方法确保了：

- 提供了创建 GEO 搜索参数对象的标准方式
- 支持了灵活的参数配置和链式调用模式
- 实现了参数对象的复用和内存优化
- 体现了现代 Java 开发中的工厂模式和建造者模式思想

这是 Spring Data Redis 中 GEO 功能参数配置的核心入口方法，体现了现代 Java 框架对 API 易用性和配置灵活性的设计理念。