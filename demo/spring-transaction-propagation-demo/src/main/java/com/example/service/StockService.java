package com.example.service;

/**
 * 库存服务接口
 */
public interface StockService {

    /**
     * 使用REQUIRED传播机制扣减库存
     */
    void deductStockWithRequired(Long productId, Integer quantity);

    /**
     * 使用REQUIRES_NEW传播机制扣减库存
     */
    void deductStockWithRequiresNew(Long productId, Integer quantity);

    /**
     * 使用SUPPORTS传播机制扣减库存
     */
    void deductStockWithSupports(Long productId, Integer quantity);

    /**
     * 使用NOT_SUPPORTED传播机制扣减库存
     */
    void deductStockWithNotSupported(Long productId, Integer quantity);

    /**
     * 使用MANDATORY传播机制扣减库存
     */
    void deductStockWithMandatory(Long productId, Integer quantity);

    /**
     * 使用NEVER传播机制扣减库存
     */
    void deductStockWithNever(Long productId, Integer quantity);

    /**
     * 使用NESTED传播机制扣减库存
     */
    void deductStockWithNested(Long productId, Integer quantity);

    /**
     * 强制抛出异常（用于测试回滚）
     */
    void forceException();
}
