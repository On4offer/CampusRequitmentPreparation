好问题 👍，**Scoped Values（范围值）** 是 Java 21 新加入的一个并发编程工具，很多人第一次看到会有点懵，尤其是和 `ThreadLocal` 的对比。下面我从**概念 → 和 ThreadLocal 对比 → 使用场景 → 代码示例**帮你梳理清楚。

------

# 1. 什么是 Scoped Values

- **ScopedValue** 是 Java 21 引入的 **预览特性**（`java.lang.ScopedValue` 类）。
- 它提供了一种 **在一段受限代码范围内** 安全地传递数据给方法调用和子线程（尤其是虚拟线程）。
- 它和 `ThreadLocal` 类似，都是让你在方法之间传递“上下文信息”，但有几个核心区别：

------

# 2. 和 ThreadLocal 的对比

| 特性     | `ThreadLocal`                            | `ScopedValue`                                          |
| -------- | ---------------------------------------- | ------------------------------------------------------ |
| 生命周期 | 绑定在线程生命周期上，必须手动清理       | 绑定在**代码作用域**内，作用结束自动清理               |
| 安全性   | 容易遗忘 `remove()` → 内存泄漏           | 作用范围严格受控，不会泄漏                             |
| 并发模型 | 每个线程维护一份副本                     | 支持父线程向子线程传递值（虚拟线程友好）               |
| 使用场景 | 长生命周期数据，如线程级缓存、事务上下文 | 短期、作用域明确的上下文传递，如用户请求信息、日志追踪 |

👉 简单理解：

- `ThreadLocal` 像是“寄存在某个线程的储物柜”。
- `ScopedValue` 像是“把值放进一个作用域大括号里，出了大括号自动消失”。

------

# 3. 典型使用场景

- **日志追踪**：在一次请求调用链里，传递 TraceId，确保日志可串起来。
- **安全上下文**：传递用户认证信息、租户ID。
- **虚拟线程**：由于虚拟线程数量非常大，`ThreadLocal` 的存取和清理代价高，而 `ScopedValue` 更轻量、安全。

------

# 4. 使用示例

## ✅ 基础示例

```java
import java.lang.ScopedValue;

public class ScopedValueDemo {
    // 定义一个范围值
    static final ScopedValue<String> USER = ScopedValue.newInstance();

    public static void main(String[] args) {
        ScopedValue.where(USER, "Alice").run(() -> {
            // 在作用域内访问
            System.out.println("当前用户: " + USER.get());
            innerMethod();

            // 开启虚拟线程，也能继承作用域值
            Thread.startVirtualThread(() -> {
                System.out.println("虚拟线程用户: " + USER.get());
            });
        });

        // 超出作用域，不能再访问
        try {
            System.out.println(USER.get());
        } catch (IllegalStateException e) {
            System.out.println("作用域已结束，无法访问 USER");
        }
    }

    static void innerMethod() {
        System.out.println("innerMethod 中用户: " + USER.get());
    }
}
```

### 输出：

```
当前用户: Alice
innerMethod 中用户: Alice
虚拟线程用户: Alice
作用域已结束，无法访问 USER
```

------

## ✅ 日志追踪场景

```java
static final ScopedValue<String> TRACE_ID = ScopedValue.newInstance();

public static void main(String[] args) {
    ScopedValue.where(TRACE_ID, "trace-12345").run(() -> {
        serviceA();
        serviceB();
    });
}

static void serviceA() {
    System.out.println("ServiceA TraceId = " + TRACE_ID.get());
}

static void serviceB() {
    System.out.println("ServiceB TraceId = " + TRACE_ID.get());
}
```

------

# 5. 面试标准回答

> Scoped Values 是 Java 21 新引入的并发特性，用于在一段代码作用域中安全传递只读数据。它类似 ThreadLocal，但作用范围更明确：在 `ScopedValue.where(...).run(...)` 的代码块内有效，退出后自动清理，不会像 ThreadLocal 那样引起内存泄漏。
>  它特别适合 **短期上下文信息的传递**（如 TraceId、用户信息），并且对虚拟线程更友好，避免了 ThreadLocal 带来的性能和管理开销。

------

要不要我帮你再写一个 **ScopedValue 在“Web 请求处理”里的示例**，比如用户认证信息如何通过 ScopedValue 在控制器、服务层、DAO 层中自动传递？这样就能和实际项目更贴近。