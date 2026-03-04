package com.example.service;

public interface LogService {
    // 记录操作日志 - REQUIRES_NEW（确保日志独立提交）
    void recordLog(Long userId, String operation, String content);
    
    // 记录操作日志 - REQUIRED（跟随主事务）
    void recordLogWithRequired(Long userId, String operation, String content);
    
    // 记录操作日志 - NESTED（嵌套事务）
    void recordLogWithNested(Long userId, String operation, String content);
}
