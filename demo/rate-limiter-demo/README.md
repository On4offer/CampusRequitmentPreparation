# 限流器 Demo（令牌桶 / 固定窗口）

校招可能考口述“令牌桶 vs 漏桶”或手写简单限流。

## 文件说明

| 文件 | 说明 |
|------|------|
| `TokenBucketLimiter.java` | 令牌桶：固定速率补令牌，tryAcquire 取到才通过，允许突发。 |
| `SlidingWindowLimiter.java` | 固定窗口计数：窗口内最多 limit 次，窗口重置后计数清空。 |

## 考点速记

- **令牌桶 vs 漏桶**：令牌桶允许突发；漏桶严格平滑输出。
- **固定窗口边界问题**：跨边界可能 2 倍流量；滑动窗口更平滑。

## 运行方式

```bash
cd demo/rate-limiter-demo
javac -d . *.java
java rate_limiter_demo.TokenBucketLimiter
java rate_limiter_demo.SlidingWindowLimiter
```
