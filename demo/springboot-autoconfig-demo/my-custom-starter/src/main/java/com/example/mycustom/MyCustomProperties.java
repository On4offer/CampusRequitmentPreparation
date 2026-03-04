package com.example.mycustom;

import org.springframework.boot.context.properties.ConfigurationProperties;

/**
 * 自定义Starter的属性配置类
 * 用于绑定application.yml中的my-custom配置项
 */
@ConfigurationProperties(prefix = "my-custom") // 配置属性的前缀
public class MyCustomProperties {

    /**
     * 是否启用自定义功能
     */
    private boolean enabled = true;

    /**
     * 自定义消息
     */
    private String message = "Default Message from Custom Starter";

    /**
     * 超时时间（毫秒）
     */
    private int timeout = 3000;

    // Getters and Setters
    public boolean isEnabled() {
        return enabled;
    }

    public void setEnabled(boolean enabled) {
        this.enabled = enabled;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public int getTimeout() {
        return timeout;
    }

    public void setTimeout(int timeout) {
        this.timeout = timeout;
    }

    @Override
    public String toString() {
        return "MyCustomProperties{" +
                "enabled=" + enabled +
                ", message='" + message + '\'' +
                ", timeout=" + timeout +
                '}';
    }
}