# 动态代理获取私有属性演示

本演示项目展示了如何在动态代理中获取和修改目标对象的私有属性。

## 项目结构

```
dynamic-proxy-private-field-demo/
├── src/main/java/com/demo/proxy/
│   ├── UserService.java              # 用户服务接口（JDK动态代理用）
│   ├── UserServiceImpl.java          # 用户服务实现类（含私有属性）
│   ├── OrderService.java             # 订单服务类（CGLIB动态代理用，含私有属性）
│   ├── ParentService.java            # 父类服务（演示获取父类私有属性）
│   ├── ChildService.java             # 子类服务（继承父类）
│   ├── ReflectionUtils.java          # 反射工具类（递归获取私有属性）
│   ├── JdkProxyHandler.java          # JDK动态代理处理器
│   ├── CglibProxyInterceptor.java    # CGLIB动态代理拦截器
│   └── DynamicProxyDemo.java         # 主演示类
├── pom.xml                           # Maven配置文件
└── README.md                         # 本文件
```

## 核心原理

动态代理获取私有属性的核心步骤：

1. **获取目标对象引用**：在代理逻辑中持有目标对象（target）的引用
2. **通过反射获取私有字段**：使用 `Class.getDeclaredField()` 获取私有字段
3. **突破访问权限**：调用 `Field.setAccessible(true)` 关闭访问检查
4. **读取/修改属性值**：使用 `Field.get()` 和 `Field.set()` 操作属性

## 运行方式

### 方式1：使用Maven编译运行

```bash
# 编译
mvn clean compile

# 运行（pom.xml已配置JVM参数，直接运行即可）
mvn exec:java
```

### 方式2：使用IDE运行

1. 在IDE中打开项目
2. **重要**：如果使用Java 9+，需要在运行配置中添加JVM参数：
   ```
   --add-opens java.base/java.lang=ALL-UNNAMED
   ```
3. 运行 `DynamicProxyDemo.java` 的 `main` 方法

### 方式3：手动编译运行（不使用Maven）

```bash
# 编译（需要先下载cglib-3.3.0.jar到lib目录）
javac -cp "lib/cglib-3.3.0.jar" -d out src/main/java/com/demo/proxy/*.java

# 运行（Java 9+需要添加模块开放参数）
java --add-opens java.base/java.lang=ALL-UNNAMED -cp "out;lib/cglib-3.3.0.jar" com.demo.proxy.DynamicProxyDemo
```

## ⚠️ 重要提示：Java 9+ 模块化问题

如果你使用的是 **Java 9 或更高版本**，CGLIB 需要访问 `java.base` 模块的内部 API，可能会遇到以下错误：

```
java.lang.reflect.InaccessibleObjectException: Unable to make ... accessible: 
module java.base does not "opens java.lang" to unnamed module
```

### 解决方案：

1. **使用Maven运行**（推荐）：`pom.xml` 已配置好JVM参数，直接运行即可
2. **在IDE中运行**：需要在运行配置的VM options中添加：
   ```
   --add-opens java.base/java.lang=ALL-UNNAMED
   ```
3. **手动运行**：在 `java` 命令后添加参数：
   ```bash
   java --add-opens java.base/java.lang=ALL-UNNAMED ...
   ```

## 演示内容

### 演示1：JDK动态代理获取私有属性

- 展示如何通过JDK动态代理获取和修改目标对象的私有属性
- 关键点：必须操作 `target` 对象，而不是 `proxy` 对象

### 演示2：CGLIB动态代理获取私有属性

- 展示如何通过CGLIB动态代理获取和修改目标对象的私有属性
- 关键点：CGLIB不需要接口，可以直接代理类

### 演示3：获取父类私有属性

- 展示如何递归查找并获取父类的私有属性
- 使用 `ReflectionUtils` 工具类实现

### 演示4：直接操作目标对象（对比验证）

- 展示直接使用反射修改私有属性（不使用代理）
- 用于对比和理解代理的本质

## 关键观察点

### 1. 代理对象 vs 目标对象

**重要**：必须操作**目标对象（target）**，而不是代理对象（proxy）

- 代理对象是动态生成的子类实例，不包含目标类的私有属性
- 目标对象才是真正包含私有属性的对象

### 2. setAccessible(true) 的作用

- 不调用 `setAccessible(true)`：会抛出 `IllegalAccessException`
- 调用后：可以突破访问权限限制，访问私有属性

### 3. 父类私有属性的获取

- 使用 `getDeclaredField()` 只能获取当前类声明的字段
- 需要递归遍历父类才能获取父类的私有属性

## 手动操作建议

为了加深理解，可以尝试以下操作：

### 1. 修改初始值
- 修改 `UserServiceImpl` 中私有属性的初始值
- 观察输出变化，理解代理如何读取初始值

### 2. 操作proxy对象（错误示例）
- 在 `JdkProxyHandler.invoke()` 中，尝试操作 `proxy` 对象而不是 `target` 对象
- 观察会发生什么错误

### 3. 不调用setAccessible(true)
- 注释掉 `field.setAccessible(true)` 这一行
- 观察会抛出什么异常

### 4. 修改final私有属性
- 在 `UserServiceImpl` 中添加一个 `private final String finalField = "final值"`
- 尝试修改它，观察会发生什么

### 5. 对比JDK和CGLIB
- 观察两种代理方式的输出差异
- 理解为什么CGLIB不需要接口

## 注意事项

1. **访问权限风险**：`setAccessible(true)` 会绕过访问控制，可能破坏封装性
2. **性能问题**：反射操作比直接访问属性慢，高频调用需缓存 `Field` 对象
3. **final私有属性**：final修饰的基本类型和String无法修改，对象类型可修改内部属性
4. **模块化影响（Java 9+）**：若目标类位于不同模块，需在 `module-info.java` 中开放权限

## 技术栈

- Java 8+
- JDK动态代理（java.lang.reflect.Proxy）
- CGLIB动态代理（cglib 3.3.0）
- Java反射机制

## 学习要点

1. 理解动态代理的核心原理
2. 掌握反射获取私有属性的方法
3. 理解代理对象和目标对象的区别
4. 掌握递归获取父类私有属性的技巧
5. 了解反射的性能和安全性问题

