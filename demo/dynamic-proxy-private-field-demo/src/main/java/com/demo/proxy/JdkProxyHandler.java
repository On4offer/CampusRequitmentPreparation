package com.demo.proxy;

import java.lang.reflect.Field;
import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;
import java.lang.reflect.Proxy;

/**
 * JDK动态代理处理器（演示如何获取目标对象的私有属性）
 */
public class JdkProxyHandler implements InvocationHandler {
    
    // 关键：持有目标对象的引用
    private final Object target;
    
    public JdkProxyHandler(Object target) {
        System.out.println("【执行位置】JdkProxyHandler.<init>() - 构造函数");
        System.out.println("【当前操作】创建JDK代理处理器实例，保存目标对象引用");
        this.target = target;
        System.out.println("【结果】代理处理器创建成功，目标对象类型：" + target.getClass().getName());
    }
    
    @Override
    public Object invoke(Object proxy, Method method, Object[] args) throws Throwable {
        System.out.println("\n========== JDK动态代理拦截方法调用 ==========");
        System.out.println("【执行位置】JdkProxyHandler.invoke() - 代理拦截方法");
        System.out.println("【框架自动完成】JDK代理框架自动调用此方法，拦截所有对代理对象的方法调用");
        System.out.println("【当前操作】处理被拦截的方法调用");
        System.out.println("  - 拦截到的方法：" + method.getName());
        System.out.println("  - 代理对象类型：" + proxy.getClass().getName());
        System.out.println("  - 目标对象类型：" + target.getClass().getName());
        
        // ========== 核心步骤：获取目标对象的私有属性 ==========
        System.out.println("\n【步骤1】开始获取目标对象的私有属性...");
        System.out.println("【执行位置】JdkProxyHandler.invoke() - 使用反射获取私有属性");
        
        try {
            // 1.1 获取私有字段 privateField
            System.out.println("\n【操作1.1】获取并修改私有属性 privateField");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"privateField\")");
            // 首先获取Field对象（只是获取字段的元数据，不访问值）
            Field privateField = target.getClass().getDeclaredField("privateField");
            System.out.println("  -> 调用：privateField.setAccessible(true) - 突破访问限制");
            privateField.setAccessible(true);
            System.out.println("  -> 调用：privateField.get(target) - 读取字段值");
            // 最后才通过get方法获取实际的字段值
            String fieldValue = (String) privateField.get(target);
            System.out.println("  ✓ 读取私有属性 privateField：" + fieldValue);
            
            // 1.2 修改私有属性 privateField
            String newValue = "【JDK代理修改后的值】";
            System.out.println("  -> 调用：privateField.set(target, \"" + newValue + "\") - 修改字段值");
            privateField.set(target, newValue);
            System.out.println("  ✓ 修改私有属性 privateField：" + fieldValue + " -> " + newValue);
            
            // 1.3 获取并修改私有属性 privateNum
            System.out.println("\n【操作1.2】获取并修改私有属性 privateNum");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"privateNum\")");
            Field privateNumField = target.getClass().getDeclaredField("privateNum");
            System.out.println("  -> 调用：privateNumField.setAccessible(true) - 突破访问限制");
            privateNumField.setAccessible(true);
            System.out.println("  -> 调用：privateNumField.get(target) - 读取字段值");
            Integer oldNum = (Integer) privateNumField.get(target);
            System.out.println("  ✓ 读取私有属性 privateNum：" + oldNum);
            
            System.out.println("  -> 调用：privateNumField.set(target, 200) - 修改字段值");
            privateNumField.set(target, 200);
            System.out.println("  ✓ 修改私有属性 privateNum：" + oldNum + " -> 200");
            
            // 1.4 获取并修改私有属性 isActive
            System.out.println("\n【操作1.3】获取并修改私有属性 isActive");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"isActive\")");
            Field isActiveField = target.getClass().getDeclaredField("isActive");
            System.out.println("  -> 调用：isActiveField.setAccessible(true) - 突破访问限制");
            isActiveField.setAccessible(true);
            System.out.println("  -> 调用：isActiveField.getBoolean(target) - 读取字段值");
            boolean oldActive = isActiveField.getBoolean(target);
            System.out.println("  ✓ 读取私有属性 isActive：" + oldActive);
            
            System.out.println("  -> 调用：isActiveField.setBoolean(target, false) - 修改字段值");
            isActiveField.setBoolean(target, false);
            System.out.println("  ✓ 修改私有属性 isActive：" + oldActive + " -> false");
            
        } catch (NoSuchFieldException e) {
            System.err.println("  ✗ 获取私有字段失败：" + e.getMessage());
        } catch (IllegalAccessException e) {
            System.err.println("  ✗ 访问私有字段失败：" + e.getMessage());
        }
        
        System.out.println("\n【步骤2】执行目标方法");
        System.out.println("【执行位置】JdkProxyHandler.invoke() - 调用目标对象的方法");
        System.out.println("【当前操作】通过反射调用目标对象的原始方法");
        System.out.println("  -> 调用：method.invoke(target, args) - 执行目标方法");
        Object result = method.invoke(target, args);
        System.out.println("  -> 目标方法执行完成，返回结果：" + result);
        System.out.println("  -> 返回method" + method);
        
        System.out.println("\n【执行位置】JdkProxyHandler.invoke() - 方法结束");
        System.out.println("【当前操作】返回方法执行结果给调用者");
        System.out.println("========== JDK动态代理方法调用结束 ==========\n");
        
        return result;
    }
    
    /**
     * 创建代理对象
     */
    public static Object createProxy(Object target) {
        System.out.println("\n【执行位置】JdkProxyHandler.createProxy() - 静态方法");
        System.out.println("【当前操作】开始创建JDK动态代理对象");
        System.out.println("【框架自动完成】调用Proxy.newProxyInstance()时，JDK框架会：");
        System.out.println("  1. 动态生成代理类（继承Proxy类，实现目标接口）");
        System.out.println("  2. 通过字节码技术创建代理类");
        System.out.println("  3. 代理类的所有方法调用都会转发到InvocationHandler.invoke()");
        
        System.out.println("\n【步骤1】创建InvocationHandler实例");
        System.out.println("  -> 调用：new JdkProxyHandler(target)");
        JdkProxyHandler handler = new JdkProxyHandler(target);
        
        System.out.println("\n【步骤2】调用Proxy.newProxyInstance()创建代理对象");
        System.out.println("  -> 参数1：ClassLoader = " + target.getClass().getClassLoader().getClass().getName());
        System.out.println("  -> 参数2：接口数组 = " + java.util.Arrays.toString(target.getClass().getInterfaces()));
        System.out.println("  -> 参数3：InvocationHandler = " + handler.getClass().getName());
        System.out.println("  -> 调用：Proxy.newProxyInstance(...) - JDK框架动态生成代理类");
        Object proxy = Proxy.newProxyInstance(
                target.getClass().getClassLoader(),
                target.getClass().getInterfaces(),
                handler
        );
        
        System.out.println("\n【框架自动完成】JDK框架已动态生成代理类并创建实例");
        System.out.println("【结果】代理对象创建成功");
        System.out.println("  - 代理对象类型：" + proxy.getClass().getName());
        System.out.println("  - 代理对象实现的接口：" + java.util.Arrays.toString(proxy.getClass().getInterfaces()));
        System.out.println("  - 注意：代理对象是JDK框架动态生成的类，不是我们编写的类");
        
        System.out.println("\n【执行位置】JdkProxyHandler.createProxy() - 方法结束");
        System.out.println("【当前操作】返回代理对象给调用者");
        return proxy;
    }
}

