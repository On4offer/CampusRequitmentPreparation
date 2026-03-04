package com.learning.framework;

import java.util.HashMap;
import java.util.Map;
import java.util.ServiceLoader;
import java.util.function.Supplier;

/**
 * 框架结合示例
 * 演示如何在Java项目中集成和使用框架特性
 */
public class FrameworkDemo {
    public static void main(String[] args) {
        // 1. 简单的依赖注入框架示例
        System.out.println("=== 1. 简单的依赖注入框架示例 ===");
        SimpleDIFramework diFramework = new SimpleDIFramework();
        
        // 注册服务
        diFramework.register(ServiceA.class, () -> new ServiceAImpl());
        diFramework.register(ServiceB.class, () -> new ServiceBImpl());
        diFramework.register(Controller.class, () -> new UserController(diFramework.get(ServiceA.class), diFramework.get(ServiceB.class)));
        
        // 获取并使用服务
        Controller controller = diFramework.get(Controller.class);
        controller.process();
        
        // 2. 简单的模板方法模式（框架常用设计模式）
        System.out.println("\n=== 2. 模板方法模式示例 ===");
        AbstractTemplate template1 = new ConcreteTemplate1();
        template1.templateMethod();
        
        AbstractTemplate template2 = new ConcreteTemplate2();
        template2.templateMethod();
        
        // 3. 简单的策略模式（框架常用设计模式）
        System.out.println("\n=== 3. 策略模式示例 ===");
        Context context = new Context(new ConcreteStrategyA());
        context.executeStrategy();
        
        context.setStrategy(new ConcreteStrategyB());
        context.executeStrategy();
        
        // 4. 简单的观察者模式（框架常用设计模式）
        System.out.println("\n=== 4. 观察者模式示例 ===");
        ConcreteSubject subject = new ConcreteSubject();
        Observer observer1 = new ConcreteObserver("观察者1");
        Observer observer2 = new ConcreteObserver("观察者2");
        
        subject.registerObserver(observer1);
        subject.registerObserver(observer2);
        
        subject.notifyObservers("第一个通知");
        subject.unregisterObserver(observer1);
        subject.notifyObservers("第二个通知");
        
        // 5. SPI（服务提供者接口）机制示例
        System.out.println("\n=== 5. SPI机制示例 ===");
        try {
            // 加载所有实现了MyService接口的服务
            ServiceLoader<MyService> serviceLoader = ServiceLoader.load(MyService.class);
            for (MyService service : serviceLoader) {
                System.out.println("SPI服务实现: " + service.getClass().getName());
                service.doSomething();
            }
        } catch (Exception e) {
            System.out.println("SPI加载失败: " + e.getMessage());
            System.out.println("注意：要使用SPI，需要在META-INF/services/下创建相应的配置文件");
        }
        
        // 6. 简单的AOP（面向切面编程）示例
        System.out.println("\n=== 6. 简单的AOP示例 ===");
        SimpleAOP aop = new SimpleAOP();
        
        // 创建目标对象
        UserService userService = new UserServiceImpl();
        
        // 创建代理对象
        UserService proxy = (UserService) aop.createProxy(userService, 
                (target, method, args1) -> {
                    System.out.println("[AOP] 方法执行前: " + method.getName());
                    try {
                        Object result = method.invoke(target, args1);
                        System.out.println("[AOP] 方法执行后: " + method.getName());
                        return result;
                    } catch (Exception e) {
                        System.out.println("[AOP] 方法执行异常: " + e.getMessage());
                        throw e.getCause();
                    }
                });
        
        // 通过代理对象调用方法
        proxy.addUser("张三");
        proxy.deleteUser("李四");
    }
}

// 1. 简单的依赖注入框架
class SimpleDIFramework {
    private final Map<Class<?>, Supplier<?>> registry = new HashMap<>();
    
    public <T> void register(Class<T> type, Supplier<T> supplier) {
        registry.put(type, supplier);
    }
    
    @SuppressWarnings("unchecked")
    public <T> T get(Class<T> type) {
        Supplier<?> supplier = registry.get(type);
        if (supplier == null) {
            throw new IllegalArgumentException("未注册的类型: " + type.getName());
        }
        return (T) supplier.get();
    }
}

// 服务接口和实现
interface ServiceA {
    void operationA();
}

class ServiceAImpl implements ServiceA {
    @Override
    public void operationA() {
        System.out.println("执行ServiceA的操作");
    }
}

interface ServiceB {
    void operationB();
}

class ServiceBImpl implements ServiceB {
    @Override
    public void operationB() {
        System.out.println("执行ServiceB的操作");
    }
}

interface Controller {
    void process();
}

class UserController implements Controller {
    private final ServiceA serviceA;
    private final ServiceB serviceB;
    
    public UserController(ServiceA serviceA, ServiceB serviceB) {
        this.serviceA = serviceA;
        this.serviceB = serviceB;
    }
    
    @Override
    public void process() {
        System.out.println("控制器处理请求");
        serviceA.operationA();
        serviceB.operationB();
        System.out.println("控制器处理完成");
    }
}

// 2. 模板方法模式
abstract class AbstractTemplate {
    // 模板方法，定义算法骨架
    public final void templateMethod() {
        System.out.println("模板方法开始执行");
        step1();
        step2(); // 抽象方法，由子类实现
        step3();
        System.out.println("模板方法执行完成\n");
    }
    
    private void step1() {
        System.out.println("步骤1: 固定实现");
    }
    
    protected abstract void step2(); // 抽象步骤
    
    private void step3() {
        System.out.println("步骤3: 固定实现");
    }
}

class ConcreteTemplate1 extends AbstractTemplate {
    @Override
    protected void step2() {
        System.out.println("模板1: 实现步骤2");
    }
}

class ConcreteTemplate2 extends AbstractTemplate {
    @Override
    protected void step2() {
        System.out.println("模板2: 实现步骤2");
    }
}

// 3. 策略模式
interface Strategy {
    void execute();
}

class ConcreteStrategyA implements Strategy {
    @Override
    public void execute() {
        System.out.println("执行策略A");
    }
}

class ConcreteStrategyB implements Strategy {
    @Override
    public void execute() {
        System.out.println("执行策略B");
    }
}

class Context {
    private Strategy strategy;
    
    public Context(Strategy strategy) {
        this.strategy = strategy;
    }
    
    public void setStrategy(Strategy strategy) {
        this.strategy = strategy;
    }
    
    public void executeStrategy() {
        strategy.execute();
    }
}

// 4. 观察者模式
interface Observer {
    void update(String message);
}

class ConcreteObserver implements Observer {
    private final String name;
    
    public ConcreteObserver(String name) {
        this.name = name;
    }
    
    @Override
    public void update(String message) {
        System.out.println(name + " 收到消息: " + message);
    }
}

interface Subject {
    void registerObserver(Observer observer);
    void unregisterObserver(Observer observer);
    void notifyObservers(String message);
}

class ConcreteSubject implements Subject {
    private final java.util.List<Observer> observers = new java.util.ArrayList<>();
    
    @Override
    public void registerObserver(Observer observer) {
        observers.add(observer);
    }
    
    @Override
    public void unregisterObserver(Observer observer) {
        observers.remove(observer);
    }
    
    @Override
    public void notifyObservers(String message) {
        for (Observer observer : observers) {
            observer.update(message);
        }
    }
}

// 5. SPI服务接口
interface MyService {
    void doSomething();
}

// 示例服务实现（实际使用时需要创建配置文件）
class MyServiceImpl1 implements MyService {
    @Override
    public void doSomething() {
        System.out.println("MyService实现1执行操作");
    }
}

class MyServiceImpl2 implements MyService {
    @Override
    public void doSomething() {
        System.out.println("MyService实现2执行操作");
    }
}

// 6. 简单的AOP示例
class SimpleAOP {
    @FunctionalInterface
    interface InvocationHandler {
        Object invoke(Object target, java.lang.reflect.Method method, Object[] args) throws Throwable;
    }
    
    public Object createProxy(Object target, InvocationHandler handler) {
        return java.lang.reflect.Proxy.newProxyInstance(
                target.getClass().getClassLoader(),
                target.getClass().getInterfaces(),
                (proxy, method, args) -> handler.invoke(target, method, args)
        );
    }
}

// AOP示例服务
interface UserService {
    void addUser(String username);
    void deleteUser(String username);
}

class UserServiceImpl implements UserService {
    @Override
    public void addUser(String username) {
        System.out.println("添加用户: " + username);
    }
    
    @Override
    public void deleteUser(String username) {
        System.out.println("删除用户: " + username);
    }
}