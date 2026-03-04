package lock_demo;

public class VisibilityDemo {
    private  boolean flag = false; // 没有volatile

    public void writer() {
        flag = true; // 线程1执行：修改flag
    }

    public void reader() {
        while (!flag) { // 线程2执行：读取flag
            // 无代码的空循环（JIT可能优化成死循环）
            System.out.println("线程2在循环中等待");
        }
        System.out.println("线程2退出循环");
    }

    public static void main(String[] args) {
        VisibilityDemo demo = new VisibilityDemo();

        // 线程2：执行reader，进入循环
        new Thread(demo::reader).start();
        System.out.println("线程2开始循环等待");

        // 主线程休眠1秒，确保线程2先进入循环
        // try { Thread.sleep(1000); } catch (InterruptedException e) {}

        // 线程1：执行writer，修改flag为true
        new Thread(demo::writer).start();
        System.out.println("线程1修改flag为true");
    }
}
