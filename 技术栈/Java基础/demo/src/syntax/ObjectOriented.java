package syntax;

/**
 * 面向对象编程示例
 * 包含类、对象、继承、多态、封装、抽象等概念
 */
public class ObjectOriented {
    public static void main(String[] args) {
        // 创建对象
        Person person = new Person("张三", 25);
        Student student = new Student("李四", 20, "计算机科学");
        Teacher teacher = new Teacher("王五", 35, "Java编程");
        
        // 调用方法
        System.out.println(person.getName() + "今年" + person.getAge() + "岁");
        System.out.println(student.getName() + "是" + student.getMajor() + "专业的学生");
        System.out.println(teacher.getName() + "教授" + teacher.getSubject());
        
        // 多态演示
        System.out.println("\n多态演示：");
        Person[] people = new Person[3];
        people[0] = person;
        people[1] = student;
        people[2] = teacher;
        
        for (Person p : people) {
            p.introduce();
        }
        
        // 接口实现
        System.out.println("\n接口实现：");
        Car car = new Car();
        Bicycle bicycle = new Bicycle();
        
        car.start();
        car.move(100);
        car.stop();
        
        bicycle.start();
        bicycle.move(20);
        bicycle.stop();
        
        // 静态方法和变量
        System.out.println("\n静态成员：");
        System.out.println("计数器：" + Counter.getCount());
        Counter.increment();
        Counter.increment();
        System.out.println("计数器：" + Counter.getCount());
    }
}

// 父类 - 封装示例
class Person {
    private String name;
    private int age;
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
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
        if (age > 0 && age < 150) {
            this.age = age;
        }
    }
    
    public void introduce() {
        System.out.println("我是" + name + "，今年" + age + "岁。");
    }
}

// 子类 - 继承示例
class Student extends Person {
    private String major;
    
    public Student(String name, int age, String major) {
        super(name, age);
        this.major = major;
    }
    
    public String getMajor() {
        return major;
    }
    
    public void setMajor(String major) {
        this.major = major;
    }
    
    @Override
    public void introduce() {
        System.out.println("我是" + getName() + "，今年" + getAge() + "岁，是" + major + "专业的学生。");
    }
}

// 子类 - 继承示例
class Teacher extends Person {
    private String subject;
    
    public Teacher(String name, int age, String subject) {
        super(name, age);
        this.subject = subject;
    }
    
    public String getSubject() {
        return subject;
    }
    
    public void setSubject(String subject) {
        this.subject = subject;
    }
    
    @Override
    public void introduce() {
        System.out.println("我是" + getName() + "，今年" + getAge() + "岁，教授" + subject + "课程。");
    }
}

// 接口定义
interface Vehicle {
    void start();
    void move(int distance);
    void stop();
}

// 接口实现类
class Car implements Vehicle {
    @Override
    public void start() {
        System.out.println("汽车启动");
    }
    
    @Override
    public void move(int distance) {
        System.out.println("汽车行驶了" + distance + "公里");
    }
    
    @Override
    public void stop() {
        System.out.println("汽车停止");
    }
}

// 接口实现类
class Bicycle implements Vehicle {
    @Override
    public void start() {
        System.out.println("自行车启动");
    }
    
    @Override
    public void move(int distance) {
        System.out.println("自行车行驶了" + distance + "公里");
    }
    
    @Override
    public void stop() {
        System.out.println("自行车停止");
    }
}

// 静态成员示例
class Counter {
    private static int count = 0;
    
    public static void increment() {
        count++;
    }
    
    public static int getCount() {
        return count;
    }
}