package com.demo.proxy;

/**
 * 子类服务（继承父类，用于演示获取父类私有属性）
 */
public class ChildService extends ParentService {
    // 子类自己的私有属性
    private String childPrivateField = "子类的私有属性";
    
    public void childMethod() {
        System.out.println("子类方法执行");
    }
}

