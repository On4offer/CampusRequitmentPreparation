@echo off

rem SpringBoot MVC项目启动脚本
rem 演示SpringBoot的简化启动方式

echo =====================================
echo        SpringBoot MVC 快速启动脚本
        echo =====================================
echo.
echo 当前目录: %cd%
echo.

:check_maven
    echo 检查Maven环境...
    mvn -v >nul 2>nul
    if %errorlevel% neq 0 (
        echo 错误: 未找到Maven环境，请确保Maven已安装并添加到环境变量中
        pause
        exit /b 1
    )
    echo Maven环境检查通过！
    echo.

:build_springboot
    echo 构建SpringBoot MVC项目...
    cd %~dp0\springboot-mvc
    mvn clean package -DskipTests
    if %errorlevel% neq 0 (
        echo 错误: SpringBoot项目构建失败
        pause
        exit /b 1
    )
    echo SpringBoot项目构建成功！
    echo.

:run_springboot
    echo 启动SpringBoot MVC项目...
    echo 正在启动内嵌Tomcat服务器...
    echo 访问地址: http://localhost:8081/springboot/springboot/index
    echo REST API地址: http://localhost:8081/springboot/api/v1/users
    echo.
    echo 按 Ctrl+C 停止服务
    echo.
    
    rem 直接使用spring-boot:run插件运行
    mvn spring-boot:run
    
    if %errorlevel% neq 0 (
        echo 错误: SpringBoot项目启动失败
        pause
        exit /b 1
    )

exit /b 0