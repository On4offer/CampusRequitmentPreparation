package factory_pattern_demo;

/**
 * 简单工厂：一个工厂类通过 if/switch 根据参数创建不同产品。不属于 GoF 23 种，但常考。
 * 缺点：新增产品要改工厂类，违反开闭原则。
 */
interface Product {
    void use();
}

class ProductA implements Product {
    @Override
    public void use() { System.out.println("ProductA"); }
}

class ProductB implements Product {
    @Override
    public void use() { System.out.println("ProductB"); }
}

class SimpleFactory {
    public static Product create(String type) {
        if ("A".equals(type)) return new ProductA();
        if ("B".equals(type)) return new ProductB();
        throw new IllegalArgumentException("unknown: " + type);
    }
}

public class SimpleFactoryDemo {
    public static void main(String[] args) {
        Product p = SimpleFactory.create("A");
        p.use();
    }
}
