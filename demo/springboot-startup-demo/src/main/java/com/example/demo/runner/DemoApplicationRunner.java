package com.example.demo.runner;

import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.util.Set;

/**
 * 自定义ApplicationRunner
 * 演示SpringBoot应用启动完成后的另一种回调机制
 * 与CommandLineRunner类似，但提供了更丰富的参数解析能力
 */
@Component
@Order(2) // 设置执行顺序，数值越小优先级越高
public class DemoApplicationRunner implements ApplicationRunner {

    @Override
    public void run(ApplicationArguments args) throws Exception {
        System.out.println("runner-----[启动阶段6] ======== ApplicationRunner.run被调用 ========");
        
        // 演示ApplicationArguments的功能
        Set<String> optionNames = args.getOptionNames();
        System.out.println("runner-----[启动阶段6] 选项参数名称: " + optionNames);
        
        // 获取所有非选项参数
        System.out.println("runner-----[启动阶段6] 非选项参数: " + args.getNonOptionArgs());
        
        // 获取所有原始参数
        System.out.println("runner-----[启动阶段6] 所有参数: " + args.getSourceArgs());
        
        System.out.println("runner-----[启动阶段6] Runner回调执行完成，应用正式启动成功！");
    }
}
