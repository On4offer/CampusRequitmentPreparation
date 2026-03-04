package com.example.controller;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.HashMap;
import java.util.Map;

/**
 * SpringBoot MVC控制器示例
 * 无需额外配置文件，SpringBoot自动装配了所有必要组件
 */
@Controller
@RequestMapping("/springboot")
public class SpringBootController {

    @Value("${custom.message}")
    private String customMessage;

    /**
     * 返回Thymeleaf视图页面
     * SpringBoot自动配置了Thymeleaf视图解析器
     */
    @GetMapping("/index")
    public String index(Model model) {
        // 无需手动配置视图解析器，SpringBoot自动处理
        model.addAttribute("message", "这是SpringBoot MVC项目的视图页面");
        model.addAttribute("framework", "SpringBoot 2.7.x");
        model.addAttribute("customMessage", customMessage);
        return "index"; // 对应 /templates/index.html
    }

    /**
     * 返回JSON数据
     * SpringBoot自动配置了Jackson消息转换器
     */
    @GetMapping("/api/data")
    @org.springframework.web.bind.annotation.ResponseBody
    public Map<String, Object> getData() {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "这是SpringBoot返回的JSON数据");
        result.put("framework", "SpringBoot MVC");
        result.put("config", "自动配置了Jackson消息转换器");
        return result;
    }

    /**
     * 健康检查接口
     */
    @GetMapping("/health")
    @org.springframework.web.bind.annotation.ResponseBody
    public String health() {
        return "SpringBoot MVC is running!";
    }
}