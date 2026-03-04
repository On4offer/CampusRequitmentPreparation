package com.example.controller;

import org.springframework.web.bind.annotation.*;

import java.util.Arrays;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * SpringBoot RESTful API控制器
 * @RestController = @Controller + @ResponseBody，所有方法自动返回JSON
 * 无需额外配置消息转换器，SpringBoot自动配置
 */
@RestController
@RequestMapping("/api/v1")
public class RestApiController {

    // 模拟数据
    private static final List<User> USERS = Arrays.asList(
            new User(1, "张三", "zhangsan@example.com"),
            new User(2, "李四", "lisi@example.com"),
            new User(3, "王五", "wangwu@example.com")
    );

    /**
     * 获取用户列表
     * SpringBoot自动将返回值转换为JSON
     */
    @GetMapping("/users")
    public List<User> getUsers() {
        // 无需@ResponseBody注解，@RestController自动处理
        return USERS;
    }

    /**
     * 根据ID获取用户
     */
    @GetMapping("/users/{id}")
    public User getUserById(@PathVariable Integer id) {
        return USERS.stream()
                .filter(user -> user.getId().equals(id))
                .findFirst()
                .orElse(null);
    }

    /**
     * 创建用户（接收JSON参数，SpringBoot自动反序列化）
     */
    @PostMapping("/users")
    public Map<String, Object> createUser(@RequestBody User user) {
        // SpringBoot自动将请求体JSON转换为User对象
        Map<String, Object> result = new HashMap<>();
        result.put("success", true);
        result.put("message", "用户创建成功");
        result.put("user", user);
        return result;
    }

    /**
     * 用户模型类
     * SpringBoot自动处理JSON序列化和反序列化
     */
    public static class User {
        private Integer id;
        private String name;
        private String email;

        public User() {
        }

        public User(Integer id, String name, String email) {
            this.id = id;
            this.name = name;
            this.email = email;
        }

        // Getters and Setters
        public Integer getId() {
            return id;
        }

        public void setId(Integer id) {
            this.id = id;
        }

        public String getName() {
            return name;
        }

        public void setName(String name) {
            this.name = name;
        }

        public String getEmail() {
            return email;
        }

        public void setEmail(String email) {
            this.email = email;
        }
    }
}