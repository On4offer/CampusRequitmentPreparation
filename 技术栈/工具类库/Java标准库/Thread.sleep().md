## Thread.sleep() 方法介绍

### 1. 基本概念
`Thread.sleep(50)` 是 Java 标准库中的原生方法，用于使当前正在执行的线程暂停执行指定的时间，让出 CPU 时间片给其他线程。

### 2. 所属体系
- **类**：`java.lang.Thread`
- **包**：`java.lang`（Java 核心包，无需导入）
- **方法签名**：`public static native void sleep(long millis) throws InterruptedException`

### 3. 功能作用
`Thread.sleep()` 方法用于：
1. **线程休眠**：使当前线程暂停执行指定毫秒数
2. **控制执行节奏**：调节程序执行频率
3. **等待资源**：给其他线程执行机会
4. **重试机制**：在失败后等待一段时间再重试

### 4. 方法定义

```java
/**
 * 使当前正在执行的线程进入休眠状态（暂时停止执行）指定的毫秒数
 * @param millis 休眠的毫秒数
 * @throws InterruptedException 如果线程在睡眠期间被中断
 */
public static native void sleep(long millis) throws InterruptedException;

/**
 * 使当前正在执行的线程进入休眠状态指定的毫秒数和纳秒数
 * @param millis 休眠的毫秒数
 * @param nanos 0-999999 的额外纳秒数
 * @throws InterruptedException 如果线程在睡眠期间被中断
 */
public static void sleep(long millis, int nanos) throws InterruptedException;
```


### 5. 在代码中的使用

```java
// 在 queryWithMutex 方法中使用
public <R, ID> R queryWithMutex(...) {
    try {
        boolean isLock = tryLock(lockKey);
        // 判断是否获取成功
        if (!isLock) {
            // 获取锁失败，休眠并重试
            Thread.sleep(50);
            return queryWithMutex(keyPrefix, id, type, dbFallback, time, unit);
        }
        // ...
    } catch (InterruptedException e) {
        throw new RuntimeException(e);
    }
}
```


在这里，当获取 Redis 分布式锁失败时，线程会休眠 50 毫秒后重新尝试获取锁，这是一种典型的重试机制。

### 6. 使用示例

#### (1) 基本使用
```java
// 休眠 1 秒
try {
    Thread.sleep(1000);
} catch (InterruptedException e) {
    // 处理中断异常
    Thread.currentThread().interrupt(); // 恢复中断状态
}
```


#### (2) 循环中的使用
```java
// 重试机制示例
int retryCount = 0;
while (retryCount < 3) {
    if (acquireLock()) {
        // 成功获取锁，执行业务逻辑
        break;
    } else {
        try {
            // 获取锁失败，休眠后重试
            Thread.sleep(100);
            retryCount++;
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            break;
        }
    }
}
```


### 7. 在缓存逻辑中的作用

```java
// 防止缓存击穿的重试机制
if (!isLock) {
    // 当获取分布式锁失败时
    // 让线程短暂休眠，避免频繁重试造成系统压力
    Thread.sleep(50);
    // 递归调用重新尝试获取锁
    return queryWithMutex(keyPrefix, id, type, dbFallback, time, unit);
}
```


### 8. 相关线程控制方法对比

| 方法                                                         | 用途         | 是否释放锁 | 是否抛出异常 |
| ------------------------------------------------------------ | ------------ | ---------- | ------------ |
| `Thread.sleep(millis)`                                       | 线程休眠     | 否         | 是           |
| `Object.wait()`                                              | 对象等待     | 是         | 是           |
| `Thread.yield()`                                             | 线程让步     | 否         | 否           |
| [join()](file://cn\hutool\core\text\CharSequenceUtil.java#L224-L224) | 等待线程结束 | 否         | 是           |

### 9. 优势

1. **简单易用**：使用简单，只需指定休眠时间
2. **精确控制**：可以精确控制休眠时间
3. **标准API**：Java 原生支持，无需第三方库
4. **跨平台**：在所有 Java 支持的平台上行为一致

### 10. 注意事项

```java
// 必须处理 InterruptedException
try {
    Thread.sleep(50);
} catch (InterruptedException e) {
    // 正确处理中断异常
    throw new RuntimeException(e);
    // 或恢复中断状态
    // Thread.currentThread().interrupt();
}

// 避免过长的休眠时间
// Thread.sleep(50) 比 Thread.sleep(1000) 更合适用于重试场景

// 在循环中使用时注意退出条件
```


### 11. 与定时任务对比

```java
// 使用 Thread.sleep 实现简单的轮询
while (!condition) {
    Thread.sleep(50); // 每 50ms 检查一次条件
}

// vs 使用 ScheduledExecutorService
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(1);
scheduler.scheduleAtFixedRate(() -> {
    // 定时执行任务
}, 0, 50, TimeUnit.MILLISECONDS);
```


`Thread.sleep(50)` 是 Java 标准库提供的线程控制方法，在缓存系统中用于实现重试机制，是一种简单有效的防止并发冲突的手段。