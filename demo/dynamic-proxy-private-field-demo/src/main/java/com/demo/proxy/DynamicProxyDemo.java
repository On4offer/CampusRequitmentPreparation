package com.demo.proxy;

import java.lang.reflect.Field;

/**
 * 动态代理获取私有属性演示主类
 * 
 * 本演示包含以下内容：
 * 1. JDK动态代理获取私有属性
 * 2. CGLIB动态代理获取私有属性
 * 3. 获取父类私有属性
 * 4. 对比验证：通过getter方法验证私有属性是否真的被修改
 */
public class DynamicProxyDemo {
    
    public static void main(String[] args) {
        System.out.println("========================================");
        System.out.println("   动态代理获取私有属性演示程序");
        System.out.println("========================================\n");
        System.out.println("【执行位置】DynamicProxyDemo.main() - 程序入口");
        System.out.println("【当前操作】启动演示程序，依次执行4个演示\n");
        
        // ========== 演示1：JDK动态代理获取私有属性 ==========
        System.out.println(">>> 准备执行演示1：JDK动态代理获取私有属性");
        demonstrateJdkProxy();
        
        System.out.println("\n\n");
        
        // ========== 演示2：CGLIB动态代理获取私有属性 ==========
        System.out.println(">>> 准备执行演示2：CGLIB动态代理获取私有属性");
        demonstrateCglibProxy();
        
        System.out.println("\n\n");
        
        // ========== 演示3：获取父类私有属性 ==========
        System.out.println(">>> 准备执行演示3：获取父类私有属性");
        demonstrateParentClassPrivateField();
        
        System.out.println("\n\n");
        
        // ========== 演示4：对比验证 - 直接操作目标对象 ==========
        System.out.println(">>> 准备执行演示4：直接操作目标对象（对比验证）");
        demonstrateDirectAccess();
        
        System.out.println("\n【执行位置】DynamicProxyDemo.main() - 程序结束");
        System.out.println("【当前操作】所有演示执行完成");
    }
    
    /**
     * 演示1：JDK动态代理获取私有属性
     */
    private static void demonstrateJdkProxy() {
        System.out.println("========== 演示1：JDK动态代理获取私有属性 ==========");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateJdkProxy()");
        System.out.println("【当前操作】开始JDK动态代理演示\n");
        
        // 创建目标对象
        System.out.println("【步骤1】创建目标对象");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateJdkProxy() - new UserServiceImpl()");
        System.out.println("【当前操作】实例化UserServiceImpl对象");
        UserService target = new UserServiceImpl();
        System.out.println("【结果】目标对象创建成功，类型：" + target.getClass().getName());
        System.out.println("【当前操作】通过getter方法读取初始私有属性值（用于后续对比）");
        System.out.println("初始私有属性值（通过getter）：");
        System.out.println("  - privateField = " + ((UserServiceImpl) target).getPrivateField());
        System.out.println("  - privateNum = " + ((UserServiceImpl) target).getPrivateNum());
        
        // 创建代理对象
        System.out.println("\n【步骤2】创建JDK动态代理对象");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateJdkProxy() - 调用JdkProxyHandler.createProxy()");
        System.out.println("【当前操作】准备调用静态方法创建代理对象");
        UserService proxy = (UserService) JdkProxyHandler.createProxy(target);
        System.out.println("【结果】代理对象创建完成，返回类型：" + proxy.getClass().getName());
        
        System.out.println("\n【步骤3】通过代理对象调用方法");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateJdkProxy() - proxy.doSomething()");
        System.out.println("【当前操作】调用代理对象的doSomething()方法");
        System.out.println("【框架自动完成】JDK代理框架会拦截此方法调用，转发到InvocationHandler.invoke()");
        proxy.doSomething();
        
        System.out.println("\n【步骤4】验证私有属性是否被修改");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateJdkProxy()");
        System.out.println("【当前操作】通过getter方法验证目标对象的私有属性是否被代理修改");
        System.out.println("修改后的私有属性值（通过getter）：");
        System.out.println("  - privateField = " + ((UserServiceImpl) target).getPrivateField());
        System.out.println("  - privateNum = " + ((UserServiceImpl) target).getPrivateNum());
        
        System.out.println("\n【执行位置】DynamicProxyDemo.demonstrateJdkProxy() - 方法结束");
        System.out.println("【关键观察点】");
        System.out.println("1. 代理对象成功读取并修改了目标对象的私有属性");
        System.out.println("2. 通过getter方法验证，私有属性确实被修改了");
        System.out.println("3. 注意：操作的是target对象，不是proxy对象");
    }
    
    /**
     * 演示2：CGLIB动态代理获取私有属性
     */
    private static void demonstrateCglibProxy() {
        System.out.println("========== 演示2：CGLIB动态代理获取私有属性 ==========");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateCglibProxy()");
        System.out.println("【当前操作】开始CGLIB动态代理演示\n");
        
        // 创建目标对象
        System.out.println("【步骤1】创建目标对象");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateCglibProxy() - new OrderService()");
        System.out.println("【当前操作】实例化OrderService对象");
        OrderService target = new OrderService();
        System.out.println("【结果】目标对象创建成功，类型：" + target.getClass().getName());
        System.out.println("【当前操作】通过getter方法读取初始私有属性值（用于后续对比）");
        System.out.println("初始私有属性值（通过getter）：");
        System.out.println("  - orderNo = " + target.getOrderNo());
        System.out.println("  - amount = " + target.getAmount());
        System.out.println("  - status = " + target.getStatus());
        
        try {
            // 创建代理对象
            System.out.println("\n【步骤2】创建CGLIB动态代理对象");
            System.out.println("【执行位置】DynamicProxyDemo.demonstrateCglibProxy() - 创建CglibProxyInterceptor并调用createProxy()");
            System.out.println("【当前操作】准备创建CGLIB代理对象");
            OrderService proxy = (OrderService) new CglibProxyInterceptor(target).createProxy();
            System.out.println("【结果】代理对象创建完成，返回类型：" + proxy.getClass().getName());
            
            System.out.println("\n【步骤3】通过代理对象调用方法");
            System.out.println("【执行位置】DynamicProxyDemo.demonstrateCglibProxy() - proxy.processOrder()");
            System.out.println("【当前操作】调用代理对象的processOrder()方法");
            System.out.println("【框架自动完成】CGLIB代理框架会拦截此方法调用，转发到MethodInterceptor.intercept()");
            proxy.processOrder();
            
            System.out.println("\n【步骤4】验证私有属性是否被修改");
            System.out.println("【执行位置】DynamicProxyDemo.demonstrateCglibProxy()");
            System.out.println("【当前操作】通过getter方法验证目标对象的私有属性是否被代理修改");
            System.out.println("修改后的私有属性值（通过getter）：");
            System.out.println("  - orderNo = " + target.getOrderNo());
            System.out.println("  - amount = " + target.getAmount());
            System.out.println("  - status = " + target.getStatus());
            
            System.out.println("\n【执行位置】DynamicProxyDemo.demonstrateCglibProxy() - 方法结束");
            System.out.println("【关键观察点】");
            System.out.println("1. CGLIB代理对象成功读取并修改了目标对象的私有属性");
            System.out.println("2. CGLIB不需要接口，可以直接代理类");
            System.out.println("3. 代理对象是目标类的子类");
            
        } catch (ExceptionInInitializerError e) {
            if (e.getCause() != null && e.getCause().getMessage() != null 
                && e.getCause().getMessage().contains("InaccessibleObjectException")) {
                System.err.println("\n❌ 【错误】CGLIB代理创建失败：Java模块化限制");
                System.err.println("\n═══════════════════════════════════════════════════════");
                System.err.println("   解决方案：在IntelliJ IDEA中添加VM参数");
                System.err.println("═══════════════════════════════════════════════════════");
                System.err.println("\n📝 详细步骤：");
                System.err.println("1. 点击右上角的运行配置下拉菜单（显示 'DynamicProxyDemo' 的位置）");
                System.err.println("2. 选择 'Edit Configurations...'（或点击 'Modify run configuration...'）");
                System.err.println("3. 在左侧找到 'DynamicProxyDemo' 配置");
                System.err.println("4. 在右侧找到 'VM options' 输入框");
                System.err.println("   （如果没有看到，点击 'Modify options' → 勾选 'Add VM options'）");
                System.err.println("5. 在 'VM options' 中输入以下内容：");
                System.err.println("   --add-opens java.base/java.lang=ALL-UNNAMED");
                System.err.println("6. 点击 'Apply' → 'OK'");
                System.err.println("7. 重新运行程序");
                System.err.println("\n💡 或者使用Maven运行（已自动配置）：");
                System.err.println("   mvn clean compile");
                System.err.println("   mvn exec:java");
                System.err.println("\n═══════════════════════════════════════════════════════\n");
                
                // 显示当前Java版本信息
                String javaVersion = System.getProperty("java.version");
                System.out.println("当前Java版本: " + javaVersion);
                System.out.println("检测到Java 9+，CGLIB需要VM参数支持\n");
            } else {
                e.printStackTrace();
            }
        } catch (Exception e) {
            System.err.println("\n❌ CGLIB代理创建失败：" + e.getMessage());
            e.printStackTrace();
        }
    }
    
    /**
     * 演示3：获取父类私有属性
     */
    private static void demonstrateParentClassPrivateField() {
        System.out.println("========== 演示3：获取父类私有属性 ==========");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateParentClassPrivateField()");
        System.out.println("【当前操作】开始演示获取父类私有属性\n");
        
        // 创建子类对象
        System.out.println("【步骤1】创建子类对象");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateParentClassPrivateField() - new ChildService()");
        System.out.println("【当前操作】实例化ChildService对象（继承自ParentService）");
        ChildService child = new ChildService();
        System.out.println("【结果】子类对象创建成功");
        System.out.println("  - 子类类型：" + child.getClass().getName());
        System.out.println("  - 父类类型：" + child.getClass().getSuperclass().getName());
        
        System.out.println("\n【步骤2】使用反射工具类获取父类私有属性");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateParentClassPrivateField() - 调用ReflectionUtils.getPrivateFieldValue()");
        
        // 获取父类的私有属性
        System.out.println("\n【操作2.1】获取父类私有属性 parentPrivateField");
        Object parentFieldValue = ReflectionUtils.getPrivateFieldValue(child, "parentPrivateField");
        System.out.println("【结果】父类私有属性 parentPrivateField 的值：" + parentFieldValue);
        
        System.out.println("\n【操作2.2】获取父类私有属性 parentPrivateNum");
        Object parentNumValue = ReflectionUtils.getPrivateFieldValue(child, "parentPrivateNum");
        System.out.println("【结果】父类私有属性 parentPrivateNum 的值：" + parentNumValue);
        
        // 修改父类的私有属性
        System.out.println("\n【步骤3】修改父类私有属性");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateParentClassPrivateField() - 调用ReflectionUtils.setPrivateFieldValue()");
        System.out.println("【操作3.1】修改 parentPrivateField");
        ReflectionUtils.setPrivateFieldValue(child, "parentPrivateField", "修改后的父类私有属性");
        System.out.println("【操作3.2】修改 parentPrivateNum");
        ReflectionUtils.setPrivateFieldValue(child, "parentPrivateNum", 888);
        
        // 再次读取验证
        System.out.println("\n【步骤4】验证修改结果");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateParentClassPrivateField() - 再次调用ReflectionUtils.getPrivateFieldValue()");
        System.out.println("【当前操作】重新读取父类私有属性，验证是否修改成功");
        Object newParentFieldValue = ReflectionUtils.getPrivateFieldValue(child, "parentPrivateField");
        System.out.println("【结果】修改后的父类私有属性 parentPrivateField 的值：" + newParentFieldValue);
        
        Object newParentNumValue = ReflectionUtils.getPrivateFieldValue(child, "parentPrivateNum");
        System.out.println("【结果】修改后的父类私有属性 parentPrivateNum 的值：" + newParentNumValue);
        
        // 获取子类自己的私有属性
        System.out.println("\n【步骤5】获取子类自己的私有属性");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateParentClassPrivateField() - 调用ReflectionUtils.getPrivateFieldValue()");
        System.out.println("【当前操作】获取子类自己的私有属性 childPrivateField");
        Object childFieldValue = ReflectionUtils.getPrivateFieldValue(child, "childPrivateField");
        System.out.println("【结果】子类私有属性 childPrivateField 的值：" + childFieldValue);
        
        System.out.println("\n【执行位置】DynamicProxyDemo.demonstrateParentClassPrivateField() - 方法结束");
        System.out.println("【关键观察点】");
        System.out.println("1. 反射工具类递归查找父类，成功获取父类私有属性");
        System.out.println("2. 可以读取和修改父类的私有属性");
        System.out.println("3. 同样可以获取子类自己的私有属性");
    }
    
    /**
     * 演示4：直接操作目标对象（对比验证）
     */
    private static void demonstrateDirectAccess() {
        System.out.println("========== 演示4：直接操作目标对象（对比验证） ==========");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateDirectAccess()");
        System.out.println("【当前操作】开始演示直接使用反射修改私有属性（不使用代理）\n");
        
        System.out.println("【步骤1】创建目标对象");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateDirectAccess() - new UserServiceImpl()");
        System.out.println("【当前操作】实例化UserServiceImpl对象");
        UserServiceImpl target = new UserServiceImpl();
        System.out.println("【当前操作】通过getter方法读取初始私有属性值");
        System.out.println("初始值（通过getter）：");
        System.out.println("  - privateField = " + target.getPrivateField());
        System.out.println("  - privateNum = " + target.getPrivateNum());
        
        System.out.println("\n【步骤2】直接使用反射修改私有属性（不使用代理）");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateDirectAccess() - 直接使用反射API");
        System.out.println("【当前操作】不使用代理，直接通过反射API操作私有属性");
        try {
            System.out.println("【操作2.1】获取privateField字段对象");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"privateField\")");
            Field field = target.getClass().getDeclaredField("privateField");
            System.out.println("  -> 调用：field.setAccessible(true) - 突破访问限制");
            field.setAccessible(true);
            System.out.println("  -> 调用：field.set(target, \"直接反射修改的值\") - 修改字段值");
            field.set(target, "直接反射修改的值");
            
            System.out.println("\n【操作2.2】获取privateNum字段对象");
            System.out.println("  -> 调用：target.getClass().getDeclaredField(\"privateNum\")");
            Field numField = target.getClass().getDeclaredField("privateNum");
            System.out.println("  -> 调用：numField.setAccessible(true) - 突破访问限制");
            numField.setAccessible(true);
            System.out.println("  -> 调用：numField.set(target, 999) - 修改字段值");
            numField.set(target, 999);
            
            System.out.println("\n【结果】修改完成！");
        } catch (Exception e) {
            System.err.println("【错误】反射操作失败");
            e.printStackTrace();
        }
        
        System.out.println("\n【步骤3】验证修改结果");
        System.out.println("【执行位置】DynamicProxyDemo.demonstrateDirectAccess()");
        System.out.println("【当前操作】通过getter方法验证私有属性是否被修改");
        System.out.println("修改后的值（通过getter）：");
        System.out.println("  - privateField = " + target.getPrivateField());
        System.out.println("  - privateNum = " + target.getPrivateNum());
        
        System.out.println("\n【执行位置】DynamicProxyDemo.demonstrateDirectAccess() - 方法结束");
        System.out.println("【关键观察点】");
        System.out.println("1. 直接使用反射也可以修改私有属性");
        System.out.println("2. 动态代理的本质就是在代理逻辑中使用反射");
        System.out.println("3. 代理对象本身不包含目标类的私有属性，必须操作target对象");
        
        System.out.println("\n【手动操作建议】");
        System.out.println("1. 尝试修改 UserServiceImpl 中的私有属性初始值，观察输出变化");
        System.out.println("2. 尝试在代理处理器中操作 proxy 对象而不是 target 对象，观察会发生什么");
        System.out.println("3. 尝试不调用 setAccessible(true)，观察会发生什么");
        System.out.println("4. 尝试修改 final 修饰的私有属性，观察会发生什么");
    }
}

