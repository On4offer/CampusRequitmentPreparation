package observer_pattern_demo;

import java.util.ArrayList;
import java.util.List;

/**
 * 观察者模式：主题维护观察者列表，状态变化时 notify 所有观察者。
 * 技术栈行为型模式高频；Spring 事件、前端响应式的基础。
 */
interface Subject {
    void attach(Observer o);
    void detach(Observer o);
    void notifyObservers();
}

interface Observer {
    void update(String state);
}

class ConcreteSubject implements Subject {
    private final List<Observer> observers = new ArrayList<>();
    private String state;

    public void setState(String state) {
        this.state = state;
        notifyObservers();
    }

    @Override
    public void attach(Observer o) {
        observers.add(o);
    }

    @Override
    public void detach(Observer o) {
        observers.remove(o);
    }

    @Override
    public void notifyObservers() {
        for (Observer o : observers) {
            o.update(state);
        }
    }
}

class ConcreteObserver implements Observer {
    private final String name;
    ConcreteObserver(String name) { this.name = name; }
    @Override
    public void update(String state) {
        System.out.println(name + " 收到: " + state);
    }
}

public class ObserverPatternDemo {
    public static void main(String[] args) {
        ConcreteSubject subject = new ConcreteSubject();
        subject.attach(new ConcreteObserver("A"));
        subject.attach(new ConcreteObserver("B"));
        subject.setState("hello");
        subject.setState("world");
    }
}
