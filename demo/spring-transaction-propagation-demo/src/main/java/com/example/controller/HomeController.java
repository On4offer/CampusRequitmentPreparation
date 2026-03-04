package com.example.controller;

import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.ResponseBody;

/**
 * 首页控制器
 */
@Controller
public class HomeController {

    /**
     * 应用首页 - 显示 API 列表
     */
    @GetMapping("/")
    @ResponseBody
    public String home() {
        return "<!DOCTYPE html>" +
                "<html>" +
                "<head>" +
                "<meta charset='UTF-8'>" +
                "<title>Spring 事务传播机制演示</title>" +
                "<style>" +
                "body { font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }" +
                "h1 { color: #333; }" +
                "h2 { color: #666; margin-top: 30px; }" +
                "ul { list-style-type: none; padding: 0; }" +
                "li { margin: 10px 0; padding: 10px; background-color: white; border-left: 4px solid #007bff; }" +
                "a { color: #007bff; text-decoration: none; font-weight: bold; }" +
                "a:hover { text-decoration: underline; }" +
                ".endpoint { font-family: monospace; color: #28a745; }" +
                ".description { color: #666; font-size: 0.9em; margin-top: 5px; }" +
                "</style>" +
                "</head>" +
                "<body>" +
                "<h1>🚀 Spring 事务传播机制演示</h1>" +
                "<p>欢迎使用 Spring 事务传播机制演示应用！</p>" +
                
                "<h2>📚 API 端点列表</h2>" +
                
                "<h3>REQUIRED 传播机制</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/required' class='endpoint'>GET /api/transaction/required</a>" +
                "<div class='description'>测试 REQUIRED 传播机制（成功场景）</div></li>" +
                "<li><a href='/api/transaction/required-rollback' class='endpoint'>GET /api/transaction/required-rollback</a>" +
                "<div class='description'>测试 REQUIRED 传播机制（回滚场景）</div></li>" +
                "</ul>" +
                
                "<h3>REQUIRES_NEW 传播机制</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/requires-new' class='endpoint'>GET /api/transaction/requires-new</a>" +
                "<div class='description'>测试 REQUIRES_NEW 传播机制</div></li>" +
                "<li><a href='/api/transaction/requires-new-rollback' class='endpoint'>GET /api/transaction/requires-new-rollback</a>" +
                "<div class='description'>测试 REQUIRES_NEW 传播机制（主事务回滚）</div></li>" +
                "</ul>" +
                
                "<h3>SUPPORTS 传播机制</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/supports' class='endpoint'>GET /api/transaction/supports</a>" +
                "<div class='description'>测试 SUPPORTS 传播机制</div></li>" +
                "</ul>" +
                
                "<h3>NOT_SUPPORTED 传播机制</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/not-supported' class='endpoint'>GET /api/transaction/not-supported</a>" +
                "<div class='description'>测试 NOT_SUPPORTED 传播机制</div></li>" +
                "</ul>" +
                
                "<h3>MANDATORY 传播机制</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/mandatory' class='endpoint'>GET /api/transaction/mandatory</a>" +
                "<div class='description'>测试 MANDATORY 传播机制（非事务环境 - 预期失败）</div></li>" +
                "<li><a href='/api/transaction/mandatory-with-transaction' class='endpoint'>GET /api/transaction/mandatory-with-transaction</a>" +
                "<div class='description'>测试 MANDATORY 传播机制（事务环境 - 成功）</div></li>" +
                "</ul>" +
                
                "<h3>NEVER 传播机制</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/never' class='endpoint'>GET /api/transaction/never</a>" +
                "<div class='description'>测试 NEVER 传播机制（非事务环境 - 成功）</div></li>" +
                "<li><a href='/api/transaction/never-with-transaction' class='endpoint'>GET /api/transaction/never-with-transaction</a>" +
                "<div class='description'>测试 NEVER 传播机制（事务环境 - 预期失败）</div></li>" +
                "</ul>" +
                
                "<h3>NESTED 传播机制</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/nested' class='endpoint'>GET /api/transaction/nested</a>" +
                "<div class='description'>测试 NESTED 传播机制</div></li>" +
                "<li><a href='/api/transaction/nested-inner-rollback' class='endpoint'>GET /api/transaction/nested-inner-rollback</a>" +
                "<div class='description'>测试 NESTED 传播机制（内部事务回滚）</div></li>" +
                "<li><a href='/api/transaction/nested-outer-rollback' class='endpoint'>GET /api/transaction/nested-outer-rollback</a>" +
                "<div class='description'>测试 NESTED 传播机制（主事务回滚）</div></li>" +
                "</ul>" +
                
                "<h3>其他测试</h3>" +
                "<ul>" +
                "<li><a href='/api/transaction/self-invocation' class='endpoint'>GET /api/transaction/self-invocation</a>" +
                "<div class='description'>测试事务自调用问题</div></li>" +
                "</ul>" +
                
                "<h2>🔧 其他资源</h2>" +
                "<ul>" +
                "<li><a href='/h2-console' class='endpoint'>H2 数据库控制台</a>" +
                "<div class='description'>访问 H2 内存数据库控制台（JDBC URL: jdbc:h2:mem:transactiondemo）</div></li>" +
                "</ul>" +
                
                "<hr>" +
                "<p style='color: #999; font-size: 0.9em;'>Spring Boot 3.1.10 | Spring 事务传播机制演示</p>" +
                "</body>" +
                "</html>";
    }
}

