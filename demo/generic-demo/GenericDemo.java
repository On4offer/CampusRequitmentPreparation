package generic_demo;

/**
 * 泛型类与泛型方法示例。技术栈泛型反射笔记、口述时常写 Box<T>、泛型方法。
 */
public class GenericDemo {
    static class Box<T> {
        private T value;
        void set(T value) { this.value = value; }
        T get() { return value; }
    }

    static <T> void printArray(T[] arr) {
        for (T t : arr) {
            System.out.print(t + " ");
        }
        System.out.println();
    }

    public static void main(String[] args) {
        Box<String> box = new Box<>();
        box.set("Hello");
        System.out.println(box.get());

        printArray(new Integer[]{1, 2, 3});
        printArray(new String[]{"a", "b", "c"});
    }
}
