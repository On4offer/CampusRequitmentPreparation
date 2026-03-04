package copy_demo;

public class Address implements Cloneable {
    private String city;

    public Address(String city) {
        this.city = city;
    }

    public String getCity() {
        return city;
    }

    public void setCity(String city) {
        this.city = city;
    }

    @Override
    public String toString() {
        return "Address{city='" + city + "'}";
    }

    @Override
    public Object clone() throws CloneNotSupportedException {
        return super.clone();
    }
}

