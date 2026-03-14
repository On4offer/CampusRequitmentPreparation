package chain_template_demo;

/**
 * 模板方法：抽象类定义骨架流程，子类实现步骤。JdbcTemplate、Servlet、JUnit 常用。
 */
abstract class AbstractTemplate {
    public final void execute() {
        step1();
        step2();
        step3();
    }
    private void step1() {
        System.out.println("模板 step1 固定");
    }
    protected abstract void step2();
    private void step3() {
        System.out.println("模板 step3 固定");
    }
}

class ConcreteTemplate extends AbstractTemplate {
    @Override
    protected void step2() {
        System.out.println("子类 step2 实现");
    }
}

public class TemplateMethodDemo {
    public static void main(String[] args) {
        AbstractTemplate t = new ConcreteTemplate();
        t.execute();
    }
}
