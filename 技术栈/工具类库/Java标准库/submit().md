## ExecutorService.submit() 方法介绍

### 1. 基本概念
`submit()` 是 Java 标准库中 `java.util.concurrent.ExecutorService` 接口的核心方法，用于提交任务到线程池执行。

### 2. 所属体系
- **接口**：`java.util.concurrent.ExecutorService`
- **包**：`java.util.concurrent`（Java 并发包）
- **JDK 版本**：Java 5+

### 3. 功能作用
`submit()` 方法用于：
1. **提交任务**：将 Runnable 或 Callable 任务提交给线程池执行
2. **异步执行**：任务在独立线程中异步执行
3. **返回结果**：可以返回 Future 对象用于获取执行结果或取消任务
4. **线程复用**：利用线程池管理线程资源

### 4. 方法签名

```java
// 提交 Runnable 任务
Future<?> submit(Runnable task);

// 提交 Runnable 任务并指定返回值
<T> Future<T> submit(Runnable task, T result);

// 提交 Callable 任务
<T> Future<T> submit(Callable<T> task);
```


### 5. 在代码中的使用

```java
// 在 queryWithLogicalExpire 方法中使用
CACHE_REBUILD_EXECUTOR.submit(() -> {
    try {
        // 查询数据库
        R newR = dbFallback.apply(id);
        // 重建缓存
        this.setWithLogicalExpire(key, newR, time, unit);
    } catch (Exception e) {
        throw new RuntimeException(e);
    } finally {
        // 释放锁
        unlock(lockKey);
    }
});
```


这里的 `submit()` 方法接收一个 Lambda 表达式（实现了 `Runnable` 接口）作为参数。

### 6. 线程池初始化

```java
// CacheClient 类中的线程池定义
private static final ExecutorService CACHE_REBUILD_EXECUTOR = Executors.newFixedThreadPool(10);
```


这是一个固定大小为 10 的线程池，用于缓存重建任务。

### 7. 使用示例

#### (1) 提交 Runnable 任务
```java
// 提交无返回值的任务
ExecutorService executor = Executors.newFixedThreadPool(2);
executor.submit(() -> {
    System.out.println("Task executed in: " + Thread.currentThread().getName());
});
```


#### (2) 提交 Callable 任务
```java
// 提交有返回值的任务
Future<String> future = executor.submit(() -> {
    Thread.sleep(1000);
    return "Task completed";
});

// 获取执行结果
String result = future.get(); // 阻塞等待结果
```


### 8. 在缓存系统中的作用

```java
// 逻辑过期缓存重建机制
if (isLock) {
    // 获取锁成功后，异步重建缓存
    CACHE_REBUILD_EXECUTOR.submit(() -> {
        try {
            // 在独立线程中执行耗时的数据库查询和缓存重建
            R newR = dbFallback.apply(id);
            this.setWithLogicalExpire(key, newR, time, unit);
        } catch (Exception e) {
            throw new RuntimeException(e);
        } finally {
            unlock(lockKey);
        }
    });
    // 主线程立即返回过期数据，不等待重建完成
}
```


### 9. submit() 与 execute() 的区别

| 方法                | 返回值    | 异常处理             | 用途             |
| ------------------- | --------- | -------------------- | ---------------- |
| `execute(Runnable)` | void      | 直接抛出异常         | 简单任务执行     |
| `submit(Runnable)`  | Future<?> | 异常包装在 Future 中 | 可监控的任务执行 |

### 10. 相关方法对比

| 方法                  | 特点                     | 适用场景             |
| --------------------- | ------------------------ | -------------------- |
| `submit(Runnable)`    | 无返回值，返回 Future    | 异步执行，不需要结果 |
| `submit(Callable<T>)` | 有返回值，返回 Future<T> | 异步执行，需要结果   |
| `execute(Runnable)`   | 无返回值，无 Future      | 简单任务执行         |

### 11. 优势

1. **异步处理**：避免阻塞主线程
2. **资源管理**：利用线程池管理线程资源
3. **性能优化**：减少线程创建和销毁开销
4. **可扩展性**：易于调整线程池大小
5. **监控能力**：通过 Future 监控任务执行状态

### 12. 完整执行流程

```java
// 1. 线程池初始化
private static final ExecutorService CACHE_REBUILD_EXECUTOR = Executors.newFixedThreadPool(10);

// 2. 提交任务
CACHE_REBUILD_EXECUTOR.submit(() -> {
    // 3. 在线程池中的某个线程执行
    // 4. 执行数据库查询和缓存重建
    // 5. 任务完成后线程返回线程池等待下一个任务
});

// 3. 主线程继续执行，不等待任务完成
```


### 13. 注意事项

```java
// 需要适时关闭线程池
// 在应用关闭时
CACHE_REBUILD_EXECUTOR.shutdown();

// 或强制关闭
CACHE_REBUILD_EXECUTOR.shutdownNow();
```


`submit()` 方法是 Java 并发编程的核心方法之一，在缓存系统中用于实现异步缓存重建，既保证了系统的响应性能，又确保了缓存数据的及时更新。