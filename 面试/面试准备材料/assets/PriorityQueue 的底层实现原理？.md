# PriorityQueue 的底层实现原理是什么？如何保证元素有序？

## 一、PriorityQueue 概述

### 1.1 定义

**PriorityQueue**：
- **包路径**：`java.util.PriorityQueue`
- **定义**：**优先级队列**，基于堆（Heap）实现的队列
- **特点**：元素按优先级排序，不遵循严格的 FIFO
- **继承关系**：继承自 `AbstractQueue`，实现 `Queue` 接口

### 1.2 核心特性

| 特性 | 说明 |
|------|------|
| **底层结构** | 最小堆（二叉堆），用数组实现 |
| **有序性** | 只保证堆顶有序，不保证整体有序 |
| **排序规则** | 默认自然排序，可自定义 Comparator |
| **线程安全** | ❌ 非线程安全 |
| **时间复杂度** | 插入 O(log n)，删除 O(log n)，查看 O(1) |

---

## 二、底层数据结构

### 2.1 堆（Heap）结构

**堆的定义**：
- **完全二叉树**：堆是一棵完全二叉树
- **堆序性**：
  - **最小堆**：父节点 <= 子节点（默认）
  - **最大堆**：父节点 >= 子节点
- **数组存储**：用数组存储完全二叉树

**数组索引关系**：
```java
// 对于索引 i 的节点：
// 父节点索引：(i - 1) / 2
// 左子节点索引：2 * i + 1
// 右子节点索引：2 * i + 2
```

**示例**：
```
        1
       / \
      3   2
     / \ / \
    4  5 6  7

数组：[1, 3, 2, 4, 5, 6, 7]
索引： 0  1  2  3  4  5  6
```

### 2.2 PriorityQueue 源码结构

```java
// PriorityQueue 源码
public class PriorityQueue<E> extends AbstractQueue<E> {
    // 底层数组
    transient Object[] queue;
    
    // 元素个数
    private int size = 0;
    
    // 比较器（null 表示使用自然排序）
    private final Comparator<? super E> comparator;
    
    // 默认初始容量
    private static final int DEFAULT_INITIAL_CAPACITY = 11;
}
```

**核心字段**：
- `queue[]`：存储堆元素的数组
- `size`：当前元素个数
- `comparator`：比较器，用于自定义排序

---

## 三、插入元素（上浮操作）

### 3.1 offer() 方法

```java
// PriorityQueue 的 offer 方法
public boolean offer(E e) {
    if (e == null)
        throw new NullPointerException();
    modCount++;
    int i = size;
    if (i >= queue.length)
        grow(i + 1);  // 扩容
    size = i + 1;
    if (i == 0)
        queue[0] = e;  // 第一个元素
    else
        siftUp(i, e);  // 上浮操作
    return true;
}
```

### 3.2 上浮（siftUp）操作

```java
// 上浮操作
private void siftUp(int k, E x) {
    if (comparator != null)
        siftUpUsingComparator(k, x);
    else
        siftUpComparable(k, x);
}

// 使用自然排序的上浮
private void siftUpComparable(int k, E x) {
    Comparable<? super E> key = (Comparable<? super E>) x;
    while (k > 0) {
        int parent = (k - 1) >>> 1;  // 父节点索引
        Object e = queue[parent];
        if (key.compareTo((E) e) >= 0)  // 如果当前节点 >= 父节点，停止
            break;
        queue[k] = e;  // 父节点下移
        k = parent;    // 继续向上比较
    }
    queue[k] = key;  // 找到合适位置，插入
}
```

**上浮过程示例**（插入元素 1）：
```
初始堆：
        3
       / \
      5   4
     / \
    7   6

插入 1：
1. 放到数组末尾：[3, 5, 4, 7, 6, 1]
2. 与父节点 6 比较：1 < 6，交换
3. 与父节点 5 比较：1 < 5，交换
4. 与父节点 3 比较：1 < 3，交换

最终堆：
        1
       / \
      3   4
     / \ / \
    7  5 6  (1)
```

### 3.3 时间复杂度

- **时间复杂度**：O(log n)
- **原因**：最多需要向上比较 log n 层（树的高度）

---

## 四、删除元素（下沉操作）

### 4.1 poll() 方法

```java
// PriorityQueue 的 poll 方法
public E poll() {
    if (size == 0)
        return null;
    int s = --size;
    modCount++;
    E result = (E) queue[0];  // 堆顶元素
    E x = (E) queue[s];       // 最后一个元素
    queue[s] = null;
    if (s != 0)
        siftDown(0, x);  // 下沉操作
    return result;
}
```

### 4.2 下沉（siftDown）操作

```java
// 下沉操作
private void siftDown(int k, E x) {
    if (comparator != null)
        siftDownUsingComparator(k, x);
    else
        siftDownComparable(k, x);
}

// 使用自然排序的下沉
private void siftDownComparable(int k, E x) {
    Comparable<? super E> key = (Comparable<? super E>) x;
    int half = size >>> 1;  // 最后一个非叶子节点
    while (k < half) {
        int child = (k << 1) + 1;  // 左子节点
        Object c = queue[child];
        int right = child + 1;
        // 选择较小的子节点
        if (right < size &&
            ((Comparable<? super E>) c).compareTo((E) queue[right]) > 0)
            c = queue[child = right];
        // 如果当前节点 <= 子节点，停止
        if (key.compareTo((E) c) <= 0)
            break;
        queue[k] = c;  // 子节点上移
        k = child;     // 继续向下比较
    }
    queue[k] = key;  // 找到合适位置，插入
}
```

**下沉过程示例**（删除堆顶元素 1）：
```
初始堆：
        1
       / \
      3   4
     / \ / \
    7  5 6  8

删除堆顶：
1. 取出堆顶 1
2. 将最后一个元素 8 放到堆顶
3. 与子节点比较：8 > 3 和 8 > 4，选择较小的 3
4. 8 与 3 交换
5. 继续向下：8 > 5，交换

最终堆：
        3
       / \
      5   4
     / \ /
    7  8 6
```

### 4.3 时间复杂度

- **时间复杂度**：O(log n)
- **原因**：最多需要向下比较 log n 层

---

## 五、如何保证元素有序？

### 5.1 堆序性保证

**核心机制**：
1. **插入时上浮**：新元素插入后，通过上浮操作维持堆序性
2. **删除时下沉**：删除堆顶后，通过下沉操作维持堆序性
3. **堆顶保证**：堆顶始终是当前最小（或最大）元素

**重要说明**：
- ⚠️ **只保证堆顶有序**：PriorityQueue 只保证堆顶是最小值，不保证整体有序
- ⚠️ **不是完全有序**：数组中的元素不是完全有序的
- ✅ **按序取出**：通过不断 poll() 可以按顺序取出所有元素

### 5.2 排序规则

**方式1：自然排序（实现 Comparable）**
```java
// 默认最小堆（小根堆）
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(3);
pq.offer(1);
pq.offer(4);
pq.offer(2);

// 堆结构（不完全有序）：
// [1, 2, 4, 3]
// 但堆顶 1 是最小的

// 按序取出
while (!pq.isEmpty()) {
    System.out.println(pq.poll());  // 1, 2, 3, 4（有序）
}
```

**方式2：自定义排序（传入 Comparator）**
```java
// 最大堆（大根堆）
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(
    Comparator.reverseOrder()
);
maxHeap.offer(3);
maxHeap.offer(1);
maxHeap.offer(4);

// 按序取出（降序）
while (!maxHeap.isEmpty()) {
    System.out.println(maxHeap.poll());  // 4, 3, 1
}
```

### 5.3 完整示例

```java
// PriorityQueue 使用示例
PriorityQueue<Student> pq = new PriorityQueue<>(
    Comparator.comparing(Student::getScore).reversed()
);

pq.offer(new Student("张三", 85));
pq.offer(new Student("李四", 90));
pq.offer(new Student("王五", 80));

// 堆顶是分数最高的
Student top = pq.peek();  // 李四（90分）

// 按分数从高到低取出
while (!pq.isEmpty()) {
    System.out.println(pq.poll());
    // 李四(90), 张三(85), 王五(80)
}
```

---

## 六、扩容机制

### 6.1 grow() 方法

```java
// PriorityQueue 的扩容方法
private void grow(int minCapacity) {
    int oldCapacity = queue.length;
    // 小容量：扩容为 2 倍
    // 大容量：扩容为 1.5 倍
    int newCapacity = oldCapacity + ((oldCapacity < 64) ?
                                     (oldCapacity + 2) :
                                     (oldCapacity >> 1));
    if (newCapacity - MAX_ARRAY_SIZE > 0)
        newCapacity = hugeCapacity(minCapacity);
    queue = Arrays.copyOf(queue, newCapacity);
}
```

**扩容规则**：
- **小容量（< 64）**：扩容为 `oldCapacity * 2 + 2`
- **大容量（>= 64）**：扩容为 `oldCapacity * 1.5`
- **默认容量**：11

**示例**：
```java
PriorityQueue<Integer> pq = new PriorityQueue<>();
// 初始容量：11
// 第1次扩容：11 * 2 + 2 = 24
// 第2次扩容：24 * 2 + 2 = 50
// 第3次扩容：50 * 1.5 = 75
```

---

## 七、时间复杂度分析

### 7.1 各操作时间复杂度

| 操作 | 时间复杂度 | 说明 |
|------|-----------|------|
| **offer()** | O(log n) | 插入元素，需要上浮 |
| **poll()** | O(log n) | 删除堆顶，需要下沉 |
| **peek()** | O(1) | 查看堆顶，直接返回 |
| **remove()** | O(n) | 删除指定元素，需要查找 |
| **contains()** | O(n) | 查找元素，需要遍历 |

### 7.2 为什么是 O(log n)？

**原因**：
- **堆的高度**：完全二叉树的高度是 log n
- **上浮/下沉**：最多需要比较 log n 次
- **平衡性**：堆始终保持平衡，不会退化为链表

---

## 八、与其他数据结构对比

### 8.1 PriorityQueue vs TreeSet

| 对比项 | PriorityQueue | TreeSet |
|--------|--------------|---------|
| **底层结构** | 堆（数组） | 红黑树 |
| **有序性** | 只保证堆顶有序 | 整体有序 |
| **重复元素** | ✅ 允许 | ❌ 不允许 |
| **性能（插入）** | O(log n) | O(log n) |
| **性能（删除）** | O(log n) | O(log n) |
| **适用场景** | 优先级队列 | 有序集合 |

### 8.2 PriorityQueue vs 普通 Queue

| 对比项 | PriorityQueue | Queue（如 LinkedList） |
|--------|--------------|----------------------|
| **遵循原则** | 按优先级 | FIFO |
| **有序性** | 按优先级排序 | 按插入顺序 |
| **性能（插入）** | O(log n) | O(1) |
| **性能（删除）** | O(log n) | O(1) |
| **适用场景** | 需要优先级 | 需要 FIFO |

---

## 九、实际应用场景

### 9.1 场景1：TOP K 问题

```java
// 找出数组中最大的 K 个数
public int[] findTopK(int[] nums, int k) {
    // 使用最小堆，维护 K 个元素
    PriorityQueue<Integer> pq = new PriorityQueue<>();
    
    for (int num : nums) {
        if (pq.size() < k) {
            pq.offer(num);
        } else if (num > pq.peek()) {
            pq.poll();
            pq.offer(num);
        }
    }
    
    int[] result = new int[k];
    for (int i = k - 1; i >= 0; i--) {
        result[i] = pq.poll();
    }
    return result;
}
```

### 9.2 场景2：任务调度

```java
// 任务按优先级调度
PriorityQueue<Task> taskQueue = new PriorityQueue<>(
    Comparator.comparing(Task::getPriority).reversed()
);

public void submitTask(Task task) {
    taskQueue.offer(task);
}

public Task getNextTask() {
    return taskQueue.poll();  // 返回优先级最高的任务
}
```

### 9.3 场景3：合并 K 个有序链表

```java
// 合并 K 个有序链表
public ListNode mergeKLists(ListNode[] lists) {
    PriorityQueue<ListNode> pq = new PriorityQueue<>(
        Comparator.comparing(node -> node.val)
    );
    
    // 将每个链表的头节点加入堆
    for (ListNode node : lists) {
        if (node != null) {
            pq.offer(node);
        }
    }
    
    ListNode dummy = new ListNode(0);
    ListNode curr = dummy;
    
    while (!pq.isEmpty()) {
        ListNode min = pq.poll();
        curr.next = min;
        curr = curr.next;
        if (min.next != null) {
            pq.offer(min.next);
        }
    }
    
    return dummy.next;
}
```

### 9.4 场景4：订单超时处理

```java
// 订单按超时时间排序
PriorityQueue<Order> timeoutQueue = new PriorityQueue<>(
    Comparator.comparing(Order::getTimeoutTime)
);

public void addOrder(Order order) {
    timeoutQueue.offer(order);
}

public void processTimeoutOrders() {
    long currentTime = System.currentTimeMillis();
    while (!timeoutQueue.isEmpty() && 
           timeoutQueue.peek().getTimeoutTime() <= currentTime) {
        Order order = timeoutQueue.poll();
        handleTimeout(order);
    }
}
```

---

## 十、常见面试追问

### Q1：PriorityQueue 和 TreeSet 的区别？

**答**：

| 对比项 | PriorityQueue | TreeSet |
|--------|--------------|---------|
| **底层结构** | 堆（数组） | 红黑树 |
| **有序性** | 只保证堆顶有序 | 整体有序 |
| **重复元素** | ✅ 允许 | ❌ 不允许 |
| **性能** | O(log n) | O(log n) |
| **适用场景** | 优先级队列 | 有序集合 |

**选择建议**：
- **需要优先级队列**：使用 PriorityQueue
- **需要有序集合**：使用 TreeSet

### Q2：如何实现最大堆？

**答**：

**方式1：使用 Comparator.reverseOrder()**
```java
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(
    Comparator.reverseOrder()
);
```

**方式2：自定义 Comparator**
```java
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(
    (a, b) -> b - a  // 降序
);
```

**方式3：反转比较逻辑**
```java
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(
    (a, b) -> b.compareTo(a)
);
```

### Q3：PriorityQueue 的扩容机制？

**答**：
- **默认容量**：11
- **小容量（< 64）**：扩容为 `oldCapacity * 2 + 2`
- **大容量（>= 64）**：扩容为 `oldCapacity * 1.5`
- **扩容时机**：插入元素时，如果容量不足

**示例**：
```
11 → 24 → 50 → 75 → 112 → ...
```

### Q4：PriorityQueue 为什么只保证堆顶有序？

**答**：
- **堆的性质**：堆只保证父节点和子节点的关系，不保证兄弟节点有序
- **性能考虑**：完全有序需要 O(n log n) 排序，堆只需要 O(log n) 维护
- **应用场景**：优先级队列只需要快速获取最值，不需要完全有序

**示例**：
```java
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(3);
pq.offer(1);
pq.offer(4);
pq.offer(2);

// 堆结构：[1, 2, 4, 3]
// 堆顶 1 是最小的，但整体不是有序的
// 通过 poll() 可以按序取出：1, 2, 3, 4
```

### Q5：PriorityQueue 是线程安全的吗？

**答**：
- ❌ **非线程安全**：PriorityQueue 不是线程安全的
- ✅ **线程安全替代**：使用 `PriorityBlockingQueue`

**示例**：
```java
// 非线程安全
PriorityQueue<Integer> pq = new PriorityQueue<>();

// 线程安全
import java.util.concurrent.PriorityBlockingQueue;
PriorityBlockingQueue<Integer> safePq = new PriorityBlockingQueue<>();
```

---

## 十一、面试回答模板

### 11.1 核心回答（1分钟）

"PriorityQueue 底层是最小堆，用数组实现完全二叉树。插入元素时先放到数组末尾，然后执行上浮操作，与父节点比较，如果小于父节点就交换，直到满足堆序性。删除堆顶时，将最后一个元素放到堆顶，然后执行下沉操作，与子节点比较，选择较小的子节点交换，直到满足堆序性。这样保证堆顶始终是最小值，时间复杂度都是 O(log n)。PriorityQueue 只保证堆顶有序，不保证整体有序，如果需要整体有序，需要不断 poll 取出元素。"

### 11.2 扩展回答（3分钟）

"从数据结构看，PriorityQueue 使用堆（完全二叉树）实现，用数组存储。数组索引关系是：父节点 (i-1)/2，左子节点 2i+1，右子节点 2i+2。插入时执行上浮操作，从插入位置向上比较，如果小于父节点就交换，时间复杂度 O(log n)。删除时执行下沉操作，从堆顶向下比较，选择较小的子节点交换，时间复杂度 O(log n)。查看堆顶是 O(1)。排序规则上，默认使用自然排序，可以传入 Comparator 自定义。扩容机制是小容量扩容 2 倍，大容量扩容 1.5 倍。需要注意的是，PriorityQueue 只保证堆顶有序，不保证整体有序，这是堆的性质决定的。"

### 11.3 加分项

- 能说出堆的数组索引关系
- 了解上浮和下沉的具体实现过程
- 知道 PriorityQueue 只保证堆顶有序
- 理解为什么时间复杂度是 O(log n)
- 能说出 PriorityQueue 的扩容机制