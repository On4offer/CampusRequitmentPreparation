package com.example.demo;

import com.example.demo.autoconfigure.DemoAutoConfiguration;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.context.ApplicationContext;
import static org.junit.jupiter.api.Assertions.*;

/**
 * SpringBoot启动流程演示项目的集成测试
 * 验证应用能否正常启动以及自动配置是否正常工作
 */
@SpringBootTest
class SpringBootStartupDemoApplicationTests {

    @Autowired
    private ApplicationContext applicationContext;

    @Test
    void contextLoads() {
        // 验证ApplicationContext是否成功加载
        assertNotNull(applicationContext, "ApplicationContext应该被成功创建");
        System.out.println("[测试] ApplicationContext加载成功");
    }

    @Test
    void testAutoConfiguration() {
        // 验证我们的DemoAutoConfiguration是否生效
        boolean hasDemoService = applicationContext.containsBean("demoService");
        assertTrue(hasDemoService, "demoService应该被自动配置创建");
        System.out.println("[测试] DemoAutoConfiguration自动配置生效，demoService Bean创建成功");

        // 获取并使用demoService
        DemoAutoConfiguration.DemoService demoService = applicationContext.getBean(DemoAutoConfiguration.DemoService.class);
        String message = demoService.getMessage();
        assertEquals("autoconfigure-----SpringBoot自动装配机制演示成功！", message, "demoService的消息应该符合预期");
        System.out.println("[测试] demoService功能正常: " + message);
    }

    @Test
    void testEnvironment() {
        // 验证Environment中的自定义属性是否被正确加载
        String appName = applicationContext.getEnvironment().getProperty("spring.application.name");
        assertEquals("springboot-startup-demo", appName, "应用名称应该从配置文件中正确加载");
        System.out.println("[测试] 配置属性加载成功: spring.application.name = " + appName);
    }
}
