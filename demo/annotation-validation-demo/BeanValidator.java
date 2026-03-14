package annotation_validation_demo;

import java.lang.reflect.Field;
import java.util.ArrayList;
import java.util.List;

/**
 * 运行时校验：反射读取字段上的 @NotNull、@Length，校验并返回错误信息。
 * 面试试卷「自定义注解处理器，非空、长度、正则校验」的简化实现。
 */
public class BeanValidator {

    public static List<String> validate(Object obj) throws IllegalAccessException {
        List<String> errors = new ArrayList<>();
        Class<?> clazz = obj.getClass();
        for (Field f : clazz.getDeclaredFields()) {
            f.setAccessible(true);
            Object value = f.get(obj);

            NotNull notNull = f.getAnnotation(NotNull.class);
            if (notNull != null && value == null) {
                errors.add(f.getName() + ": " + notNull.message());
            }

            Length length = f.getAnnotation(Length.class);
            if (length != null && value != null && value instanceof CharSequence) {
                int len = ((CharSequence) value).length();
                if (len < length.min() || len > length.max()) {
                    errors.add(f.getName() + ": " + length.message() + " (min=" + length.min() + ", max=" + length.max() + ")");
                }
            }
        }
        return errors;
    }

    public static void main(String[] args) throws IllegalAccessException {
        User user = new User();
        user.name = "";
        user.age = 18;
        List<String> errs = validate(user);
        System.out.println(errs);  // [name: 不能为空] 或长度相关
    }
}
