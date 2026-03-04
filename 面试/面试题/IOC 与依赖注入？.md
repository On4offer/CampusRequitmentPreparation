好，我来帮你整理这一道 **IOC & DI 面试题** 的完整回答模板（符合你准备八股文的思路：概念 → 原理 → 案例 → 使用场景 → 面试模板 → 扩展追问）：

------

# 面试题：什么是 IOC（控制反转）？DI（依赖注入）有哪些方式？

## 1. 概念解释

- **IOC（Inversion of Control，控制反转）**：
   一种设计思想，把对象的创建和依赖管理交给 Spring 容器，而不是由开发者在代码中手动控制。核心是 **降低耦合、提高可维护性**。
  - 传统方式：对象 A 依赖对象 B → A 主动 `new B()`
  - IOC 方式：由容器负责创建并注入 B → A 被动接收依赖
- **DI（Dependency Injection，依赖注入）**：
   IOC 的实现方式之一。Spring 通过注入（构造方法（循环依赖无法解决、Setter、字段等）来把依赖对象传给目标对象。

------

## 2. DI 的实现方式

Spring 常见的注入方式：

1. **构造器注入**

   - 通过构造方法传入依赖对象。

   - 优点：强制依赖，保证对象完整性，适合必需依赖。

   - 示例：

     ```java
     @Component
     public class UserService {
         private final UserRepository userRepository;
     
         @Autowired
         public UserService(UserRepository userRepository) {
             this.userRepository = userRepository;
         }
     }
     ```

2. **Setter 方法注入**

   - 通过 `setXxx()` 方法注入依赖对象。

   - 优点：灵活，可选依赖时常用。

   - 示例：

     ```java
     @Component
     public class OrderService {
         private PaymentService paymentService;
     
         @Autowired
         public void setPaymentService(PaymentService paymentService) {
             this.paymentService = paymentService;
         }
     }
     ```

3. **字段注入（反射注入）**

   - 直接在属性上用 `@Autowired`，Spring 通过反射赋值。

   - 优点：简洁，常用。缺点：不利于测试和解耦。

   - 示例：

     ```java
     @Component
     public class CartService {
         @Autowired
         private ProductService productService;
     }
     ```

4. **接口注入（不推荐）**

   - 早期方案，通过接口方法注入依赖。Spring 基本不常用。

------

## 3. 案例（结合项目）

在 **苍穹外卖项目**中：

- Controller 依赖 Service：

  ```java
  @RestController
  @RequestMapping("/order")
  public class OrderController {
      private final OrderService orderService;
  
      @Autowired
      public OrderController(OrderService orderService) {
          this.orderService = orderService;
      }
  }
  ```

- Service 依赖 Mapper：Spring 会自动把 Mapper 的实现注入进来。

在 **黑马点评项目**中：

- `ShopServiceImpl` 依赖 `StringRedisTemplate`，通过 IOC 注入，无需自己 `new`，Spring 自动管理。

------

## 4. 使用场景

- 构造器注入：强依赖（必不可少的依赖），如 **订单必须依赖用户信息**。
- Setter 注入：弱依赖或可选依赖，如 **缓存工具类**。
- 字段注入：日常开发高频，但在 **单元测试**场景下不太友好。

------

## 5. 面试标准回答（简洁版）

> IOC 是一种设计思想，把对象的创建和依赖关系交给容器管理，降低代码耦合。Spring 中 IOC 的实现方式就是 DI，即依赖注入。
>  常见的注入方式有三种：**构造器注入（强依赖）**、**Setter 注入（可选依赖）** 和 **字段注入（常用但耦合度高）**。在实际项目中，推荐使用构造器注入保证对象完整性。

------

## 6. 扩展追问

1. IOC 的底层原理是什么？
   - 反射 + 工厂模式 + 配置/注解扫描 + 容器管理。
2. 为什么推荐构造器注入？
   - 保证依赖的不可变性，利于测试。
3. 字段注入为什么被认为是“坏实践”？
   - 反射赋值，破坏了依赖的显式性，不利于单元测试和解耦。
4. IOC 和 Service Locator 有什么区别？
   - IOC 依赖注入 → 被动获取依赖；
   - Service Locator → 主动查找依赖。

------

要不要我帮你把 **“Bean 的生命周期流程”** 也整理成同样的结构化答案？这样你可以形成一个 **IOC 模块的完整八股文闭环**。