package com.example.demo.initializer;

import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.ConfigurableEnvironment;
import org.springframework.util.ClassUtils;

import java.util.Locale;

/**
 * 应用类型调试初始化器
 * 用于打印Spring Boot应用类型推断的相关信息
 */
public class AppTypeDebugInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        System.out.println("\ninitializer------===== 应用类型推断调试信息 =====");
        
        // 检查Web应用相关的类是否存在
        boolean hasServletWebContext = ClassUtils.isPresent(
                "org.springframework.web.context.ConfigurableWebApplicationContext", null);
        boolean hasReactiveWebContext = ClassUtils.isPresent(
                "org.springframework.web.reactive.config.ConfigurableReactiveWebApplicationContext", null);
        
        // 获取应用类型
        String applicationType = determineApplicationType(hasServletWebContext, hasReactiveWebContext);
        
        // 打印推断依据和结果
        System.out.println("方法路径: org.springframework.boot.SpringApplication.deduceWebApplicationType()");
        System.out.println("判断依据: 通过ClassUtils.isPresent检查classpath中的特定类");
        System.out.println("- 存在Servlet Web Context类: " + hasServletWebContext);
        System.out.println("- 存在Reactive Web Context类: " + hasReactiveWebContext);
        System.out.println("推断结果: " + applicationType);
        
        // 打印当前ApplicationContext的类型
        System.out.println("实际创建的ApplicationContext类型: " + applicationContext.getClass().getName());
        
        // 添加应用类型信息到环境变量中，以便后续使用
        ConfigurableEnvironment environment = applicationContext.getEnvironment();
        environment.getSystemProperties().put("app.type.debug", applicationType);
        
        System.out.println("initializer------===== 应用类型推断调试完成 =====\n");
    }
    
    /**
     * 模拟Spring Boot内部的应用类型推断逻辑
     */
    private String determineApplicationType(boolean hasServletWebContext, boolean hasReactiveWebContext) {
        if (hasReactiveWebContext) {
            return "REACTIVE (响应式Web应用)";
        } else if (hasServletWebContext) {
            return "SERVLET (Servlet Web应用)";
        } else {
            return "NONE (普通应用)";
        }
    }
}
