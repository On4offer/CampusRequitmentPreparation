// 这是传统SpringMVC项目中的静态资源文件
// 需要在spring-mvc.xml中通过 <mvc:resources mapping="/static/**" location="/static/" /> 配置才能访问

console.log('传统SpringMVC项目的静态资源已加载');

function demoFunction() {
    alert('这是传统SpringMVC静态资源中的JavaScript函数');
}
