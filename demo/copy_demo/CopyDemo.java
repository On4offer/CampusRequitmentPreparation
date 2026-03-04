package copy_demo;

public class CopyDemo {
    public static void main(String[] args) throws CloneNotSupportedException {
        System.out.println("=== 演示开始：引用拷贝、浅拷贝、深拷贝 ===\n");

        Address commonAddress = new Address("北京");
        Person original = new Person("张三", commonAddress);

        System.out.println("原始对象: " + original);
        System.out.println("原始对象的 Address Hash: " + System.identityHashCode(original.getAddress()));
        System.out.println("------------------------------------------");

        // 1. 引用拷贝 (Reference Copy)
        System.out.println("[1] 演示：引用拷贝");
        Person refCopy = original;
        System.out.println("引用拷贝对象: " + refCopy);
        System.out.println("original == refCopy: " + (original == refCopy) + " (两个变量指向同一个堆内存地址)");
        refCopy.setName("张三-修改后");
        System.out.println("修改引用拷贝的姓名后，原始对象姓名: " + original.getName());
        System.out.println("------------------------------------------");

        // 重置原始对象
        System.out.println("重置原始对象姓名为 '张三'...\n");
        original.setName("张三");
        
        // 2. 浅拷贝 (Shallow Copy)
        System.out.println("[2] 演示：浅拷贝");
        Person shallowCopy = original.shallowCopy();
        System.out.println("浅拷贝对象: " + shallowCopy);
        System.out.println("original == shallowCopy: " + (original == shallowCopy) + " (对象本身是新的)");
        System.out.println("original.address == shallowCopy.address: " + (original.getAddress() == shallowCopy.getAddress()) + " (内部引用类型还是同一个)");
        
        System.out.println("修改浅拷贝的城市为 '上海'...");
        shallowCopy.getAddress().setCity("上海");
        System.out.println("修改后，原始对象的城市: " + original.getAddress().getCity() + " (受影响！)");
        System.out.println("------------------------------------------");

        // 重置城市
        System.out.println("重置原始对象城市为 '北京'...\n");
        original.getAddress().setCity("北京");

        // 3. 深拷贝 (Deep Copy)
        System.out.println("[3] 演示：深拷贝");
        Person deepCopy = original.deepCopy();
        System.out.println("深拷贝对象: " + deepCopy);
        System.out.println("original == deepCopy: " + (original == deepCopy) + " (对象本身是新的)");
        System.out.println("original.address == deepCopy.address: " + (original.getAddress() == deepCopy.getAddress()) + " (内部引用类型也是新的)");
        
        System.out.println("修改深拷贝的城市为 '深圳'...");
        deepCopy.getAddress().setCity("深圳");
        System.out.println("修改后，原始对象的城市: " + original.getAddress().getCity() + " (不受影响！)");
        System.out.println("------------------------------------------");

        System.out.println("\n=== 演示结束 ===");
    }
}

