package com.example.service.impl;

import com.example.entity.Log;
import com.example.repository.LogRepository;
import com.example.service.LogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;

@Service
public class LogServiceImpl implements LogService {

    @Autowired
    private LogRepository logRepository;

    /**
     * 记录操作日志 - 使用REQUIRES_NEW传播机制
     * 无论外层是否有事务，都创建新事务，保证日志一定被记录
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void recordLog(Long userId, String operation, String content) {
        Log log = new Log();
        log.setUserId(userId);
        log.setOperation(operation);
        log.setContent(content);
        log.setCreateTime(LocalDateTime.now());
        logRepository.save(log);
        System.out.println("[日志记录成功] 用户ID: " + userId + ", 操作: " + operation);
    }

    /**
     * 记录操作日志 - 使用REQUIRED传播机制
     * 如果外层有事务，则加入外层事务，外层回滚时日志也会回滚
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public void recordLogWithRequired(Long userId, String operation, String content) {
        Log log = new Log();
        log.setUserId(userId);
        log.setOperation(operation);
        log.setContent(content);
        log.setCreateTime(LocalDateTime.now());
        logRepository.save(log);
        System.out.println("[日志记录成功-REQUIRED] 用户ID: " + userId + ", 操作: " + operation);
    }

    /**
     * 记录操作日志 - 使用NESTED传播机制
     * 创建嵌套事务，基于保存点机制
     */
    @Override
    @Transactional(propagation = Propagation.NESTED)
    public void recordLogWithNested(Long userId, String operation, String content) {
        Log log = new Log();
        log.setUserId(userId);
        log.setOperation(operation);
        log.setContent(content);
        log.setCreateTime(LocalDateTime.now());
        logRepository.save(log);
        System.out.println("[日志记录成功-NESTED] 用户ID: " + userId + ", 操作: " + operation);
    }
}
