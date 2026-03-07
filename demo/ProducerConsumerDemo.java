import java.util.concurrent.ArrayBlockingQueue; // 导入数组阻塞队列类
import java.util.concurrent.BlockingQueue; // 导入阻塞队列接口

public class ProducerConsumerDemo { // 生产者-消费者模式演示类
    private static final BlockingQueue<Integer> queue = new ArrayBlockingQueue<>(10); // 容量为10的线程安全队列

    public static void main(String[] args) { // 主方法入口
        // 创建生产者线程，使用Lambda表达式定义任务
        Thread producer = new Thread(() -> {
            try { // 捕获线程中断异常
                for (int i = 0; i < 20; i++) { // 循环生产20个数据
                    queue.put(i); // 将数据放入队列，若队列满则阻塞等待
                    System.out.println("生产: " + i); // 打印生产的数据
                }
            } catch (InterruptedException e) { // 处理中断异常
                Thread.currentThread().interrupt(); // 恢复线程的中断状态
            }
        });
        // 创建消费者线程，使用Lambda表达式定义任务
        Thread consumer = new Thread(() -> {
            try { // 捕获线程中断异常
                for (int i = 0; i < 20; i++) { // 循环消费20个数据
                    Integer v = queue.take(); // 从队列取数据，若队列空则阻塞等待
                    System.out.println("消费: " + v); // 打印消费的数据
                }
            } catch (InterruptedException e) { // 处理中断异常
                Thread.currentThread().interrupt(); // 恢复线程的中断状态
            }
        });
        producer.start(); // 启动生产者线程
        consumer.start(); // 启动消费者线程
    }
}