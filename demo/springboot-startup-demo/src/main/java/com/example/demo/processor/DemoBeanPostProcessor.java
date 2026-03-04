package com.example.demo.processor;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanPostProcessor;
import org.springframework.stereotype.Component;

/**
 * 自定义BeanPostProcessor
 * 演示Bean实例化过程中对Bean进行前后处理的阶段
 */
@Component
public class DemoBeanPostProcessor implements BeanPostProcessor {

    /**
     * 在Bean初始化之前进行后处理操作
     *
     * @param bean 需要处理的Bean实例
     * @param beanName Bean的名称
     * @return 处理后的Bean实例，可以是原始Bean或包装后的Bean
     * @throws BeansException 如果处理过程中发生错误
     */
    @Override
    public Object postProcessBeforeInitialization(Object bean, String beanName) throws BeansException {
        // 只对我们自己的组件进行打印，避免过多日志
        if (beanName.startsWith("demo") || beanName.equals("demoApplicationListener") ||
            beanName.equals("demoBeanFactoryPostProcessor")) {
            System.out.println("\nprocessor-----[启动阶段5] BeanPostProcessor.postProcessBeforeInitialization: " + beanName);
        }
        return bean; // 返回原始bean或包装后的bean
    }

    /**
     * 在Bean初始化完成后执行的后处理方法
     * 该方法是BeanPostProcessor接口的一部分，在Spring容器完成Bean的初始化后被调用
     *
     * @param bean Spring容器中的Bean实例
     * @param beanName Bean的名称
     * @return 处理后的Bean实例，可以是原始Bean或经过包装的Bean
     * @throws BeansException 如果在处理过程中发生错误
     */
    @Override
    public Object postProcessAfterInitialization(Object bean, String beanName) throws BeansException {
        // 只对我们自己的组件进行打印，避免过多日志
        if (beanName.startsWith("demo") || beanName.equals("demoApplicationListener") ||
            beanName.equals("demoBeanFactoryPostProcessor")) {
            System.out.println("processor-----[启动阶段5] BeanPostProcessor.postProcessAfterInitialization: " + beanName);
        }
        return bean; // 返回原始bean或包装后的bean
    }
}
