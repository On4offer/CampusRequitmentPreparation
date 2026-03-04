package com.example.config;

import com.example.entity.Product;
import com.example.entity.User;
import com.example.repository.ProductRepository;
import com.example.repository.UserRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

import java.math.BigDecimal;
import java.time.LocalDateTime;

@Component
public class DataInitializer implements CommandLineRunner {

    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private ProductRepository productRepository;

    /**
     * 运行数据初始化任务
     *
     * @param args 可变参数字符串数组，用于接收运行时传入的参数
     * @throws Exception 当初始化过程中发生错误时抛出异常
     */
    @Override
    public void run(String... args) throws Exception {
        // 初始化用户数据
        User user = new User();
        user.setUsername("testuser");
        user.setPassword("123456");
        user.setName("测试用户");
        user.setBalance(new BigDecimal(10000));
        user.setCreateTime(LocalDateTime.now());
        user.setUpdateTime(LocalDateTime.now());
        userRepository.save(user);

        // 初始化产品数据
        Product product = new Product();
        product.setName("测试商品");
        product.setDescription("这是一个测试商品");
        product.setPrice(new BigDecimal(500));
        product.setStock(100);
        product.setCreateTime(LocalDateTime.now());
        product.setUpdateTime(LocalDateTime.now());
        productRepository.save(product);
    }

}
