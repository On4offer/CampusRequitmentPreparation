package callable_future_demo;

import java.util.concurrent.*;

/**
 * Callable + Future 取结果。校招手撕题「用阻塞队列存结果，get() 时 take」的典型实现方式。
 * 考点：Callable 有返回值、Future.get() 阻塞、线程池 submit(Callable) 返回 Future。
 */
public class CallableFutureDemo {
    public static void main(String[] args) throws Exception {
        ExecutorService executor = Executors.newSingleThreadExecutor();
        Callable<Integer> task = () -> {
            Thread.sleep(500);
            return 42;
        };
        Future<Integer> future = executor.submit(task);
        System.out.println("主线程可先做别的事");
        Integer result = future.get();  // 阻塞直到完成
        System.out.println("结果: " + result);
        executor.shutdown();
    }
}
