package com.example.demo.runner;

import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.stereotype.Component;

import java.util.Arrays;

/**
 * 自定义CommandLineRunner
 * 演示SpringBoot应用启动完成后（容器初始化完成）执行的回调
 */
@Component
@Order(1) // 设置执行顺序，数值越小优先级越高
public class DemoCommandLineRunner implements CommandLineRunner {

    @Override
    public void run(String... args) throws Exception {
        System.out.println("runner-----[启动阶段6] ======== CommandLineRunner.run被调用 ========");
        System.out.println("runner-----[启动阶段6] 命令行参数: " + Arrays.toString(args));
        System.out.println("runner-----[启动阶段6] 此阶段表示SpringBoot应用已经完成了IOC容器的初始化、Bean的实例化和自动装配");
        System.out.println("runner-----[启动阶段6] 应用即将进入可服务状态，可以在这里执行一些初始化任务");
    }
}
