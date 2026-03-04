@echo off
chcp 65001 >nul
echo ========================================
echo   动态代理获取私有属性演示程序
echo ========================================
echo.

echo 正在编译项目...
call mvn clean compile -q

if %errorlevel% neq 0 (
    echo 编译失败！
    pause
    exit /b 1
)

echo 编译成功！
echo.
echo 正在运行演示程序...
echo.
echo 注意：如果使用Java 9+，pom.xml已自动配置JVM参数
echo.

call mvn exec:java -q

pause

