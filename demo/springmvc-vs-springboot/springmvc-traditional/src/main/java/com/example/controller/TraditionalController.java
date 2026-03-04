package com.example.controller;

import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseBody;

import java.util.HashMap;
import java.util.Map;

/**
 * 传统SpringMVC控制器示例
 * 需要通过web.xml配置DispatcherServlet和spring-mvc.xml配置视图解析器等
 */
@Controller
@RequestMapping("/traditional")
public class TraditionalController {

    /**
     * 返回视图页面
     */
    @GetMapping("/index")
    public String index(Model model) {
        // 需要手动配置InternalResourceViewResolver才能正确解析视图路径
        model.addAttribute("message", "这是传统SpringMVC项目的视图页面");
        model.addAttribute("framework", "SpringMVC 5.x");
        return "index"; // 对应 /WEB-INF/views/index.jsp
    }

    /**
     * 返回JSON数据
     * 需要手动配置MappingJackson2HttpMessageConverter
     */
    @GetMapping("/api/data")
    @ResponseBody
    public Map<String, Object> getData() {
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "这是传统SpringMVC返回的JSON数据");
        result.put("framework", "SpringMVC");
        result.put("config", "需要手动配置Jackson消息转换器");
        return result;
    }

    /**
     * 健康检查接口
     */
    @GetMapping("/health")
    @ResponseBody
    public String health() {
        return "Traditional SpringMVC is running!";
    }
}