package serialization_obj_create_demo;

import java.io.*;

/**
 * 演示通过序列化和反序列化创建对象
 */
public class SerializationDemo {
    public static void main(String[] args) {
        String fileName = "user.ser";
        User originalUser = new User("张三", 25);
        System.out.println("原始对象: " + originalUser);

        // 1. 序列化：将对象写入文件
        try (ObjectOutputStream oos = new ObjectOutputStream(new FileOutputStream(fileName))) {
            oos.writeObject(originalUser);
            System.out.println("对象已序列化到文件 " + fileName);
        } catch (IOException e) {
            e.printStackTrace();
        }

        System.out.println("------------------------------------");

        // 2. 反序列化：从文件中读取并创建新对象
        try (ObjectInputStream ois = new ObjectInputStream(new FileInputStream(fileName))) {
            // 反序列化过程中，不会调用 User 类的构造函数
            User deserializedUser = (User) ois.readObject();
            System.out.println("反序列化完成，创建了新对象");
            System.out.println("反序列化后的对象: " + deserializedUser);
            
            // 验证是否是同一个对象
            System.out.println("originalUser == deserializedUser: " + (originalUser == deserializedUser));
        } catch (IOException | ClassNotFoundException e) {
            e.printStackTrace();
        } finally {
            // 清理测试产生的文件
            File file = new File(fileName);
            if (file.exists()) {
                file.delete();
            }
        }
    }
}

