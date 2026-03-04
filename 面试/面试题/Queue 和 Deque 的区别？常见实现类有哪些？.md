以下是 **Queue** 和 **Deque** 的区别以及常见实现类的详细解答，按标准面试模板整理：

------

# 📌 面试题：Queue 和 Deque 的区别？常见实现类有哪些？

## 一、核心回答（面试官想听的点）

1. **Queue**（队列）：
   - **特点**：遵循 **FIFO**（先入先出）原则，队列的元素按插入顺序进行处理。
   - **操作**：
     - **offer**：将元素插入队列尾部。
     - **poll**：从队列头部移除并返回元素。
     - **peek**：查看队列头部元素，但不移除。
   - **适用场景**：常用于需要按照顺序处理元素的情况，如任务队列、消息队列等。
2. **Deque**（双端队列）：
   - **特点**：支持在队列两端（头部和尾部）进行插入和删除操作，既能作为栈（LIFO）也能作为队列（FIFO）使用。
   - **操作**：
     - **addFirst**、**offerFirst**：将元素插入到队列的头部。
     - **addLast**、**offerLast**：将元素插入到队列的尾部。
     - **removeFirst**、**pollFirst**：从队列头部移除元素。
     - **removeLast**、**pollLast**：从队列尾部移除元素。
     - **getFirst**、**peekFirst**：查看队列头部元素。
     - **getLast**、**peekLast**：查看队列尾部元素。
   - **适用场景**：适用于需要双端操作的情况，如任务调度、缓存管理等。

## 二、扩展回答（可展开细讲）

1. **Queue 和 Deque 的区别**：
   - **Queue**：只能从队列头部移除元素，队列尾部添加元素，始终遵循 FIFO 顺序。
   - **Deque**：双端队列，允许从两端进行插入和删除，支持更多灵活的操作。
   - **灵活性**：Deque 提供更多功能，Queue 只支持队列操作，Deque 既支持队列也支持栈操作。
2. **线程安全**：
   - `Queue` 和 `Deque` 可能有不同的线程安全实现，如 **ConcurrentLinkedQueue**（线程安全的 Queue），但一般来说它们都不是线程安全的，除非使用明确线程安全的类。
3. **接口与实现**：
   - **Queue** 和 **Deque** 都是接口，`Queue` 只支持单端操作，而 `Deque` 支持双端操作。

## 三、常见实现类

1. **Queue** 的常见实现类：
   - **LinkedList**：支持所有队列操作，既能作为队列也能作为双端队列使用。
   - **PriorityQueue**：实现了队列接口，元素根据优先级进行排序，不遵循 FIFO。
   - **ArrayBlockingQueue**：线程安全的队列，常用于线程池、消息队列等。
   - **ConcurrentLinkedQueue**：线程安全的队列，采用无阻塞算法。
2. **Deque** 的常见实现类：
   - **LinkedList**：实现了 `Deque` 接口，支持双端插入和删除操作。
   - **ArrayDeque**：基于数组实现的双端队列，性能上通常优于 `LinkedList`，但不能使用 `null` 元素。
   - **ConcurrentLinkedDeque**：线程安全的双端队列实现，适用于并发场景。

## 四、常见追问

1. **Queue 和 Deque 能否替换？**
   - `Deque` 是 `Queue` 的超集，若只需要队列操作，可以选择 `Queue`，但如果需要双端操作，可以选择 `Deque`。
2. **LinkedList 和 ArrayDeque 的区别？**
   - `LinkedList` 支持双端队列和队列操作，但由于是链表实现，性能上会有额外的开销（如指针分配）。`ArrayDeque` 基于数组实现，通常在大多数情况下更高效，但不能使用 `null` 元素。
3. **PriorityQueue 是队列吗？为什么是？**
   - 是的，`PriorityQueue` 实现了 `Queue` 接口，但它按元素的优先级排序，不遵循严格的 FIFO 原则。

------

✅ **一分钟口述版总结**：
 `Queue` 是单端操作的队列，遵循 FIFO 原则；而 `Deque` 是双端队列，可以在两端进行插入和删除操作，支持 FIFO 和 LIFO。`Queue` 常用实现有 `LinkedList`、`PriorityQueue` 等，`Deque` 常用实现有 `LinkedList`、`ArrayDeque`、`ConcurrentLinkedDeque` 等。

------

希望这个模板对你有所帮助！如果需要进一步扩展或调整，随时告诉我！