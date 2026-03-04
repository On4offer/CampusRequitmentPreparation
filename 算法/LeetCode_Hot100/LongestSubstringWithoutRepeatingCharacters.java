import java.util.HashMap;
import java.util.Map;

/**
 * LeetCode Hot100 - 3. Longest Substring Without Repeating Characters (无重复字符的最长子串)
 * 难度：中等
 * 题目描述：给定一个字符串 s ，请你找出其中不含有重复字符的 最长子串 的长度。
 */
public class LongestSubstringWithoutRepeatingCharacters {
    
    /**
     * 方法：滑动窗口 + 哈希表
     * 时间复杂度：O(n)
     * 空间复杂度：O(min(m, n))，其中 m 是字符集的大小
     */
    public int lengthOfLongestSubstring(String s) {
        int n = s.length();
        if (n == 0) {
            return 0;
        }
        
        Map<Character, Integer> map = new HashMap<>();
        int maxLength = 0;
        int left = 0;
        
        for (int right = 0; right < n; right++) {
            char currentChar = s.charAt(right);
            
            // 如果字符已经存在于哈希表中，更新左指针
            if (map.containsKey(currentChar)) {
                left = Math.max(left, map.get(currentChar) + 1);
            }
            
            // 更新字符的位置
            map.put(currentChar, right);
            
            // 更新最大长度
            maxLength = Math.max(maxLength, right - left + 1);
        }
        
        return maxLength;
    }
    
    public static void main(String[] args) {
        LongestSubstringWithoutRepeatingCharacters solution = new LongestSubstringWithoutRepeatingCharacters();
        
        // 测试用例1
        String s1 = "abcabcbb";
        System.out.println("测试用例1结果: " + solution.lengthOfLongestSubstring(s1)); // 输出: 3
        
        // 测试用例2
        String s2 = "bbbbb";
        System.out.println("测试用例2结果: " + solution.lengthOfLongestSubstring(s2)); // 输出: 1
        
        // 测试用例3
        String s3 = "pwwkew";
        System.out.println("测试用例3结果: " + solution.lengthOfLongestSubstring(s3)); // 输出: 3
        
        // 测试用例4
        String s4 = "";
        System.out.println("测试用例4结果: " + solution.lengthOfLongestSubstring(s4)); // 输出: 0
        
        // 测试用例5
        String s5 = "abcdefg";
        System.out.println("测试用例5结果: " + solution.lengthOfLongestSubstring(s5)); // 输出: 7
    }
}