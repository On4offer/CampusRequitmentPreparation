# 📌 JavaScript（ES6+）常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重 **ES6+ 语法、常用 API 与场景**，便于速查与校招复习。

---

## 一、变量与类型

| 语法/API | 说明 | 示例 |
|----------|------|------|
| **let / const** | 块级作用域；const 引用不可改 | let a = 1; const obj = {}; obj.x = 1 ✅ |
| **typeof** | 类型判断（注意 null 为 "object"） | typeof [] === 'object' |
| **??** | 空值合并，仅 null/undefined 取右侧 | value ?? 'default' |
| **?.** | 可选链，避免 undefined 报错 | obj?.a?.b |

---

## 二、函数与 this

| 用法 | 说明 |
|------|------|
| **箭头函数** | 无自身 this，继承外层；无 arguments |
| **call / apply / bind** | 显式指定 this；bind 返回新函数 |
| **闭包** | 函数引用外层变量，形成私有作用域；注意内存泄漏 |

```js
// 防抖
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}
```

---

## 三、解构与展开

| 语法 | 示例 |
|------|------|
| **数组解构** | const [a, b, ...rest] = [1, 2, 3, 4] |
| **对象解构** | const { name, age = 18 } = user |
| **展开运算符** | [...arr], { ...obj }; 函数参数 ...args |

---

## 四、Promise 与 async/await

| API | 说明 |
|-----|------|
| **new Promise((resolve, reject) => {})** | 创建 Promise |
| **.then / .catch / .finally** | 链式处理结果与错误 |
| **Promise.all(iterable)** | 全部成功才 resolve，一个失败即 reject |
| **Promise.race(iterable)** | 先完成（成功或失败）的结果 |
| **Promise.allSettled(iterable)** | 等全部结束，返回每项状态与值 |
| **async / await** | async 函数返回 Promise；await 等待 Promise 结果 |

```js
const res = await fetch(url);
const data = await res.json();
```

---

## 五、数组常用 API

| 方法 | 说明 | 返回值/注意 |
|------|------|-------------|
| **map** | 映射 | 新数组 |
| **filter** | 过滤 | 新数组 |
| **find / findIndex** | 查找首个满足项 | 元素 / 索引 |
| **reduce** | 归并 | 单值 |
| **some / every** | 是否存在/全部满足 | boolean |
| **includes** | 是否包含 | boolean |
| **flat(depth)** | 扁平化 | 新数组 |
| **Array.isArray** | 是否数组 | boolean |

---

## 六、对象与字符串

| 用法 | 说明 |
|------|------|
| **Object.keys(obj)** | 自身可枚举属性键数组 |
| **Object.values(obj)** | 属性值数组 |
| **Object.entries(obj)** | [key, value] 数组 |
| **Object.assign(target, ...sources)** | 浅拷贝合并 |
| **str.includes / startsWith / endsWith** | 字符串包含与前后缀 |
| **str.padStart(len, pad)** | 前补位（如数字前导零） |

---

## 七、模块化（ES Module）

```js
// 导出
export const x = 1;
export default function fn() {}

// 导入
import fn, { x } from './module.js';
import * as M from './module.js';
```

---

## 八、事件循环与执行顺序（校招常考）

- **宏任务**：script、setTimeout、setInterval、I/O、UI 渲染。
- **微任务**：Promise.then/catch/finally、queueMicrotask、MutationObserver。
- **顺序**：每轮取一个宏任务执行 → 清空当前微任务队列 → 必要时渲染 → 下一宏任务。

---

## 九、与学习笔记的对应关系

- 第 1 章 → 运行环境；第 2 章 → 一；第 3 章 → 二；第 4 章 → 面向对象（见学习笔记）；第 5 章 → 四；第 6 章 → 三、五、六、七；第 7 章 → 二（防抖）、八（事件循环）。
