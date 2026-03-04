package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;

/**
 * SpringBoot自动装配演示应用
 */
@SpringBootApplication
public class SpringBootAutoConfigDemoApplication {

    public static void main(String[] args) {
        // 启动SpringBoot应用
        ConfigurableApplicationContext context = SpringApplication.run(SpringBootAutoConfigDemoApplication.class, args);
        
        // 输出应用启动信息
        System.out.println("\n=== SpringBoot自动装配演示应用启动成功 ===");
        System.out.println("应用名称: " + context.getEnvironment().getProperty("spring.application.name"));
        System.out.println("应用端口: " + context.getEnvironment().getProperty("server.port"));
        System.out.println("=== 自动装配的Bean列表（部分） ===");
        
        // 输出部分自动装配的Bean名称
        String[] beanNames = context.getBeanDefinitionNames();
        int count = 0;
        for (String beanName : beanNames) {
            if (beanName.startsWith("org.springframework.boot.autoconfigure") || 
                beanName.startsWith("myCustom")) {
                System.out.println("  - " + beanName);
                count++;
            }
        }
        System.out.println("\n共找到 " + count + " 个自动装配的Bean");
        System.out.println("======================================\n");
    }
}