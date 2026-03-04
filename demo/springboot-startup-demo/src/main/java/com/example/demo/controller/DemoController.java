package com.example.demo.controller;

import com.example.demo.autoconfigure.DemoAutoConfiguration;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 演示控制器
 * 用于验证SpringBoot应用启动成功并能处理HTTP请求
 */
@RestController
public class DemoController {

    @Autowired(required = false)
    private DemoAutoConfiguration.DemoService demoService;

    @GetMapping("/status")
    public String status() {
        String autoConfigMessage = demoService != null ? 
                demoService.getMessage() : "自动配置服务未加载";
        
        return "<h1>SpringBoot启动流程演示应用</h1>" +
               "<p>应用启动成功！</p>" +
               "<p>自动配置状态：" + autoConfigMessage + "</p>" +
               "<p>访问地址: http://localhost:8080/demo/status</p>" +
               "<p>启动流程已完整执行，包括：</p>" +
               "<ul>" +
               "<li>1. 创建SpringApplication对象</li>" +
               "<li>2. 准备运行环境（Environment）</li>" +
               "<li>3. 打印启动Banner（已关闭，使用自定义日志）</li>" +
               "<li>4. 创建IOC容器（ApplicationContext）</li>" +
               "<li>5. 执行自动装配，完成Bean的加载与实例化</li>" +
               "<li>6. 调用CommandLineRunner / ApplicationRunner收尾</li>" +
               "</ul>";
    }
}
