package com.learning.advanced;

import java.lang.annotation.ElementType;
import java.lang.annotation.Retention;
import java.lang.annotation.RetentionPolicy;
import java.lang.annotation.Target;
import java.lang.reflect.Field;
import java.lang.reflect.Method;
import java.util.ArrayList;
import java.util.List;

/**
 * 泛型、反射与注解示例
 * 演示Java高级特性的使用
 */
public class GenericReflectionAnnotationDemo {
    public static void main(String[] args) {
        // 1. 泛型示例
        System.out.println("=== 1. 泛型示例 ===");
        
        // 泛型类使用
        GenericClass<String> stringGeneric = new GenericClass<>("Hello Generics");
        GenericClass<Integer> integerGeneric = new GenericClass<>(100);
        GenericClass<?> variableGeneric = new GenericClass<>("variable");
        
        System.out.println("String泛型值: " + stringGeneric.getValue());
        System.out.println("Integer泛型值: " + integerGeneric.getValue());
        System.out.println("泛型变量值: " + variableGeneric.getValue());
        
        // 泛型方法使用
        String result1 = GenericMethodDemo.<String, String>convert("test", String::toUpperCase);
        Integer result2 = GenericMethodDemo.<Double, Integer>convert(5.5, Double::intValue);
        
        System.out.println("字符串转换结果: " + result1);
        System.out.println("Double转Integer结果: " + result2);
        
        // 泛型接口使用
        GenericInterface<String> stringProcessor = new StringProcessor();
        GenericInterface<Integer> integerProcessor = new IntegerProcessor();
        
        System.out.println("字符串处理器结果: " + stringProcessor.process("Java"));
        System.out.println("整数处理器结果: " + integerProcessor.process(100));
        
        // 2. 反射示例
        System.out.println("\n=== 2. 反射示例 ===");
        try {
            // 获取Class对象
            Class<?> clazz = ReflectClass.class;
            System.out.println("类名: " + clazz.getName());
            
            // 获取类的所有方法
            System.out.println("\n类的方法:");
            Method[] methods = clazz.getDeclaredMethods();
            for (Method method : methods) {
                System.out.println("- " + method.getName());
            }
            
            // 获取类的所有字段
            System.out.println("\n类的字段:");
            Field[] fields = clazz.getDeclaredFields();
            for (Field field : fields) {
                System.out.println("- " + field.getName());
            }
            
            // 创建对象并调用方法
            Object reflectObj = clazz.getDeclaredConstructor(String.class, int.class).newInstance("反射对象", 20);
            Method displayMethod = clazz.getDeclaredMethod("display");
            displayMethod.invoke(reflectObj);
            
            // 访问私有字段
            Field privateField = clazz.getDeclaredField("privateField");
            privateField.setAccessible(true); // 突破封装
            privateField.set(reflectObj, "修改后的私有字段值");
            System.out.println("修改后的私有字段: " + privateField.get(reflectObj));
            
        } catch (Exception e) {
            e.printStackTrace();
        }
        
        // 3. 注解示例
        System.out.println("\n=== 3. 注解示例 ===");
        try {
            // 获取注解信息
            Class<?> annotatedClass = AnnotatedClass.class;
            
            if (annotatedClass.isAnnotationPresent(MyClassAnnotation.class)) {
                MyClassAnnotation classAnnotation = annotatedClass.getAnnotation(MyClassAnnotation.class);
                System.out.println("类注解信息:");
                System.out.println("- name: " + classAnnotation.name());
                System.out.println("- version: " + classAnnotation.version());
            }
            
            // 获取方法注解信息
            Method[] methods = annotatedClass.getDeclaredMethods();
            for (Method method : methods) {
                if (method.isAnnotationPresent(MyMethodAnnotation.class)) {
                    MyMethodAnnotation methodAnnotation = method.getAnnotation(MyMethodAnnotation.class);
                    System.out.println("\n方法注解信息:");
                    System.out.println("- 方法名: " + method.getName());
                    System.out.println("- description: " + methodAnnotation.description());
                    System.out.println("- isTest: " + methodAnnotation.isTest());
                    
                    // 如果是测试方法，则调用
                    if (methodAnnotation.isTest()) {
                        Object obj = annotatedClass.getDeclaredConstructor().newInstance();
                        method.invoke(obj);
                    }
                }
            }
            
            // 获取字段注解信息
            Field[] fields = annotatedClass.getDeclaredFields();
            for (Field field : fields) {
                if (field.isAnnotationPresent(MyFieldAnnotation.class)) {
                    MyFieldAnnotation fieldAnnotation = field.getAnnotation(MyFieldAnnotation.class);
                    System.out.println("\n字段注解信息:");
                    System.out.println("- 字段名: " + field.getName());
                    System.out.println("- required: " + fieldAnnotation.required());
                    System.out.println("- maxLength: " + fieldAnnotation.maxLength());
                }
            }
            
        } catch (Exception e) {
            e.printStackTrace();
        }
    }
}

// 泛型类示例
class GenericClass<T> {
    private T value;
    
    public GenericClass(T value) {
        this.value = value;
    }
    
    public T getValue() {
        return value;
    }
    
    public void setValue(T value) {
        this.value = value;
    }
}

// 泛型方法示例
class GenericMethodDemo {
    public static <T, R> R convert(T input, Converter<T, R> converter) {
        return converter.convert(input);
    }
    
    // 函数式接口
    interface Converter<T, R> {
        R convert(T input);
    }
}

// 泛型接口示例
interface GenericInterface<T> {
    T process(T input);
}

class StringProcessor implements GenericInterface<String> {
    @Override
    public String process(String input) {
        return "Processed: " + input;
    }
}

class IntegerProcessor implements GenericInterface<Integer> {
    @Override
    public Integer process(Integer input) {
        return input * 2;
    }
}

// 反射示例类
class ReflectClass {
    private String name;
    private int age;
    private String privateField = "初始私有字段值";
    
    public ReflectClass(String name, int age) {
        this.name = name;
        this.age = age;
    }
    
    public void display() {
        System.out.println("ReflectClass: name = " + name + ", age = " + age);
    }
    
    private void privateMethod() {
        System.out.println("这是一个私有方法");
    }
}

// 注解定义 - 类注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.TYPE)
@interface MyClassAnnotation {
    String name();
    String version() default "1.0";
}

// 注解定义 - 方法注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
@interface MyMethodAnnotation {
    String description();
    boolean isTest() default false;
}

// 注解定义 - 字段注解
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
@interface MyFieldAnnotation {
    boolean required() default false;
    int maxLength() default 255;
}

// 使用注解的类
@MyClassAnnotation(name = "AnnotatedClass", version = "1.0.0")
class AnnotatedClass {
    @MyFieldAnnotation(required = true, maxLength = 100)
    private String name;
    
    @MyFieldAnnotation(maxLength = 20)
    private int age;
    
    @MyMethodAnnotation(description = "测试方法", isTest = true)
    public void testMethod() {
        System.out.println("执行测试方法");
    }
    
    @MyMethodAnnotation(description = "普通方法")
    public void normalMethod() {
        System.out.println("执行普通方法");
    }
}