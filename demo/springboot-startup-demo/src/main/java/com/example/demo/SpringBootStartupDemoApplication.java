package com.example.demo;

import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;

import java.util.Arrays;
import java.util.Set;

/**
 * SpringBoot启动流程演示主类
 * 展示SpringBoot应用从main方法到IOC容器初始化的完整过程
 */
@SpringBootApplication
public class SpringBootStartupDemoApplication {

    public static void main(String[] args) {
        System.out.println("[启动阶段1] ======== 开始SpringBoot应用启动流程 ========");
        System.out.println("[启动阶段1] main方法被调用，准备创建SpringApplication对象，这个阶段适合做一些轻量级、快速的准备工作，避免影响应用启动速度");

        // 1. 创建SpringApplication对象并运行
        // 这一步包含了：
        // - 根据classpath推断应用类型（Web/Servlet/普通应用） - 通过SpringApplication.deduceWebApplicationType()方法实现
        // - 推断逻辑：通过ClassUtils.isPresent()检查classpath中是否存在特定类
        //   - 如果存在org.springframework.web.reactive.config.ConfigurableReactiveWebApplicationContext，则为REACTIVE应用
        //   - 如果存在org.springframework.web.context.ConfigurableWebApplicationContext，则为SERVLET应用
        //   - 否则为NONE应用（普通应用）
        // - 加载初始化器（ApplicationContextInitializer）
        // - 加载监听器（ApplicationListener）
        System.out.println("[启动阶段1] 即将开始应用类型推断过程，详细信息将在自定义初始化器中显示");
        System.out.println("[启动阶段1] 调用SpringApplication.run()方法");
        ConfigurableApplicationContext context = SpringApplication.run(SpringBootStartupDemoApplication.class, args);

        System.out.println("[启动阶段7] ======== SpringBoot应用启动完成 ========");
        
        // 演示：输出容器中的一些Bean信息
        System.out.println("[验证] IOC容器初始化完成，包含" + context.getBeanDefinitionCount() + "个Bean定义");
        
        // 比较不同阶段的BeanDefinition数量差异
        System.out.println("\n[比较分析] 开始比较不同阶段的BeanDefinition差异：");
        String[] finalBeanNames = context.getBeanDefinitionNames();
        Set<String> earlyBeanNames = com.example.demo.processor.DemoBeanFactoryPostProcessor.getEarlyBeanDefinitions();
        
        // 找出新增的Bean
        System.out.println("[比较分析] 新增的BeanDefinition列表：");
        int count = 0;
        // 获取ConfigurableListableBeanFactory以访问getBeanDefinition方法
        ConfigurableListableBeanFactory beanFactory = context.getBeanFactory();
        for (String beanName : finalBeanNames) {
            if (!earlyBeanNames.contains(beanName)) {
                count++;
                // 通过beanFactory获取BeanDefinition
                String beanClassName = beanFactory.getBeanDefinition(beanName).getBeanClassName();
                System.out.println("  - 新增Bean: " + beanName + " (类型: " + (beanClassName != null ? beanClassName : "未知") + ")");
            }
        }
        System.out.println("[比较分析] 总共新增" + count + "个BeanDefinition");
        
        System.out.println("\n[验证] 容器中的部分Bean名称示例：");
        String[] beanNames = Arrays.copyOfRange(finalBeanNames, 0, Math.min(5, finalBeanNames.length));
        for (String beanName : beanNames) {
            System.out.println("  - " + beanName);
        }
        System.out.println("----------结束----------");
    }
}
