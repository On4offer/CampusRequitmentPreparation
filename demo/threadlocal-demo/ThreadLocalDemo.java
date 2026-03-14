package threadlocal_demo;

/**
 * ThreadLocal 使用演示：每个线程独立副本，常用于用户上下文、连接等。
 * 考点：原理（Thread 内 threadLocals 的 Map）；为什么 key 用弱引用（防内存泄漏）；使用完要 remove。
 */
public class ThreadLocalDemo {
    private static final ThreadLocal<String> USER = new ThreadLocal<>();
    private static final ThreadLocal<Integer> REQUEST_ID = new ThreadLocal<>();

    public static void main(String[] args) throws InterruptedException {
        Thread t1 = new Thread(() -> {
            USER.set("user-A");
            REQUEST_ID.set(100);
            System.out.println(Thread.currentThread().getName() + " user=" + USER.get() + " id=" + REQUEST_ID.get());
            USER.remove();
            REQUEST_ID.remove();
        }, "T1");
        Thread t2 = new Thread(() -> {
            USER.set("user-B");
            REQUEST_ID.set(200);
            System.out.println(Thread.currentThread().getName() + " user=" + USER.get() + " id=" + REQUEST_ID.get());
            USER.remove();
            REQUEST_ID.remove();
        }, "T2");
        t1.start();
        t2.start();
        t1.join();
        t2.join();
    }
}
