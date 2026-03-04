package com.example;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * SpringBoot MVC应用程序入口类
 * 
 * 核心特性：
 * 1. 一行@SpringBootApplication注解搞定所有配置
 * 2. 自动扫描com.example包下的所有组件
 * 3. 自动配置DispatcherServlet、视图解析器、消息转换器等
 * 4. 内嵌Tomcat服务器
 */
@SpringBootApplication // 组合了@ComponentScan、@EnableAutoConfiguration、@Configuration三个注解
public class SpringBootMvcApplication {

    public static void main(String[] args) {
        // 一行代码启动整个应用，自动处理所有配置
        SpringApplication.run(SpringBootMvcApplication.class, args);
    }
}