package annotation_validation_demo;

public class User {
    @NotNull(message = "用户名不能为空")
    @Length(min = 1, max = 20, message = "用户名长度 1-20")
    public String name;

    @NotNull(message = "年龄不能为空")
    public Integer age;
}
