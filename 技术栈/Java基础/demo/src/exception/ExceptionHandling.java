package exception;

import java.io.*;
import java.util.*;

/**
 * 异常处理机制示例
 * 包含异常的捕获、抛出、自定义异常等
 */
public class ExceptionHandling {
    public static void main(String[] args) {
        System.out.println("===== Java异常处理机制示例 =====\n");
        
        // 1. 基本异常捕获示例
        System.out.println("1. 基本异常捕获示例：");
        try {
            int result = divide(10, 0);
            System.out.println("结果: " + result); // 这行不会执行
        } catch (ArithmeticException e) {
            System.out.println("捕获到算术异常: " + e.getMessage());
        } finally {
            System.out.println("无论是否发生异常，finally块都会执行");
        }
        System.out.println();
        
        // 2. 多个异常的捕获
        System.out.println("2. 多个异常的捕获：");
        try {
            String[] names = {"Java", "Python", "C++"};
            System.out.println("第三个元素: " + names[2]);
            System.out.println("第五个元素: " + names[4]); // 数组越界异常
            int num = Integer.parseInt("abc"); // 数字格式异常
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("数组下标越界: " + e.getMessage());
        } catch (NumberFormatException e) {
            System.out.println("数字格式错误: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("捕获到其他异常: " + e.getMessage());
        }
        System.out.println();
        
        // 3. 使用try-with-resources自动关闭资源
        System.out.println("3. 使用try-with-resources自动关闭资源：");
        try (Scanner scanner = new Scanner(System.in)) {
            System.out.print("请输入一个数字: ");
            int num = scanner.nextInt();
            System.out.println("您输入的数字是: " + num);
        } catch (InputMismatchException e) {
            System.out.println("输入类型错误，请输入整数！");
        }
        System.out.println();
        
        // 4. 抛出异常
        System.out.println("4. 抛出异常：");
        try {
            checkAge(-5);
        } catch (IllegalArgumentException e) {
            System.out.println("捕获到非法参数异常: " + e.getMessage());
        }
        System.out.println();
        
        // 5. 自定义异常
        System.out.println("5. 自定义异常：");
        try {
            withdrawMoney(1000, 500);
            System.out.println("取款成功！");
            
            withdrawMoney(200, 500); // 余额不足
        } catch (InsufficientFundsException e) {
            System.out.println("捕获到自定义异常: " + e.getMessage());
            System.out.println("缺少的金额: " + e.getAmount());
        }
        System.out.println();
        
        // 6. 异常链
        System.out.println("6. 异常链：");
        try {
            processFile();
        } catch (ApplicationException e) {
            System.out.println("应用异常: " + e.getMessage());
            System.out.println("根本原因: " + e.getCause().getMessage());
        }
        System.out.println();
        
        // 7. 异常处理最佳实践示例
        System.out.println("7. 异常处理最佳实践：");
        String filePath = "test.txt";
        String content = readFileContent(filePath);
        System.out.println("文件内容读取结果: " + content);
        System.out.println();
        
        // 8. finally块中可能出现的问题
        System.out.println("8. finally块中的return语句：");
        int value = testFinallyReturn();
        System.out.println("testFinallyReturn返回值: " + value); // 输出100而不是200
    }
    
    // 简单的除法方法，可能抛出算术异常
    public static int divide(int a, int b) {
        return a / b; // 当b为0时抛出ArithmeticException
    }
    
    // 检查年龄的方法，抛出IllegalArgumentException
    public static void checkAge(int age) {
        if (age < 0 || age > 150) {
            throw new IllegalArgumentException("年龄必须在0-150之间，当前值: " + age);
        }
        System.out.println("年龄有效: " + age);
    }
    
    // 取款方法，可能抛出自定义异常
    public static void withdrawMoney(double balance, double amount) throws InsufficientFundsException {
        if (amount <= 0) {
            throw new IllegalArgumentException("取款金额必须大于0");
        }
        if (amount > balance) {
            double shortage = amount - balance;
            throw new InsufficientFundsException("余额不足", shortage);
        }
        // 正常取款逻辑
    }
    
    // 文件处理方法，演示异常链
    public static void processFile() throws ApplicationException {
        try {
            FileInputStream fis = new FileInputStream("non_existent_file.txt");
            fis.read();
        } catch (FileNotFoundException e) {
            // 将检查异常包装为运行时异常
            throw new ApplicationException("处理文件时出错", e);
        } catch (IOException e) {
            throw new ApplicationException("读取文件时出错", e);
        }
    }
    
    // 演示异常处理最佳实践的文件读取方法
    public static String readFileContent(String filePath) {
        // 返回值初始化
        String content = "";
        
        // 使用try-with-resources确保资源关闭
        try (BufferedReader reader = new BufferedReader(new FileReader(filePath))) {
            StringBuilder sb = new StringBuilder();
            String line;
            while ((line = reader.readLine()) != null) {
                sb.append(line).append("\n");
            }
            content = sb.toString();
        } catch (FileNotFoundException e) {
            System.out.println("警告: 文件未找到 - " + filePath);
            // 返回默认值
        } catch (IOException e) {
            System.out.println("错误: 读取文件时发生IO异常 - " + e.getMessage());
            // 返回默认值
        } catch (Exception e) {
            System.out.println("错误: 发生未预期的异常 - " + e.getMessage());
            // 记录日志，返回默认值
        }
        
        return content;
    }
    
    // 演示finally块中的return问题
    public static int testFinallyReturn() {
        try {
            return 200;
        } catch (Exception e) {
            return 300;
        } finally {
            // finally块中的return会覆盖try或catch中的return值
            return 100;
        }
    }
}

// 自定义检查异常
class InsufficientFundsException extends Exception {
    private double amount; // 缺少的金额
    
    public InsufficientFundsException(String message, double amount) {
        super(message);
        this.amount = amount;
    }
    
    public double getAmount() {
        return amount;
    }
}

// 自定义运行时异常（包装异常）
class ApplicationException extends RuntimeException {
    public ApplicationException(String message) {
        super(message);
    }
    
    public ApplicationException(String message, Throwable cause) {
        super(message, cause);
    }
}

// 演示多重异常捕获和抑制异常
class ExceptionDemo {
    // try-with-resources中可能产生多个异常的示例
    public void readData() {
        try (CustomResource resource1 = new CustomResource("Resource1");
             CustomResource resource2 = new CustomResource("Resource2")) {
            resource1.use();
            throw new RuntimeException("主异常"); // 主异常
        } catch (Exception e) {
            System.out.println("捕获到的主异常: " + e.getMessage());
            // 获取抑制的异常
            Throwable[] suppressedExceptions = e.getSuppressed();
            System.out.println("抑制的异常数量: " + suppressedExceptions.length);
            for (Throwable suppressed : suppressedExceptions) {
                System.out.println("抑制的异常: " + suppressed.getMessage());
            }
        }
    }
    
    // 自定义资源类，实现AutoCloseable接口
    class CustomResource implements AutoCloseable {
        private String name;
        
        public CustomResource(String name) {
            this.name = name;
            System.out.println(name + " 被创建");
        }
        
        public void use() {
            System.out.println(name + " 被使用");
        }
        
        @Override
        public void close() throws Exception {
            System.out.println(name + " 被关闭");
            throw new RuntimeException(name + " 在关闭时发生异常");
        }
    }
}