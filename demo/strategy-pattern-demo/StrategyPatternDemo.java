package strategy_pattern_demo;

/**
 * 策略模式：算法族可互换，与使用解耦。技术栈行为型+创建型 OCP 均提到；支付方式、排序比较器常用。
 */
interface Strategy {
    void execute();
}

class StrategyA implements Strategy {
    @Override
    public void execute() {
        System.out.println("策略 A");
    }
}

class StrategyB implements Strategy {
    @Override
    public void execute() {
        System.out.println("策略 B");
    }
}

class Context {
    private Strategy strategy;
    void setStrategy(Strategy s) {
        this.strategy = s;
    }
    void doSomething() {
        if (strategy != null) strategy.execute();
    }
}

public class StrategyPatternDemo {
    public static void main(String[] args) {
        Context ctx = new Context();
        ctx.setStrategy(new StrategyA());
        ctx.doSomething();
        ctx.setStrategy(new StrategyB());
        ctx.doSomething();
    }
}
