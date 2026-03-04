package com.example.demo;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class InvalidationService {

    @Autowired
    private AccountRepository accountRepository;

    // 增加 Setter 方法，方便手动注入演示
    public void setAccountRepository(AccountRepository accountRepository) {
        this.accountRepository = accountRepository;
    }

    /**
     * 失效场景 1: 内部自调用 (Self-Invocation)
     */
    public void internalCallFailure(String from, Double amount) {
        System.out.println("--- 场景 1: 内部自调用 (绕过代理对象) ---");
        // 直接调用内部带有事务的方法，事务不生效
        this.doTransferWithTransaction(from, amount);
    }

    @Transactional
    public void doTransferWithTransaction(String name, Double amount) {
        updateBalance(name, -amount);
        throw new RuntimeException("内部事务方法抛出异常！");
    }

    /**
     * 失效场景 2: 方法非 public
     */
    @Transactional
    protected void protectedMethodFailure(String from, Double amount) {
        System.out.println("--- 场景 2: 非 public 方法 (拦截器忽略) ---");
        updateBalance(from, -amount);
        throw new RuntimeException("非 public 方法抛出异常");
    }

    public void callProtectedMethod(String from, Double amount) {
        try {
            this.protectedMethodFailure(from, amount);
        } catch (Exception e) {
            System.out.println("捕获到异常: " + e.getMessage());
        }
    }

    /**
     * 失效场景 3: 异常被 catch 且未重新抛出
     */
    @Transactional
    public void exceptionCaughtFailure(String from, Double amount) {
        System.out.println("--- 场景 3: 异常被 catch (拦截器感知不到) ---");
        updateBalance(from, -amount);
        try {
            throw new RuntimeException("由于异常被 catch，事务将正常提交");
        } catch (Exception e) {
            System.out.println("捕获了异常: " + e.getMessage());
        }
    }

    /**
     * 失效场景 4: 抛出受检异常 (Checked Exception)
     */
    @Transactional
    public void checkedExceptionFailure(String from, Double amount) throws Exception {
        System.out.println("--- 场景 4: 抛出受检异常 (默认不回滚) ---");
        updateBalance(from, -amount);
        throw new Exception("我是受检异常，Spring 默认不回滚我");
    }

    public void updateBalance(String name, Double delta) {
        Account account = accountRepository.findAll().stream()
                .filter(a -> a.getName().equals(name))
                .findFirst()
                .get();
        account.setBalance(account.getBalance() + delta);
        accountRepository.save(account);
        System.out.println("更新账户 [" + name + "] 余额，变化: " + delta + "，当前余额: " + account.getBalance());
    }
}

