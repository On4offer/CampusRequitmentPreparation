package generics;

import java.lang.annotation.*;
import java.lang.reflect.*;
import java.util.*;

/**
 * 反射与注解示例
 * 演示Java的反射机制和注解的定义与使用
 */
public class ReflectionAndAnnotation {
    public static void main(String[] args) throws Exception {
        // 反射机制示例
        System.out.println("===== 反射机制示例 =====");
        
        // 1. 获取Class对象
        System.out.println("\n1. 获取Class对象的三种方式：");
        // 方式1：通过对象的getClass()方法
        Person personObj = new Person("张三", 25);
        Class<?> class1 = personObj.getClass();
        System.out.println("方式1 - getClass(): " + class1.getName());
        
        // 方式2：通过类名.class
        Class<?> class2 = Person.class;
        System.out.println("方式2 - .class: " + class2.getName());
        
        // 方式3：通过Class.forName()
        Class<?> class3 = Class.forName("generics.Person");
        System.out.println("方式3 - Class.forName(): " + class3.getName());
        
        // 2. 获取类的信息
        System.out.println("\n2. 获取类的信息：");
        Class<?> personClass = Person.class;
        
        // 获取类名
        System.out.println("类名: " + personClass.getName());
        System.out.println("简单类名: " + personClass.getSimpleName());
        
        // 获取包信息
        Package pkg = personClass.getPackage();
        System.out.println("包名: " + pkg.getName());
        
        // 获取父类
        Class<?> superClass = personClass.getSuperclass();
        System.out.println("父类: " + superClass.getName());
        
        // 获取接口
        Class<?>[] interfaces = personClass.getInterfaces();
        System.out.println("实现的接口: ");
        for (Class<?> iface : interfaces) {
            System.out.println("  - " + iface.getName());
        }
        
        // 3. 获取构造方法并创建对象
        System.out.println("\n3. 获取构造方法并创建对象：");
        // 获取指定的构造方法
        Constructor<?> constructor = personClass.getConstructor(String.class, int.class);
        // 使用构造方法创建对象
        Object personInstance = constructor.newInstance("李四", 30);
        System.out.println("创建的对象: " + personInstance);
        
        // 4. 获取和调用方法
        System.out.println("\n4. 获取和调用方法：");
        // 获取指定的方法
        Method getNameMethod = personClass.getMethod("getName");
        Method setAgeMethod = personClass.getMethod("setAge", int.class);
        Method introduceMethod = personClass.getMethod("introduce");
        
        // 调用方法
        String name = (String) getNameMethod.invoke(personInstance);
        System.out.println("调用getName()方法: " + name);
        
        setAgeMethod.invoke(personInstance, 35);
        System.out.println("调用setAge(35)方法后，再次调用introduce():");
        introduceMethod.invoke(personInstance);
        
        // 5. 获取和修改字段
        System.out.println("\n5. 获取和修改字段：");
        // 获取字段（需要设置可访问，因为是private的）
        Field nameField = personClass.getDeclaredField("name");
        nameField.setAccessible(true); // 设置为可访问
        
        // 获取字段值
        String currentName = (String) nameField.get(personInstance);
        System.out.println("修改前的name字段值: " + currentName);
        
        // 修改字段值
        nameField.set(personInstance, "王五");
        String newName = (String) nameField.get(personInstance);
        System.out.println("修改后的name字段值: " + newName);
        
        // 6. 反射调用静态方法
        System.out.println("\n6. 反射调用静态方法：");
        Method staticMethod = personClass.getMethod("staticMethod");
        staticMethod.invoke(null); // 静态方法调用时，第一个参数为null
        
        // 注解示例
        System.out.println("\n===== 注解示例 =====");
        
        // 1. 检查类上的注解
        System.out.println("\n1. 检查类上的注解：");
        if (Person.class.isAnnotationPresent(MyClassAnnotation.class)) {
            MyClassAnnotation classAnnotation = Person.class.getAnnotation(MyClassAnnotation.class);
            System.out.println("类注解名称: " + classAnnotation.name());
            System.out.println("类注解版本: " + classAnnotation.version());
        }
        
        // 2. 检查方法上的注解
        System.out.println("\n2. 检查方法上的注解：");
        Method[] methods = Person.class.getDeclaredMethods();
        for (Method method : methods) {
            if (method.isAnnotationPresent(MyMethodAnnotation.class)) {
                MyMethodAnnotation methodAnnotation = method.getAnnotation(MyMethodAnnotation.class);
                System.out.println("方法名: " + method.getName());
                System.out.println("  方法注解描述: " + methodAnnotation.description());
                System.out.println("  方法注解作者: " + methodAnnotation.author());
                System.out.println("  方法注解日期: " + methodAnnotation.date());
            }
        }
        
        // 3. 检查字段上的注解
        System.out.println("\n3. 检查字段上的注解：");
        Field[] fields = Person.class.getDeclaredFields();
        for (Field field : fields) {
            if (field.isAnnotationPresent(MyFieldAnnotation.class)) {
                MyFieldAnnotation fieldAnnotation = field.getAnnotation(MyFieldAnnotation.class);
                System.out.println("字段名: " + field.getName());
                System.out.println("  字段注解描述: " + fieldAnnotation.description());
                System.out.println("  字段注解是否必填: " + fieldAnnotation.required());
            }
        }
        
        // 4. 运行时注解处理示例
        System.out.println("\n4. 运行时注解处理示例：");
        processAnnotations(personClass);
        
        // 5. 使用注解进行简单的验证
        System.out.println("\n5. 使用注解进行简单的验证：");
        User user = new User();
        user.setUsername("admin");
        user.setPassword("123"); // 密码太短，应该大于6位
        user.setEmail("invalid-email"); // 无效的邮箱格式
        
        validateUser(user);
    }
    
    // 运行时处理注解的方法
    public static void processAnnotations(Class<?> clazz) {
        System.out.println("处理类: " + clazz.getSimpleName() + " 的注解");
        
        // 处理类注解
        if (clazz.isAnnotationPresent(MyClassAnnotation.class)) {
            MyClassAnnotation classAnnotation = clazz.getAnnotation(MyClassAnnotation.class);
            System.out.println("类级注解处理 - 注册类: " + classAnnotation.name() + " v" + classAnnotation.version());
        }
        
        // 处理方法注解
        for (Method method : clazz.getDeclaredMethods()) {
            if (method.isAnnotationPresent(MyMethodAnnotation.class)) {
                MyMethodAnnotation methodAnnotation = method.getAnnotation(MyMethodAnnotation.class);
                System.out.println("方法级注解处理 - " + method.getName() + ": " + methodAnnotation.description());
            }
        }
    }
    
    // 使用注解进行用户验证
    public static void validateUser(User user) throws Exception {
        Class<?> userClass = user.getClass();
        List<String> errors = new ArrayList<>();
        
        for (Field field : userClass.getDeclaredFields()) {
            if (field.isAnnotationPresent(ValidationAnnotation.class)) {
                ValidationAnnotation validation = field.getAnnotation(ValidationAnnotation.class);
                field.setAccessible(true);
                Object value = field.get(user);
                
                // 检查是否为空
                if (validation.notEmpty() && (value == null || value.toString().trim().isEmpty())) {
                    errors.add(field.getName() + " 不能为空");
                }
                
                // 检查最小长度
                if (value instanceof String && ((String) value).length() < validation.minLength()) {
                    errors.add(field.getName() + " 的长度不能小于 " + validation.minLength());
                }
                
                // 检查正则表达式
                if (value instanceof String && !validation.regex().isEmpty() && 
                    !((String) value).matches(validation.regex())) {
                    errors.add(field.getName() + " 不符合格式要求");
                }
            }
        }
        
        // 输出验证结果
        if (errors.isEmpty()) {
            System.out.println("用户验证通过！");
        } else {
            System.out.println("验证失败，错误信息：");
            for (String error : errors) {
                System.out.println("  - " + error);
            }
        }
    }
}

// 自定义类级注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface MyClassAnnotation {
    String name();
    String version() default "1.0";
}

// 自定义方法级注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface MyMethodAnnotation {
    String description();
    String author();
    String date();
}

// 自定义字段级注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface MyFieldAnnotation {
    String description();
    boolean required() default false;
}

// 自定义验证注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface ValidationAnnotation {
    boolean notEmpty() default false;
    int minLength() default 0;
    String regex() default "";
}

// 用于演示反射和注解的Person类
@MyClassAnnotation(name = "Person", version = "1.0.0")
class Person implements Comparable<Person> {
    @MyFieldAnnotation(description = "姓名", required = true)
    private String name;
    
    @MyFieldAnnotation(description = "年龄")
    private int age;
    
    public Person() {
    }
    
    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    @MyMethodAnnotation(description = "获取姓名", author = "Java", date = "2024-01-01")
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
        this.age = age;
    }
    
    @MyMethodAnnotation(description = "介绍自己", author = "Java", date = "2024-01-01")
    public void introduce() {
        System.out.println("我是" + name + "，今年" + age + "岁。");
    }
    
    public static void staticMethod() {
        System.out.println("这是一个静态方法");
    }
    
    @Override
    public String toString() {
        return "Person{name='" + name + "', age=" + age + "}";
    }
    
    @Override
    public int compareTo(Person o) {
        return Integer.compare(this.age, o.age);
    }
}

// 用于验证的User类
class User {
    @ValidationAnnotation(notEmpty = true, minLength = 3)
    private String username;
    
    @ValidationAnnotation(notEmpty = true, minLength = 6)
    private String password;
    
    @ValidationAnnotation(regex = "^[\\w-\\.]+@([\\w-]+\\.)+[\\w-]{2,4}$")
    private String email;
    
    public String getUsername() {
        return username;
    }
    
    public void setUsername(String username) {
        this.username = username;
    }
    
    public String getPassword() {
        return password;
    }
    
    public void setPassword(String password) {
        this.password = password;
    }
    
    public String getEmail() {
        return email;
    }
    
    public void setEmail(String email) {
        this.email = email;
    }
}