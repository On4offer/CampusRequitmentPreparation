package com.example.service.impl;

import com.example.repository.ProductRepository;
import com.example.service.StockService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

@Service
public class StockServiceImpl implements StockService {

    @Autowired
    private ProductRepository productRepository;

    /**
     * 扣减库存 - 使用REQUIRED传播机制（默认）
     * 如果当前有事务，则加入事务；如果没有，则创建新事务
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public void deductStockWithRequired(Long productId, Integer quantity) {
        System.out.println("[REQUIRED] 开始扣减库存，商品ID: " + productId + ", 数量: " + quantity);
        int result = productRepository.decreaseStock(productId, quantity);
        System.out.println("[REQUIRED] 扣减库存" + (result > 0 ? "成功" : "失败"));
    }

    /**
     * 扣减库存 - 使用REQUIRES_NEW传播机制
     * 总是创建新事务，如果当前有事务则挂起
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public void deductStockWithRequiresNew(Long productId, Integer quantity) {
        System.out.println("[REQUIRES_NEW] 开始扣减库存，商品ID: " + productId + ", 数量: " + quantity);
        int result = productRepository.decreaseStock(productId, quantity);
        System.out.println("[REQUIRES_NEW] 扣减库存" + (result > 0 ? "成功" : "失败"));
    }

    /**
     * 扣减库存 - 使用SUPPORTS传播机制
     * 如果当前有事务，则加入事务；如果没有，则以非事务方式执行
     */
    @Override
    @Transactional(propagation = Propagation.SUPPORTS)
    public void deductStockWithSupports(Long productId, Integer quantity) {
        System.out.println("[SUPPORTS] 开始扣减库存，商品ID: " + productId + ", 数量: " + quantity);
        int result = productRepository.decreaseStock(productId, quantity);
        System.out.println("[SUPPORTS] 扣减库存" + (result > 0 ? "成功" : "失败"));
    }

    /**
     * 扣减库存 - 使用NOT_SUPPORTED传播机制
     * 总是以非事务方式执行，如果当前有事务则挂起
     */
    @Override
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    public void deductStockWithNotSupported(Long productId, Integer quantity) {
        System.out.println("[NOT_SUPPORTED] 开始扣减库存，商品ID: " + productId + ", 数量: " + quantity);
        int result = productRepository.decreaseStock(productId, quantity);
        System.out.println("[NOT_SUPPORTED] 扣减库存" + (result > 0 ? "成功" : "失败"));
    }

    /**
     * 扣减库存 - 使用MANDATORY传播机制
     * 必须在事务中执行，如果当前没有事务则抛出异常
     */
    @Override
    @Transactional(propagation = Propagation.MANDATORY)
    public void deductStockWithMandatory(Long productId, Integer quantity) {
        System.out.println("[MANDATORY] 开始扣减库存，商品ID: " + productId + ", 数量: " + quantity);
        int result = productRepository.decreaseStock(productId, quantity);
        System.out.println("[MANDATORY] 扣减库存" + (result > 0 ? "成功" : "失败"));
    }

    /**
     * 扣减库存 - 使用NEVER传播机制
     * 必须在非事务方式执行，如果当前有事务则抛出异常
     */
    @Override
    @Transactional(propagation = Propagation.NEVER)
    public void deductStockWithNever(Long productId, Integer quantity) {
        System.out.println("[NEVER] 开始扣减库存，商品ID: " + productId + ", 数量: " + quantity);
        int result = productRepository.decreaseStock(productId, quantity);
        System.out.println("[NEVER] 扣减库存" + (result > 0 ? "成功" : "失败"));
    }

    /**
     * 扣减库存 - 使用NESTED传播机制
     * 如果当前有事务，则创建嵌套事务（保存点）；如果没有，则创建新事务
     */
    @Override
    @Transactional(propagation = Propagation.NESTED)
    public void deductStockWithNested(Long productId, Integer quantity) {
        System.out.println("[NESTED] 开始扣减库存，商品ID: " + productId + ", 数量: " + quantity);
        int result = productRepository.decreaseStock(productId, quantity);
        System.out.println("[NESTED] 扣减库存" + (result > 0 ? "成功" : "失败"));
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
