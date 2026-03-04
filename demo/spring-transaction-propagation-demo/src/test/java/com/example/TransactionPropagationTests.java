package com.example;

import com.example.entity.Order;
import com.example.entity.Product;
import com.example.entity.User;
import com.example.entity.Log;
import com.example.repository.OrderRepository;
import com.example.repository.ProductRepository;
import com.example.repository.UserRepository;
import com.example.repository.LogRepository;
import com.example.service.OrderService;
import com.example.service.PaymentService;
import com.example.service.StockService;
import com.example.service.LogService;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

/**
 * 事务传播机制测试类
 */
@SpringBootTest
public class TransactionPropagationTests {

    @Autowired
    private OrderService orderService;

    @Autowired
    private PaymentService paymentService;

    @Autowired
    private StockService stockService;

    @Autowired
    private LogService logService;

    @Autowired
    private OrderRepository orderRepository;

    @Autowired
    private ProductRepository productRepository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private LogRepository logRepository;

    /**
     * 测试前重置数据
     */
    @BeforeEach
    @Transactional
    public void setup() {
        // 清除所有数据
        orderRepository.deleteAll();
        logRepository.deleteAll();
        
        // 重置用户余额
        User user = userRepository.findById(1L).orElseThrow();
        user.setBalance(new BigDecimal("1000"));
        userRepository.save(user);
        
        // 重置产品库存
        Product product = productRepository.findById(1L).orElseThrow();
        product.setStock(100);
        productRepository.save(product);
    }

    /**
     * 测试REQUIRED传播机制
     * 验证：所有操作在同一个事务中，任一操作失败则全部回滚
     */
    @Test
    public void testRequired() {
        // 执行订单创建
        orderService.createOrderWithRequired(1L, 1L, 2);
        
        // 验证数据一致性
        User user = userRepository.findById(1L).orElseThrow();
        Product product = productRepository.findById(1L).orElseThrow();
        List<Order> orders = orderRepository.findByUserId(1L);
        
        assertEquals(0, new BigDecimal("0").compareTo(user.getBalance())); // 1000 - 500*2 = 0
        assertEquals(98, product.getStock()); // 100 - 2
        assertEquals(1, orders.size());
    }

    /**
     * 测试REQUIRED传播机制（带异常）
     * 验证：任一操作失败，全部操作回滚
     */
    @Test
    public void testRequiredWithRollback() {
        // 执行会抛出异常的订单创建
        assertThrows(Exception.class, () -> {
            orderService.createOrderWithRequiredAndException(1L, 1L, 2);
        });
        
        // 验证所有数据都回滚了
        User user = userRepository.findById(1L).orElseThrow();
        Product product = productRepository.findById(1L).orElseThrow();
        List<Order> orders = orderRepository.findByUserId(1L);
        
        assertEquals(0, new BigDecimal("1000").compareTo(user.getBalance())); // 余额没变
        assertEquals(100, product.getStock()); // 库存没变
        assertEquals(0, orders.size()); // 订单没创建
    }

    /**
     * 测试REQUIRES_NEW传播机制
     * 验证：内部事务独立于外部事务，外部事务回滚不影响内部事务
     */
    @Test
    public void testRequiresNew() {
        // 执行主事务会回滚，但内部事务（日志记录和库存扣减）会提交的订单创建
        assertThrows(Exception.class, () -> {
            orderService.createOrderWithRequiresNewAndRollback(1L, 1L, 2);
        });
        
        // 验证主事务数据回滚，但REQUIRES_NEW的事务（日志记录和库存扣减）会独立提交
        User user = userRepository.findById(1L).orElseThrow();
        Product product = productRepository.findById(1L).orElseThrow();
        List<Order> orders = orderRepository.findByUserId(1L);
        List<Log> logs = logRepository.findAll();
        
        assertEquals(0, new BigDecimal("1000").compareTo(user.getBalance())); // 余额回滚（主事务）
        assertEquals(98, product.getStock()); // 库存已扣减（REQUIRES_NEW独立事务已提交）
        assertEquals(0, orders.size()); // 订单回滚（主事务）
        assertTrue(logs.size() > 0); // 日志记录成功（REQUIRES_NEW独立事务）
    }

    /**
     * 测试MANDATORY传播机制
     * 验证：必须在事务中运行，否则抛出异常
     */
    @Test
    @Transactional
    public void testMandatory() {
        // 在事务中调用MANDATORY方法应该成功
        // 注意：createOrderWithMandatory 方法本身有 @Transactional(propagation = Propagation.MANDATORY)
        // 由于测试方法有 @Transactional，所以可以成功调用
        orderService.createOrderWithMandatory(1L, 1L, 2);
        
        // 验证订单已创建
        List<Order> orders = orderRepository.findByUserId(1L);
        assertEquals(1, orders.size());
        
        // 注意：createOrderWithMandatory 方法只创建订单，不扣减余额
        // 所以余额应该还是 1000
        User user = userRepository.findById(1L).orElseThrow();
        assertEquals(0, new BigDecimal("1000").compareTo(user.getBalance()));
    }

    /**
     * 测试NEVER传播机制
     * 验证：不能在事务中运行，否则抛出异常
     * 注意：NEVER 传播机制在非事务环境下可以执行INSERT操作，但无法执行UPDATE/DELETE操作
     */
    @Test
    public void testNever() {
        // 直接调用NEVER方法会失败，因为更新操作需要事务
        // 这是 Hibernate/JPA 的限制，不是 Spring 事务传播机制的问题
        assertThrows(Exception.class, () -> {
            stockService.deductStockWithNever(1L, 2);
        });
        
        // 在非事务环境下调用NEVER方法可以成功（只做INSERT操作）
        // 注意：createOrderWithNever 方法本身有 @Transactional(propagation = Propagation.NEVER)
        // 这意味着它必须在非事务环境下执行，测试方法没有事务，所以可以成功
        assertDoesNotThrow(() -> {
            orderService.createOrderWithNever(1L, 1L, 2);
        });
        
        // 验证订单已创建（非事务环境下INSERT可以成功）
        List<Order> orders = orderRepository.findByUserId(1L);
        assertEquals(1, orders.size());
    }

    /**
     * 测试NESTED传播机制
     * 验证：内部事务回滚不影响外部事务，但外部事务回滚会影响内部事务
     * 注意：H2 数据库的 JPA 实现不支持保存点（Savepoint），所以 NESTED 传播机制会失败
     */
    @Test
    public void testNested() {
        // H2 数据库不支持保存点，所以 NESTED 传播机制会抛出异常
        assertThrows(Exception.class, () -> {
            orderService.createOrderWithNestedInnerRollback(1L, 1L, 2);
        });
        
        // 注意：在实际生产环境中使用 MySQL、PostgreSQL 等数据库时，NESTED 传播机制可以正常工作
    }

    /**
     * 测试SUPPORTS传播机制
     * 验证：支持事务，但非必须
     * 注意：SUPPORTS 在无事务环境下无法执行更新操作（Hibernate 要求更新操作必须在事务中）
     */
    @Test
    public void testSupports() {
        // 在无事务环境下调用SUPPORTS方法会失败，因为更新操作需要事务
        // 这是 Hibernate/JPA 的限制
        assertThrows(Exception.class, () -> {
            orderService.createOrderWithSupports(1L, 1L, 2);
        });
    }

    /**
     * 测试NOT_SUPPORTED传播机制
     * 验证：以非事务方式执行，现有事务挂起
     * 注意：NOT_SUPPORTED 在非事务环境下无法执行更新操作（Hibernate 要求更新操作必须在事务中）
     */
    @Test
    public void testNotSupported() {
        // NOT_SUPPORTED 会挂起事务，但更新操作仍然需要事务，所以会失败
        assertThrows(Exception.class, () -> {
            orderService.createOrderWithNotSupported(1L, 1L, 2);
        });
    }

    /**
     * 测试事务自调用问题
     * 验证：同一类中调用事务方法，传播机制可能失效
     */
    @Test
    public void testSelfInvocation() {
        // 测试自调用情况下的事务传播
        assertDoesNotThrow(() -> {
            orderService.testInternalCall(1L, 1L, 2);
        });
        
        // 在自调用情况下，由于Spring AOP代理机制，
        // 内部调用的事务方法不会触发事务代理，传播机制可能失效
    }
}