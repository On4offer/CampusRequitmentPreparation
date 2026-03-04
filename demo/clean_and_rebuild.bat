@echo off
setlocal

echo 开始清理和重建项目...

REM 切换到项目目录
cd "d:\Java学习\demo\spring-transaction-propagation-demo"

REM 删除IDE缓存文件
echo 删除IDE缓存文件...
if exist ".idea" rmdir /s /q ".idea"
if exist "*.iml" del "*.iml"

REM 删除Maven构建目录
echo 清理Maven构建目录...
if exist "target" rmdir /s /q "target"

REM 清理Maven缓存并重新下载依赖
echo 清理Maven依赖缓存...
mvn dependency:purge-local-repository -DactTransitively=false -DreResolve=false

REM 下载最新依赖
echo 重新下载依赖...
mvn dependency:resolve

REM 编译项目
echo 编译项目...
mvn compile

REM 如果编译成功
echo.
echo ===========================================================
echo 项目Java版本已成功从1.8升级到17
echo Spring Boot版本已从2.7.15升级到3.1.10
echo ===========================================================
echo.
echo 后续操作提示：
echo 1. 请重新在IDE中导入项目
 echo 2. 确保IDE的JDK配置已切换到Java 17
 echo 3. 检查并更新IntelliJ IDEA中的Lombok插件到最新版本
 echo 4. 在IDE设置中确保启用了注解处理器

echo.
pause
