<%@ page contentType="text/html;charset=UTF-8" language="java" %>
<html>
<head>
    <title>传统SpringMVC示例</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 40px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            border-bottom: 2px solid #4CAF50;
            padding-bottom: 10px;
        }
        .highlight {
            background-color: #e3f2fd;
            padding: 15px;
            border-left: 4px solid #2196F3;
            margin: 20px 0;
        }
        code {
            background-color: #f1f1f1;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: Consolas, monospace;
        }
    </style>
</head>
<body>
<div class="container">
    <h1>传统SpringMVC项目演示</h1>
    
    <div class="highlight">
        <h3>配置说明：</h3>
        <p>✅ 需要在 <code>web.xml</code> 中配置 DispatcherServlet</p>
        <p>✅ 需要在 <code>spring-mvc.xml</code> 中配置：</p>
        <ul>
            <li>组件扫描（component-scan）</li>
            <li>MVC注解驱动（annotation-driven）</li>
            <li>视图解析器（InternalResourceViewResolver）</li>
            <li>静态资源处理（mvc:resources）</li>
            <li>消息转换器（MappingJackson2HttpMessageConverter）</li>
        </ul>
    </div>
    
    <p><strong>消息：</strong> ${message}</p>
    <p><strong>框架：</strong> ${framework}</p>
    
    <h3>访问链接：</h3>
    <ul>
        <li><a href="/traditional/api/data">查看JSON数据接口</a></li>
        <li><a href="/traditional/health">健康检查接口</a></li>
    </ul>
</div>
</body>
</html>