好题！这道题最能体现“会不会线上排障”。给你一份 **面试标准答案 + 实战清单 + 决策树**，背这个就行。

------

# 📌 面试题：如何排查和解决 Full GC 频繁的问题？

## 一、先给定义（10s）

**Full GC** 是对 **整堆（新生代+老年代）以及元空间/方法区** 的一次回收，**STW 最长、影响最大**。频繁 Full GC 通常意味着：老年代或元空间顶满、提升失败、错误触发等。

------

## 二、排查三板斧（按优先级执行）

### 1）确认“真频繁”与影响面（观察）

- 关键指标：**Full GC 次数/分钟、单次停顿、GC占比、吞吐率**
- 统一 GC 日志（JDK9+）：`-Xlog:gc*,safepoint:file=gc.log:tags,uptime,time,levels`
- 旧版：`-XX:+PrintGCDetails -XX:+PrintGCDateStamps -Xloggc:gc.log`
- 运行态概览：
  - `jstat -gcutil <pid> 1s 20`（新老年代使用率、FGC 次数）
  - `jcmd <pid> GC.class_histogram`（对象分布热度）

### 2）定位 Full GC 触发原因（诊断）

- **日志里找触发词**（示例）
  - `System.gc()` → 显式触发
  - `Allocation Failure` / `Promotion failed` → 晋升失败
  - `Concurrent Mode Failure`（CMS）→ 并发清理赶不上分配
  - `Metadata GC Threshold` / `Metaspace` OOM → 元空间不足
  - `Humongous allocation`（G1）→ 巨型对象导致整堆压力
  - `CodeCache full` → JIT 代码缓存满
- **内存形态**
  - 堆直方图：`jmap -histo <pid>`（TOP N 类、数量/大小）
  - Dump 分析：`jmap -dump:live,format=b,file=heap.hprof <pid>` → MAT/VisualVM 看**大对象、泄漏路径**
  - 本地/堆外：`jcmd <pid> VM.native_memory summary`（直接内存、线程栈、Metaspace、CodeCache）

### 3）确认是否“业务行为”导致（归因）

- **突刺型分配**：大批量 JSON 反序列化、一次性聚合大集合、无界缓存
- **类动态加载**：频繁代理/热部署/脚本引擎 → Metaspace 涨
- **堆外使用**：Netty/NIO `allocateDirect()`、图片/压缩库
- **线程过多**：`Unable to create new native thread` 伴随 STW 卡顿
- **错误调用**：`System.gc()`、RMI 定时 GC

------

## 三、解决的“对症方案”决策树

### A. **被 `System.gc()` 或 RMI 触发**

- 现象：日志可见 `System.gc()`
- 方案：
  - **禁用显式 GC**：`-XX:+DisableExplicitGC`
  - RMI：调大 `sun.rmi.dgc.*` 间隔或关闭

### B. **晋升失败 / 老年代顶满（Allocation/Promotion failed）**

- 现象：Minor GC 后对象放不进 Survivor/Old，转 Full GC
- 方案（择要）：
  - **加大老年代**或总体堆：`-Xms/-Xmx`、合理新老代比例
  - **降低晋升压力**：
    - 调 Survivor：`-XX:SurvivorRatio`、增加 Survivor 容量
    - 延迟晋升：`-XX:MaxTenuringThreshold`（让对象多“熬”几轮）
  - **减少短命大对象**：分批处理、流式化，避免一次性创建超大集合/数组
  - **改用 G1**：对大堆、可预测停顿更稳（设 `-XX:MaxGCPauseMillis`）

### C. **CMS 的 Concurrent Mode Failure**

- 现象：CMS 并发清理赶不上分配，退化 Full GC
- 方案：
  - 提前触发 CMS：`-XX:CMSInitiatingOccupancyFraction=70 -XX:+UseCMSInitiatingOccupancyOnly`
  - 允许整理：`-XX:+UseCMSCompactAtFullCollection -XX:CMSFullGCsBeforeCompaction=1`
  - **考虑切到 G1/ZGC**（CMS 已被标记为过时）

### D. **G1 的 Humongous Allocation / Mixed GC 乏力**

- 现象：日志含 `Humongous`；Region 大对象占比高
- 方案：
  - **降低巨型对象产生**：拆分数组/缓冲、复用缓冲池
  - 调整 Region：`-XX:G1HeapRegionSize=8m/16m`（让大对象不至于跨太多 Region）
  - 合理暂停目标：`-XX:MaxGCPauseMillis=200`（过小会导致回收跟不上）

### E. **Metaspace/PermGen 顶满**

- 现象：`OutOfMemoryError: Metaspace` 或 `Metadata GC Threshold` 频发
- 方案：
  - 增加：`-XX:MaxMetaspaceSize=`（或 `-XX:MetaspaceSize` 初始阈值）
  - **修 ClassLoader 泄漏**：Web 容器热部署、插件式加载记得释放；避免把大对象挂到 ClassLoader 可达链

### F. **直接内存（堆外）顶满**

- 现象：`OutOfMemoryError: Direct buffer memory` 或 NMT 显示巨大 `Native Memory`
- 方案：
  - 调整：`-XX:MaxDirectMemorySize=`
  - 确保释放：Netty/ByteBuffer 池化、引用及时失效；避免忘记 `cleaner` 路径（JDK 变更后由库负责）

### G. **代码缓存（CodeCache）顶满**

- 现象：`CodeCache is full. Compiler has been disabled.`
- 方案：`-XX:ReservedCodeCacheSize=256m`（或更大），检查过度 JIT

### H. **实实在在的内存泄漏**

- 现象：Full GC 后老年代**回不去**（基线持续升高）
- 方案：
  - Heap Dump → MAT 找 **Dominator Tree**、泄漏可达链（典型：无界缓存、静态集合、Listener 未移除、ThreadLocal 泄漏）
  - 给缓存**上限 + 淘汰**（Caffeine/Guava LRU/LFU + `maximumSize/maximumWeight`）
  - 用 **弱/软引用** 承载易泄漏对象

------

## 四、调优参数“最小集合”（按收集器分）

- **通用**：`-Xms -Xmx`（保持一致），`-Xlog:gc*`
- **新生代/晋升**：`-XX:NewRatio` 或 `-Xmn`、`-XX:SurvivorRatio`、`-XX:MaxTenuringThreshold`
- **G1**：`-XX:+UseG1GC -XX:MaxGCPauseMillis=200 -XX:InitiatingHeapOccupancyPercent=45 -XX:G1HeapRegionSize=8m -XX:+G1SummarizeRSetStats`
- **ZGC**（JDK11+）：`-XX:+UseZGC`（通常少调参）
- **Metaspace**：`-XX:MetaspaceSize=128m -XX:MaxMetaspaceSize=512m`
- **禁显式 GC**：`-XX:+DisableExplicitGC`

------

## 五、示例：看一段 GC 日志怎么判因（速背）

```
[gc,cause] GC(42) Pause Full (Allocation Failure)
[gc] GC(42) Old: 82% -> 63% … Metaspace: 95% …
[gc] GC(42) Pause Young (G1 Evacuation Pause) (to-space exhausted)
```

- `Pause Full (Allocation Failure)`：分配失败导致 Full GC
- **Old 82%** + `to-space exhausted`：新生代复制空间不足、晋升到老年代也不足 → **晋升失败**
- **处理**：加老年代/Survivor、调 `MaxTenuringThreshold`、压缩大对象、或上 G1/调暂停目标

------

## 六、代码层面“通用止血术”

- **限流 + 分批**：大批量处理改流水线/分页/分块
- **缓存必设上限**：Caffeine `maximumSize/expireAfter*`
- **复用对象**：缓冲池/对象池（连接池、ByteBuf pool）
- **避免无界集合**：队列/Map 必设容量与回压
- **谨慎 `System.gc()`**：禁用或移除
- **减少巨型对象**：大数组拆段；避免一次性拼巨大 JSON/字节数组

------

## 七、面试“3 句话标准作答”（60~90 秒）

1. **先确认**：打开统一 GC 日志 + `jstat`/`jcmd` 看 FullGC 触发原因（Allocation/Promotion failed、Metaspace、System.gc、Humongous）。
2. **再定位**：用 `jmap -histo`/Dump + MAT 查是否泄漏、是否有巨型对象/类加载过多/堆外超限。
3. **对症修复**：禁显式 GC；调 Survivor/晋升阈值/老年代/G1 目标；控制分配速率与缓存上限；必要时更换收集器（G1/ZGC）。

------

## 八、追问清单（给面试官台阶）

- G1 的 Humongous 对象阈值是什么？（≥ 一半 Region，大对象触发特殊路径）
- CMS 为什么会 Concurrent Mode Failure？怎么避免？
- 你线上如何判定“泄漏” vs “高需求”（看 FullGC 后基线是否回落 + MAT Dominator Tree）

— 完。