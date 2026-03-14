package com.learning.exceptionio;

import java.io.*;
import java.nio.file.*;
import java.util.Scanner;

/**
 * 异常机制与IO操作示例
 * 演示Java中的异常处理和文件操作
 */
public class ExceptionIODemo {
    public static void main(String[] args) {
        // 1. 异常处理示例
        System.out.println("=== 1. 异常处理示例 ===");
        
        // try-catch基本用法
        try {
            int result = divide(10, 0);
            System.out.println("结果: " + result);
        } catch (ArithmeticException e) {
            System.out.println("捕获到算术异常: " + e.getMessage());
        } finally {
            System.out.println("finally块执行 - 无论是否发生异常都会执行");
        }
        
        // 多重catch块
        try {
            String[] array = {"a", "b", "c"};
            System.out.println(array[5]); // 数组越界异常
        } catch (ArrayIndexOutOfBoundsException e) {
            System.out.println("数组索引越界: " + e.getMessage());
        } catch (Exception e) {
            System.out.println("捕获到其他异常: " + e.getMessage());
        }
        
        // 自定义异常
        try {
            checkAge(-5);
        } catch (InvalidAgeException e) {
            System.out.println("捕获到自定义异常: " + e.getMessage());
        }
        
        // throws关键字
        try {
            methodWithThrows(0);
        } catch (IOException e) {
            System.out.println("捕获到throws声明的异常: " + e.getMessage());
        }
        
        // 2. IO操作示例
        System.out.println("\n=== 2. IO操作示例 ===");
        
        // 2.1 文件操作 - 使用File类
        System.out.println("\n--- 2.1 File类操作 ---");
        try {
            File file = new File("test.txt");
            System.out.println("文件是否存在: " + file.exists());
            
            if (file.createNewFile()) {
                System.out.println("文件创建成功");
            } else {
                System.out.println("文件已存在");
            }
            
            System.out.println("文件路径: " + file.getAbsolutePath());
            System.out.println("文件大小: " + file.length() + " 字节");
            
        } catch (IOException e) {
            System.out.println("文件操作异常: " + e.getMessage());
        }
        
        // 2.2 字节流 - 文件读写
        System.out.println("\n--- 2.2 字节流操作 ---");
        // 写入文件
        try (FileOutputStream fos = new FileOutputStream("bytes_test.txt")) {
            String content = "Hello Byte Stream!";
            fos.write(content.getBytes());
            System.out.println("字节流写入成功");
        } catch (IOException e) {
            System.out.println("字节流写入异常: " + e.getMessage());
        }
        
        // 读取文件
        try (FileInputStream fis = new FileInputStream("bytes_test.txt")) {
            byte[] buffer = new byte[1024];
            int bytesRead = fis.read(buffer);
            String content = new String(buffer, 0, bytesRead);
            System.out.println("字节流读取内容: " + content);
        } catch (IOException e) {
            System.out.println("字节流读取异常: " + e.getMessage());
        }
        
        // 2.3 字符流 - 文件读写
        System.out.println("\n--- 2.3 字符流操作 ---");
        // 写入文件
        try (FileWriter writer = new FileWriter("chars_test.txt")) {
            String content = "你好，字符流！";
            writer.write(content);
            System.out.println("字符流写入成功");
        } catch (IOException e) {
            System.out.println("字符流写入异常: " + e.getMessage());
        }
        
        // 读取文件
        try (FileReader reader = new FileReader("chars_test.txt")) {
            char[] buffer = new char[1024];
            int charsRead = reader.read(buffer);
            String content = new String(buffer, 0, charsRead);
            System.out.println("字符流读取内容: " + content);
        } catch (IOException e) {
            System.out.println("字符流读取异常: " + e.getMessage());
        }
        
        // 2.4 缓冲流
        System.out.println("\n--- 2.4 缓冲流操作 ---");
        // 写入文件
        try (BufferedWriter bw = new BufferedWriter(new FileWriter("buffered_test.txt"))) {
            bw.write("第一行内容");
            bw.newLine();
            bw.write("第二行内容");
            System.out.println("缓冲流写入成功");
        } catch (IOException e) {
            System.out.println("缓冲流写入异常: " + e.getMessage());
        }
        
        // 读取文件
        try (BufferedReader br = new BufferedReader(new FileReader("buffered_test.txt"))) {
            String line;
            System.out.println("缓冲流读取内容:");
            while ((line = br.readLine()) != null) {
                System.out.println("- " + line);
            }
        } catch (IOException e) {
            System.out.println("缓冲流读取异常: " + e.getMessage());
        }
        
        // 2.5 Java NIO操作
        System.out.println("\n--- 2.5 Java NIO操作 ---");
        try {
            // 写入文件
            String content = "Hello Java NIO!";
            Path path = Paths.get("nio_test.txt");
            Files.write(path, content.getBytes());
            System.out.println("NIO写入成功");
            
            // 读取文件
            byte[] bytes = Files.readAllBytes(path);
            String readContent = new String(bytes);
            System.out.println("NIO读取内容: " + readContent);
            
            // 列出目录内容
            System.out.println("当前目录文件列表:");
            Files.list(Paths.get(".")).forEach(System.out::println);
            
        } catch (IOException e) {
            System.out.println("NIO操作异常: " + e.getMessage());
        }
        
        // 3. 扫描器读取输入
        System.out.println("\n=== 3. 扫描器读取输入 ===");
        System.out.println("(此示例需要交互输入，这里仅做演示)");
        System.out.println("使用Scanner scanner = new Scanner(System.in); 来读取用户输入");
    }
    
    // 演示异常抛出
    public static int divide(int a, int b) {
        if (b == 0) {
            throw new ArithmeticException("除数不能为零");
        }
        return a / b;
    }
    
    // 演示自定义异常
    public static void checkAge(int age) throws InvalidAgeException {
        if (age < 0 || age > 150) {
            throw new InvalidAgeException("年龄必须在0到150之间，当前值: " + age);
        }
        System.out.println("年龄有效: " + age);
    }
    
    // 演示throws关键字
    public static void methodWithThrows(int value) throws IOException {
        if (value == 0) {
            throw new IOException("值不能为零");
        }
        System.out.println("方法正常执行");
    }
}

// 自定义异常类
class InvalidAgeException extends Exception {
    public InvalidAgeException(String message) {
        super(message);
    }
}