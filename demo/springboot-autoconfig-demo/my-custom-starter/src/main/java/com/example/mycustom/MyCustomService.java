package com.example.mycustom;

/**
 * 自定义Starter的核心服务类
 * 该类将被自动装配为Spring Bean
 */
public class MyCustomService {

    private final MyCustomProperties properties;

    /**
     * 构造函数注入属性配置
     * @param properties 配置属性
     */
    public MyCustomService(MyCustomProperties properties) {
        this.properties = properties;
    }

    /**
     * 演示方法：获取配置的消息
     * @return 配置的消息
     */
    public String getMessage() {
        return properties.getMessage();
    }

    /**
     * 演示方法：执行自定义操作
     * @param input 输入参数
     * @return 处理结果
     */
    public String doSomething(String input) {
        if (!properties.isEnabled()) {
            return "Custom service is disabled!";
        }
        
        // 模拟处理过程（使用超时配置）
        try {
            Thread.sleep(properties.getTimeout() / 10); // 使用10%的超时时间模拟处理
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return "Operation interrupted!";
        }
        
        return String.format("[%s] Processing '%s' with timeout %dms", 
                properties.getMessage(), input, properties.getTimeout());
    }

    @Override
    public String toString() {
        return "MyCustomService{" +
                "properties=" + properties +
                '}';
    }
}