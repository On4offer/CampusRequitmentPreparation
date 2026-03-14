# 手写简单线程池 Demo

固定 worker + BlockingQueue，submit 入队，worker 循环 take 执行。校招可考手写核心逻辑或口述执行流程。

## 文件说明

| 文件 | 说明 |
|------|------|
| `SimpleThreadPool.java` | 固定核心线程数、有界队列、Worker 循环 take 执行。 |

## 考点速记

- **执行流程**：线程数 < 核心数 → 新建核心线程；否则入队；队列满且 < 最大数 → 新建非核心；否则拒绝。
- **为什么用 BlockingQueue**：take 阻塞等待任务，不占 CPU。
- **ThreadPoolExecutor 七参数（口述）**：corePoolSize、maximumPoolSize、keepAliveTime、unit、workQueue、threadFactory、handler（拒绝策略）。
- **拒绝策略**：AbortPolicy（抛异常）、CallerRunsPolicy（调用者线程跑）、DiscardPolicy（丢弃）、DiscardOldestPolicy（丢弃最老任务）。

## 运行方式

```bash
cd demo/simple-thread-pool-demo
javac -d . *.java
java simple_thread_pool_demo.SimpleThreadPool
```
