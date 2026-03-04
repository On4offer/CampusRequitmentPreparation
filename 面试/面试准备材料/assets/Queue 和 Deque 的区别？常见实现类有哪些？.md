# Queue 和 Deque 的区别？常见实现类有哪些？

## 一、核心概念

### 1.1 Queue 接口

**Queue 接口**：
- **包路径**：`java.util.Queue`
- **定义**：**队列**接口，遵循 **FIFO**（First In First Out，先入先出）原则
- **特点**：只能从队列头部移除元素，从队列尾部添加元素
- **继承关系**：继承自 `Collection` 接口

### 1.2 Deque 接口

**Deque 接口**：
- **包路径**：`java.util.Deque`
- **定义**：**双端队列**接口（Double Ended Queue），支持在两端进行插入和删除
- **特点**：既支持队列（FIFO）操作，也支持栈（LIFO）操作
- **继承关系**：继承自 `Queue` 接口

### 1.3 核心区别

| 对比项 | Queue | Deque |
|--------|-------|-------|
| **操作位置** | 单端（头部移除，尾部添加） | 双端（头部和尾部都可以操作） |
| **遵循原则** | FIFO（先入先出） | FIFO 或 LIFO（先入先出或后入先出） |
| **功能** | 只能作为队列使用 | 可以作为队列或栈使用 |
| **灵活性** | 较低 | 较高 |
| **接口关系** | 父接口 | 继承 Queue，是 Queue 的超集 |

---

## 二、Queue 接口详解

### 2.1 核心方法

**Queue 接口的核心方法**：

| 方法 | 说明 | 异常处理 |
|------|------|---------|
| `boolean add(E e)` | 添加元素到队列尾部 | 队列满时抛出异常 |
| `boolean offer(E e)` | 添加元素到队列尾部 | 队列满时返回 false |
| `E remove()` | 移除并返回队列头部元素 | 队列空时抛出异常 |
| `E poll()` | 移除并返回队列头部元素 | 队列空时返回 null |
| `E element()` | 查看队列头部元素（不移除） | 队列空时抛出异常 |
| `E peek()` | 查看队列头部元素（不移除） | 队列空时返回 null |

### 2.2 方法对比

**添加元素**：
```java
// add：队列满时抛出 IllegalStateException
queue.add("element");

// offer：队列满时返回 false（推荐）
boolean success = queue.offer("element");
```

**移除元素**：
```java
// remove：队列空时抛出 NoSuchElementException
String element = queue.remove();

// poll：队列空时返回 null（推荐）
String element = queue.poll();
```

**查看元素**：
```java
// element：队列空时抛出 NoSuchElementException
String head = queue.element();

// peek：队列空时返回 null（推荐）
String head = queue.peek();
```

### 2.3 使用示例

```java
// Queue 使用示例
Queue<String> queue = new LinkedList<>();

// 添加元素
queue.offer("apple");
queue.offer("banana");
queue.offer("cherry");

// 查看头部元素
System.out.println(queue.peek());  // "apple"

// 移除头部元素
String first = queue.poll();  // "apple"
System.out.println(queue.peek());  // "banana"

// 遍历队列
while (!queue.isEmpty()) {
    System.out.println(queue.poll());
}
```

---

## 三、Deque 接口详解

### 3.1 核心方法

**Deque 接口的核心方法**（继承 Queue 的所有方法，并扩展双端操作）：

| 操作位置 | 添加元素 | 移除元素 | 查看元素 |
|---------|---------|---------|---------|
| **头部** | `addFirst(E e)` / `offerFirst(E e)` | `removeFirst()` / `pollFirst()` | `getFirst()` / `peekFirst()` |
| **尾部** | `addLast(E e)` / `offerLast(E e)` | `removeLast()` / `pollLast()` | `getLast()` / `peekLast()` |

### 3.2 作为队列使用（FIFO）

```java
// Deque 作为队列使用
Deque<String> deque = new ArrayDeque<>();

// 尾部添加
deque.offerLast("apple");
deque.offerLast("banana");
deque.offerLast("cherry");

// 头部移除（FIFO）
String first = deque.pollFirst();  // "apple"
String second = deque.pollFirst();  // "banana"
```

### 3.3 作为栈使用（LIFO）

```java
// Deque 作为栈使用
Deque<String> stack = new ArrayDeque<>();

// 头部添加（入栈）
stack.push("apple");  // 等价于 offerFirst
stack.push("banana");
stack.push("cherry");

// 头部移除（出栈，LIFO）
String top = stack.pop();  // "cherry"（等价于 pollFirst）
String next = stack.pop();  // "banana"
```

### 3.4 使用示例

```java
// Deque 双端操作示例
Deque<String> deque = new ArrayDeque<>();

// 头部添加
deque.offerFirst("first");
deque.offerFirst("second");

// 尾部添加
deque.offerLast("third");
deque.offerLast("fourth");

// 当前状态：[second, first, third, fourth]

// 头部移除
String head = deque.pollFirst();  // "second"

// 尾部移除
String tail = deque.pollLast();  // "fourth"

// 查看头部和尾部
String first = deque.peekFirst();  // "first"
String last = deque.peekLast();    // "third"
```

---

## 四、Queue 常见实现类

### 4.1 LinkedList

**特点**：
- ✅ **实现 Queue 和 Deque**：同时实现两个接口
- ✅ **链表实现**：基于双向链表
- ✅ **允许 null**：允许 null 值
- ❌ **线程不安全**：非线程安全

**使用示例**：
```java
Queue<String> queue = new LinkedList<>();
queue.offer("apple");
queue.offer("banana");
String first = queue.poll();  // "apple"
```

### 4.2 PriorityQueue

**特点**：
- ✅ **优先级队列**：元素按优先级排序
- ✅ **堆实现**：基于堆（小根堆）
- ❌ **不遵循 FIFO**：按优先级排序，不是严格的 FIFO
- ❌ **线程不安全**：非线程安全

**使用示例**：
```java
// 自然排序（小根堆）
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(3);
pq.offer(1);
pq.offer(4);
pq.offer(2);

while (!pq.isEmpty()) {
    System.out.println(pq.poll());  // 1, 2, 3, 4（按优先级）
}

// 自定义排序（大根堆）
PriorityQueue<Integer> maxHeap = new PriorityQueue<>(Comparator.reverseOrder());
maxHeap.offer(3);
maxHeap.offer(1);
maxHeap.offer(4);

while (!maxHeap.isEmpty()) {
    System.out.println(maxHeap.poll());  // 4, 3, 1（降序）
}
```

### 4.3 ArrayBlockingQueue

**特点**：
- ✅ **线程安全**：使用 ReentrantLock 保证线程安全
- ✅ **有界队列**：固定容量，创建时指定大小
- ✅ **阻塞操作**：队列满时阻塞，队列空时阻塞
- ✅ **数组实现**：基于数组的循环队列

**使用示例**：
```java
import java.util.concurrent.ArrayBlockingQueue;

// 创建容量为 10 的有界队列
BlockingQueue<String> queue = new ArrayBlockingQueue<>(10);

// 添加元素（队列满时阻塞）
queue.put("element1");

// 移除元素（队列空时阻塞）
String element = queue.take();
```

### 4.4 ConcurrentLinkedQueue

**特点**：
- ✅ **线程安全**：使用 CAS 无锁算法
- ✅ **无界队列**：容量无限制
- ✅ **高性能**：无锁算法，性能好
- ✅ **链表实现**：基于链表的无锁队列

**使用示例**：
```java
import java.util.concurrent.ConcurrentLinkedQueue;

Queue<String> queue = new ConcurrentLinkedQueue<>();
queue.offer("element1");
queue.offer("element2");

String element = queue.poll();
```

---

## 五、Deque 常见实现类

### 5.1 ArrayDeque

**特点**：
- ✅ **数组实现**：基于数组的循环队列
- ✅ **性能高**：比 LinkedList 性能更好
- ✅ **不允许 null**：不允许 null 值
- ❌ **线程不安全**：非线程安全

**使用示例**：
```java
// 作为队列使用
Deque<String> queue = new ArrayDeque<>();
queue.offerLast("apple");
queue.offerLast("banana");
String first = queue.pollFirst();  // "apple"

// 作为栈使用
Deque<String> stack = new ArrayDeque<>();
stack.push("apple");
stack.push("banana");
String top = stack.pop();  // "banana"
```

### 5.2 LinkedList（作为 Deque）

**特点**：
- ✅ **链表实现**：基于双向链表
- ✅ **允许 null**：允许 null 值
- ✅ **功能完整**：同时实现 Queue 和 Deque
- ❌ **性能较低**：比 ArrayDeque 性能差

**使用示例**：
```java
Deque<String> deque = new LinkedList<>();
deque.offerFirst("first");
deque.offerLast("last");
String head = deque.pollFirst();
```

### 5.3 ConcurrentLinkedDeque

**特点**：
- ✅ **线程安全**：使用无锁算法
- ✅ **高性能**：支持高并发
- ✅ **无界队列**：容量无限制
- ✅ **链表实现**：基于链表的无锁双端队列

**使用示例**：
```java
import java.util.concurrent.ConcurrentLinkedDeque;

Deque<String> deque = new ConcurrentLinkedDeque<>();
deque.offerFirst("first");
deque.offerLast("last");
String head = deque.pollFirst();
```

---

## 六、详细对比表

### 6.1 Queue vs Deque

| 对比项 | Queue | Deque |
|--------|-------|-------|
| **操作位置** | 单端（头部移除，尾部添加） | 双端（头部和尾部都可以操作） |
| **遵循原则** | FIFO | FIFO 或 LIFO |
| **功能** | 只能作为队列 | 可以作为队列或栈 |
| **方法数量** | 6 个核心方法 | 12+ 个方法（包含 Queue 的方法） |
| **灵活性** | 较低 | 较高 |
| **接口关系** | 父接口 | 继承 Queue |

### 6.2 实现类对比

| 实现类 | 接口 | 底层实现 | 线程安全 | 特点 |
|--------|------|---------|---------|------|
| **LinkedList** | Queue + Deque | 双向链表 | ❌ | 允许 null，性能较低 |
| **ArrayDeque** | Deque | 数组（循环队列） | ❌ | 性能高，不允许 null |
| **PriorityQueue** | Queue | 堆（小根堆） | ❌ | 优先级排序，不遵循 FIFO |
| **ArrayBlockingQueue** | BlockingQueue | 数组（循环队列） | ✅ | 有界，阻塞操作 |
| **ConcurrentLinkedQueue** | Queue | 链表（无锁） | ✅ | 无界，高性能 |
| **ConcurrentLinkedDeque** | Deque | 链表（无锁） | ✅ | 无界，高性能 |

### 6.3 LinkedList vs ArrayDeque

| 对比项 | LinkedList | ArrayDeque |
|--------|-----------|-----------|
| **底层实现** | 双向链表 | 数组（循环队列） |
| **性能** | 较低（指针开销） | 较高（连续内存） |
| **允许 null** | ✅ | ❌ |
| **内存占用** | 较高（指针） | 较低（数组） |
| **推荐使用** | 需要 null 值时 | 大多数场景（推荐） |

---

## 七、实际应用场景

### 7.1 场景1：任务队列（Queue）

```java
// 任务队列（FIFO）
Queue<Task> taskQueue = new LinkedList<>();

public void submitTask(Task task) {
    taskQueue.offer(task);
}

public void processTasks() {
    while (!taskQueue.isEmpty()) {
        Task task = taskQueue.poll();
        task.execute();
    }
}
```

### 7.2 场景2：消息队列（BlockingQueue）

```java
// 生产者-消费者模式
BlockingQueue<Message> messageQueue = new ArrayBlockingQueue<>(100);

// 生产者
public void produce(Message message) throws InterruptedException {
    messageQueue.put(message);  // 队列满时阻塞
}

// 消费者
public Message consume() throws InterruptedException {
    return messageQueue.take();  // 队列空时阻塞
}
```

### 7.3 场景3：优先级任务调度（PriorityQueue）

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

### 7.4 场景4：栈操作（Deque）

```java
// 使用 Deque 实现栈
Deque<String> stack = new ArrayDeque<>();

// 表达式求值：中缀转后缀
public void evaluateExpression(String expression) {
    Deque<Character> operators = new ArrayDeque<>();
    
    for (char c : expression.toCharArray()) {
        if (c == '(') {
            operators.push(c);
        } else if (c == ')') {
            while (!operators.isEmpty() && operators.peek() != '(') {
                processOperator(operators.pop());
            }
            operators.pop();  // 移除 '('
        } else if (isOperator(c)) {
            operators.push(c);
        }
    }
}
```

### 7.5 场景5：滑动窗口（Deque）

```java
// 滑动窗口最大值
public int[] maxSlidingWindow(int[] nums, int k) {
    Deque<Integer> deque = new ArrayDeque<>();
    int[] result = new int[nums.length - k + 1];
    
    for (int i = 0; i < nums.length; i++) {
        // 移除窗口外的元素
        while (!deque.isEmpty() && deque.peekFirst() < i - k + 1) {
            deque.pollFirst();
        }
        
        // 移除小于当前元素的元素
        while (!deque.isEmpty() && nums[deque.peekLast()] < nums[i]) {
            deque.pollLast();
        }
        
        deque.offerLast(i);
        
        if (i >= k - 1) {
            result[i - k + 1] = nums[deque.peekFirst()];
        }
    }
    
    return result;
}
```

---

## 八、常见面试追问

### Q1：Queue 和 Deque 能否替换？

**答**：
- ✅ **Deque 是 Queue 的超集**：Deque 继承 Queue，包含 Queue 的所有方法
- ✅ **可以替换**：如果需要队列功能，可以用 Deque 替代 Queue
- ⚠️ **语义清晰**：如果只需要队列功能，使用 Queue 更语义清晰
- ✅ **推荐**：需要双端操作时使用 Deque，只需要队列时使用 Queue

**示例**：
```java
// Queue 用法
Queue<String> queue = new LinkedList<>();
queue.offer("element");

// Deque 也可以实现队列功能
Deque<String> deque = new ArrayDeque<>();
deque.offerLast("element");  // 等价于 queue.offer()
```

### Q2：LinkedList 和 ArrayDeque 的区别？

**答**：

| 对比项 | LinkedList | ArrayDeque |
|--------|-----------|-----------|
| **底层实现** | 双向链表 | 数组（循环队列） |
| **性能** | 较低（指针开销，内存不连续） | 较高（连续内存，缓存友好） |
| **允许 null** | ✅ | ❌ |
| **内存占用** | 较高（每个节点需要指针） | 较低（数组连续存储） |
| **推荐使用** | 需要 null 值或需要 List 功能 | 大多数场景（推荐） |

**选择建议**：
- **大多数场景**：使用 ArrayDeque（性能更好）
- **需要 null 值**：使用 LinkedList
- **需要 List 功能**：使用 LinkedList（LinkedList 也实现 List）

### Q3：PriorityQueue 是队列吗？为什么是？

**答**：
- ✅ **是队列**：PriorityQueue 实现了 Queue 接口
- ❌ **不遵循 FIFO**：按优先级排序，不是严格的先入先出
- ✅ **堆实现**：基于堆（小根堆）实现
- ✅ **应用场景**：任务调度、事件处理等需要优先级的场景

**示例**：
```java
PriorityQueue<Integer> pq = new PriorityQueue<>();
pq.offer(3);
pq.offer(1);
pq.offer(4);

// 输出：1, 3, 4（按优先级，不是插入顺序）
while (!pq.isEmpty()) {
    System.out.println(pq.poll());
}
```

### Q4：什么时候用 Queue，什么时候用 Deque？

**答**：

**使用 Queue**：
- ✅ 只需要队列功能（FIFO）
- ✅ 语义清晰，代码可读性好
- ✅ 不需要栈功能

**使用 Deque**：
- ✅ 需要双端操作
- ✅ 需要栈功能（LIFO）
- ✅ 需要更灵活的操作
- ✅ 可以用 Deque 替代 Queue（功能更全）

### Q5：ArrayBlockingQueue 和 ConcurrentLinkedQueue 的区别？

**答**：

| 对比项 | ArrayBlockingQueue | ConcurrentLinkedQueue |
|--------|-------------------|----------------------|
| **线程安全** | ✅ | ✅ |
| **容量** | 有界（固定大小） | 无界 |
| **阻塞操作** | ✅（put/take 会阻塞） | ❌（offer/poll 不阻塞） |
| **底层实现** | 数组（循环队列） | 链表（无锁） |
| **锁机制** | ReentrantLock | CAS 无锁算法 |
| **适用场景** | 生产者-消费者，需要控制容量 | 高并发，不需要阻塞 |

---

## 九、面试回答模板

### 9.1 核心回答（1分钟）

"Queue 是队列接口，遵循 FIFO 原则，只能从头部移除元素，尾部添加元素，核心方法有 offer、poll、peek。Deque 是双端队列接口，继承 Queue，支持在头部和尾部进行插入和删除，既可以用作队列（FIFO）也可以用作栈（LIFO）。Queue 的常见实现有 LinkedList、PriorityQueue、ArrayBlockingQueue、ConcurrentLinkedQueue。Deque 的常见实现有 LinkedList、ArrayDeque、ConcurrentLinkedDeque。区别是 Queue 只能单端操作，Deque 可以双端操作，功能更灵活。"

### 9.2 扩展回答（3分钟）

"从接口关系看，Deque 继承 Queue，是 Queue 的超集。Queue 只能从头部移除、尾部添加，遵循 FIFO。Deque 支持头部和尾部都可以插入删除，可以用作队列或栈。实现类方面，LinkedList 同时实现 Queue 和 Deque，基于双向链表，允许 null 但性能较低。ArrayDeque 基于数组循环队列，性能高但不允许 null，推荐使用。PriorityQueue 实现 Queue 但按优先级排序，不遵循严格 FIFO，基于堆实现。线程安全的有 ArrayBlockingQueue（有界阻塞队列）、ConcurrentLinkedQueue（无界无锁队列）、ConcurrentLinkedDeque（无界无锁双端队列）。选择上，只需要队列用 Queue，需要双端操作用 Deque，大多数场景推荐 ArrayDeque。"

### 9.3 加分项

- 能说出 Queue 和 Deque 的接口关系和核心方法
- 了解 PriorityQueue 不遵循严格 FIFO 的特点
- 知道 ArrayDeque 和 LinkedList 的性能差异
- 理解阻塞队列和非阻塞队列的区别
- 能说出不同实现类的适用场景