package com.demo.proxy;

import net.sf.cglib.proxy.Enhancer;
import net.sf.cglib.proxy.MethodInterceptor;
import net.sf.cglib.proxy.MethodProxy;

import java.lang.reflect.Field;
import java.lang.reflect.Method;

/**
 * CGLIB动态代理拦截器（演示如何获取目标对象的私有属性）
 */
public class CglibProxyInterceptor implements MethodInterceptor {
    
    // 关键：持有目标对象的引用
    private final Object target;
    
    public CglibProxyInterceptor(Object target) {
        System.out.println("【执行位置】CglibProxyInterceptor.<init>() - 构造函数");
        System.out.println("【当前操作】创建CGLIB代理拦截器实例，保存目标对象引用");
        this.target = target;
        System.out.println("【结果】代理拦截器创建成功，目标对象类型：" + target.getClass().getName());
    }
    
    /**
     * 创建代理对象
     */
    public Object createProxy() {
        System.out.println("\n【执行位置】CglibProxyInterceptor.createProxy() - 实例方法");
        System.out.println("【当前操作】开始创建CGLIB动态代理对象");
        System.out.println("【框架自动完成】调用Enhancer.create()时，CGLIB框架会：");
        System.out.println("  1. 动态生成目标类的子类（继承目标类）");
        System.out.println("  2. 通过字节码技术创建代理类");
        System.out.println("  3. 代理类的所有方法调用都会转发到MethodInterceptor.intercept()");
        
        System.out.println("\n【步骤1】创建Enhancer增强器");
        System.out.println("  -> 调用：new Enhancer()");
        Enhancer enhancer = new Enhancer();
        
        System.out.println("\n【步骤2】配置Enhancer");
        System.out.println("  -> 调用：enhancer.setSuperclass(" + target.getClass().getName() + ") - 设置父类（目标类）");
        enhancer.setSuperclass(target.getClass());
        System.out.println("  -> 调用：enhancer.setCallback(this) - 设置回调拦截器");
        enhancer.setCallback(this);
        
        System.out.println("\n【步骤3】调用Enhancer.create()创建代理对象");
        System.out.println("  -> 调用：enhancer.create() - CGLIB框架动态生成代理类");
        System.out.println("  -> 【框架自动完成】CGLIB框架正在：");
        System.out.println("     1. 生成目标类的子类字节码");
        System.out.println("     2. 使用ASM框架操作字节码");
        System.out.println("     3. 创建代理类并实例化");
        Object proxy = enhancer.create();
        
        System.out.println("\n【框架自动完成】CGLIB框架已动态生成代理类并创建实例");
        System.out.println("【结果】代理对象创建成功");
        System.out.println("  - 代理对象类型：" + proxy.getClass().getName());
        System.out.println("  - 代理对象的父类：" + proxy.getClass().getSuperclass().getName());
        System.out.println("  - 注意：代理对象是CGLIB框架动态生成的子类，继承自目标类");
        
        System.out.println("\n【执行位置】CglibProxyInterceptor.createProxy() - 方法结束");
        System.out.println("【当前操作】返回代理对象给调用者");
        return proxy;
    }
    
    @Override
    public Object intercept(Object proxy, Method method, Object[] args, MethodProxy methodProxy) throws Throwable {
        System.out.println("\n========== CGLIB动态代理拦截方法调用 ==========");
        System.out.println("【执行位置】CglibProxyInterceptor.intercept() - 代理拦截方法");
        System.out.println("【框架自动完成】CGLIB代理框架自动调用此方法，拦截所有对代理对象的方法调用");
        System.out.println("【当前操作】处理被拦截的方法调用");
        System.out.println("  - 拦截到的方法：" + method.getName());
        System.out.println("  - 代理对象类型：" + proxy.getClass().getName());
        System.out.println("  - 目标对象类型：" + target.getClass().getName());
        
        // ========== 核心步骤：获取目标对象的私有属性 ==========
        System.out.println("\n【步骤1】开始获取目标对象的私有属性...");
        System.out.println("【执行位置】CglibProxyInterceptor.intercept() - 使用反射获取私有属性");
        
        try {
            // 1.1 获取并修改私有属性 orderNo
            System.out.println("\n【操作1.1】获取并修改私有属性 orderNo");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"orderNo\")");
            Field orderNoField = target.getClass().getDeclaredField("orderNo");
            System.out.println("  -> 调用：orderNoField.setAccessible(true) - 突破访问限制");
            orderNoField.setAccessible(true);
            System.out.println("  -> 调用：orderNoField.get(target) - 读取字段值");
            String oldOrderNo = (String) orderNoField.get(target);
            System.out.println("  ✓ 读取私有属性 orderNo：" + oldOrderNo);
            
            System.out.println("  -> 调用：orderNoField.set(target, \"ORDER_002\") - 修改字段值");
            orderNoField.set(target, "ORDER_002");
            System.out.println("  ✓ 修改私有属性 orderNo：" + oldOrderNo + " -> ORDER_002");
            
            // 1.2 获取并修改私有属性 amount
            System.out.println("\n【操作1.2】获取并修改私有属性 amount");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"amount\")");
            Field amountField = target.getClass().getDeclaredField("amount");
            System.out.println("  -> 调用：amountField.setAccessible(true) - 突破访问限制");
            amountField.setAccessible(true);
            System.out.println("  -> 调用：amountField.get(target) - 读取字段值");
            Double oldAmount = (Double) amountField.get(target);
            System.out.println("  ✓ 读取私有属性 amount：" + oldAmount);
            
            System.out.println("  -> 调用：amountField.set(target, 199.99) - 修改字段值");
            amountField.set(target, 199.99);
            System.out.println("  ✓ 修改私有属性 amount：" + oldAmount + " -> 199.99");
            
            // 1.3 获取并修改私有属性 status
            System.out.println("\n【操作1.3】获取并修改私有属性 status");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"status\")");
            Field statusField = target.getClass().getDeclaredField("status");
            System.out.println("  -> 调用：statusField.setAccessible(true) - 突破访问限制");
            statusField.setAccessible(true);
            System.out.println("  -> 调用：statusField.get(target) - 读取字段值");
            String oldStatus = (String) statusField.get(target);
            System.out.println("  ✓ 读取私有属性 status：" + oldStatus);
            
            System.out.println("  -> 调用：statusField.set(target, \"已支付\") - 修改字段值");
            statusField.set(target, "已支付");
            System.out.println("  ✓ 修改私有属性 status：" + oldStatus + " -> 已支付");
            
        } catch (NoSuchFieldException e) {
            System.err.println("  ✗ 获取私有字段失败：" + e.getMessage());
        } catch (IllegalAccessException e) {
            System.err.println("  ✗ 访问私有字段失败：" + e.getMessage());
        }
        
        System.out.println("\n【步骤2】执行目标方法");
        System.out.println("【执行位置】CglibProxyInterceptor.intercept() - 调用目标对象的方法");
        System.out.println("【当前操作】通过MethodProxy调用目标对象的原始方法");
        System.out.println("  -> 调用：methodProxy.invoke(target, args) - 执行目标方法");
        System.out.println("  -> 注意：使用MethodProxy.invoke()比Method.invoke()性能更好（CGLIB优化）");
        Object result = methodProxy.invoke(target, args);
        System.out.println("  -> 目标方法执行完成，返回结果：" + result);
        
        System.out.println("\n【执行位置】CglibProxyInterceptor.intercept() - 方法结束");
        System.out.println("【当前操作】返回方法执行结果给调用者");
        System.out.println("========== CGLIB动态代理方法调用结束 ==========\n");
        
        return result;
    }
}

