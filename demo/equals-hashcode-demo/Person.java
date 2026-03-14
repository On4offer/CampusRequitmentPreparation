package equals_hashcode_demo;

import java.util.Objects;

/**
 * 正确重写 equals 和 hashCode 的示例。用于 HashMap/HashSet 等。
 * 考点：equals 与 == 区别；hashCode 契约（equals 相等则 hashCode 必相等）；为什么重写 equals 要重写 hashCode。
 */
public class Person {
    private final String name;
    private final int age;

    public Person(String name, int age) {
        this.name = name;
        this.age = age;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Person person = (Person) o;
        return age == person.age && Objects.equals(name, person.name);
    }

    @Override
    public int hashCode() {
        return Objects.hash(name, age);
    }

    public static void main(String[] args) {
        Person p1 = new Person("Tom", 20);
        Person p2 = new Person("Tom", 20);
        System.out.println("p1 == p2: " + (p1 == p2));           // false
        System.out.println("p1.equals(p2): " + p1.equals(p2));   // true
        System.out.println("p1.hashCode() == p2.hashCode(): " + (p1.hashCode() == p2.hashCode())); // true

        java.util.Set<Person> set = new java.util.HashSet<>();
        set.add(p1);
        set.add(p2);
        System.out.println("set.size(): " + set.size());  // 1，若未重写 hashCode 则为 2
    }
}
