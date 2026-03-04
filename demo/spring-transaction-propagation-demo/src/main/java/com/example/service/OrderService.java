package com.example.service;

/**
 * 订单服务接口
 */
public interface OrderService {
    /**
     * 使用REQUIRED传播机制创建订单
     */
    String createOrderWithRequired(Long userId, Long productId, Integer quantity);

    /**
     * 使用REQUIRED传播机制创建订单（带异常回滚）
     */
    String createOrderWithRequiredAndException(Long userId, Long productId, Integer quantity);

    /**
     * 使用REQUIRES_NEW传播机制创建订单
     */
    String createOrderWithRequiresNew(Long userId, Long productId, Integer quantity);

    /**
     * 使用REQUIRES_NEW传播机制创建订单（主事务回滚）
     */
    String createOrderWithRequiresNewAndRollback(Long userId, Long productId, Integer quantity);

    /**
     * 使用SUPPORTS传播机制创建订单
     */
    String createOrderWithSupports(Long userId, Long productId, Integer quantity);

    /**
     * 使用NOT_SUPPORTED传播机制创建订单
     */
    String createOrderWithNotSupported(Long userId, Long productId, Integer quantity);

    /**
     * 使用MANDATORY传播机制创建订单
     */
    String createOrderWithMandatory(Long userId, Long productId, Integer quantity);

    /**
     * 使用NEVER传播机制创建订单
     */
    String createOrderWithNever(Long userId, Long productId, Integer quantity);

    /**
     * 使用NESTED传播机制创建订单
     */
    String createOrderWithNested(Long userId, Long productId, Integer quantity);

    /**
     * 使用NESTED传播机制创建订单（内部回滚）
     */
    String createOrderWithNestedInnerRollback(Long userId, Long productId, Integer quantity);

    /**
     * 使用NESTED传播机制创建订单（外部回滚）
     */
    String createOrderWithNestedOuterRollback(Long userId, Long productId, Integer quantity);

    /**
     * 测试内部调用（事务自调用问题）
     */
    String testInternalCall(Long userId, Long productId, Integer quantity);
}
