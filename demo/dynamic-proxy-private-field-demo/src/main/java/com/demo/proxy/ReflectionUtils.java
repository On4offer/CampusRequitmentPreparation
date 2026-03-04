package com.demo.proxy;

import java.lang.reflect.Field;

/**
 * 反射工具类（用于递归获取私有属性，包括父类的私有属性）
 */
public class ReflectionUtils {
    
    /**
     * 递归获取私有字段（包括父类的私有字段）
     * 
     * @param target 目标对象
     * @param fieldName 字段名
     * @return Field对象
     * @throws NoSuchFieldException 如果字段不存在
     */
    public static Field getDeclaredField(Object target, String fieldName) throws NoSuchFieldException {
        System.out.println("【执行位置】ReflectionUtils.getDeclaredField() - 静态方法");
        System.out.println("【当前操作】递归查找字段（包括父类的私有字段）");
        Class<?> clazz = target.getClass();
        System.out.println("【反射工具】开始查找字段：" + fieldName);
        System.out.println("  -> 起始类：" + clazz.getName());
        
        int level = 0;
        while (clazz != null) {
            level++;
            System.out.println("  -> 第" + level + "层：正在检查类：" + clazz.getName());
            System.out.println("    -> 调用：clazz.getDeclaredField(\"" + fieldName + "\")");
            try {
                Field field = clazz.getDeclaredField(fieldName);
                System.out.println("    -> ✓ 在类 " + clazz.getName() + " 中找到字段：" + fieldName);
                System.out.println("【执行位置】ReflectionUtils.getDeclaredField() - 方法结束");
                System.out.println("【结果】字段查找成功，返回Field对象");
                return field;
            } catch (NoSuchFieldException e) {
                System.out.println("    -> ✗ 当前类未找到字段，准备查找父类");
                clazz = clazz.getSuperclass(); // 向上查找父类
                if (clazz != null) {
                    System.out.println("    -> 调用：clazz.getSuperclass() - 获取父类");
                    System.out.println("    -> 继续查找父类：" + clazz.getName());
                } else {
                    System.out.println("    -> 已到达Object类，没有父类了");
                }
            }
        }
        
        System.out.println("【执行位置】ReflectionUtils.getDeclaredField() - 抛出异常");
        throw new NoSuchFieldException("字段 " + fieldName + " 在类 " + target.getClass().getName() + " 及其父类中不存在");
    }
    
    /**
     * 安全地获取私有字段的值
     * 
     * @param target 目标对象
     * @param fieldName 字段名
     * @return 字段值
     */
    public static Object getPrivateFieldValue(Object target, String fieldName) {
        System.out.println("【执行位置】ReflectionUtils.getPrivateFieldValue() - 静态方法");
        System.out.println("【当前操作】安全地获取私有字段的值");
        try {
            System.out.println("  -> 步骤1：调用getDeclaredField()查找字段");
            Field field = getDeclaredField(target, fieldName);
            System.out.println("  -> 步骤2：调用field.setAccessible(true) - 突破访问限制");
            field.setAccessible(true);
            System.out.println("  -> 步骤3：调用field.get(target) - 读取字段值");
            Object value = field.get(target);
            System.out.println("【反射工具】成功读取字段值：" + fieldName + " = " + value);
            System.out.println("【执行位置】ReflectionUtils.getPrivateFieldValue() - 方法结束");
            return value;
        } catch (Exception e) {
            System.err.println("【反射工具】读取字段失败：" + e.getMessage());
            e.printStackTrace();
            return null;
        }
    }
    
    /**
     * 安全地设置私有字段的值
     * 
     * @param target 目标对象
     * @param fieldName 字段名
     * @param value 新值
     */
    public static void setPrivateFieldValue(Object target, String fieldName, Object value) {
        System.out.println("【执行位置】ReflectionUtils.setPrivateFieldValue() - 静态方法");
        System.out.println("【当前操作】安全地设置私有字段的值");
        try {
            System.out.println("  -> 步骤1：调用getDeclaredField()查找字段");
            Field field = getDeclaredField(target, fieldName);
            System.out.println("  -> 步骤2：调用field.setAccessible(true) - 突破访问限制");
            field.setAccessible(true);
            System.out.println("  -> 步骤3：调用field.get(target) - 读取旧值");
            Object oldValue = field.get(target);
            System.out.println("  -> 步骤4：调用field.set(target, value) - 设置新值");
            field.set(target, value);
            System.out.println("【反射工具】成功修改字段值：" + fieldName + " (" + oldValue + " -> " + value + ")");
            System.out.println("【执行位置】ReflectionUtils.setPrivateFieldValue() - 方法结束");
        } catch (Exception e) {
            System.err.println("【反射工具】修改字段失败：" + e.getMessage());
            e.printStackTrace();
        }
    }
}

