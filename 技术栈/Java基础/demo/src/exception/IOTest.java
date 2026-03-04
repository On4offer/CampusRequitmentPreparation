package exception;

import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import java.util.zip.*;

/**
 * IO操作示例
 * 包含文件读写、字节流、字符流、缓冲流、NIO等
 */
public class IOTest {
    private static final String TEST_DIR = "io_test_dir";
    private static final String TEST_FILE = TEST_DIR + "/test.txt";
    private static final String COPY_FILE = TEST_DIR + "/copy.txt";
    private static final String BINARY_FILE = TEST_DIR + "/data.bin";
    private static final String ZIP_FILE = TEST_DIR + "/archive.zip";
    
    public static void main(String[] args) {
        System.out.println("===== Java IO操作示例 =====\n");
        
        try {
            // 创建测试目录
            createTestDirectory();
            
            // 1. 字符流文件操作
            System.out.println("1. 字符流文件操作：");
            writeFileWithCharacterStream();
            readFileWithCharacterStream();
            System.out.println();
            
            // 2. 字节流文件操作
            System.out.println("2. 字节流文件操作：");
            writeBinaryFile();
            readBinaryFile();
            copyFileWithByteStream();
            System.out.println();
            
            // 3. 缓冲流操作
            System.out.println("3. 缓冲流操作：");
            writeFileWithBufferedStream();
            readFileWithBufferedStream();
            System.out.println();
            
            // 4. Java NIO操作
            System.out.println("4. Java NIO操作：");
            nioFileOperations();
            nioPathOperations();
            System.out.println();
            
            // 5. 对象序列化与反序列化
            System.out.println("5. 对象序列化与反序列化：");
            serializeObject();
            deserializeObject();
            System.out.println();
            
            // 6. ZIP压缩操作
            System.out.println("6. ZIP压缩操作：");
            createZipFile();
            extractZipFile();
            System.out.println();
            
            // 7. 文件系统操作
            System.out.println("7. 文件系统操作：");
            fileSystemOperations();
            System.out.println();
            
            // 8. 控制台输入输出
            System.out.println("8. 控制台输入输出：");
            consoleIO();
            
        } catch (Exception e) {
            e.printStackTrace();
        } finally {
            // 清理测试文件（可选）
            // cleanupTestDirectory();
        }
    }
    
    // 创建测试目录
    private static void createTestDirectory() {
        File dir = new File(TEST_DIR);
        if (!dir.exists()) {
            dir.mkdir();
            System.out.println("创建测试目录: " + TEST_DIR);
        }
    }
    
    // 字符流写文件
    private static void writeFileWithCharacterStream() throws IOException {
        // 使用try-with-resources自动关闭资源
        try (FileWriter writer = new FileWriter(TEST_FILE);
             BufferedWriter bw = new BufferedWriter(writer)) {
            
            bw.write("这是第一行文本\n");
            bw.write("这是第二行文本\n");
            bw.write("这是第三行文本");
            
            System.out.println("字符流写入文件成功: " + TEST_FILE);
        }
    }
    
    // 字符流读文件
    private static void readFileWithCharacterStream() throws IOException {
        try (FileReader reader = new FileReader(TEST_FILE);
             BufferedReader br = new BufferedReader(reader)) {
            
            String line;
            System.out.println("文件内容：");
            while ((line = br.readLine()) != null) {
                System.out.println(line);
            }
        }
    }
    
    // 字节流写二进制文件
    private static void writeBinaryFile() throws IOException {
        try (FileOutputStream fos = new FileOutputStream(BINARY_FILE);
             DataOutputStream dos = new DataOutputStream(fos)) {
            
            dos.writeInt(100);
            dos.writeDouble(3.14159);
            dos.writeBoolean(true);
            dos.writeUTF("Hello Binary Data");
            
            System.out.println("二进制文件写入成功: " + BINARY_FILE);
        }
    }
    
    // 字节流读二进制文件
    private static void readBinaryFile() throws IOException {
        try (FileInputStream fis = new FileInputStream(BINARY_FILE);
             DataInputStream dis = new DataInputStream(fis)) {
            
            int intValue = dis.readInt();
            double doubleValue = dis.readDouble();
            boolean booleanValue = dis.readBoolean();
            String stringValue = dis.readUTF();
            
            System.out.println("二进制文件内容：");
            System.out.println("整数: " + intValue);
            System.out.println("浮点数: " + doubleValue);
            System.out.println("布尔值: " + booleanValue);
            System.out.println("字符串: " + stringValue);
        }
    }
    
    // 字节流复制文件
    private static void copyFileWithByteStream() throws IOException {
        try (FileInputStream fis = new FileInputStream(TEST_FILE);
             FileOutputStream fos = new FileOutputStream(COPY_FILE)) {
            
            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                fos.write(buffer, 0, bytesRead);
            }
            
            System.out.println("文件复制成功: " + TEST_FILE + " -> " + COPY_FILE);
        }
    }
    
    // 缓冲流写文件
    private static void writeFileWithBufferedStream() throws IOException {
        String largeTextFile = TEST_DIR + "/large_text.txt";
        try (BufferedWriter bw = new BufferedWriter(new FileWriter(largeTextFile))) {
            
            for (int i = 1; i \u003c= 100; i++) {
                bw.write("这是第" + i + "行数据，用于测试缓冲流的性能。\n");
            }
            
            System.out.println("缓冲流写入大文件成功: " + largeTextFile);
        }
    }
    
    // 缓冲流读文件
    private static void readFileWithBufferedStream() throws IOException {
        String largeTextFile = TEST_DIR + "/large_text.txt";
        try (BufferedReader br = new BufferedReader(new FileReader(largeTextFile))) {
            
            String line;
            int lineCount = 0;
            while ((line = br.readLine()) != null) {
                lineCount++;
            }
            
            System.out.println("大文件读取完成，共" + lineCount + "行");
        }
    }
    
    // Java NIO文件操作
    private static void nioFileOperations() throws IOException {
        // 写文件
        String nioFile = TEST_DIR + "/nio_test.txt";
        byte[] data = "Java NIO 文件操作示例".getBytes();
        Path path = Paths.get(nioFile);
        Files.write(path, data);
        System.out.println("NIO写入文件成功: " + nioFile);
        
        // 读文件
        byte[] readData = Files.readAllBytes(path);
        System.out.println("NIO读取文件内容: " + new String(readData));
        
        // 按行读取
        List\u003cString\u003e lines = Files.readAllLines(path);
        System.out.println("NIO按行读取 - 行数: " + lines.size());
    }
    
    // Java NIO Path操作
    private static void nioPathOperations() throws IOException {
        Path path = Paths.get(TEST_FILE);
        
        System.out.println("文件名称: " + path.getFileName());
        System.out.println("父路径: " + path.getParent());
        System.out.println("绝对路径: " + path.toAbsolutePath());
        System.out.println("文件是否存在: " + Files.exists(path));
        System.out.println("是否为文件: " + Files.isRegularFile(path));
        System.out.println("文件大小: " + Files.size(path) + " 字节");
        
        // 创建临时文件
        Path tempFile = Files.createTempFile("temp-", ".txt");
        System.out.println("创建临时文件: " + tempFile);
        Files.deleteIfExists(tempFile); // 删除临时文件
    }
    
    // 对象序列化
    private static void serializeObject() throws IOException {
        String objectFile = TEST_DIR + "/person.ser";
        Person person = new Person("张三", 30, "zhangsan@example.com");
        
        try (FileOutputStream fos = new FileOutputStream(objectFile);
             ObjectOutputStream oos = new ObjectOutputStream(fos)) {
            
            oos.writeObject(person);
            System.out.println("对象序列化成功: " + person + " -> " + objectFile);
        }
    }
    
    // 对象反序列化
    private static void deserializeObject() throws IOException, ClassNotFoundException {
        String objectFile = TEST_DIR + "/person.ser";
        
        try (FileInputStream fis = new FileInputStream(objectFile);
             ObjectInputStream ois = new ObjectInputStream(fis)) {
            
            Person person = (Person) ois.readObject();
            System.out.println("对象反序列化成功: " + person);
        }
    }
    
    // 创建ZIP文件
    private static void createZipFile() throws IOException {
        try (FileOutputStream fos = new FileOutputStream(ZIP_FILE);
             ZipOutputStream zos = new ZipOutputStream(fos);
             FileInputStream fis = new FileInputStream(TEST_FILE)) {
            
            ZipEntry entry = new ZipEntry("test.txt");
            zos.putNextEntry(entry);
            
            byte[] buffer = new byte[1024];
            int bytesRead;
            while ((bytesRead = fis.read(buffer)) != -1) {
                zos.write(buffer, 0, bytesRead);
            }
            
            zos.closeEntry();
            System.out.println("ZIP文件创建成功: " + ZIP_FILE);
        }
    }
    
    // 解压ZIP文件
    private static void extractZipFile() throws IOException {
        String extractDir = TEST_DIR + "/extracted";
        new File(extractDir).mkdir();
        
        try (ZipInputStream zis = new ZipInputStream(new FileInputStream(ZIP_FILE))) {
            ZipEntry entry;
            while ((entry = zis.getNextEntry()) != null) {
                String filePath = extractDir + "/" + entry.getName();
                try (FileOutputStream fos = new FileOutputStream(filePath)) {
                    byte[] buffer = new byte[1024];
                    int bytesRead;
                    while ((bytesRead = zis.read(buffer)) != -1) {
                        fos.write(buffer, 0, bytesRead);
                    }
                }
                zis.closeEntry();
                System.out.println("解压文件: " + entry.getName() + " 到 " + extractDir);
            }
        }
    }
    
    // 文件系统操作
    private static void fileSystemOperations() throws IOException {
        // 列出目录内容
        File dir = new File(TEST_DIR);
        File[] files = dir.listFiles();
        if (files != null) {
            System.out.println("目录 " + TEST_DIR + " 中的文件和文件夹：");
            for (File file : files) {
                String type = file.isDirectory() ? "[目录]" : "[文件]";
                System.out.println(type + " " + file.getName() + ", 大小: " + file.length() + " 字节");
            }
        }
        
        // 文件重命名
        String oldName = TEST_DIR + "/rename_test.txt";
        String newName = TEST_DIR + "/renamed_test.txt";
        
        try (FileWriter writer = new FileWriter(oldName)) {
            writer.write("用于重命名测试的文件");
        }
        
        File oldFile = new File(oldName);
        File newFile = new File(newName);
        if (oldFile.renameTo(newFile)) {
            System.out.println("文件重命名成功: " + oldName + " -> " + newName);
        }
        
        // 删除文件
        if (newFile.delete()) {
            System.out.println("文件删除成功: " + newName);
        }
    }
    
    // 控制台输入输出
    private static void consoleIO() {
        System.out.println("\n控制台输入演示（请输入一些文本，输入'exit'退出）：");
        try (Scanner scanner = new Scanner(System.in)) {
            while (true) {
                System.out.print("请输入: ");
                String input = scanner.nextLine();
                if (input.equalsIgnoreCase("exit")) {
                    break;
                }
                System.out.println("你输入的是: " + input);
            }
        }
        System.out.println("控制台输入演示结束");
    }
    
    // 清理测试目录
    private static void cleanupTestDirectory() {
        File dir = new File(TEST_DIR);
        if (dir.exists()) {
            deleteDirectory(dir);
            System.out.println("清理测试目录: " + TEST_DIR);
        }
    }
    
    // 递归删除目录
    private static void deleteDirectory(File directory) {
        File[] files = directory.listFiles();
        if (files != null) {
            for (File file : files) {
                if (file.isDirectory()) {
                    deleteDirectory(file);
                } else {
                    file.delete();
                }
            }
        }
        directory.delete();
    }
}

// 可序列化的Person类
class Person implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String name;
    private int age;
    private String email;
    
    public Person(String name, int age, String email) {
        this.name = name;
        this.age = age;
        this.email = email;
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + ", email='" + email + "'}";
    }
}