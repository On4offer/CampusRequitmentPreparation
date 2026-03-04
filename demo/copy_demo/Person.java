package copy_demo;

public class Person implements Cloneable {
    private String name;
    private Address address;

    public Person(String name, Address address) {
        this.name = name;
        this.address = address;
    }

    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }

    public Address getAddress() {
        return address;
    }

    public void setAddress(Address address) {
        this.address = address;
    }

    // 浅拷贝实现
    public Person shallowCopy() throws CloneNotSupportedException {
        return (Person) super.clone();
    }

    // 深拷贝实现
    public Person deepCopy() throws CloneNotSupportedException {
        Person copy = (Person) super.clone();
        // 对引用类型进行手动拷贝
        copy.setAddress((Address) address.clone());
        return copy;
    }

    @Override
    public String toString() {
        return "Person{name='" + name + "', address=" + address + "} @Hash=" + System.identityHashCode(this);
    }
}

