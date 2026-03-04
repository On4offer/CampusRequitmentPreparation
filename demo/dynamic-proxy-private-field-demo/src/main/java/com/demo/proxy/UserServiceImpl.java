package com.demo.proxy;

/**
 * 用户服务实现类（含私有属性，用于JDK动态代理演示）
 */
public class UserServiceImpl implements UserService {
    // 私有属性1：字符串类型
    private String privateField = "我是私有属性-初始值";
    
    // 私有属性2：整数类型
    private Integer privateNum = 100;
    
    // 私有属性3：布尔类型
    private boolean isActive = true;
    
    // 公共方法
    @Override
    public void doSomething() {
        System.out.println("【执行位置】UserServiceImpl.doSomething() - 目标方法");
        System.out.println("【当前操作】执行目标对象的原始业务逻辑");
        System.out.println("【注意】此方法是通过代理对象调用的，但实际执行的是目标对象的方法");
        System.out.println("【目标方法执行】UserServiceImpl.doSomething()");
        System.out.println("当前私有属性值：privateField=" + privateField + ", privateNum=" + privateNum);
        System.out.println("【执行位置】UserServiceImpl.doSomething() - 方法结束");
    }
    
    @Override
    public String getUserInfo() {
        return "用户信息：privateField=" + privateField + ", privateNum=" + privateNum;
    }
    
    // 提供getter方法用于对比（验证私有属性是否真的被修改）
    public String getPrivateField() {
        return privateField;
    }
    
    public Integer getPrivateNum() {
        return privateNum;
    }
}

