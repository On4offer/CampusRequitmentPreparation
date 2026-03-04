package com.example.demo.processor;

import org.springframework.beans.BeansException;
import org.springframework.beans.factory.config.BeanDefinition;
import org.springframework.beans.factory.config.ConfigurableListableBeanFactory;
import org.springframework.beans.factory.support.BeanDefinitionRegistry;
import org.springframework.beans.factory.support.BeanDefinitionRegistryPostProcessor;
import org.springframework.stereotype.Component;

import java.util.HashSet;
import java.util.Set;

/**
 * 自定义BeanFactoryPostProcessor
 * 演示在Bean实例化之前对BeanDefinition的处理阶段
 */
@Component
public class DemoBeanFactoryPostProcessor implements BeanDefinitionRegistryPostProcessor {
    
    // 存储启动阶段4的BeanDefinition名称集合，用于后续比较
    private static final Set<String> EARLY_BEAN_DEFINITIONS = new HashSet<>();
    
    /**
     * 获取早期阶段的BeanDefinition名称集合
     * @return 早期阶段的BeanDefinition名称集合
     */
    public static Set<String> getEarlyBeanDefinitions() {
        return new HashSet<>(EARLY_BEAN_DEFINITIONS);
    }

    /**
     * 在Bean定义注册完成后进行后处理操作
     *
     * @param registry Bean定义注册器，用于访问和修改已注册的BeanDefinition
     * @throws BeansException 当处理过程中发生错误时抛出
     */
    @Override
    public void postProcessBeanDefinitionRegistry(BeanDefinitionRegistry registry) throws BeansException {
        System.out.println("\nprocessor-----[启动阶段4] ========== BeanDefinitionRegistryPostProcessor.postProcessBeanDefinitionRegistry被调用 ===========");
        System.out.println("processor-----[启动阶段4] 当前已注册的BeanDefinition数量: " + registry.getBeanDefinitionCount());

        // 保存当前阶段的BeanDefinition名称，用于后续比较
        String[] beanDefinitionNames = registry.getBeanDefinitionNames();
        for (String name : beanDefinitionNames) {
            EARLY_BEAN_DEFINITIONS.add(name);
        }
        System.out.println("processor-----[启动阶段4] 已保存BeanDefinition名称集合，数量: " + EARLY_BEAN_DEFINITIONS.size());

        // 可以在此阶段动态注册新的BeanDefinition
        // 例如：registry.registerBeanDefinition(...);
    }

    /**
     * 在BeanFactory标准初始化之后、任何bean实例化之前调用此方法，
     * 用于修改应用程序上下文的内部bean工厂的bean定义。
     *
     * @param beanFactory 可配置的可列出的bean工厂，提供对bean定义的访问和修改能力
     * @throws BeansException 如果在处理过程中发生bean相关的异常
     */
    @Override
    public void postProcessBeanFactory(ConfigurableListableBeanFactory beanFactory) throws BeansException {
        System.out.println("processor-----[启动阶段4] ======== BeanFactoryPostProcessor.postProcessBeanFactory被调用 ========");
        System.out.println("processor-----[启动阶段4] 当前BeanFactory中的BeanDefinition数量: " + beanFactory.getBeanDefinitionCount());

        // 获取并打印部分BeanDefinition信息
        String[] beanDefinitionNames = beanFactory.getBeanDefinitionNames();
        System.out.println("processor-----[启动阶段4] 部分BeanDefinition名称示例:");
        for (int i = 0; i < Math.min(3, beanDefinitionNames.length); i++) {
            String beanName = beanDefinitionNames[i];
            BeanDefinition beanDefinition = beanFactory.getBeanDefinition(beanName);
            System.out.println("  - " + beanName + " (类型: " + beanDefinition.getBeanClassName() + ")");
        }
    }
}
