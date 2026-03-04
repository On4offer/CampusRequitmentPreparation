package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class InvalidationRunner implements CommandLineRunner {

    @Autowired
    private InvalidationService invalidationService;

    @Autowired
    private AccountRepository accountRepository;

    @Override
    public void run(String... args) throws Exception {
        System.out.println("========== 事务失效场景演示开始 ==========");
        
        // 初始化 5 个账户
        initData();

        // 场景 1: 内部自调用
        try {
            invalidationService.internalCallFailure("Account1", 100.0);
        } catch (Exception e) {
            System.out.println("捕获到异常: " + e.getMessage());
        }
        checkResult("Account1", 1000.0);

        // 场景 2: 非 public 方法
        invalidationService.callProtectedMethod("Account2", 200.0);
        checkResult("Account2", 1000.0);

        // 场景 3: 异常被 catch
        invalidationService.exceptionCaughtFailure("Account3", 300.0);
        checkResult("Account3", 1000.0);

        // 场景 4: 受检异常
        try {
            invalidationService.checkedExceptionFailure("Account4", 400.0);
        } catch (Exception e) {
            System.out.println("捕获到异常: " + e.getMessage());
        }
        checkResult("Account4", 1000.0);

        // 场景 5: 手动 new 对象
        System.out.println("--- 场景 5: 手动 new 对象 (非 Spring Bean) ---");
        try {
            // 1. 手动创建一个普通 Java 对象
            InvalidationService manualService = new InvalidationService();
            // 2. 手动注入 Repository (模拟解决空指针问题)
            manualService.setAccountRepository(accountRepository);
            // 3. 调用带有 @Transactional 的方法
            manualService.doTransferWithTransaction("Account5", 500.0);
        } catch (Exception e) {
            System.out.println("捕获到预期异常: " + e.getMessage());
        }
        checkResult("Account5", 1000.0);

        System.out.println("========== 演示全部结束 ==========");
    }

    private void initData() {
        accountRepository.save(new Account("Account1", 1000.0));
        accountRepository.save(new Account("Account2", 1000.0));
        accountRepository.save(new Account("Account3", 1000.0));
        accountRepository.save(new Account("Account4", 1000.0));
        accountRepository.save(new Account("Account5", 1000.0));
    }

    private void checkResult(String name, Double expected) {
        Double actual = accountRepository.findAll().stream()
                .filter(a -> a.getName().equals(name))
                .findFirst().get().getBalance();
        if (actual.equals(expected)) {
            System.out.println("==> 结果验证: 回滚成功 (余额仍为 " + actual + ")");
        } else {
            System.out.println("==> 结果验证: [事务失效] (余额变为 " + actual + "，预期回滚值为 " + expected + ")");
        }
        System.out.println();
    }
}
