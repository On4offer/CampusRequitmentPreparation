package comparable_comparator_demo;

import java.util.*;

/**
 * Comparable（自然排序）与 Comparator（比较器）演示。集合排序、TreeSet/TreeMap、面试常问。
 */
class PersonByAge implements Comparable<PersonByAge> {
    String name;
    int age;
    PersonByAge(String name, int age) {
        this.name = name;
        this.age = age;
    }
    @Override
    public int compareTo(PersonByAge o) {
        return Integer.compare(this.age, o.age);
    }
    @Override
    public String toString() {
        return name + "(" + age + ")";
    }
}

public class ComparableComparatorDemo {
    public static void main(String[] args) {
        List<PersonByAge> list = Arrays.asList(
            new PersonByAge("Tom", 20),
            new PersonByAge("Jerry", 18),
            new PersonByAge("Bob", 22)
        );
        Collections.sort(list);
        System.out.println("Comparable 按年龄: " + list);

        // Comparator 按名字
        list.sort(Comparator.comparing(p -> p.name));
        System.out.println("Comparator 按名字: " + list);
    }
}
