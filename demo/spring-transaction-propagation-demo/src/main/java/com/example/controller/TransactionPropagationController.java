package com.example.controller;

import com.example.service.OrderService;
import com.example.service.PaymentService;
import com.example.service.StockService;
import com.example.service.LogService;
import java.math.BigDecimal;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

/**
 * 事务传播机制演示控制器
 */
@RestController
@RequestMapping("/api/transaction")
public class TransactionPropagationController {

    private static final Logger logger = LoggerFactory.getLogger(TransactionPropagationController.class);

    @Autowired
    private OrderService orderService;

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private StockService stockService;

    @Autowired
    private LogService logService;

    /**
     * 测试REQUIRED传播机制
     */
    @GetMapping("/required")
    public String testRequired() {
        logger.info("开始测试 REQUIRED 传播机制");
        try {
            orderService.createOrderWithRequired(1L, 1L, 2);
            return "REQUIRED 测试成功：订单创建成功，事务提交";
        } catch (Exception e) {
            logger.error("REQUIRED 测试失败", e);
            return "REQUIRED 测试失败：" + e.getMessage();
        }
    }

    /**
     * 测试REQUIRED传播机制（带异常）
     */
    @GetMapping("/required-rollback")
    public String testRequiredWithRollback() {
        logger.info("开始测试 REQUIRED 传播机制（带异常）");
        try {
            // 内部方法会抛出异常，测试事务回滚
            orderService.createOrderWithRequiredAndException(1L, 1L, 2);
            return "不应该执行到这里";
        } catch (Exception e) {
            logger.error("REQUIRED 测试回滚", e);
            return "REQUIRED 测试回滚成功：" + e.getMessage();
        }
    }

    /**
     * 测试REQUIRES_NEW传播机制
     */
    @GetMapping("/requires-new")
    public String testRequiresNew() {
        logger.info("开始测试 REQUIRES_NEW 传播机制");
        try {
            orderService.createOrderWithRequiresNew(1L, 1L, 2);
            return "REQUIRES_NEW 测试成功：订单创建成功";
        } catch (Exception e) {
            logger.error("REQUIRES_NEW 测试失败", e);
            return "REQUIRES_NEW 测试失败：" + e.getMessage();
        }
    }

    /**
     * 测试REQUIRES_NEW传播机制（主事务回滚，内部事务独立）
     */
    @GetMapping("/requires-new-rollback")
    public String testRequiresNewWithRollback() {
        logger.info("开始测试 REQUIRES_NEW 传播机制（主事务回滚）");
        try {
            // 主事务会回滚，但内部事务（日志记录）会提交
            orderService.createOrderWithRequiresNewAndRollback(1L, 1L, 2);
            return "不应该执行到这里";
        } catch (Exception e) {
            logger.error("REQUIRES_NEW 主事务回滚", e);
            return "REQUIRES_NEW 主事务回滚成功，但内部事务（日志）会独立提交：" + e.getMessage();
        }
    }

    /**
     * 测试SUPPORTS传播机制
     */
    @GetMapping("/supports")
    public String testSupports() {
        logger.info("开始测试 SUPPORTS 传播机制");
        try {
            orderService.createOrderWithSupports(1L, 1L, 2);
            return "SUPPORTS 测试成功：订单创建成功";
        } catch (Exception e) {
            logger.error("SUPPORTS 测试失败", e);
            return "SUPPORTS 测试失败：" + e.getMessage();
        }
    }

    /**
     * 测试NOT_SUPPORTED传播机制
     */
    @GetMapping("/not-supported")
    public String testNotSupported() {
        logger.info("开始测试 NOT_SUPPORTED 传播机制");
        try {
            orderService.createOrderWithNotSupported(1L, 1L, 2);
            return "NOT_SUPPORTED 测试成功：订单创建成功";
        } catch (Exception e) {
            logger.error("NOT_SUPPORTED 测试失败", e);
            return "NOT_SUPPORTED 测试失败：" + e.getMessage();
        }
    }

    /**
     * 测试MANDATORY传播机制
     */
    @GetMapping("/mandatory")
    public String testMandatory() {
        logger.info("开始测试 MANDATORY 传播机制");
        try {
            // 直接调用会失败，因为没有事务上下文
            paymentService.deductBalanceWithMandatory(1L, new BigDecimal("100"));
            return "不应该执行到这里";
        } catch (Exception e) {
            logger.error("MANDATORY 测试失败（预期行为）", e);
            return "MANDATORY 测试失败（预期行为）：" + e.getMessage();
        }
    }

    /**
     * 测试MANDATORY传播机制（在事务中调用）
     */
    @GetMapping("/mandatory-with-transaction")
    public String testMandatoryWithTransaction() {
        logger.info("开始测试 MANDATORY 传播机制（在事务中调用）");
        try {
            // 在事务中调用Mandatory方法
            orderService.createOrderWithMandatory(1L, 1L, 2);
            return "MANDATORY 测试成功：在事务中调用成功";
        } catch (Exception e) {
            logger.error("MANDATORY 在事务中调用失败", e);
            return "MANDATORY 在事务中调用失败：" + e.getMessage();
        }
    }

    /**
     * 测试NEVER传播机制
     */
    @GetMapping("/never")
    public String testNever() {
        logger.info("开始测试 NEVER 传播机制");
        try {
            // 直接调用应该成功，因为没有事务上下文
            stockService.deductStockWithNever(1L, 2);
            return "NEVER 测试成功：非事务环境下调用成功";
        } catch (Exception e) {
            logger.error("NEVER 测试失败", e);
            return "NEVER 测试失败：" + e.getMessage();
        }
    }

    /**
     * 测试NEVER传播机制（在事务中调用 - 应该失败）
     */
    @GetMapping("/never-with-transaction")
    public String testNeverWithTransaction() {
        logger.info("开始测试 NEVER 传播机制（在事务中调用）");
        try {
            // 在事务中调用Never方法应该失败
            orderService.createOrderWithNever(1L, 1L, 2);
            return "不应该执行到这里";
        } catch (Exception e) {
            logger.error("NEVER 在事务中调用失败（预期行为）", e);
            return "NEVER 在事务中调用失败（预期行为）：" + e.getMessage();
        }
    }

    /**
     * 测试NESTED传播机制
     */
    @GetMapping("/nested")
    public String testNested() {
        logger.info("开始测试 NESTED 传播机制");
        try {
            orderService.createOrderWithNested(1L, 1L, 2);
            return "NESTED 测试成功：订单创建成功";
        } catch (Exception e) {
            logger.error("NESTED 测试失败", e);
            return "NESTED 测试失败：" + e.getMessage();
        }
    }

    /**
     * 测试NESTED传播机制（内部事务回滚）
     */
    @GetMapping("/nested-inner-rollback")
    public String testNestedWithInnerRollback() {
        logger.info("开始测试 NESTED 传播机制（内部事务回滚）");
        try {
            // 内部事务回滚，但主事务可以继续执行
            orderService.createOrderWithNestedInnerRollback(1L, 1L, 2);
            return "NESTED 内部事务回滚成功，但主事务继续执行";
        } catch (Exception e) {
            logger.error("NESTED 测试失败", e);
            return "NESTED 测试失败：" + e.getMessage();
        }
    }

    /**
     * 测试NESTED传播机制（主事务回滚）
     */
    @GetMapping("/nested-outer-rollback")
    public String testNestedWithOuterRollback() {
        logger.info("开始测试 NESTED 传播机制（主事务回滚）");
        try {
            // 主事务回滚，内部事务也会回滚
            orderService.createOrderWithNestedOuterRollback(1L, 1L, 2);
            return "不应该执行到这里";
        } catch (Exception e) {
            logger.error("NESTED 主事务回滚", e);
            return "NESTED 主事务回滚成功，内部事务也会回滚：" + e.getMessage();
        }
    }

    /**
     * 测试事务自调用问题（传播机制失效）
     */
    @GetMapping("/self-invocation")
    public String testSelfInvocation() {
        logger.info("开始测试事务自调用问题");
        try {
            // 测试同一类中调用事务方法，传播机制可能失效
            orderService.testInternalCall(1L, 1L, 2);
            return "事务自调用测试完成：请注意检查日志了解传播机制是否生效";
        } catch (Exception e) {
            logger.error("事务自调用测试失败", e);
            return "事务自调用测试失败：" + e.getMessage();
        }
    }
}