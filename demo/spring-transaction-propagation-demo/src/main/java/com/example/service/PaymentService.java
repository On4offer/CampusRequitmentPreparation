package com.example.service;

import java.math.BigDecimal;

public interface PaymentService {
    // 扣减用户余额 - REQUIRED
    boolean deductBalance(Long userId, BigDecimal amount);
    
    // 扣减用户余额 - REQUIRES_NEW
    boolean deductBalanceWithRequiresNew(Long userId, BigDecimal amount);
    
    // 扣减用户余额 - SUPPORTS
    boolean deductBalanceWithSupports(Long userId, BigDecimal amount);
    
    // 扣减用户余额 - NOT_SUPPORTED
    boolean deductBalanceWithNotSupported(Long userId, BigDecimal amount);
    
    // 扣减用户余额 - MANDATORY
    boolean deductBalanceWithMandatory(Long userId, BigDecimal amount);
    
    // 扣减用户余额 - NEVER
    boolean deductBalanceWithNever(Long userId, BigDecimal amount);
    
    // 扣减用户余额 - NESTED
    boolean deductBalanceWithNested(Long userId, BigDecimal amount);
    
    // 强制抛出异常的方法，用于测试回滚
    void forceException();
}
