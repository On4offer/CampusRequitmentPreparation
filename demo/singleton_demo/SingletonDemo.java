package singleton_demo;

/**
 * 单例模式（Singleton Pattern）演示
 * 
 * 单例模式是一种创建型设计模式，它保证一个类只有一个实例，并提供一个全局访问点。
 * 
 * 本文件演示了7种常见的单例模式实现方式，并详细说明了每种方式的关键步骤和作用。
 */
public class SingletonDemo {
    
    // ==================== 方式1：饿汉式（静态常量）====================
    /**
     * 优点：
     * 1. 实现简单，线程安全（JVM类加载机制保证）
     * 2. 在类加载时就创建实例，避免了线程同步问题
     * 
     * 缺点：
     * 1. 没有延迟加载，如果实例从未使用，会造成内存浪费
     * 2. 如果实例创建依赖参数或配置文件，无法使用此方式
     */
    static class EagerSingleton1 {
        // 关键步骤1：私有化构造函数，防止外部通过new创建实例
        private EagerSingleton1() {
            System.out.println("饿汉式（静态常量）- 实例被创建");
        }
        
        // 关键步骤2：在类内部创建唯一实例（静态常量）
        // static修饰：属于类，不依赖实例，在类加载时初始化
        // final修饰：不可变，保证唯一性
        private static final EagerSingleton1 INSTANCE = new EagerSingleton1();
        
        // 关键步骤3：提供公共的静态方法获取实例
        public static EagerSingleton1 getInstance() {
            return INSTANCE;
        }
        
        public void showMessage() {
            System.out.println("饿汉式（静态常量）单例实例");
        }
    }
    
    // ==================== 方式2：饿汉式（静态代码块）====================
    /**
     * 与方式1类似，只是将实例化放在静态代码块中
     * 这种方式可以在静态代码块中做一些初始化操作
     */
    static class EagerSingleton2 {
        private EagerSingleton2() {
            System.out.println("饿汉式（静态代码块）- 实例被创建");
        }
        
        // 关键步骤：声明静态变量，但不立即赋值
        private static EagerSingleton2 INSTANCE;
        
        // 关键步骤：在静态代码块中创建实例
        // 静态代码块在类加载时执行，且只执行一次，保证线程安全
        static {
            INSTANCE = new EagerSingleton2();
        }
        
        public static EagerSingleton2 getInstance() {
            return INSTANCE;
        }
        
        public void showMessage() {
            System.out.println("饿汉式（静态代码块）单例实例");
        }
    }
    
    // ==================== 方式3：懒汉式（线程不安全）====================
    /**
     * 优点：
     * 1. 延迟加载，只有在需要时才创建实例
     * 
     * 缺点：
     * 1. 线程不安全，多线程环境下可能创建多个实例
     * 2. 不推荐在生产环境使用
     */
    static class LazySingletonUnsafe {
        private LazySingletonUnsafe() {
            System.out.println("懒汉式（线程不安全）- 实例被创建");
        }
        
        // 关键步骤：声明静态变量，但不立即初始化（延迟加载）
        private static LazySingletonUnsafe INSTANCE;
        
        // 关键问题：没有同步机制，多线程环境下不安全
        // 线程A检查INSTANCE为null，准备创建；线程B也检查为null，也创建
        // 结果：可能创建多个实例
        public static LazySingletonUnsafe getInstance() {
            if (INSTANCE == null) {  // 检查步骤
                INSTANCE = new LazySingletonUnsafe();  // 创建步骤
            }
            return INSTANCE;
        }
        
        public void showMessage() {
            System.out.println("懒汉式（线程不安全）单例实例");
        }
    }
    
    // ==================== 方式4：懒汉式（同步方法，线程安全）====================
    /**
     * 优点：
     * 1. 延迟加载
     * 2. 线程安全（使用synchronized同步方法）
     * 
     * 缺点：
     * 1. 效率低，每次获取实例都要同步，实际上只需要第一次创建时同步
     * 2. 不推荐使用
     */
    static class LazySingletonSynchronizedMethod {
        private LazySingletonSynchronizedMethod() {
            System.out.println("懒汉式（同步方法）- 实例被创建");
        }
        
        private static LazySingletonSynchronizedMethod INSTANCE;
        
        // 关键步骤：使用synchronized修饰整个方法
        // 优点：线程安全
        // 缺点：每次调用都要同步，性能开销大（实际上只需要第一次创建时同步）
        public static synchronized LazySingletonSynchronizedMethod getInstance() {
            if (INSTANCE == null) {
                INSTANCE = new LazySingletonSynchronizedMethod();
            }
            return INSTANCE;
        }
        
        public void showMessage() {
            System.out.println("懒汉式（同步方法）单例实例");
        }
    }
    
    // ==================== 方式5：双重检查锁定（Double-Check Locking）====================
    /**
     * 优点：
     * 1. 延迟加载
     * 2. 线程安全
     * 3. 性能较好，只在第一次创建时同步
     * 
     * 关键点：
     * 1. 两次检查INSTANCE是否为null
     * 2. 使用synchronized同步代码块
     * 3. 使用volatile关键字防止指令重排序（JDK 5+）
     */
    static class DoubleCheckLockingSingleton {
        private DoubleCheckLockingSingleton() {
            System.out.println("双重检查锁定 - 实例被创建");
        }
        
        // 关键步骤1：使用volatile修饰
        // volatile的作用：
        // 1. 保证可见性：一个线程修改后，其他线程立即可见
        // 2. 防止指令重排序：禁止JVM对new操作的指令重排序
        //    new操作分为三步：分配内存、初始化对象、将引用指向内存地址
        //    如果不加volatile，可能发生重排序，导致其他线程看到未完全初始化的对象
        private static volatile DoubleCheckLockingSingleton INSTANCE;
        
        public static DoubleCheckLockingSingleton getInstance() {
            // 关键步骤2：第一次检查（不加锁，提高性能）
            // 如果实例已存在，直接返回，避免不必要的同步
            if (INSTANCE == null) {
                // 关键步骤3：同步代码块，只同步创建实例的部分
                synchronized (DoubleCheckLockingSingleton.class) {
                    // 关键步骤4：第二次检查（加锁后再次检查）
                    // 防止多个线程同时通过第一次检查后，重复创建实例
                    if (INSTANCE == null) {
                        INSTANCE = new DoubleCheckLockingSingleton();
                    }
                }
            }
            return INSTANCE;
        }
        
        public void showMessage() {
            System.out.println("双重检查锁定单例实例");
        }
    }
    
    // ==================== 方式6：静态内部类（推荐）====================
    /**
     * 优点：
     * 1. 延迟加载（只有在调用getInstance时才加载内部类）
     * 2. 线程安全（JVM类加载机制保证）
     * 3. 实现简单，无需同步
     * 4. 推荐使用
     * 
     * 原理：
     * JVM在加载外部类时，不会立即加载内部类，只有使用内部类时才会加载
     * 而类的静态成员变量初始化在类加载时完成，且JVM保证线程安全
     */
    static class StaticInnerClassSingleton {
        private StaticInnerClassSingleton() {
            System.out.println("静态内部类 - 实例被创建");
        }
        
        // 关键步骤：静态内部类
        // 1. 静态内部类在外部类加载时不会立即加载
        // 2. 只有在调用getInstance()时，才会加载StaticInnerClass
        // 3. 类加载是线程安全的，由JVM保证
        private static class StaticInnerClass {
            // 关键步骤：在静态内部类中创建外部类的实例
            // 这个实例在内部类加载时创建，且只创建一次
            private static final StaticInnerClassSingleton INSTANCE = new StaticInnerClassSingleton();
        }
        
        public static StaticInnerClassSingleton getInstance() {
            // 访问内部类的静态成员，触发内部类加载，从而创建实例
            return StaticInnerClass.INSTANCE;
        }
        
        public void showMessage() {
            System.out.println("静态内部类单例实例");
        }
    }
    
    // ==================== 方式7：枚举（最推荐）====================
    /**
     * 优点：
     * 1. 实现最简单，代码最简洁
     * 2. 线程安全（JVM保证）
     * 3. 防止反射攻击（枚举类无法通过反射创建实例）
     * 4. 防止反序列化创建新实例（枚举类有特殊的序列化机制）
     * 5. 最推荐使用（Joshua Bloch在《Effective Java》中推荐）
     * 
     * 缺点：
     * 1. 不能延迟加载（枚举在类加载时初始化）
     */
    enum EnumSingleton {
        // 关键步骤：枚举实例
        // JVM保证枚举实例的唯一性，且线程安全
        INSTANCE;
        
        // 可以添加方法和属性
        private String message = "枚举单例";
        
        // 可以添加业务方法
        public void showMessage() {
            System.out.println("枚举单例实例: " + message);
        }
        
        public void setMessage(String message) {
            this.message = message;
        }
    }
    
    // ==================== 测试代码 ====================
    public static void main(String[] args) {
        System.out.println("========== 单例模式演示 ==========\n");
        
        // 测试1：饿汉式（静态常量）
        System.out.println("--- 方式1：饿汉式（静态常量）---");
        EagerSingleton1 instance1_1 = EagerSingleton1.getInstance();
        EagerSingleton1 instance1_2 = EagerSingleton1.getInstance();
        System.out.println("instance1_1 == instance1_2: " + (instance1_1 == instance1_2));
        instance1_1.showMessage();
        System.out.println();
        
        // 测试2：饿汉式（静态代码块）
        System.out.println("--- 方式2：饿汉式（静态代码块）---");
        EagerSingleton2 instance2_1 = EagerSingleton2.getInstance();
        EagerSingleton2 instance2_2 = EagerSingleton2.getInstance();
        System.out.println("instance2_1 == instance2_2: " + (instance2_1 == instance2_2));
        instance2_1.showMessage();
        System.out.println();
        
        // 测试3：懒汉式（线程不安全）- 单线程测试
        System.out.println("--- 方式3：懒汉式（线程不安全）---");
        LazySingletonUnsafe instance3_1 = LazySingletonUnsafe.getInstance();
        LazySingletonUnsafe instance3_2 = LazySingletonUnsafe.getInstance();
        System.out.println("instance3_1 == instance3_2: " + (instance3_1 == instance3_2));
        instance3_1.showMessage();
        System.out.println();
        
        // 测试4：懒汉式（同步方法）
        System.out.println("--- 方式4：懒汉式（同步方法）---");
        LazySingletonSynchronizedMethod instance4_1 = LazySingletonSynchronizedMethod.getInstance();
        LazySingletonSynchronizedMethod instance4_2 = LazySingletonSynchronizedMethod.getInstance();
        System.out.println("instance4_1 == instance4_2: " + (instance4_1 == instance4_2));
        instance4_1.showMessage();
        System.out.println();
        
        // 测试5：双重检查锁定
        System.out.println("--- 方式5：双重检查锁定 ---");
        DoubleCheckLockingSingleton instance5_1 = DoubleCheckLockingSingleton.getInstance();
        DoubleCheckLockingSingleton instance5_2 = DoubleCheckLockingSingleton.getInstance();
        System.out.println("instance5_1 == instance5_2: " + (instance5_1 == instance5_2));
        instance5_1.showMessage();
        System.out.println();
        
        // 测试6：静态内部类
        System.out.println("--- 方式6：静态内部类（推荐）---");
        StaticInnerClassSingleton instance6_1 = StaticInnerClassSingleton.getInstance();
        StaticInnerClassSingleton instance6_2 = StaticInnerClassSingleton.getInstance();
        System.out.println("instance6_1 == instance6_2: " + (instance6_1 == instance6_2));
        instance6_1.showMessage();
        System.out.println();
        
        // 测试7：枚举
        System.out.println("--- 方式7：枚举（最推荐）---");
        EnumSingleton instance7_1 = EnumSingleton.INSTANCE;
        EnumSingleton instance7_2 = EnumSingleton.INSTANCE;
        System.out.println("instance7_1 == instance7_2: " + (instance7_1 == instance7_2));
        instance7_1.showMessage();
        System.out.println();
        
        System.out.println("========== 演示完成 ==========");
    }
}

