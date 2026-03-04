package com.example.demo.listener;

import org.springframework.boot.context.event.*;
import org.springframework.context.ApplicationEvent;
import org.springframework.context.ApplicationListener;
import org.springframework.context.event.ContextRefreshedEvent;
import org.springframework.context.event.ContextStartedEvent;
/**
 * 自定义ApplicationListener
 * 演示SpringBoot启动过程中各个阶段的事件触发
 * 通过spring.factories注册，而不是@Component注解，以确保能捕获所有早期事件
 */
public class DemoApplicationListener implements ApplicationListener<ApplicationEvent> {

    @Override
    public void onApplicationEvent(ApplicationEvent event) {
        if (event instanceof ApplicationStartingEvent) {
            System.out.println("\nListener------[启动阶段1] ApplicationStartingEvent：应用启动开始，SpringApplication对象创建后触发\n");
        } else if (event instanceof ApplicationEnvironmentPreparedEvent) {
            System.out.println("\nListener------[启动阶段2] ApplicationEnvironmentPreparedEvent：环境变量准备完成，此时ApplicationContext尚未创建\n");
        } else if (event instanceof ApplicationContextInitializedEvent) {
            System.out.println("\nListener------[启动阶段3] ApplicationContextInitializedEvent：ApplicationContext初始化完成，但Bean尚未加载\n");
        } else if (event instanceof ApplicationPreparedEvent) {
            System.out.println("\nListener------[启动阶段4] ApplicationPreparedEvent：ApplicationContext准备完成，Bean定义已加载，但尚未实例化\n");
        } else if (event instanceof ContextRefreshedEvent) {
            System.out.println("\nListener------[启动阶段5] ContextRefreshedEvent：ApplicationContext刷新完成，所有Bean已实例化并初始化\n");
        } else if (event instanceof ApplicationStartedEvent) {
            System.out.println("\nListener------[启动阶段6] ApplicationStartedEvent：Spring容器已完全启动，但CommandLineRunner和ApplicationRunner尚未执行\n");
        } else if (event instanceof ApplicationReadyEvent) {
            System.out.println("\nListener------[启动阶段7] ApplicationReadyEvent：应用已准备就绪，可以开始接收请求，所有Runner已执行完毕\n");
        } else if (event instanceof ContextStartedEvent) {
            System.out.println("\nListener------[启动阶段] ContextStartedEvent：ApplicationContext启动完成\n");
        }
    }
}
