### [121. 买卖股票的最佳时机](https://leetcode.cn/problems/best-time-to-buy-and-sell-stock/)

给定一个数组 `prices` ，它的第 `i` 个元素 `prices[i]` 表示一支给定股票第 `i` 天的价格。

你只能选择 **某一天** 买入这只股票，并选择在 **未来的某一个不同的日子** 卖出该股票。设计一个算法来计算你所能获取的最大利润。

返回你可以从这笔交易中获取的最大利润。如果你不能获取任何利润，返回 `0` 。

**示例 1：**

```
输入：[7,1,5,3,6,4]
输出：5
解释：在第 2 天（股票价格 = 1）的时候买入，在第 5 天（股票价格 = 6）的时候卖出，最大利润 = 6-1 = 5 。
注意利润不能是 7-1 = 6, 因为卖出价格需要大于买入价格；同时，你不能在买入前卖出股票。
```

**示例 2：**

```
输入：prices = [7,6,4,3,1]
输出：0
解释：在这种情况下, 没有交易完成, 所以最大利润为 0。
```

leetcode模式：

```java
class Solution {
    /*
     * 解题思路：贪心算法（一次遍历法）
     * 1. 题目要求：只能买卖一次，先买后卖，求最大利润，无利润返回0
     * 2. 核心思想：
     *    - 遍历过程中始终记录【历史最低价格】作为最佳买入价
     *    - 每一天计算：当天价格 - 历史最低价 = 当天卖出可获得的利润
     *    - 不断更新最大利润，最终得到全局最优解
     * 3. 复杂度：时间 O(n)，空间 O(1)
     */
    public int maxProfit(int[] prices) {
        // 边界处理：无法完成交易，直接返回0
        if(prices == null || prices.length < 2) return 0;
        
        // 记录遍历到当前位置的【最低买入价格】
        int minPrice = prices[0];
        // 记录遍历到当前位置的【最大利润】
        int maxProfit = 0;

        // 从第二天开始遍历
        for(int i = 1; i < prices.length; i++){
            // 贪心选择1：更新最低价格（保证买入价最便宜）
            if(prices[i] < minPrice){
                minPrice = prices[i];
            }
            // 贪心选择2：计算当前卖出利润，更新最大利润（保证利润最大）
            else{
                maxProfit = Math.max(maxProfit, prices[i] - minPrice);
            }
        }
        return maxProfit;
    }
}
```

ACM模式：

```java
import java.util.Scanner;

public class Main {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // 1. 读取输入：第一行是数组长度，第二行是价格数组
        int n = sc.nextInt();
        int[] prices = new int[n];
        for (int i = 0; i < n; i++) {
            prices[i] = sc.nextInt();
        }
        
        // 2. 调用算法计算最大利润
        int result = maxProfit(prices);
        
        // 3. 输出结果
        System.out.println(result);
    }

    // 核心算法（和你 LeetCode 代码一致）
    public static int maxProfit(int[] prices) {
        if (prices == null || prices.length < 2) {
            return 0;
        }
        int minPrice = prices[0];
        int maxProfit = 0;
        
        for (int i = 1; i < prices.length; i++) {
            // 更新最低买入价
            if (prices[i] < minPrice) {
                minPrice = prices[i];
            } 
            // 计算利润并更新最大值
            else {
                int currentProfit = prices[i] - minPrice;
                if (currentProfit > maxProfit) {
                    maxProfit = currentProfit;
                }
            }
        }
        return maxProfit;
    }
}
```

### [3. 无重复字符的最长子串](https://leetcode.cn/problems/longest-substring-without-repeating-characters/)

给定一个字符串 `s` ，请你找出其中不含有重复字符的 **最长 子串** 的长度。

**示例 1:**

```
输入: s = "abcabcbb"
输出: 3 
解释: 因为无重复字符的最长子串是 "abc"，所以其长度为 3。注意 "bca" 和 "cab" 也是正确答案。
```

**示例 2:**

```
输入: s = "bbbbb"
输出: 1
解释: 因为无重复字符的最长子串是 "b"，所以其长度为 1。
```

**示例 3:**

```
输入: s = "pwwkew"
输出: 3
解释: 因为无重复字符的最长子串是 "wke"，所以其长度为 3。
     请注意，你的答案必须是 子串 的长度，"pwke" 是一个子序列，不是子串。
```

leetcode模式：

```Java
import java.util.HashMap;
import java.util.Map;

class Solution {
    public int lengthOfLongestSubstring(String s) {
        // 哈希表：存储 字符 -> 字符最后一次出现的索引位置
        // 作用：快速查询当前字符是否重复，并且直接拿到重复位置
        Map<Character, Integer> charIndexMap = new HashMap<>();
        
        // 记录最长无重复子串的长度
        int maxLength = 0;
        // 滑动窗口左边界，代表当前无重复子串的起始位置
        int left = 0;

        // 右边界遍历整个字符串，不断扩大窗口
        for(int right = 0; right < s.length(); right++){
            // 获取当前右指针指向的字符
            char currentChar = s.charAt(right);
            
            // 如果当前字符已经出现过
            // 并且 上一次出现的位置 在当前窗口内（>= left）
            if(charIndexMap.containsKey(currentChar)){
                // 关键优化：
                // 左指针直接跳到 上一次重复位置的下一位
                // 用 Math.max 防止左指针往回退（保证窗口合法性）
                // charIndexMap.get(currentChar) 拿到的是这个字符历史上最后一次出现的位置，
                // 但这个位置可能早就不在当前窗口里了！
                // 按它的位置 + 1 来跳，会把 left 往回拉，导致窗口包含重复字符
                left = Math.max(left, charIndexMap.get(currentChar) + 1);
            }
            
            // 更新当前字符的最新索引（覆盖旧值，保证存的是最后一次出现的位置）
            charIndexMap.put(currentChar, right);
            
            // 计算当前窗口长度：right - left + 1
            // 并更新最大长度
            maxLength = Math.max(maxLength, right - left + 1);
        }
        
        // 返回结果
        return maxLength;
    }
}
```

ACM模式：

```java
import java.util.HashMap;
import java.util.Map;
import java.util.Scanner;

public class Main {  // ACM 必须用 public class Main

    // 核心算法（和你原来的一模一样）
    public static int lengthOfLongestSubstring(String s) {
        Map<Character, Integer> charIndexMap = new HashMap<>();
        int maxLength = 0;
        int left = 0;

        for (int right = 0; right < s.length(); right++) {
            char currentChar = s.charAt(right);
            if (charIndexMap.containsKey(currentChar)) {
                left = Math.max(left, charIndexMap.get(currentChar) + 1);
            }
            charIndexMap.put(currentChar, right);
            maxLength = Math.max(maxLength, right - left + 1);
        }
        return maxLength;
    }

    // 主函数：输入 → 运行 → 输出
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        String str = sc.next();  // 读取输入字符串
        int ans = lengthOfLongestSubstring(str);
        System.out.println(ans); // 输出答案
    }
}
```

### [146. LRU 缓存](https://leetcode.cn/problems/lru-cache/)

请你设计并实现一个满足 [LRU (最近最少使用) 缓存](https://baike.baidu.com/item/LRU) 约束的数据结构。

实现 `LRUCache` 类：

- `LRUCache(int capacity)` 以 **正整数** 作为容量 `capacity` 初始化 LRU 缓存
- `int get(int key)` 如果关键字 `key` 存在于缓存中，则返回关键字的值，否则返回 `-1` 。
- `void put(int key, int value)` 如果关键字 `key` 已经存在，则变更其数据值 `value` ；如果不存在，则向缓存中插入该组 `key-value` 。如果插入操作导致关键字数量超过 `capacity` ，则应该 **逐出** 最久未使用的关键字。

函数 `get` 和 `put` 必须以 `O(1)` 的平均时间复杂度运行。

**示例：**

```
输入
["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
输出
[null, null, null, 1, null, -1, null, -1, 3, 4]

解释
LRUCache lRUCache = new LRUCache(2);
lRUCache.put(1, 1); // 缓存是 {1=1}
lRUCache.put(2, 2); // 缓存是 {1=1, 2=2}
lRUCache.get(1);    // 返回 1
lRUCache.put(3, 3); // 该操作会使得关键字 2 作废，缓存是 {1=1, 3=3}
lRUCache.get(2);    // 返回 -1 (未找到)
lRUCache.put(4, 4); // 该操作会使得关键字 1 作废，缓存是 {4=4, 3=3}
lRUCache.get(1);    // 返回 -1 (未找到)
lRUCache.get(3);    // 返回 3
lRUCache.get(4);    // 返回 4
```

leetcode模式：

```java
class LRUCache {
    // 双向链表节点：存储key、value、前后指针
    static class DNode{
        int key, value;
        DNode prev, next;
        public DNode(int key, int value){
            this.key = key;
            this.value = value;
        }
    }

    // 缓存容量
    private final int capacity;
    // HashMap：key → 节点地址（引用），O(1) 定位节点
    private final Map<Integer, DNode> cacheMap;
    // 虚拟头、尾节点：避免空指针，简化链表操作
    private final DNode head, tail;

    // 构造函数：初始化容量、哈希表、双向链表
    public LRUCache(int capacity) {
        this.capacity = capacity;
        cacheMap = new HashMap<>();
        // 创建虚拟节点
        head = new DNode(-1,-1);        
        tail = new DNode(-1,-1);
        // 双向链表初始化：head <-> tail
        head.next = tail;
        tail.prev = head;
    }
    
    // 获取 key 对应 value
    public int get(int key) {
        DNode node = cacheMap.get(key);
        // 不存在返回 -1
        if(node == null) return -1;
        // 访问过 → 移到头部（标记为最近使用）
        moveToHead(node);
        return node.value;
    }
    
    // 插入/更新 key-value
    public void put(int key, int value) {
        DNode node = cacheMap.get(key);
        if(node == null){
            // key 不存在：新建节点
            DNode newNode = new DNode(key, value);
            // 存入哈希表
            cacheMap.put(key, newNode);
            // 加入链表头部
            addToHead(newNode);

            // 超过容量：删除最久未使用（尾部节点）
            if(cacheMap.size() > capacity){
                DNode removeNode = removeTail();
                // 同步删除哈希表
                cacheMap.remove(removeNode.key);
            }
        }else{
            // key 已存在：更新 value
            node.value = value;
            // 移到头部
            moveToHead(node);
        }
    }

    // 将节点移动到头部：先删除，再添加
    private void moveToHead(DNode node){
        removeNode(node);
        addToHead(node);
    }

    // 添加节点到头部（最近使用位置）
    private void addToHead(DNode node){
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    // 删除任意节点
    private void removeNode(DNode node){
        node.next.prev = node.prev;
        node.prev.next = node.next;
    }

    // 删除尾部节点（最久未使用）
    private DNode removeTail(){
        DNode res = tail.prev;
        removeNode(res);
        return res;
    }
}
```

ACM模式：

```java
import java.util.HashMap;
import java.util.Map;

// 完整可运行的 ACM 模式
public class LRUCacheACM {
    static class DNode {
        int key, value;
        DNode prev, next;
        public DNode(int key, int value) {
            this.key = key;
            this.value = value;
        }
    }

    private final int capacity;
    private final Map<Integer, DNode> cacheMap;
    private final DNode head, tail;

    public LRUCacheACM(int capacity) {
        this.capacity = capacity;
        cacheMap = new HashMap<>();
        head = new DNode(-1, -1);
        tail = new DNode(-1, -1);
        head.next = tail;
        tail.prev = head;
    }

    public int get(int key) {
        DNode node = cacheMap.get(key);
        if (node == null) return -1;
        moveToHead(node);
        return node.value;
    }

    public void put(int key, int value) {
        DNode node = cacheMap.get(key);
        if (node == null) {
            DNode newNode = new DNode(key, value);
            cacheMap.put(key, newNode);
            addToHead(newNode);
            if (cacheMap.size() > capacity) {
                DNode removeNode = removeTail();
                cacheMap.remove(removeNode.key);
            }
        } else {
            node.value = value;
            moveToHead(node);
        }
    }

    private void moveToHead(DNode node) {
        removeNode(node);
        addToHead(node);
    }

    private void addToHead(DNode node) {
        node.next = head.next;
        node.prev = head;
        head.next.prev = node;
        head.next = node;
    }

    private void removeNode(DNode node) {
        node.next.prev = node.prev;
        node.prev.next = node.next;
    }

    private DNode removeTail() {
        DNode res = tail.prev;
        removeNode(res);
        return res;
    }

    // 测试主函数
    public static void main(String[] args) {
        LRUCacheACM lru = new LRUCacheACM(2);
        lru.put(1, 1);
        lru.put(2, 2);
        System.out.println(lru.get(1)); // 输出 1
        lru.put(3, 3);
        System.out.println(lru.get(2)); // 输出 -1（被淘汰）
        lru.put(4, 4);
        System.out.println(lru.get(1)); // 输出 -1
        System.out.println(lru.get(3)); // 输出 3
        System.out.println(lru.get(4)); // 输出 4
    }
}
```

### [25. K 个一组翻转链表](https://leetcode.cn/problems/reverse-nodes-in-k-group/)

给你链表的头节点 `head` ，每 `k` 个节点一组进行翻转，请你返回修改后的链表。

`k` 是一个正整数，它的值小于或等于链表的长度。如果节点总数不是 `k` 的整数倍，那么请将最后剩余的节点保持原有顺序。

你不能只是单纯的改变节点内部的值，而是需要实际进行节点交换。

**示例 1：**

![img](https://assets.leetcode.com/uploads/2020/10/03/reverse_ex1.jpg)

```
输入：head = [1,2,3,4,5], k = 2
输出：[2,1,4,3,5]
```

**示例 2：**

![img](https://assets.leetcode.com/uploads/2020/10/03/reverse_ex2.jpg)

```
输入：head = [1,2,3,4,5], k = 3
输出：[3,2,1,4,5]
```

leetcode模式：

```Java
/**
 * Definition for singly-linked list.
 * public class ListNode {
 *     int val;
 *     ListNode next;
 *     ListNode() {}
 *     ListNode(int val) { this.val = val; }
 *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }
 * }
 */
class Solution {
    /**
     * K 个一组翻转链表主函数
     * 核心思路：
     * 1. 用虚拟头节点统一处理头部翻转逻辑，避免边界判断
     * 2. 循环找到每一组的起始节点和结束节点
     * 3. 切断链表，单独翻转当前组，再重新拼接回原链表
     * 4. 移动指针，处理下一组，直到剩余节点不足 K 个
     */
    public ListNode reverseKGroup(ListNode head, int k) {
        // 1. 创建虚拟头节点，指向原链表头，统一处理头节点翻转边界
        ListNode dummy = new ListNode(0, head);
        // prev 始终指向【当前要翻转组的前一个节点】，初始为虚拟头
        ListNode prev = dummy;

        // 无限循环，直到剩余节点不足 K 个退出
        while(true){
            // 2. 找到当前组的最后一个节点 end
            // 从 prev 出发，向后走 k 步，就是本组末尾
            ListNode end = prev;
            for(int i = 0; i < k && end != null; i++){
                end = end.next;
            }
            // 如果走到 null，说明剩余节点不足 k 个，终止循环
            if(end == null) break;

            // 3. 记录关键节点，准备翻转
            ListNode nextGroup = end.next;  // 保存下一组的头节点，用于后续拼接
            ListNode start = prev.next;      // 当前组的起始节点
            end.next = null;                 // 切断当前组与下一组的连接，方便单独翻转

            // 4. 翻转当前组，得到翻转后的新头节点
            ListNode nextHead = reverse(start);
            prev.next = nextHead;            // 前一组的尾节点 指向 翻转后的新头
            start.next = nextGroup;          // 原组头（翻转后变组尾）指向 下一组头，完成拼接

            // 5. prev 移动到【当前组的尾节点】，准备处理下一组
            prev = start;
        }
        // 返回虚拟头的下一个节点，即最终链表的头
        return dummy.next;
    }

    /**
     * 翻转整个单链表的辅助函数
     * 标准三指针翻转法
     */
    private ListNode reverse(ListNode head){
        ListNode prev = null;    // 前驱节点
        ListNode curr = head;    // 当前节点
        // 遍历链表，逐个改变指针方向
        while(curr != null){
            ListNode next = curr.next;  // 保存下一个节点
            curr.next = prev;           // 翻转当前节点指针
            prev = curr;                // 前驱指针后移
            curr = next;                // 当前指针后移
        }
        // 遍历结束，prev 就是翻转后的链表头
        return prev;
    }
}
```

ACM模式

```java
import java.util.Scanner;

// 链表节点定义
class ListNode {
    int val;
    ListNode next;
    ListNode() {}
    ListNode(int val) { this.val = val; }
    ListNode(int val, ListNode next) { this.val = val; this.next = next; }
}

public class Main {  // ACM 模式用 public class Main
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        
        // 1. 输入：读取数组长度 + 数组元素 + k
        int n = sc.nextInt();
        int[] nums = new int[n];
        for (int i = 0; i < n; i++) {
            nums[i] = sc.nextInt();
        }
        int k = sc.nextInt();
        
        // 2. 构建链表
        ListNode head = buildList(nums);
        
        // 3. K个一组翻转
        ListNode newHead = reverseKGroup(head, k);
        
        // 4. 输出结果链表
        printList(newHead);
    }

    // =============== 核心算法：K个一组翻转链表 ===============
    public static ListNode reverseKGroup(ListNode head, int k) {
        ListNode dummy = new ListNode(0, head);
        ListNode prev = dummy;

        while (true) {
            // 找到当前组的尾节点
            ListNode end = prev;
            for (int i = 0; i < k && end != null; i++) {
                end = end.next;
            }
            // 不足k个，退出
            if (end == null) break;

            // 记录关键节点
            ListNode nextGroup = end.next;
            ListNode start = prev.next;
            end.next = null;

            // 翻转 + 拼接
            ListNode reversedHead = reverse(start);
            prev.next = reversedHead;
            start.next = nextGroup;

            // 移动指针
            prev = start;
        }
        return dummy.next;
    }

    // 翻转单链表
    private static ListNode reverse(ListNode head) {
        ListNode prev = null;
        ListNode curr = head;
        while (curr != null) {
            ListNode next = curr.next;
            curr.next = prev;
            prev = curr;
            curr = next;
        }
        return prev;
    }

    // =============== 工具方法：构建链表 ===============
    private static ListNode buildList(int[] nums) {
        if (nums == null || nums.length == 0) return null;
        ListNode dummy = new ListNode();
        ListNode cur = dummy;
        for (int num : nums) {
            cur.next = new ListNode(num);
            cur = cur.next;
        }
        return dummy.next;
    }

    // =============== 工具方法：打印链表 ===============
    private static void printList(ListNode head) {
        while (head != null) {
            System.out.print(head.val + " ");
            head = head.next;
        }
    }
}
```

### [200. 岛屿数量](https://leetcode.cn/problems/number-of-islands/)

给你一个由 `'1'`（陆地）和 `'0'`（水）组成的的二维网格，请你计算网格中岛屿的数量。

岛屿总是被水包围，并且每座岛屿只能由水平方向和/或竖直方向上相邻的陆地连接形成。

此外，你可以假设该网格的四条边均被水包围。

**示例 1：**

```
输入：grid = [
  ['1','1','1','1','0'],
  ['1','1','0','1','0'],
  ['1','1','0','0','0'],
  ['0','0','0','0','0']
]
输出：1
```

**示例 2：**

```
输入：grid = [
  ['1','1','0','0','0'],
  ['1','1','0','0','0'],
  ['0','0','1','0','0'],
  ['0','0','0','1','1']
]
输出：3
```

leetcode代码：

```Java
/**
 * 岛屿数量问题：求解二维网格中岛屿的数量
 * 岛屿定义：由 '1'（陆地）组成，上下左右相邻，被 '0'（水）包围
 * 解题方法：深度优先搜索（DFS）
 */
class Solution {
    /**
     * 主方法：统计岛屿数量
     * @param grid 二维字符网格，仅包含'0'和'1'
     * @return 岛屿总数
     */
    public int numIslands(char[][] grid) {
        // 边界条件：网格为空 或 网格行数为0，直接返回0个岛屿
        if(grid == null || grid.length == 0) return 0;
        
        // 获取网格的 行数 和 列数
        int rows = grid.length;    // 行数
        int cols = grid[0].length; // 列数
        int count = 0;             // 岛屿数量计数器
        
        // 双层循环：遍历网格中每一个格子
        for(int i = 0; i < rows; i++){      // 遍历每一行
            for(int j = 0; j < cols; j++){ // 遍历每一列
                // 如果当前格子是陆地'1'，说明发现了一个新岛屿
                if(grid[i][j] == '1'){
                    count++; // 岛屿数量+1
                    // DFS：把当前岛屿所有相连的陆地都淹掉（标记为0），防止重复计数
                    dfs(grid, i, j, rows, cols);
                }
            }
        }
        // 遍历完成，返回最终岛屿数量
        return count;
    }

    /**
     * DFS递归方法：淹没当前岛屿所有相连的陆地
     * @param grid 原始网格
     * @param i 当前遍历的行坐标
     * @param j 当前遍历的列坐标
     * @param rows 网格总行数
     * @param cols 网格总列数
     */
    private void dfs(char[][] grid, int i, int j, int rows, int cols){
        // 递归终止条件（满足任意一个就返回）：
        // 1. 行坐标越界（<0 或 >=总行数）
        // 2. 列坐标越界（<0 或 >=总列数）
        // 3. 当前格子是水'0'
        if(i < 0 || i >= rows || j < 0 || j >= cols || grid[i][j] == '0'){
            return;
        }

        // 核心操作：将当前陆地'1'标记为水'0'（淹掉，避免重复访问）
        grid[i][j] = '0';

        // 递归搜索 上下左右 四个方向的相邻格子
        dfs(grid, i - 1, j, rows, cols); // 向上搜索
        dfs(grid, i + 1, j, rows, cols); // 向下搜索
        dfs(grid, i, j - 1, rows, cols); // 向左搜索
        dfs(grid, i, j + 1, rows, cols); // 向右搜索
    }
}
```

ACM模式：

```java
import java.util.Scanner;

/**
 * ACM模式 岛屿数量 DFS解法
 * 输入格式：
 * 第一行输入 行数 m 列数 n
 * 接下来 m 行，每行输入由0/1组成的字符串（代表网格）
 * 输出：岛屿数量
 */
public class Main {
    public static void main(String[] args) {
        // ACM模式标准输入
        Scanner sc = new Scanner(System.in);
        
        // 1. 输入网格行数和列数
        int m = sc.nextInt();
        int n = sc.nextInt();
        sc.nextLine(); // 吸收换行符
        
        // 2. 初始化网格
        char[][] grid = new char[m][n];
        for (int i = 0; i < m; i++) {
            // 读取一行字符串，转为字符数组
            String line = sc.nextLine().trim();
            grid[i] = line.toCharArray();
        }
        
        // 3. 计算岛屿数量并输出
        int result = numIslands(grid);
        System.out.println(result);
        
        sc.close();
    }

    /**
     * DFS计算岛屿数量（核心算法）
     */
    public static int numIslands(char[][] grid) {
        // 边界判断：网格为空直接返回0
        if (grid == null || grid.length == 0) {
            return 0;
        }

        int rows = grid.length;    // 行数
        int cols = grid[0].length; // 列数
        int count = 0;             // 岛屿计数器

        // 遍历整个网格
        for (int i = 0; i < rows; i++) {
            for (int j = 0; j < cols; j++) {
                // 遇到陆地，发现新岛屿
                if (grid[i][j] == '1') {
                    count++;
                    // DFS淹没整个岛屿
                    dfs(grid, i, j, rows, cols);
                }
            }
        }
        return count;
    }

    /**
     * DFS递归：将当前连通的陆地全部置为0
     */
    private static void dfs(char[][] grid, int i, int j, int rows, int cols) {
        // 越界 / 已为海水，直接返回
        if (i < 0 || i >= rows || j < 0 || j >= cols || grid[i][j] == '0') {
            return;
        }

        // 标记为海水（避免重复遍历）
        grid[i][j] = '0';

        // 上下左右四个方向递归
        dfs(grid, i - 1, j, rows, cols); // 上
        dfs(grid, i + 1, j, rows, cols); // 下
        dfs(grid, i, j - 1, rows, cols); // 左
        dfs(grid, i, j + 1, rows, cols); // 右
    }
}
```

