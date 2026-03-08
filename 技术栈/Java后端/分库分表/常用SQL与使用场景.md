# 📋 分库分表 常用SQL与使用场景

> 本文档是《学习笔记.md》的配套速查手册，提供日常开发中常用的 SQL、配置和代码片段。

------

## 🎯 使用场景索引

| 场景 | 关键词 | 章节 |
|------|--------|------|
| **分片键选择** | user_id、order_id、取模、范围 | 1️⃣ 分片键选择 |
| **主键生成** | 雪花算法、UUID、号段模式 | 2️⃣ 主键生成 |
| **跨分片查询** | 广播查询、冗余字段、ES | 3️⃣ 跨分片查询 |
| **分布式事务** | TCC、本地消息表、Saga | 4️⃣ 分布式事务 |
| **数据迁移** | 双写、增量同步、扩容 | 5️⃣ 数据迁移 |
| **ShardingSphere 配置** | 分库分表、读写分离、Seata | 6️⃣ ShardingSphere |
| **MyCAT 配置** | schema.xml、rule.xml、server.xml | 7️⃣ MyCAT |

------

## 1️⃣ 分片键选择

### （1）取模分片

```java
// 简单取模
public int getDbIndex(Long userId) {
    return (int) (userId % 4); // 0-3
}

public int getTableIndex(Long orderId) {
    return (int) (orderId % 2); // 0-1
}

// 一致性哈希
public int getShardIndex(Long userId) {
    int hash = Hashing.murmur3_128().hashLong(userId).asInt();
    return Math.abs(hash) % 4;
}
```

### （2）范围分片

```java
// 按时间范围
public String getTableName(LocalDate orderDate) {
    int year = orderDate.getYear();
    int month = orderDate.getMonthValue();
    return String.format("orders_%d_%02d", year, month);
}

// 按ID范围
public int getDbIndex(Long userId) {
    if (userId >= 1 && userId <= 1000000) {
        return 0;
    } else if (userId >= 1000001 && userId <= 2000000) {
        return 1;
    } else {
        return 2;
    }
}
```

### （3）地理位置分片

```java
// 按地区分片
public int getDbIndex(Integer regionId) {
    if (regionId >= 1 && regionId <= 10) {
        return 0; // 华北
    } else if (regionId >= 11 && regionId <= 20) {
        return 1; // 华南
    } else {
        return 2; // 华东
    }
}
```

### （4）复合分片

```java
// 先按用户ID取模，再按时间分表
public ShardInfo getShardInfo(Long userId, LocalDate orderDate) {
    int dbIndex = (int) (userId % 4);
    String tableName = String.format("orders_%d_%02d", 
        orderDate.getYear(), orderDate.getMonthValue());
    return new ShardInfo(dbIndex, tableName);
}
```

------

## 2️⃣ 主键生成

### （1）雪花算法

```java
public class SnowflakeIdGenerator {
    private final long workerId;
    private final long datacenterId;
    private long sequence = 0;
    private long lastTimestamp = -1L;

    public SnowflakeIdGenerator(long workerId, long datacenterId) {
        this.workerId = workerId;
        this.datacenterId = datacenterId;
    }

    public synchronized long nextId() {
        long timestamp = System.currentTimeMillis();
        
        if (timestamp < lastTimestamp) {
            throw new RuntimeException("Clock moved backwards");
        }
        
        if (timestamp == lastTimestamp) {
            sequence = (sequence + 1) & 0xFFF;
            if (sequence == 0) {
                timestamp = tilNextMillis(lastTimestamp);
            }
        } else {
            sequence = 0;
        }
        
        lastTimestamp = timestamp;
        
        return ((timestamp - 1288834974657L) << 22)
            | (datacenterId << 17)
            | (workerId << 12)
            | sequence;
    }

    private long tilNextMillis(long lastTimestamp) {
        long timestamp = System.currentTimeMillis();
        while (timestamp <= lastTimestamp) {
            timestamp = System.currentTimeMillis();
        }
        return timestamp;
    }
}

// 使用
SnowflakeIdGenerator idGenerator = new SnowflakeIdGenerator(1, 1);
Long orderId = idGenerator.nextId();
```

### （2）号段模式

```sql
-- 号段表
CREATE TABLE id_segment (
    biz_tag VARCHAR(32) PRIMARY KEY,
    max_id BIGINT NOT NULL,
    step INT NOT NULL DEFAULT 1000,
    version INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 初始化
INSERT INTO id_segment (biz_tag, max_id, step, version) 
VALUES ('order', 0, 1000, 0);
```

```java
@Service
public class IdSegmentService {
    
    @Autowired
    private IdSegmentMapper idSegmentMapper;
    
    @Autowired
    private RedisTemplate<String, Long> redisTemplate;
    
    public Long nextId(String bizTag) {
        String redisKey = "id_segment:" + bizTag;
        
        // 从 Redis 获取
        Long currentId = redisTemplate.opsForValue().get(redisKey);
        if (currentId != null && currentId > 0) {
            return redisTemplate.opsForValue().increment(redisKey);
        }
        
        // 从数据库获取号段
        IdSegment segment = idSegmentMapper.selectById(bizTag);
        if (segment == null) {
            throw new RuntimeException("Business tag not found: " + bizTag);
        }
        
        // 更新数据库
        int updated = idSegmentMapper.updateMaxId(bizTag, segment.getVersion());
        if (updated == 0) {
            // 并发冲突，重试
            return nextId(bizTag);
        }
        
        // 设置 Redis
        Long newMaxId = segment.getMaxId() + segment.getStep();
        redisTemplate.opsForValue().set(redisKey, segment.getMaxId() + 1, segment.getStep());
        
        return segment.getMaxId() + 1;
    }
}
```

### （3）Redis INCR

```java
@Service
public class RedisIdGenerator {
    
    @Autowired
    private RedisTemplate<String, Long> redisTemplate;
    
    public Long nextId(String bizTag) {
        String key = "id:" + bizTag;
        return redisTemplate.opsForValue().increment(key);
    }
    
    public Long nextId(String bizTag, long delta) {
        String key = "id:" + bizTag;
        return redisTemplate.opsForValue().increment(key, delta);
    }
}
```

### （4）UUID

```java
// 生成 UUID
String id = UUID.randomUUID().toString();

// 去掉横线
String id = UUID.randomUUID().toString().replace("-", "");

// 使用 Base64 编码
String id = Base64.getEncoder().encodeToString(
    UUID.randomUUID().toString().getBytes()
);
```

------

## 3️⃣ 跨分片查询

### （1）广播查询

```java
// 查询所有分片
public List<Order> getOrdersByRegionId(Integer regionId) {
    List<Order> allOrders = new ArrayList<>();
    
    for (int i = 0; i < 4; i++) {
        List<Order> orders = orderMapper.selectList(
            new LambdaQueryWrapper<Order>()
                .eq(Order::getRegionId, regionId)
                .last("/*+ shardIndex(" + i + ") */")
        );
        allOrders.addAll(orders);
    }
    
    return allOrders;
}
```

### （2）冗余字段

```java
// 在订单表中冗余用户ID和地区ID
@TableName("t_order")
public class Order {
    @TableId(type = IdType.ASSIGN_ID)
    private Long orderId;
    
    private Long userId;
    private Integer regionId; // 冗余字段
    
    private BigDecimal orderAmount;
    
    private Integer orderStatus;
}

// 查询时使用冗余字段
public List<Order> getOrdersByRegionId(Integer regionId) {
    return orderMapper.selectList(
        new LambdaQueryWrapper<Order>()
            .eq(Order::getRegionId, regionId)
    );
}
```

### （3）使用 ES

```java
@Document(indexName = "order")
public class OrderDocument {
    @Id
    private Long orderId;
    
    @Field(type = FieldType.Long)
    private Long userId;
    
    @Field(type = FieldType.Integer)
    private Integer regionId;
    
    @Field(type = FieldType.Double)
    private BigDecimal orderAmount;
    
    @Field(type = FieldType.Integer)
    private Integer orderStatus;
}

@Service
public class OrderSearchService {
    
    @Autowired
    private ElasticsearchRestTemplate elasticsearchTemplate;
    
    public List<OrderDocument> searchOrdersByRegionId(Integer regionId) {
        NativeSearchQuery query = new NativeSearchQueryBuilder()
            .withQuery(QueryBuilders.termQuery("regionId", regionId))
            .build();
        
        SearchHits<OrderDocument> hits = elasticsearchTemplate.search(query, OrderDocument.class);
        return hits.stream()
            .map(SearchHit::getContent)
            .collect(Collectors.toList());
    }
}
```

### （4）数据聚合

```java
// 先查询用户ID，再查询订单
public List<Order> getOrdersByMerchantId(Long merchantId) {
    // 查询商户下的所有用户
    List<Long> userIds = userService.getUserIdsByMerchantId(merchantId);
    
    if (userIds.isEmpty()) {
        return Collections.emptyList();
    }
    
    // 分批查询订单（避免 IN 查询过大）
    List<Order> allOrders = new ArrayList<>();
    int batchSize = 1000;
    
    for (int i = 0; i < userIds.size(); i += batchSize) {
        int end = Math.min(i + batchSize, userIds.size());
        List<Long> batchUserIds = userIds.subList(i, end);
        
        List<Order> orders = orderMapper.selectList(
            new LambdaQueryWrapper<Order>()
                .in(Order::getUserId, batchUserIds)
        );
        allOrders.addAll(orders);
    }
    
    return allOrders;
}
```

------

## 4️⃣ 分布式事务

### （1）TCC 模式

```java
@Service
public class InventoryService {
    
    @Autowired
    private InventoryMapper inventoryMapper;
    
    // Try 阶段：预留库存
    @Transactional
    public void tryDecreaseStock(Long productId, Integer quantity) {
        Inventory inventory = inventoryMapper.selectById(productId);
        if (inventory.getAvailableStock() < quantity) {
            throw new RuntimeException("库存不足");
        }
        
        inventory.setAvailableStock(inventory.getAvailableStock() - quantity);
        inventory.setFrozenStock(inventory.getFrozenStock() + quantity);
        inventoryMapper.updateById(inventory);
    }
    
    // Confirm 阶段：确认扣减
    @Transactional
    public void confirmDecreaseStock(Long productId, Integer quantity) {
        Inventory inventory = inventoryMapper.selectById(productId);
        inventory.setFrozenStock(inventory.getFrozenStock() - quantity);
        inventory.setTotalStock(inventory.getTotalStock() - quantity);
        inventoryMapper.updateById(inventory);
    }
    
    // Cancel 阶段：取消预留
    @Transactional
    public void cancelDecreaseStock(Long productId, Integer quantity) {
        Inventory inventory = inventoryMapper.selectById(productId);
        inventory.setAvailableStock(inventory.getAvailableStock() + quantity);
        inventory.setFrozenStock(inventory.getFrozenStock() - quantity);
        inventoryMapper.updateById(inventory);
    }
}
```

### （2）本地消息表

```sql
-- 本地消息表
CREATE TABLE local_message (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    business_id VARCHAR(64) NOT NULL,
    business_type VARCHAR(32) NOT NULL,
    payload JSON,
    status TINYINT DEFAULT 0, -- 0: 待处理, 1: 已处理, 2: 处理失败
    retry_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_business (business_id, business_type),
    INDEX idx_status (status, retry_count)
);
```

```java
@Service
public class OrderService {
    
    @Autowired
    private OrderMapper orderMapper;
    
    @Autowired
    private LocalMessageMapper localMessageMapper;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Transactional
    public void createOrder(Order order) {
        // 创建订单
        orderMapper.insert(order);
        
        // 保存本地消息
        LocalMessage message = new LocalMessage();
        message.setBusinessId(order.getOrderId().toString());
        message.setBusinessType("order_created");
        message.setPayload(JSON.toJSONString(order));
        message.setStatus(0);
        localMessageMapper.insert(message);
        
        // 扣减库存（本地事务）
        inventoryService.decreaseStock(order.getProductId(), order.getQuantity());
    }
}

@Service
public class MessageProcessor {
    
    @Autowired
    private LocalMessageMapper localMessageMapper;
    
    @Autowired
    private InventoryService inventoryService;
    
    @Scheduled(fixedDelay = 5000)
    public void processMessages() {
        List<LocalMessage> messages = localMessageMapper.selectList(
            new LambdaQueryWrapper<LocalMessage>()
                .eq(LocalMessage::getStatus, 0)
                .lt(LocalMessage::getRetryCount, 3)
                .orderByAsc(LocalMessage::getCreatedAt)
                .last("LIMIT 100")
        );
        
        for (LocalMessage message : messages) {
            try {
                // 处理消息
                Order order = JSON.parseObject(message.getPayload(), Order.class);
                inventoryService.decreaseStock(order.getProductId(), order.getQuantity());
                
                // 更新状态
                message.setStatus(1);
                localMessageMapper.updateById(message);
            } catch (Exception e) {
                // 重试
                message.setRetryCount(message.getRetryCount() + 1);
                if (message.getRetryCount() >= 3) {
                    message.setStatus(2);
                }
                localMessageMapper.updateById(message);
            }
        }
    }
}
```

### （3）Saga 模式

```java
@Data
@AllArgsConstructor
public class TransactionStep {
    private String name;
    private Runnable action;
    private Runnable compensate;
}

@Service
public class SagaTransaction {
    
    public void execute(List<TransactionStep> steps) {
        List<TransactionStep> executedSteps = new ArrayList<>();
        
        try {
            for (TransactionStep step : steps) {
                step.action.run();
                executedSteps.add(step);
            }
        } catch (Exception e) {
            // 回滚已执行的步骤
            Collections.reverse(executedSteps);
            for (TransactionStep step : executedSteps) {
                try {
                    step.compensate.run();
                } catch (Exception ex) {
                    log.error("Compensate failed: {}", step.getName(), ex);
                }
            }
            throw new RuntimeException("Transaction failed", e);
        }
    }
}

// 使用
@Service
public class OrderService {
    
    @Autowired
    private SagaTransaction sagaTransaction;
    
    public void createOrderWithInventory(Order order) {
        List<TransactionStep> steps = Arrays.asList(
            new TransactionStep(
                "decreaseStock",
                () -> inventoryService.decreaseStock(order.getProductId(), order.getQuantity()),
                () -> inventoryService.increaseStock(order.getProductId(), order.getQuantity())
            ),
            new TransactionStep(
                "createOrder",
                () -> orderMapper.insert(order),
                () -> orderMapper.deleteById(order.getOrderId())
            ),
            new TransactionStep(
                "addPoints",
                () -> userService.addPoints(order.getUserId(), order.getOrderAmount().intValue()),
                () -> userService.deductPoints(order.getUserId(), order.getOrderAmount().intValue())
            )
        );
        
        sagaTransaction.execute(steps);
    }
}
```

------

## 5️⃣ 数据迁移

### （1）双写方案

```java
@Service
public class OrderService {
    
    @Autowired
    private OldOrderMapper oldOrderMapper;
    
    @Autowired
    private NewOrderMapper newOrderMapper;
    
    @Autowired
    private MigrationFlagService migrationFlagService;
    
    // 双写：同时写入新旧库
    @Transactional
    public void createOrder(Order order) {
        // 写入旧库
        oldOrderMapper.insert(order);
        
        // 写入新库（分库分表）
        if (migrationFlagService.isWriteNewDb()) {
            newOrderMapper.insert(order);
        }
    }
    
    // 读新库
    public Order getOrderById(Long orderId) {
        if (migrationFlagService.isReadNewDb()) {
            return newOrderMapper.selectById(orderId);
        } else {
            return oldOrderMapper.selectById(orderId);
        }
    }
}
```

### （2）增量同步

```java
@Service
public class DataSyncService {
    
    @Autowired
    private OldOrderMapper oldOrderMapper;
    
    @Autowired
    private NewOrderMapper newOrderMapper;
    
    @Autowired
    private RedisTemplate<String, Long> redisTemplate;
    
    @Scheduled(fixedDelay = 60000)
    public void syncIncrementalData() {
        String redisKey = "sync:last_id";
        Long lastId = redisTemplate.opsForValue().get(redisKey);
        if (lastId == null) {
            lastId = 0L;
        }
        
        // 查询增量数据
        List<Order> orders = oldOrderMapper.selectList(
            new LambdaQueryWrapper<Order>()
                .gt(Order::getOrderId, lastId)
                .orderByAsc(Order::getOrderId)
                .last("LIMIT 1000")
        );
        
        if (!orders.isEmpty()) {
            // 写入新库
            for (Order order : orders) {
                newOrderMapper.insert(order);
            }
            
            // 更新 Redis
            Long maxId = orders.stream()
                .mapToLong(Order::getOrderId)
                .max()
                .orElse(lastId);
            redisTemplate.opsForValue().set(redisKey, maxId);
        }
    }
}
```

### （3）数据校验

```java
@Service
public class DataValidationService {
    
    @Autowired
    private OldOrderMapper oldOrderMapper;
    
    @Autowired
    private NewOrderMapper newOrderMapper;
    
    public void validateData(Long startId, Long endId) {
        List<Order> oldOrders = oldOrderMapper.selectList(
            new LambdaQueryWrapper<Order>()
                .ge(Order::getOrderId, startId)
                .le(Order::getOrderId, endId)
        );
        
        for (Order oldOrder : oldOrders) {
            Order newOrder = newOrderMapper.selectById(oldOrder.getOrderId());
            
            if (newOrder == null) {
                log.error("Order not found in new db: {}", oldOrder.getOrderId());
                continue;
            }
            
            if (!oldOrder.equals(newOrder)) {
                log.error("Order data mismatch: {}", oldOrder.getOrderId());
            }
        }
    }
}
```

------

## 6️⃣ ShardingSphere 配置

### （1）分库分表配置

```yaml
spring:
  shardingsphere:
    datasource:
      names: ds0,ds1
      ds0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/db_0?useSSL=false
        username: root
        password: root
      ds1:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/db_1?useSSL=false
        username: root
        password: root
    
    rules:
      sharding:
        tables:
          t_order:
            actual-data-nodes: ds$->{0..1}.t_order_$->{0..1}
            database-strategy:
              standard:
                sharding-column: user_id
                sharding-algorithm-name: db_inline
            table-strategy:
              standard:
                sharding-column: order_id
                sharding-algorithm-name: table_inline
            key-generate-strategy:
              column: order_id
              key-generator-name: snowflake
        
        sharding-algorithms:
          db_inline:
            type: INLINE
            props:
              algorithm-expression: ds$->{user_id % 2}
          table_inline:
            type: INLINE
            props:
              algorithm-expression: t_order_$->{order_id % 2}
        
        key-generators:
          snowflake:
            type: SNOWFLAKE
            props:
              worker-id: 123
    
    props:
      sql-show: true
```

### （2）读写分离配置

```yaml
spring:
  shardingsphere:
    datasource:
      names: master,slave0,slave1
      master:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/db_master?useSSL=false
        username: root
        password: root
      slave0:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/db_slave0?useSSL=false
        username: root
        password: root
      slave1:
        type: com.zaxxer.hikari.HikariDataSource
        driver-class-name: com.mysql.cj.jdbc.Driver
        jdbc-url: jdbc:mysql://localhost:3306/db_slave1?useSSL=false
        username: root
        password: root
    
    rules:
      readwrite-splitting:
        data-sources:
          prds:
            type: Static
            props:
              write-data-source-name: master
              read-data-source-names: slave0,slave1
            load-balancers:
              round-robin:
                type: ROUND_ROBIN
```

### （3）Seata 集成

```xml
<dependency>
    <groupId>io.seata</groupId>
    <artifactId>seata-spring-boot-starter</artifactId>
    <version>1.7.0</version>
</dependency>
```

```yaml
seata:
  enabled: true
  application-id: order-service
  tx-service-group: order-tx-group
  service:
    vgroup-mapping:
      order-tx-group: default
    grouplist:
      default: localhost:8091
```

```java
@GlobalTransactional(name = "create-order")
public void createOrderWithInventory(Order order, OrderItem item) {
    orderService.createOrder(order);
    inventoryService.decreaseStock(item.getProductId(), item.getQuantity());
}
```

------

## 7️⃣ MyCAT 配置

### （1）server.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mycat:server SYSTEM "server.dtd">
<mycat:server xmlns:mycat="http://io.mycat/">
    <system>
        <property name="defaultSqlParser">druidparser</property>
        <property name="processors">4</property>
        <property name="processorExecutor">16</property>
        <property name="bufferPoolChunkSize">1024</property>
    </system>
    
    <user name="root">
        <property name="password">root</property>
        <property name="schemas">TESTDB</property>
    </user>
</mycat:server>
```

### （2）schema.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mycat:schema SYSTEM "schema.dtd">
<mycat:schema xmlns:mycat="http://io.mycat/">
    
    <schema name="TESTDB" checkSQLschema="false" sqlMaxLimit="100">
        <table name="t_order" dataNode="dn0,dn1" rule="rule1">
            <childTable name="t_order_item" primaryKey="id" joinKey="order_id" parentKey="order_id"/>
        </table>
    </schema>
    
    <dataNode name="dn0" dataHost="host0" database="db_0"/>
    <dataNode name="dn1" dataHost="host1" database="db_1"/>
    
    <dataHost name="host0" maxCon="1000" minCon="10" balance="0" writeType="0" dbType="mysql" dbDriver="native">
        <heartbeat>select user()</heartbeat>
        <writeHost host="hostM1" url="localhost:3306" user="root" password="root"/>
    </dataHost>
    
    <dataHost name="host1" maxCon="1000" minCon="10" balance="0" writeType="0" dbType="mysql" dbDriver="native">
        <heartbeat>select user()</heartbeat>
        <writeHost host="hostM2" url="localhost:3307" user="root" password="root"/>
    </dataHost>
</mycat:schema>
```

### （3）rule.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mycat:rule SYSTEM "rule.dtd">
<mycat:rule xmlns:mycat="http://io.mycat/">
    
    <tableRule name="rule1">
        <rule>
            <columns>user_id</columns>
            <algorithm>func1</algorithm>
        </rule>
    </tableRule>
    
    <function name="func1" class="io.mycat.route.function.PartitionByLong">
        <property name="partitionCount">2</property>
        <property name="partitionLength">512</property>
    </function>
</mycat:rule>
```

------

## 📊 常用 SQL 模板

### （1）创建分片表

```sql
-- 创建分片表模板
CREATE TABLE t_order_0 (
    order_id BIGINT PRIMARY KEY,
    user_id BIGINT NOT NULL,
    order_amount DECIMAL(10, 2),
    order_status TINYINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 创建多个分片表
CREATE TABLE t_order_1 LIKE t_order_0;
CREATE TABLE t_order_2 LIKE t_order_0;
CREATE TABLE t_order_3 LIKE t_order_0;
```

### （2）创建号段表

```sql
CREATE TABLE id_segment (
    biz_tag VARCHAR(32) PRIMARY KEY,
    max_id BIGINT NOT NULL,
    step INT NOT NULL DEFAULT 1000,
    version INT NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

INSERT INTO id_segment (biz_tag, max_id, step, version) 
VALUES ('order', 0, 1000, 0);
```

### （3）创建本地消息表

```sql
CREATE TABLE local_message (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    business_id VARCHAR(64) NOT NULL,
    business_type VARCHAR(32) NOT NULL,
    payload JSON,
    status TINYINT DEFAULT 0,
    retry_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_business (business_id, business_type),
    INDEX idx_status (status, retry_count)
);
```

### （4）创建库存表（TCC）

```sql
CREATE TABLE inventory (
    product_id BIGINT PRIMARY KEY,
    total_stock INT NOT NULL,
    available_stock INT NOT NULL,
    frozen_stock INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_available_stock (available_stock)
);
```

------

## 🔧 常用命令

### （1）MyCAT 命令

```bash
# 启动 MyCAT
cd mycat/bin
./mycat start

# 停止 MyCAT
./mycat stop

# 重启 MyCAT
./mycat restart

# 查看状态
./mycat status

# 查看日志
tail -f ../logs/mycat.log
```

### （2）连接 MyCAT

```bash
# 连接 MyCAT
mysql -h 127.0.0.1 -P 8066 -u root -p

# 查看 MyCAT 状态
SHOW @@DATASOURCE;
SHOW @@DATANODE;
SHOW @@CACHE;
```

### （3）ShardingSphere 命令

```bash
# 查看分片信息
curl http://localhost:8080/sharding/nodes

# 查看指标
curl http://localhost:9090/metrics
```

------

## 💡 最佳实践

### （1）分片键选择

- ✅ 选择查询频率高的字段
- ✅ 确保数据分布均匀
- ✅ 避免分片键变更
- ❌ 不要选择枚举值少的字段
- ❌ 不要选择经常变更的字段

### （2）主键生成

- ✅ 使用雪花算法（推荐）
- ✅ 使用号段模式（高并发）
- ❌ 不要使用 UUID（无序、占用空间大）
- ❌ 不要使用数据库自增（分库分表不适用）

### （3）分布式事务

- ✅ 优先使用本地消息表
- ✅ 对一致性要求高的场景使用 TCC
- ✅ 长事务使用 Saga 模式
- ❌ 尽量避免跨库事务
- ❌ 不要使用 2PC（性能差）

### （4）数据迁移

- ✅ 使用双写方案
- ✅ 做好数据校验
- ✅ 分阶段切换流量
- ❌ 不要一次性迁移大量数据
- ❌ 不要忽略数据一致性

### （5）监控运维

- ✅ 监控分片数据量
- ✅ 监控慢查询
- ✅ 定期检查数据倾斜
- ✅ 定期验证备份
- ❌ 不要忽视告警

------

> 💡 **提示**：本文档用于日常速查，系统学习请查看《学习笔记.md》
