package com.example.demo.autoconfigure;

import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 自定义自动配置类
 * 演示SpringBoot自动装配机制
 */
@Configuration(proxyBeanMethods = false)
@ConditionalOnProperty(name = "demo.autoconfig.enabled", havingValue = "true", matchIfMissing = true)
public class DemoAutoConfiguration {

    static {
        System.out.println("autoconfigure-----[启动阶段4] ======== DemoAutoConfiguration被加载 ========");
        System.out.println("autoconfigure-----[启动阶段4] 此阶段演示了SpringBoot的自动装配机制");
        System.out.println("autoconfigure-----[启动阶段4] 自动配置类通过@EnableAutoConfiguration触发，从spring.factories加载");
    }

    @Bean
    public DemoService demoService() {
        System.out.println("autoconfigure-----[启动阶段5] DemoAutoConfiguration创建demoService Bean");
        return new DemoService();
    }

    /**
     * 演示用的服务类
     */
    public static class DemoService {
        public DemoService() {
            System.out.println("autoconfigure-----[启动阶段5] DemoService被实例化");
        }

        public String getMessage() {
            return "autoconfigure-----SpringBoot自动装配机制演示成功！";
        }
    }
}
