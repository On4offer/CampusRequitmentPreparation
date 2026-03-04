package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AccountService {

    @Autowired
    private AccountRepository accountRepository;

    /**
     * 演示成功提交事务
     */
    @Transactional
    public void transferSuccess(String from, String to, Double amount) {
        System.out.println("--- 执行转账 (成功场景) ---");
        updateBalance(from, -amount);
        updateBalance(to, amount);
        System.out.println("转账逻辑执行完毕，准备提交事务...");
    }

    /**
     * 演示 RuntimeException 导致的回滚
     */
    @Transactional
    public void transferWithRuntimeException(String from, String to, Double amount) {
        System.out.println("--- 执行转账 (运行时异常回滚场景) ---");
        updateBalance(from, -amount);
        
        if (true) {
            throw new RuntimeException("模拟运行时异常，触发事务回滚！");
        }
        
        updateBalance(to, amount);
    }

    /**
     * 演示 Checked Exception (非 RuntimeException) 默认不回滚
     */
    @Transactional
    public void transferWithCheckedException(String from, String to, Double amount) throws Exception {
        System.out.println("--- 执行转账 (受检异常不回滚场景) ---");
        updateBalance(from, -amount);
        
        if (true) {
            throw new Exception("模拟受检异常，默认不回滚事务！");
        }
        
        updateBalance(to, amount);
    }

    /**
     * 演示如何配置受检异常回滚
     */
    @Transactional(rollbackFor = Exception.class)
    public void transferWithCheckedExceptionAndRollback(String from, String to, Double amount) throws Exception {
        System.out.println("--- 执行转账 (配置受检异常回滚场景) ---");
        updateBalance(from, -amount);
        
        if (true) {
            throw new Exception("模拟受检异常，配置了 rollbackFor = Exception.class，触发回滚！");
        }
        
        updateBalance(to, amount);
    }

    private void updateBalance(String name, Double delta) {
        Account account = accountRepository.findAll().stream()
                .filter(a -> a.getName().equals(name))
                .findFirst()
                .orElseThrow(() -> new RuntimeException("账户未找到: " + name));
        account.setBalance(account.getBalance() + delta);
        accountRepository.save(account);
        System.out.println("更新账户 [" + name + "] 余额，变化: " + delta + "，当前余额: " + account.getBalance());
    }

    public void printAllBalances() {
        System.out.println("当前账户信息:");
        accountRepository.findAll().forEach(a -> 
            System.out.println("  ID: " + a.getId() + ", Name: " + a.getName() + ", Balance: " + a.getBalance())
        );
    }
}

