package com.example.demo.initializer;

import org.springframework.context.ApplicationContextInitializer;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.core.env.ConfigurableEnvironment;

/**
 * 自定义ApplicationContextInitializer
 * 演示SpringBoot启动流程中Environment准备完成后，容器刷新前的初始化过程
 */
public class DemoApplicationContextInitializer implements ApplicationContextInitializer<ConfigurableApplicationContext> {

    @Override
    public void initialize(ConfigurableApplicationContext applicationContext) {
        System.out.println("initializer------[启动阶段2] ======== ApplicationContextInitializer被调用 ========");
        
        ConfigurableEnvironment environment = applicationContext.getEnvironment();
        // 可以在此阶段操作Environment，如添加属性源、修改配置等
        String activeProfilesStr = (environment.getActiveProfiles().length > 0 ?
                String.join(", ", environment.getActiveProfiles()) : "default");
        System.out.println("initializer------[启动阶段2] 当前应用环境: " + activeProfilesStr);
        
        // 打印默认环境
        System.out.println("initializer------[启动阶段2] 默认环境: " + String.join(", ", environment.getDefaultProfiles()));
        
        // 检查环境特定的属性
        System.out.println("initializer------[启动阶段2] 检查环境特定属性:");
        String[] possibleProps = {
            "demo.startup.dev-specific-property",
            "demo.startup.test-specific-property",
            "demo.startup.prod-specific-property"
        };
        
        for (String prop : possibleProps) {
            if (environment.containsProperty(prop)) {
                System.out.println("initializer------[启动阶段2] - " + prop + ": " + environment.getProperty(prop));
            }
        }
        
        // 打印应用描述
        if (environment.containsProperty("demo.startup.description")) {
            System.out.println("initializer------[启动阶段2] 应用描述: " + environment.getProperty("demo.startup.description"));
        }
        
        // 添加自定义属性
        environment.getSystemProperties().put("demo.initializer.executed", "true");
        System.out.println("initializer------[启动阶段2] 已向Environment添加自定义属性: demo.initializer.executed=true");
        
        // 根据当前环境添加特定标记
        for (String profile : environment.getActiveProfiles()) {
            environment.getSystemProperties().put("demo.profile." + profile, "true");
            System.out.println("initializer------[启动阶段2] 已添加环境标记: demo.profile." + profile + "=true");
        }
    }
}
