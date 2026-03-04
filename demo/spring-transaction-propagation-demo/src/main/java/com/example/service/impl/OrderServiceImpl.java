package com.example.service.impl;

import com.example.entity.Order;
import com.example.entity.Product;
import com.example.entity.User;

import com.example.service.LogService;
import com.example.service.OrderService;
import com.example.service.PaymentService;
import com.example.service.StockService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Propagation;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.UUID;

import com.example.repository.OrderRepository;
import com.example.repository.ProductRepository;
import com.example.repository.UserRepository;

@Service
public class OrderServiceImpl implements OrderService {

    @Autowired
    private OrderRepository orderRepository;
    
    @Autowired
    private ProductRepository productRepository;
    
    @Autowired
    private UserRepository userRepository;
    
    @Autowired
    private StockService stockService;
    
    @Autowired
    private PaymentService paymentService;
    
    @Autowired
    private LogService logService;

    /**
     * 创建订单 - 使用REQUIRED传播机制（默认）
     * 场景：普通订单创建流程，所有操作在同一事务中
     */
    /**
     * 创建订单 - 使用REQUIRED传播机制（带异常回滚）
     * 场景：创建订单后抛出异常，测试事务回滚
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public String createOrderWithRequiredAndException(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[REQUIRED_WITH_EXCEPTION] 开始创建订单流程，稍后将抛出异常...");
            
            // 执行与REQUIRED相同的订单创建逻辑
            // 1. 扣减库存
            stockService.deductStockWithRequired(productId, quantity);
            
            // 2. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));
            
            // 3. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 4. 扣减用户余额
            paymentService.deductBalance(userId, totalAmount);
            
            // 5. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 6. 故意抛出异常，测试事务回滚
            System.out.println("[REQUIRED_WITH_EXCEPTION] 准备抛出异常，触发事务回滚...");
            throw new RuntimeException("测试订单创建异常，触发事务回滚");
            
        } catch (Exception e) {
            System.out.println("[REQUIRED_WITH_EXCEPTION] 订单创建失败并回滚：" + e.getMessage());
            // 使用REQUIRES_NEW记录日志，确保即使事务回滚，日志也能保存
            String errorMsg = e.getMessage();
            if (errorMsg != null && errorMsg.length() > 200) {
                errorMsg = errorMsg.substring(0, 200) + "...";
            }
            logService.recordLog(userId, "CREATE_ORDER_EXCEPTION", "订单创建异常并回滚：" + errorMsg);
            throw e;
        }
    }

    /**
     * 创建订单 - 使用REQUIRED传播机制（默认）
     * 场景：普通订单创建流程，所有操作在同一事务中
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public String createOrderWithRequired(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[REQUIRED] 开始创建订单流程...");
            
            // 1. 扣减库存（默认REQUIRED，加入当前事务）
            stockService.deductStockWithRequired(productId, quantity);
            
            // 2. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));
            
            // 3. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 4. 扣减用户余额（默认REQUIRED，加入当前事务）
            paymentService.deductBalance(userId, totalAmount);
            
            // 5. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 6. 记录日志（REQUIRES_NEW，创建新事务，独立提交）
            logService.recordLog(userId, "CREATE_ORDER", "用户下单成功，订单号：" + order.getOrderNo());
            
            System.out.println("[REQUIRED] 订单创建成功，订单号：" + order.getOrderNo());
            return "订单创建成功，订单号：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[REQUIRED] 订单创建失败：" + e.getMessage());
            logService.recordLog(userId, "CREATE_ORDER_FAIL", "订单创建失败：" + truncateErrorMessage(e.getMessage()));
            throw e; // 抛出异常，触发事务回滚
        }
    }

    /**
     * 创建订单 - 使用REQUIRES_NEW传播机制
     * 场景：订单创建在新事务中执行，与外层事务隔离
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    public String createOrderWithRequiresNew(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[REQUIRES_NEW] 开始创建订单流程...");
            
            // 1. 扣减库存（REQUIRES_NEW，创建新事务）
            stockService.deductStockWithRequiresNew(productId, quantity);
            
            // 2. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));
            
            // 3. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 4. 扣减用户余额（REQUIRES_NEW，创建新事务）
            paymentService.deductBalanceWithRequiresNew(userId, totalAmount);
            
            // 5. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 6. 记录日志
            logService.recordLog(userId, "CREATE_ORDER_REQUIRES_NEW", "使用REQUIRES_NEW创建订单成功，订单号：" + order.getOrderNo());
            
            System.out.println("[REQUIRES_NEW] 订单创建成功，订单号：" + order.getOrderNo());
            return "使用REQUIRES_NEW创建订单成功，订单号：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[REQUIRES_NEW] 订单创建失败：" + e.getMessage());
            logService.recordLog(userId, "CREATE_ORDER_REQUIRES_NEW_FAIL", "订单创建失败：" + truncateErrorMessage(e.getMessage()));
            throw e;
        }
    }

    /**
     * 创建订单 - 使用SUPPORTS传播机制
     * 场景：支持事务但不强制，如果外层没有事务则以非事务方式执行
     */
    @Override
    @Transactional(propagation = Propagation.SUPPORTS)
    public String createOrderWithSupports(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[SUPPORTS] 开始创建订单流程...");
            
            // 1. 扣减库存（SUPPORTS，跟随外层事务状态）
            stockService.deductStockWithSupports(productId, quantity);
            
            // 2. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));
            
            // 3. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 4. 扣减用户余额（SUPPORTS，跟随外层事务状态）
            paymentService.deductBalanceWithSupports(userId, totalAmount);
            
            // 5. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 6. 记录日志
            logService.recordLog(userId, "CREATE_ORDER_SUPPORTS", "使用SUPPORTS创建订单成功，订单号：" + order.getOrderNo());
            
            System.out.println("[SUPPORTS] 订单创建成功，订单号：" + order.getOrderNo());
            return "使用SUPPORTS创建订单成功，订单号：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[SUPPORTS] 订单创建失败：" + e.getMessage());
            logService.recordLog(userId, "CREATE_ORDER_SUPPORTS_FAIL", "订单创建失败：" + truncateErrorMessage(e.getMessage()));
            throw e;
        }
    }

    /**
     * 创建订单 - 使用NOT_SUPPORTED传播机制
     * 场景：不支持事务，以非事务方式执行，适合一些对一致性要求不高的操作
     */
    @Override
    @Transactional(propagation = Propagation.NOT_SUPPORTED)
    public String createOrderWithNotSupported(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[NOT_SUPPORTED] 开始创建订单流程（非事务模式）...");
            
            // 注意：这里使用非事务方式执行，数据可能不一致
            // 实际生产环境不建议这样使用，这里仅作演示
            
            // 1. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));

            
            // 2. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 3. 扣减库存和余额（NOT_SUPPORTED，非事务执行）
            stockService.deductStockWithNotSupported(productId, quantity);
            paymentService.deductBalanceWithNotSupported(userId, totalAmount);
            
            // 4. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 5. 记录日志
            logService.recordLog(userId, "CREATE_ORDER_NOT_SUPPORTED", "使用NOT_SUPPORTED创建订单成功，订单号：" + order.getOrderNo());
            
            System.out.println("[NOT_SUPPORTED] 订单创建成功，订单号：" + order.getOrderNo());
            return "使用NOT_SUPPORTED创建订单成功，订单号：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[NOT_SUPPORTED] 订单创建失败：" + e.getMessage());
            logService.recordLog(userId, "CREATE_ORDER_NOT_SUPPORTED_FAIL", "订单创建失败：" + truncateErrorMessage(e.getMessage()));
            throw e;
        }
    }

    /**
     * 创建订单 - 使用MANDATORY传播机制
     * 场景：必须在事务中执行，如果外层没有事务会抛出异常
     */
    @Override
    @Transactional(propagation = Propagation.MANDATORY)
    public String createOrderWithMandatory(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[MANDATORY] 开始创建订单流程（必须在事务中执行）...");
            
            // 1. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));
            
            // 2. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 3. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 4. 记录日志
            logService.recordLog(userId, "CREATE_ORDER_MANDATORY", "使用MANDATORY创建订单成功，订单号：" + order.getOrderNo());
            
            System.out.println("[MANDATORY] 订单创建成功，订单号：" + order.getOrderNo());
            return "使用MANDATORY创建订单成功，订单号：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[MANDATORY] 订单创建失败：" + e.getMessage());
            logService.recordLog(userId, "CREATE_ORDER_MANDATORY_FAIL", "订单创建失败：" + truncateErrorMessage(e.getMessage()));
            throw e;
        }
    }

    /**
     * 创建订单 - 使用NEVER传播机制
     * 场景：必须在非事务中执行，如果外层有事务会抛出异常
     */
    @Override
    @Transactional(propagation = Propagation.NEVER)
    public String createOrderWithNever(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[NEVER] 开始创建订单流程（必须在非事务中执行）...");
            
            // 注意：这里使用非事务方式执行，数据可能不一致
            // 实际生产环境不建议这样使用，这里仅作演示
            
            // 1. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));
            
            // 2. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 3. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PENDING"); // 设置为待支付，因为NEVER模式下无法保证事务一致性
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 4. 记录日志
            logService.recordLog(userId, "CREATE_ORDER_NEVER", "使用NEVER创建订单成功，订单号：" + order.getOrderNo());
            
            System.out.println("[NEVER] 订单创建成功，订单号：" + order.getOrderNo());
            return "使用NEVER创建订单成功，订单号：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[NEVER] 订单创建失败：" + e.getMessage());
            logService.recordLog(userId, "CREATE_ORDER_NEVER_FAIL", "订单创建失败：" + truncateErrorMessage(e.getMessage()));
            throw e;
        }
    }

    /**
     * 创建订单 - 使用NESTED传播机制
     * 场景：嵌套事务，使用保存点机制，内层回滚不影响外层，外层回滚会影响内层
     */
    @Override
    @Transactional(propagation = Propagation.NESTED)
    public String createOrderWithNested(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[NESTED] 开始创建订单流程（嵌套事务）...");
            
            // 1. 扣减库存（NESTED，创建嵌套事务）
            stockService.deductStockWithNested(productId, quantity);
            
            // 2. 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));
            
            // 3. 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 4. 扣减用户余额（NESTED，创建嵌套事务）
            paymentService.deductBalanceWithNested(userId, totalAmount);
            
            // 5. 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 6. 使用嵌套事务记录日志
            logService.recordLogWithNested(userId, "CREATE_ORDER_NESTED", "使用NESTED创建订单成功，订单号：" + order.getOrderNo());
            
            System.out.println("[NESTED] 订单创建成功，订单号：" + order.getOrderNo());
            return "使用NESTED创建订单成功，订单号：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[NESTED] 订单创建失败：" + e.getMessage());
            // 使用REQUIRES_NEW记录日志，确保即使嵌套事务回滚，日志也能保存
            logService.recordLog(userId, "CREATE_ORDER_NESTED_FAIL", "订单创建失败：" + truncateErrorMessage(e.getMessage()));
            throw e;
        }
    }

    /**
     * 测试同一类中内部调用的事务传播（会失效的情况）
     * 说明：Spring的事务是通过代理实现的，同一类中的方法调用不会通过代理，所以事务注解会失效
     */
    @Override
    @Transactional
    public String testInternalCall(Long userId, Long productId, Integer quantity) {
        System.out.println("[内部调用测试] 开始执行...");
        
        // 直接调用本类中的方法，事务注解会失效
        // 正确做法是通过AopContext.currentProxy()获取代理对象再调用
        
        try {
            // 这里直接调用本类方法，事务注解不会生效
            stockService.deductStockWithRequired(productId, quantity);
            
            // 模拟异常
            if (quantity > 5) {
                throw new RuntimeException("测试内部调用的事务回滚");
            }
            
            return "内部调用测试完成";
            
        } catch (Exception e) {
            System.out.println("[内部调用测试] 发生异常：" + e.getMessage());
            // 注意：如果内部调用的方法有事务注解，这里的异常不会触发内部方法的事务回滚
            throw e;
        }
    }

    /**
     * 生成订单号
     */
    private String generateOrderNo() {
        return "ORDER_" + UUID.randomUUID().toString().replace("-", "").substring(0, 16);
    }
    
    /**
     * 截断错误消息，避免日志内容过长
     */
    private String truncateErrorMessage(String message) {
        if (message == null) {
            return "未知错误";
        }
        if (message.length() > 200) {
            return message.substring(0, 200) + "...";
        }
        return message;
    }
    
    /**
     * 创建订单 - 使用REQUIRES_NEW传播机制（主事务回滚）
     * 场景：测试主事务回滚时，内部REQUIRES_NEW事务是否仍然提交
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public String createOrderWithRequiresNewAndRollback(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[主事务] 开始创建订单流程，内部使用REQUIRES_NEW...");
            
            // 扣减库存（REQUIRES_NEW，创建新事务）
            stockService.deductStockWithRequiresNew(productId, quantity);
            
            // 记录日志（REQUIRES_NEW）- 这个操作会独立提交
            logService.recordLog(userId, "CREATE_ORDER_ATTEMPT", "用户尝试创建订单");
            
            // 故意抛出异常，测试主事务回滚但内部事务提交
            throw new RuntimeException("主事务测试回滚，但日志记录应该独立提交");
            
        } catch (Exception e) {
            System.out.println("[主事务] 订单创建失败并回滚：" + e.getMessage());
            throw e;
        }
    }
    
    /**
     * 创建订单 - 使用NESTED传播机制（内部回滚）
     * 场景：测试嵌套事务内部回滚时，不影响外部事务继续执行
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public String createOrderWithNestedInnerRollback(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[外部事务] 开始创建订单流程，测试NESTED内部回滚...");
            
            // 扣减库存（NESTED，嵌套事务）
            stockService.deductStockWithNested(productId, quantity);
            
            // 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));

            
            // 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 扣减用户余额（NESTED，嵌套事务）
            paymentService.deductBalanceWithNested(userId, totalAmount);
            
            // 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            System.out.println("[外部事务] 订单创建成功，即使内部嵌套事务回滚，主事务仍然成功");
            return "订单创建成功：" + order.getOrderNo();
            
        } catch (Exception e) {
            System.out.println("[外部事务] 订单创建失败：" + e.getMessage());
            throw e;
        }
    }
    
    /**
     * 创建订单 - 使用NESTED传播机制（外部回滚）
     * 场景：测试外部事务回滚时，内部嵌套事务也会一起回滚
     */
    @Override
    @Transactional(propagation = Propagation.REQUIRED)
    public String createOrderWithNestedOuterRollback(Long userId, Long productId, Integer quantity) {
        try {
            System.out.println("[外部事务] 开始创建订单流程，测试NESTED外部回滚...");
            
            // 扣减库存（NESTED，嵌套事务）
            stockService.deductStockWithNested(productId, quantity);
            
            // 查询商品和用户信息
            Product product = productRepository.findById(productId).orElseThrow(() -> new RuntimeException("商品不存在"));
            User user = userRepository.findById(userId).orElseThrow(() -> new RuntimeException("用户不存在"));

            
            // 计算订单金额
            BigDecimal totalAmount = product.getPrice().multiply(new BigDecimal(quantity));
            
            // 扣减用户余额（NESTED，嵌套事务）
            paymentService.deductBalanceWithNested(userId, totalAmount);
            
            // 创建订单
            Order order = new Order();
            order.setOrderNo(generateOrderNo());
            order.setUserId(userId);
            order.setProductId(productId);
            order.setQuantity(quantity);
            order.setTotalAmount(totalAmount);
            order.setStatus("PAID");
            order.setCreateTime(LocalDateTime.now());
            order.setUpdateTime(LocalDateTime.now());
            orderRepository.save(order);
            
            // 主事务抛出异常，导致嵌套事务也回滚
            throw new RuntimeException("模拟外部事务异常，测试所有嵌套事务回滚");
            
        } catch (Exception e) {
            System.out.println("[外部事务] 订单创建失败并回滚：" + e.getMessage());
            throw e;
        }
    }
}
