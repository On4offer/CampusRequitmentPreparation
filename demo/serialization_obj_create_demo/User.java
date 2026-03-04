package serialization_obj_create_demo;

import java.io.Serializable;

/**
 * 实现 Serializable 接口的类，才能被序列化
 */
public class User implements Serializable {
    private static final long serialVersionUID = 1L;
    
    private String name;
    private int age;

    public User(String name, int age) {
        System.out.println("调用了构造函数: User(String name, int age)");
        this.name = name;
        this.age = age;
    }

    public String getName() {
        return name;
    }

    public int getAge() {
        return age;
    }

    @Override
    public String toString() {
        return "User{name='" + name + "', age=" + age + "}";
    }
}

