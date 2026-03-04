package com.example.mycustom;

import org.springframework.boot.autoconfigure.condition.ConditionalOnClass;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * 自定义Starter的自动配置类
 * 演示SpringBoot的自动装配原理
 */
@Configuration // 标记为配置类
@EnableConfigurationProperties(MyCustomProperties.class) // 启用配置属性
@ConditionalOnClass(MyCustomService.class) // 当类路径中存在MyCustomService时才生效
@ConditionalOnProperty( // 当配置项my-custom.enabled为true时才生效，默认值为true
    prefix = "my-custom", 
    name = "enabled", 
    havingValue = "true", 
    matchIfMissing = true
)
public class MyCustomAutoConfiguration {

    private final MyCustomProperties properties;

    /**
     * 构造函数注入配置属性
     * @param properties 配置属性
     */
    public MyCustomAutoConfiguration(MyCustomProperties properties) {
        this.properties = properties;
        System.out.println("=== MyCustomAutoConfiguration初始化 ===");
        System.out.println("配置属性: " + properties);
    }

    /**
     * 自动装配MyCustomService为Spring Bean
     * @return MyCustomService实例
     */
    @Bean
    @ConditionalOnMissingBean // 当Spring容器中不存在MyCustomService Bean时才创建
    public MyCustomService myCustomService() {
        System.out.println("=== 创建MyCustomService Bean ===");
        return new MyCustomService(properties);
    }
}
