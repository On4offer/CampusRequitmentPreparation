package chain_template_demo;

/**
 * 责任链：请求沿链传递，多个处理器可依次处理。Filter、Interceptor、审批流常用。
 */
abstract class Handler {
    protected Handler next;
    public void setNext(Handler next) { this.next = next; }
    public final void handle(Request req) {
        if (doHandle(req)) return;
        if (next != null) next.handle(req);
    }
    /** 返回 true 表示已处理完毕不再传递 */
    protected abstract boolean doHandle(Request req);
}

class Request {
    String content;
    Request(String content) { this.content = content; }
}

class HandlerA extends Handler {
    @Override
    protected boolean doHandle(Request req) {
        System.out.println("HandlerA: " + req.content);
        return false;
    }
}

class HandlerB extends Handler {
    @Override
    protected boolean doHandle(Request req) {
        System.out.println("HandlerB: " + req.content);
        return true;  // 终止传递
    }
}

public class ChainOfResponsibilityDemo {
    public static void main(String[] args) {
        Handler a = new HandlerA();
        Handler b = new HandlerB();
        a.setNext(b);
        a.handle(new Request("req"));
    }
}
