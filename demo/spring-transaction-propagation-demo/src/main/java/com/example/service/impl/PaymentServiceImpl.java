package com.example.service.impl;

import com.example.repository.UserRepository;
import com.example.service.PaymentService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;

@Service
public class PaymentServiceImpl implements PaymentService {

    @Autowired
    private UserRepository userRepository;

    /**
     * 扣减用户余额 - 使用REQUIRED传播机制（默认）
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public boolean deductBalance(Long userId, BigDecimal amount) {
        System.out.println("[REQUIRED] 开始扣减余额，用户ID: " + userId + ", 金额: " + amount);
        int result = userRepository.decreaseBalance(userId, amount);
        boolean success = result > 0;
        System.out.println("[REQUIRED] 扣减余额" + (success ? "成功" : "失败"));
        return success;
    }

    /**
     * 扣减用户余额 - 使用REQUIRES_NEW传播机制
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public boolean deductBalanceWithRequiresNew(Long userId, BigDecimal amount) {
        System.out.println("[REQUIRES_NEW] 开始扣减余额，用户ID: " + userId + ", 金额: " + amount);
        int result = userRepository.decreaseBalance(userId, amount);
        boolean success = result > 0;
        System.out.println("[REQUIRES_NEW] 扣减余额" + (success ? "成功" : "失败"));
        return success;
    }

    /**
     * 扣减用户余额 - 使用SUPPORTS传播机制
     */
    @Override
    @Transactional(propagation = Propagation.SUPPORTS)
    public boolean deductBalanceWithSupports(Long userId, BigDecimal amount) {
        System.out.println("[SUPPORTS] 开始扣减余额，用户ID: " + userId + ", 金额: " + amount);
        int result = userRepository.decreaseBalance(userId, amount);
        boolean success = result > 0;
        System.out.println("[SUPPORTS] 扣减余额" + (success ? "成功" : "失败"));
        return success;
    }

    /**
     * 扣减用户余额 - 使用NOT_SUPPORTED传播机制
     */
    @Override
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    public boolean deductBalanceWithNotSupported(Long userId, BigDecimal amount) {
        System.out.println("[NOT_SUPPORTED] 开始扣减余额，用户ID: " + userId + ", 金额: " + amount);
        int result = userRepository.decreaseBalance(userId, amount);
        boolean success = result > 0;
        System.out.println("[NOT_SUPPORTED] 扣减余额" + (success ? "成功" : "失败"));
        return success;
    }

    /**
     * 扣减用户余额 - 使用MANDATORY传播机制
     */
    @Override
    @Transactional(propagation = Propagation.MANDATORY)
    public boolean deductBalanceWithMandatory(Long userId, BigDecimal amount) {
        System.out.println("[MANDATORY] 开始扣减余额，用户ID: " + userId + ", 金额: " + amount);
        int result = userRepository.decreaseBalance(userId, amount);
        boolean success = result > 0;
        System.out.println("[MANDATORY] 扣减余额" + (success ? "成功" : "失败"));
        return success;
    }

    /**
     * 扣减用户余额 - 使用NEVER传播机制
     */
    @Override
    @Transactional(propagation = Propagation.NEVER)
    public boolean deductBalanceWithNever(Long userId, BigDecimal amount) {
        System.out.println("[NEVER] 开始扣减余额，用户ID: " + userId + ", 金额: " + amount);
        int result = userRepository.decreaseBalance(userId, amount);
        boolean success = result > 0;
        System.out.println("[NEVER] 扣减余额" + (success ? "成功" : "失败"));
        return success;
    }

    /**
     * 扣减用户余额 - 使用NESTED传播机制
     */
    @Override
    @Transactional(propagation = Propagation.NESTED)
    public boolean deductBalanceWithNested(Long userId, BigDecimal amount) {
        System.out.println("[NESTED] 开始扣减余额，用户ID: " + userId + ", 金额: " + amount);
        int result = userRepository.decreaseBalance(userId, amount);
        boolean success = result > 0;
        System.out.println("[NESTED] 扣减余额" + (success ? "成功" : "失败"));
        return success;
    }

    /**
     * 强制抛出异常，用于测试事务回滚
     */
    @Override
    public void forceException() {
        System.out.println("[强制抛出异常] 测试事务回滚");
        throw new RuntimeException("测试事务回滚的异常");
    }
}
