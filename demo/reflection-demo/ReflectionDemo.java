package reflection_demo;

import java.lang.reflect.Constructor;
import java.lang.reflect.Method;

/**
 * Java 反射简单演示：获取类、构造实例、调用方法。
 * 考点：反射概念、Class.forName、getDeclaredMethod、setAccessible、应用场景（框架、序列化等）。
 */
public class ReflectionDemo {
    public static class Foo {
        private String name;
        public Foo() {}
        public Foo(String name) { this.name = name; }
        public String getName() { return name; }
        public void setName(String name) { this.name = name; }
    }

    public static void main(String[] args) throws Exception {
        Class<?> clazz = Class.forName("reflection_demo.ReflectionDemo$Foo");

        // 无参构造
        Object obj1 = clazz.getDeclaredConstructor().newInstance();
        Method setName = clazz.getMethod("setName", String.class);
        setName.invoke(obj1, "Tom");
        Method getName = clazz.getMethod("getName");
        System.out.println(getName.invoke(obj1));  // Tom

        // 有参构造
        Constructor<?> ctor = clazz.getDeclaredConstructor(String.class);
        Object obj2 = ctor.newInstance("Jerry");
        System.out.println(getName.invoke(obj2));  // Jerry
    }
}
