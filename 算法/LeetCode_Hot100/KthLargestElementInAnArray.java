import java.util.PriorityQueue;
import java.util.Random;

/**
 * LeetCode Hot100 - 215. Kth Largest Element in an Array (数组中的第K个最大元素)
 * 难度：中等
 * 题目描述：给定整数数组 nums 和整数 k，请返回数组中第 k 个最大的元素。
 * 请注意，你需要找的是数组排序后的第 k 个最大的元素，而不是第 k 个不同的元素。
 */
public class KthLargestElementInAnArray {
    
    /**
     * 方法一：优先队列（最小堆）
     * 时间复杂度：O(n log k)
     * 空间复杂度：O(k)
     */
    public int findKthLargestUsingHeap(int[] nums, int k) {
        // 创建一个最小堆，大小为k
        PriorityQueue<Integer> minHeap = new PriorityQueue<>(k);
        
        for (int num : nums) {
            // 先将元素加入堆中
            minHeap.offer(num);
            // 如果堆的大小超过k，弹出最小的元素
            if (minHeap.size() > k) {
                minHeap.poll();
            }
        }
        
        // 堆顶元素就是第k个最大的元素
        return minHeap.peek();
    }
    
    /**
     * 方法二：快速选择算法
     * 时间复杂度：平均O(n)，最坏O(n^2)
     * 空间复杂度：O(log n)
     */
    private Random random = new Random();
    
    public int findKthLargest(int[] nums, int k) {
        // 第k个最大的元素，等价于排序后数组中索引为 nums.length - k 的元素
        int targetIndex = nums.length - k;
        return quickSelect(nums, 0, nums.length - 1, targetIndex);
    }
    
    private int quickSelect(int[] nums, int left, int right, int targetIndex) {
        if (left == right) {
            return nums[left];
        }
        
        // 随机选择 pivot
        int pivotIndex = left + random.nextInt(right - left + 1);
        pivotIndex = partition(nums, left, right, pivotIndex);
        
        if (pivotIndex == targetIndex) {
            return nums[pivotIndex];
        } else if (pivotIndex < targetIndex) {
            return quickSelect(nums, pivotIndex + 1, right, targetIndex);
        } else {
            return quickSelect(nums, left, pivotIndex - 1, targetIndex);
        }
    }
    
    private int partition(int[] nums, int left, int right, int pivotIndex) {
        int pivotValue = nums[pivotIndex];
        // 将pivot移到数组末尾
        swap(nums, pivotIndex, right);
        
        int storeIndex = left;
        for (int i = left; i < right; i++) {
            if (nums[i] < pivotValue) {
                swap(nums, storeIndex, i);
                storeIndex++;
            }
        }
        
        // 将pivot移回正确位置
        swap(nums, storeIndex, right);
        return storeIndex;
    }
    
    private void swap(int[] nums, int i, int j) {
        int temp = nums[i];
        nums[i] = nums[j];
        nums[j] = temp;
    }
    
    public static void main(String[] args) {
        KthLargestElementInAnArray solution = new KthLargestElementInAnArray();
        
        // 测试用例1
        int[] nums1 = {3, 2, 1, 5, 6, 4};
        int k1 = 2;
        System.out.println("测试用例1结果(堆方法): " + solution.findKthLargestUsingHeap(nums1, k1)); // 输出: 5
        System.out.println("测试用例1结果(快速选择): " + solution.findKthLargest(nums1, k1)); // 输出: 5
        
        // 测试用例2
        int[] nums2 = {3, 2, 3, 1, 2, 4, 5, 5, 6};
        int k2 = 4;
        System.out.println("测试用例2结果(堆方法): " + solution.findKthLargestUsingHeap(nums2, k2)); // 输出: 4
        System.out.println("测试用例2结果(快速选择): " + solution.findKthLargest(nums2, k2)); // 输出: 4
    }
}