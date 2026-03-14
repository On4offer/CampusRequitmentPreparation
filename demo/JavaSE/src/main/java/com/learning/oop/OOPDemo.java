package com.learning.oop;

/**
 * 面向对象编程示例
 * 演示类、对象、继承、多态、封装等概念
 */
public class OOPDemo {
    public static void main(String[] args) {
        // 创建对象
        Person person = new Person("张三", 25);
        Student student = new Student("李四", 20, "计算机科学", 85.5);
        Teacher teacher = new Teacher("王老师", 35, "Java编程", 8000);
        
        // 调用方法
        System.out.println("=== 人员信息 ===");
        person.displayInfo();
        System.out.println();
        student.displayInfo();
        System.out.println();
        teacher.displayInfo();
        
        // 多态演示
        System.out.println("\n=== 多态演示 ===");
        Person[] people = {person, student, teacher};
        for (Person p : people) {
            p.work(); // 多态调用
            System.out.println();
        }
        
        // 封装演示
        System.out.println("=== 封装演示 ===");
        person.setName("张三三");
        person.setAge(26);
        System.out.println("修改后的姓名: " + person.getName());
        System.out.println("修改后的年龄: " + person.getAge());
        
        // 静态方法演示
        System.out.println("\n=== 静态方法演示 ===");
        System.out.println("Person类的总人数: " + Person.getTotalCount());
        
        // 常量演示
        System.out.println("\n=== 常量演示 ===");
        System.out.println("Person类的版本号: " + Person.VERSION);

        // 报错：Person.VERSION = "2.0.0";
    }
}

/**
 * 父类：Person
 * 演示封装、构造方法、继承基础
 */
class Person {
    // 常量
    public static final String VERSION = "1.0.0";
    
    // 静态变量
    private static int totalCount = 0;
    
    // 成员变量（封装）
    private String name;
    private int age;
    
    // 构造方法
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
        totalCount++;
    }
    
    // getter和setter方法（封装）
    public String getName() {
        return name;
    }
    
    public void setName(String name) {
        this.name = name;
    }
    
    public int getAge() {
        return age;
    }
    
    public void setAge(int age) {
        if (age >= 0 && age < 150) {
            this.age = age;
        } else {
            System.out.println("年龄输入无效！");
        }
    }
    
    // 普通方法
    public void displayInfo() {
        System.out.println("姓名: " + name);
        System.out.println("年龄: " + age);
    }
    
    // 可被子类重写的方法
    public void work() {
        System.out.println(name + " 在工作中...");
    }
    
    // 静态方法
    public static int getTotalCount() {
        return totalCount;
    }
}

/**
 * 子类：Student
 * 演示继承、方法重写
 */
class Student extends Person {
    private String major; // 专业
    private double score; // 成绩
    
    // 构造方法
    public Student(String name, int age, String major, double score) {
        super(name, age); // 调用父类构造方法
        this.major = major;
        this.score = score;
    }
    
    // 重写父类方法
    @Override
    public void displayInfo() {
        super.displayInfo(); // 调用父类方法
        System.out.println("专业: " + major);
        System.out.println("成绩: " + score);
    }
    
    // 重写父类方法
    @Override
    public void work() {
        System.out.println(getName() + " 正在学习 " + major + "，成绩为: " + score);
    }
}

/**
 * 子类：Teacher
 * 演示继承、方法重写
 */
class Teacher extends Person {
    private String subject; // 教授科目
    private double salary;  // 薪资
    
    // 构造方法
    public Teacher(String name, int age, String subject, double salary) {
        super(name, age); // 调用父类构造方法
        this.subject = subject;
        this.salary = salary;
    }
    
    // 重写父类方法
    @Override
    public void displayInfo() {
        super.displayInfo(); // 调用父类方法
        System.out.println("教授科目: " + subject);
        System.out.println("薪资: " + salary);
    }
    
    // 重写父类方法
    @Override
    public void work() {
        System.out.println(getName() + " 正在教授 " + subject + "，月薪: " + salary);
    }
}