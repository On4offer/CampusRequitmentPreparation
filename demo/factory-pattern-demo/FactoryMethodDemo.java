package factory_pattern_demo;

/**
 * 工厂方法（GoF）：抽象工厂定义 factoryMethod，具体工厂子类决定创建哪种产品。
 * 新增产品只需新增具体工厂+具体产品，符合开闭原则。Spring BeanFactory、LoggerFactory 思路。
 */
interface Product2 {
    void use();
}

interface Factory {
    Product2 createProduct();
}

class ConcreteProductA implements Product2 {
    @Override
    public void use() { System.out.println("ConcreteProductA"); }
}

class ConcreteProductB implements Product2 {
    @Override
    public void use() { System.out.println("ConcreteProductB"); }
}

class FactoryA implements Factory {
    @Override
    public Product2 createProduct() {
        return new ConcreteProductA();
    }
}

class FactoryB implements Factory {
    @Override
    public Product2 createProduct() {
        return new ConcreteProductB();
    }
}

public class FactoryMethodDemo {
    public static void main(String[] args) {
        Factory f = new FactoryA();
        Product2 p = f.createProduct();
        p.use();
    }
}
