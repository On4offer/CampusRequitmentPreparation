package com.learning.basic;

/**
 * Java语法基础示例
 * 演示变量、数据类型、运算符、控制流等基础语法
 */
public class SyntaxBasics {
    public static void main(String[] args) {
        // 1. 变量和数据类型
        System.out.println("=== 1. 变量和数据类型 ===");
        // 基本数据类型
        byte b = 121;          // 字节型，范围 -128 到 127
        short s = 32767;       // 短整型
        int i = 2147483647;    // 整型
        long l = 9223372036854775807L; // 长整型，需要在数字后加L
        float f = 3.14f;       // 浮点型，需要在数字后加f
        double d = 3.1415926;  // 双精度浮点型
        char c = 'A';          // 字符型
        boolean bool = true;   // 布尔型

        // 引用数据类型 - String
        String str = "Hello Java!";

        System.out.println("byte: " + b);
        System.out.println("short: " + s);
        System.out.println("int: " + i);
        System.out.println("long: " + l);
        System.out.println("float: " + f);
        System.out.println("double: " + d);
        System.out.println("char: " + c);
        System.out.println("boolean: " + bool);
        System.out.println("String: " + str);

        // 2. 运算符
        System.out.println("\n=== 2. 运算符 ===");
        int a = 10, b1 = 5;
        System.out.println("a + b = " + (a + b1));
        System.out.println("a - b = " + (a - b1));
        System.out.println("a * b = " + (a * b1));
        System.out.println("a / b = " + (a / b1));
        System.out.println("a % b = " + (a % b1));
        System.out.println("a++ = " + (a++));
        System.out.println("++a = " + (++a));

        // 3. 控制流 - if-else
        System.out.println("\n=== 3. 控制流 - if-else ===");
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

        // 4. 控制流 - switch
        System.out.println("\n=== 4. 控制流 - switch ===");
        char grade = 'A';
        switch (grade) {
            case 'A':
                System.out.println("优秀");
                break;
            case 'B':
                System.out.println("良好");
                break;
            case 'C':
                System.out.println("及格");
                break;
            default:
                System.out.println("不及格");
        }

        // 5. 控制流 - for循环
        System.out.println("\n=== 5. 控制流 - for循环 ===");
        for (int j = 0; j < 5; j++) {
            System.out.println("for循环: " + j);
        }

        // 6. 控制流 - 增强for循环
        System.out.println("\n=== 6. 控制流 - 增强for循环 ===");
        int[] numbers = {1, 2, 3, 4, 5};
        for (int num : numbers) {
            System.out.println("增强for循环: " + num);
        }

        // 7. 控制流 - while循环
        System.out.println("\n=== 7. 控制流 - while循环 ===");
        int k = 0;
        while (k < 5) {
            System.out.println("while循环: " + k);
            k++;
        }

        // 8. 控制流 - do-while循环
        System.out.println("\n=== 8. 控制流 - do-while循环 ===");
        int m = 0;
        do {
            System.out.println("do-while循环: " + m);
            m++;
        } while (m < 5);

        // 9. 数组
        System.out.println("\n=== 9. 数组 ===");
        int[] arr = new int[5];
        arr[0] = 10;
        arr[1] = 20;
        arr[2] = 30;
        arr[3] = 40;
        arr[4] = 50;
        
        System.out.print("数组元素: ");
        for (int n = 0; n < arr.length; n++) {
            System.out.print(arr[n] + " ");
        }
        System.out.println();

        // 10. 字符串操作
        System.out.println("\n=== 10. 字符串操作 ===");
        String str1 = "Hello";
        String str2 = "World";
        String str3 = str1 + " " + str2;  // 字符串拼接
        System.out.println("拼接结果: " + str3);
        System.out.println("长度: " + str3.length());
        System.out.println("包含'Java': " + str3.contains("Java"));
        System.out.println("转大写: " + str3.toUpperCase());
        System.out.println("转小写: " + str3.toLowerCase());
        System.out.println("截取: " + str3.substring(0, 5));
    }
}