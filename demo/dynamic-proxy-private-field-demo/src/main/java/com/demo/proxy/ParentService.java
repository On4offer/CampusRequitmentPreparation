package com.demo.proxy;

/**
 * 父类服务（用于演示获取父类私有属性）
 */
public class ParentService {
    // 父类的私有属性
    private String parentPrivateField = "父类的私有属性";
    private int parentPrivateNum = 999;
    
    public void parentMethod() {
        System.out.println("父类方法执行");
    }
}

