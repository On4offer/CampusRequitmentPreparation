# 自定义注解 + 运行时校验 Demo

反射扫描字段上的 @NotNull、@Length，运行时校验 Bean 并返回错误列表。面试试卷「自定义注解处理器，非空、长度、正则」的简化实现。

## 文件说明

| 文件 | 说明 |
|------|------|
| `NotNull.java` | 运行时注解，表示字段不能为 null。 |
| `Length.java` | 运行时注解，min/max 限制字符长度（用于 CharSequence）。 |
| `BeanValidator.java` | 反射遍历字段，读注解并校验，返回 List\<String\> 错误信息。 |
| `User.java` | 示例 Bean，name 非空+长度 1–20，age 非空。 |

## 考点速记

- **@Retention(RetentionPolicy.RUNTIME)**：运行时保留，反射才能拿到。
- **流程**：getDeclaredFields → getAnnotation → 根据注解类型校验 value，违反则加入 errors。
- **扩展**：可加 @Pattern 用正则校验，或仿 JSR-303 做 ConstraintValidator 接口统一处理。

## 运行方式

```bash
cd demo/annotation-validation-demo
javac -d . *.java
java annotation_validation_demo.BeanValidator
```

可修改 User 的 name/age 为 null 或超长字符串观察错误列表。
