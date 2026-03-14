package syntax;

/**
 * Java基础语法示例
 * 包含变量、数据类型、运算符、控制语句等基础知识点
 */
public class BasicSyntax {
    public static void main(String[] args) {
        // 变量和数据类型
        int num1 = 10;
        long num2 = 1000000000L;
        double num3 = 3.14159;
        boolean flag = true;
        char ch = 'A';
        String str = "Hello Java";
        
        System.out.println("基本数据类型示例：");
        System.out.println("整数: " + num1);
        System.out.println("长整数: " + num2);
        System.out.println("浮点数: " + num3);
        System.out.println("布尔值: " + flag);
        System.out.println("字符: " + ch);
        System.out.println("字符串: " + str);
        
        // 运算符
        System.out.println("\n运算符示例：");
        int a = 10, b = 3;
        System.out.println("加法: " + (a + b));
        System.out.println("减法: " + (a - b));
        System.out.println("乘法: " + (a * b));
        System.out.println("除法: " + (a / b));
        System.out.println("取余: " + (a % b));
        System.out.println("自增: " + (++a));
        System.out.println("自减: " + (--b));
        
        // 控制语句 - if-else
        System.out.println("\n控制语句 - if-else：");
        int score = 85;
        if (score >= 90) {
            System.out.println("优秀");
        } else if (score >= 80) {
            System.out.println("良好");
        } else if (score >= 60) {
            System.out.println("及格");
        } else {
            System.out.println("不及格");
        }
        
        // 控制语句 - switch
        System.out.println("\n控制语句 - switch：");
        int month = 3;
        String season;
        switch (month) {
            case 12: case 1: case 2:
                season = "冬季";
                break;
            case 3: case 4: case 5:
                season = "春季";
                break;
            case 6: case 7: case 8:
                season = "夏季";
                break;
            case 9: case 10: case 11:
                season = "秋季";
                break;
            default:
                season = "月份错误";
        }
        System.out.println(month + "月是" + season);
        
        // 控制语句 - for循环
        System.out.println("\n控制语句 - for循环：");
        for (int i = 1; i <= 5; i++) {
            System.out.print(i + " ");
        }
        System.out.println();
        
        // 控制语句 - while循环
        System.out.println("\n控制语句 - while循环：");
        int j = 1;
        while (j <= 5) {
            System.out.print(j + " ");
            j++;
        }
        System.out.println();
        
        // 数组
        System.out.println("\n数组示例：");
        int[] arr = {1, 2, 3, 4, 5};
        for (int k = 0; k < arr.length; k++) {
            System.out.print(arr[k] + " ");
        }
        System.out.println();
        
        // 增强for循环
        System.out.println("\n增强for循环：");
        for (int value : arr) {
            System.out.print(value + " ");
        }
        System.out.println();
    }
}