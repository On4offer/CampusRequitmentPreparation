package com.example.controller;

import com.example.mycustom.MyCustomService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RestController;

/**
 * 自动装配演示控制器
 * 用于展示自动装配的MyCustomService如何工作
 */
@RestController
public class AutoconfigDemoController {

    // 自动注入MyCustomService（由自定义Starter自动装配）
    @Autowired
    private MyCustomService myCustomService;

    /**
     * 测试自动装配的服务是否可用
     * @return 服务状态信息
     */
    @GetMapping("/test")
    public String testAutoconfig() {
        return "自动装配演示：" + myCustomService.getMessage();
    }

    /**
     * 测试自动装配服务的功能
     * @param input 输入参数
     * @return 处理结果
     */
    @GetMapping("/do/{input}")
    public String doSomething(@PathVariable String input) {
        return myCustomService.doSomething(input);
    }

    /**
     * 获取当前应用的自动装配信息
     * @return 应用信息
     */
    @GetMapping("/info")
    public String getInfo() {
        return "SpringBoot自动装配演示应用\n" +
               "- 使用自定义Starter演示自动装配原理\n" +
               "- 通过@SpringBootApplication开启自动装配\n" +
               "- 支持通过application.yml配置自定义服务\n" +
               "- 支持通过@Conditional注解控制装配条件";
    }
}
