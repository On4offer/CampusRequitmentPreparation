package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

@Component
public class TransactionDemoRunner implements CommandLineRunner {

    @Autowired
    private AccountService accountService;

    @Autowired
    private AccountRepository accountRepository;

    /**
     * 执行账户转账相关场景的演示流程。
     * <p>
     * 该方法用于模拟并验证在不同异常情况下事务的回滚行为，
     * 包括运行时异常、受检异常及其配置回滚条件的情况。
     *
     * @param args 启动参数（可变参数）
     * @throws Exception 启动过程中可能抛出的异常
     */
    @Override
    public void run(String... args) throws Exception {
        // 初始化数据
        System.out.println("\n========== 初始化账户数据 ==========");
        accountRepository.save(new Account("Alice", 1000.0));
        accountRepository.save(new Account("Bob", 1000.0));
        accountService.printAllBalances();

        // 场景 1: 成功转账，无异常发生
        System.out.println("========== 测试成功场景 ==========");
        try {
            accountService.transferSuccess("Alice", "Bob", 100.0);
        } catch (Exception e) {
            System.err.println("发生异常: " + e.getMessage());
        }
        accountService.printAllBalances();

        // 场景 2: 转账过程抛出运行时异常，验证事务是否自动回滚
        System.out.println("\n========== 测试运行时异常场景 ==========");
        try {
            accountService.transferWithRuntimeException("Alice", "Bob", 200.0);
        } catch (Exception e) {
            System.out.println("捕获异常: " + e.getMessage());
        }
        System.out.println("检查余额 (Alice 应为 900.0，说明回滚成功)");
        accountService.printAllBalances();

        // 场景 3: 抛出受检异常，默认不触发事务回滚
        System.out.println("\n========== 测试受检异常场景 ==========");
        try {
            accountService.transferWithCheckedException("Alice", "Bob", 300.0);
        } catch (Exception e) {
            System.out.println("捕获异常: " + e.getMessage());
        }
        System.out.println("检查余额 (Alice 应为 600.0，说明没有回滚)");
        accountService.printAllBalances();

        // 场景 4: 受检异常但通过 rollbackFor 明确指定需回滚
        System.out.println("\n========== 测试受检异常回滚场景 ==========");
        try {
            accountService.transferWithCheckedExceptionAndRollback("Alice", "Bob", 400.0);
        } catch (Exception e) {
            System.out.println("捕获异常: " + e.getMessage());
        }
        System.out.println("检查余额 (Alice 应为 600.0，说明回滚成功)");
        accountService.printAllBalances();

        System.out.println("========== 演示结束 ==========");
    }

}

