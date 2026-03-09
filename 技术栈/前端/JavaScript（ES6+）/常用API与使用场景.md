# 📌 JavaScript（ES6+）常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重 **ES6+ 语法、常用 API 与场景**，便于速查与校招复习。

---

## 🌱 一、变量与类型

### 📖 核心 API 与语法

| 语法/API | 说明 | 示例 | 应用场景 |
|----------|------|------|----------|
| **let / const** | 块级作用域；const 引用不可改 | `let a = 1; const obj = {}; obj.x = 1` | 变量声明与作用域管理 |
| **typeof** | 类型判断（注意 null 为 "object"） | `typeof [] === 'object'` | 基本类型检查 |
| **instanceof** | 实例判断 | `[] instanceof Array` | 引用类型检查 |
| **Object.prototype.toString.call** | 准确类型判断 | `Object.prototype.toString.call(null) === '[object Null]'` | 所有类型检查 |
| **??** | 空值合并，仅 null/undefined 取右侧 | `value ?? 'default'` | 默认值设置 |
| **?.** | 可选链，避免 undefined 报错 | `obj?.a?.b` | 安全访问嵌套对象 |
| **!!** | 强制转为布尔值 | `!!value` | 布尔值转换 |
| **+** | 快捷数字转换 | `+"123"` | 字符串转数字 |

### 💡 实用技巧

**类型判断工具函数**：
```javascript
function getType(value) {
    return Object.prototype.toString.call(value).slice(8, -1).toLowerCase();
}

console.log(getType(1)); // 'number'
console.log(getType('hello')); // 'string'
console.log(getType([])); // 'array'
console.log(getType(null)); // 'null'
```

**空值处理**：
```javascript
// 传统方式
const name = user.name || '默认值'; // 会把空字符串、0等falsy值替换为默认值

// 空值合并
const name = user.name ?? '默认值'; // 只有null和undefined才会使用默认值

// 可选链 + 空值合并
const city = user?.address?.city ?? '未知城市';
```

---

## 🌱 二、函数与 this

### 📖 核心 API 与语法

| 用法 | 说明 | 示例 | 应用场景 |
|------|------|------|----------|
| **箭头函数** | 无自身 this，继承外层；无 arguments | `const fn = () => this.value` | 回调函数、保持 this 上下文 |
| **call** | 立即执行，指定 this 和参数列表 | `fn.call(obj, arg1, arg2)` | 显式绑定 this |
| **apply** | 立即执行，指定 this 和参数数组 | `fn.apply(obj, [arg1, arg2])` | 显式绑定 this，参数为数组 |
| **bind** | 返回新函数，绑定 this 和预设参数 | `const boundFn = fn.bind(obj, arg1)` | 延迟执行，预设参数 |
| **闭包** | 函数引用外层变量，形成私有作用域 | `function createCounter() { let count = 0; return () => ++count; }` | 私有变量、状态管理 |

### 🔍 手写实现

**防抖函数**：
```javascript
function debounce(fn, delay) {
  let timer;
  return function (...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 使用
const debouncedSearch = debounce(searchFunction, 300);
input.addEventListener('input', debouncedSearch);
```

**节流函数**：
```javascript
function throttle(fn, delay) {
  let lastCall = 0;
  return function (...args) {
    const now = Date.now();
    if (now - lastCall >= delay) {
      lastCall = now;
      return fn.apply(this, args);
    }
  };
}

// 使用
const throttledScroll = throttle(scrollFunction, 100);
window.addEventListener('scroll', throttledScroll);
```

**深拷贝**：
```javascript
function deepClone(obj) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof Array) return obj.map(item => deepClone(item));
  if (typeof obj === 'object') {
    const clonedObj = {};
    for (const key in obj) {
      if (obj.hasOwnProperty(key)) {
        clonedObj[key] = deepClone(obj[key]);
      }
    }
    return clonedObj;
  }
}
```

### 💬 面试问答

> **问：箭头函数与普通函数的区别？**
> **答**：箭头函数没有自己的 this，继承外层作用域的 this；没有 arguments 对象；不能作为构造函数使用；没有 prototype 属性；语法更简洁。

> **问：call、apply、bind 的区别？**
> **答**：call 和 apply 会立即执行函数，call 接收参数列表，apply 接收参数数组；bind 返回一个新函数，不会立即执行，可预设参数。

> **问：闭包的优缺点？**
> **答**：优点：实现私有变量、延长变量生命周期、模块化；缺点：可能导致内存泄漏（变量长期被引用）。

---

## 🌱 三、解构与展开

### 📖 核心语法

| 语法 | 示例 | 应用场景 |
|------|------|----------|
| **数组解构** | `const [a, b, ...rest] = [1, 2, 3, 4]` | 数组元素提取 |
| **对象解构** | `const { name, age = 18 } = user` | 对象属性提取 |
| **嵌套解构** | `const { address: { city } } = user` | 嵌套对象属性提取 |
| **参数解构** | `function fn({ name, age }) {}` | 函数参数简化 |
| **展开运算符** | `[...arr], { ...obj }` | 数组/对象展开 |
| **剩余参数** | `function fn(...args) {}` | 不定参数收集 |

### 💡 实用技巧

**函数参数默认值**：
```javascript
function createUser({ 
  name = '匿名', 
  age = 18, 
  gender = '未知' 
} = {}) {
  return { name, age, gender };
}

const user = createUser({ name: '张三' });
```

**数组操作**：
```javascript
// 合并数组
const arr1 = [1, 2];
const arr2 = [3, 4];
const merged = [...arr1, ...arr2]; // [1, 2, 3, 4]

// 复制数组
const copy = [...arr1];

// 转换类数组对象
const args = [...arguments];
const nodes = [...document.querySelectorAll('div')];
```

**对象操作**：
```javascript
// 合并对象
const obj1 = { a: 1 };
const obj2 = { b: 2 };
const merged = { ...obj1, ...obj2 }; // { a: 1, b: 2 }

// 复制对象
const copy = { ...obj1 };

// 覆盖属性
const updated = { ...obj1, a: 10 };
```

---

## 🌱 四、Promise 与 async/await

### 📖 核心 API

| API | 说明 | 示例 | 应用场景 |
|-----|------|------|----------|
| **new Promise** | 创建 Promise | `new Promise((resolve, reject) => {})` | 异步操作封装 |
| **.then** | 处理成功结果 | `promise.then(result => {})` | 链式调用 |
| **.catch** | 处理错误 | `promise.catch(error => {})` | 错误处理 |
| **.finally** | 无论成功失败都执行 | `promise.finally(() => {})` | 清理操作 |
| **Promise.all** | 全部成功才 resolve | `Promise.all([p1, p2])` | 并行请求 |
| **Promise.race** | 先完成的结果 | `Promise.race([p1, p2])` | 超时处理 |
| **Promise.allSettled** | 等全部结束 | `Promise.allSettled([p1, p2])` | 并行请求，关注所有结果 |
| **Promise.resolve** | 创建已解决的 Promise | `Promise.resolve(value)` | 快速创建 Promise |
| **Promise.reject** | 创建已拒绝的 Promise | `Promise.reject(error)` | 快速创建拒绝的 Promise |
| **async / await** | 异步函数语法 | `async function() { await promise }` | 同步化异步代码 |

### 🔍 实用示例

**异步函数错误处理**：
```javascript
async function fetchData() {
  try {
    const res = await fetch('https://api.example.com/data');
    if (!res.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await res.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
}
```

**并行请求**：
```javascript
async function fetchAllData() {
  try {
    const [user, posts, comments] = await Promise.all([
      fetch('/api/user').then(res => res.json()),
      fetch('/api/posts').then(res => res.json()),
      fetch('/api/comments').then(res => res.json())
    ]);
    return { user, posts, comments };
  } catch (error) {
    console.error('Error:', error);
  }
}
```

**超时处理**：
```javascript
function withTimeout(promise, timeout) {
  return Promise.race([
    promise,
    new Promise((_, reject) => {
      setTimeout(() => reject(new Error('Timeout')), timeout);
    })
  ]);
}

// 使用
const data = await withTimeout(fetchData(), 5000);
```

---

## 🌱 五、数组常用 API

### 📖 核心方法

| 方法 | 说明 | 返回值 | 应用场景 |
|------|------|--------|----------|
| **map** | 映射每个元素 | 新数组 | 数据转换 |
| **filter** | 过滤元素 | 新数组 | 数据筛选 |
| **find** | 查找首个满足条件的元素 | 元素或 undefined | 查找单个元素 |
| **findIndex** | 查找首个满足条件的索引 | 索引或 -1 | 查找元素位置 |
| **reduce** | 归并计算 | 累积值 | 求和、对象转换等 |
| **some** | 是否存在满足条件的元素 | boolean | 存在性检查 |
| **every** | 是否所有元素都满足条件 | boolean | 全量检查 |
| **includes** | 是否包含指定元素 | boolean | 包含性检查 |
| **flat** | 扁平化数组 | 新数组 | 嵌套数组处理 |
| **flatMap** | 映射后扁平化 | 新数组 | 映射+扁平化 |
| **sort** | 排序 | 原数组 | 数组排序 |
| **reverse** | 反转 | 原数组 | 数组反转 |
| **concat** | 合并数组 | 新数组 | 数组合并 |
| **slice** | 截取子数组 | 新数组 | 数组截取 |
| **splice** | 添加/删除元素 | 被删除的元素数组 | 数组修改 |
| **join** | 连接为字符串 | 字符串 | 数组转字符串 |
| **Array.isArray** | 是否为数组 | boolean | 类型检查 |
| **Array.from** | 从类数组对象创建数组 | 新数组 | 类数组转数组 |
| **Array.of** | 创建包含指定元素的数组 | 新数组 | 数组创建 |

### 🔍 实用示例

**数组去重**：
```javascript
// 方法1：Set
const unique = [...new Set(arr)];

// 方法2：filter
const unique = arr.filter((item, index) => arr.indexOf(item) === index);

// 方法3：reduce
const unique = arr.reduce((acc, item) => acc.includes(item) ? acc : [...acc, item], []);
```

**数组扁平化**：
```javascript
// 方法1：flat
const flattened = arr.flat(Infinity);

// 方法2：reduce
const flattened = arr.reduce((acc, item) => {
  return acc.concat(Array.isArray(item) ? flattened(item) : item);
}, []);
```

**数组求和**：
```javascript
const sum = arr.reduce((acc, curr) => acc + curr, 0);
```

**对象数组处理**：
```javascript
// 根据属性分组
const grouped = arr.reduce((acc, item) => {
  const key = item.category;
  if (!acc[key]) acc[key] = [];
  acc[key].push(item);
  return acc;
}, {});

// 提取属性
const names = arr.map(item => item.name);

// 按属性排序
const sorted = arr.sort((a, b) => a.age - b.age);
```

---

## 🌱 六、对象与字符串

### 📖 对象 API

| API | 说明 | 示例 | 应用场景 |
|-----|------|------|----------|
| **Object.keys** | 自身可枚举属性键数组 | `Object.keys(obj)` | 对象遍历 |
| **Object.values** | 属性值数组 | `Object.values(obj)` | 值提取 |
| **Object.entries** | [key, value] 数组 | `Object.entries(obj)` | 键值对遍历 |
| **Object.assign** | 浅拷贝合并 | `Object.assign(target, ...sources)` | 对象合并 |
| **Object.freeze** | 冻结对象 | `Object.freeze(obj)` | 防止修改 |
| **Object.seal** | 密封对象 | `Object.seal(obj)` | 防止添加/删除属性 |
| **Object.getOwnPropertyDescriptor** | 获取属性描述符 | `Object.getOwnPropertyDescriptor(obj, 'key')` | 属性详情 |
| **Object.defineProperty** | 定义属性 | `Object.defineProperty(obj, 'key', descriptor)` | 属性定制 |
| **Object.hasOwnProperty** | 检查自身属性 | `obj.hasOwnProperty('key')` | 属性检查 |
| **Object.prototype.toString** | 类型判断 | `Object.prototype.toString.call(obj)` | 类型检查 |

### 📖 字符串 API

| API | 说明 | 示例 | 应用场景 |
|-----|------|------|----------|
| **includes** | 是否包含子串 | `str.includes('sub')` | 包含性检查 |
| **startsWith** | 是否以子串开头 | `str.startsWith('prefix')` | 前缀检查 |
| **endsWith** | 是否以子串结尾 | `str.endsWith('suffix')` | 后缀检查 |
| **padStart** | 前补位 | `str.padStart(5, '0')` | 格式化数字 |
| **padEnd** | 后补位 | `str.padEnd(5, '0')` | 格式化 |
| **trim** | 去除首尾空白 | `str.trim()` | 清理输入 |
| **trimStart** | 去除开头空白 | `str.trimStart()` | 清理输入 |
| **trimEnd** | 去除结尾空白 | `str.trimEnd()` | 清理输入 |
| **split** | 分割为数组 | `str.split(',')` | 字符串分割 |
| **join** | 连接数组为字符串 | `arr.join(',')` | 数组转字符串 |
| **replace** | 替换子串 | `str.replace('old', 'new')` | 字符串替换 |
| **replaceAll** | 替换所有匹配 | `str.replaceAll('old', 'new')` | 全局替换 |
| **substring** | 截取子串 | `str.substring(0, 5)` | 字符串截取 |
| **slice** | 截取子串 | `str.slice(0, 5)` | 字符串截取 |
| **substr** | 截取子串（已废弃） | `str.substr(0, 5)` | 字符串截取 |
| **toUpperCase** | 转为大写 | `str.toUpperCase()` | 大小写转换 |
| **toLowerCase** | 转为小写 | `str.toLowerCase()` | 大小写转换 |
| **charAt** | 获取指定位置字符 | `str.charAt(0)` | 字符获取 |
| **charCodeAt** | 获取指定位置字符编码 | `str.charCodeAt(0)` | 字符编码 |
| **indexOf** | 查找子串位置 | `str.indexOf('sub')` | 位置查找 |
| **lastIndexOf** | 从后查找子串位置 | `str.lastIndexOf('sub')` | 位置查找 |
| **match** | 正则匹配 | `str.match(/pattern/)` | 正则匹配 |
| **search** | 正则搜索 | `str.search(/pattern/)` | 正则搜索 |
| **test** | 正则测试 | `/pattern/.test(str)` | 正则测试 |

### 🔍 实用示例

**对象深拷贝**：
```javascript
function deepClone(obj) {
  return JSON.parse(JSON.stringify(obj));
  // 注意：此方法无法处理函数、Date、RegExp等特殊类型
}
```

**对象遍历**：
```javascript
// 方法1：for...in
for (const key in obj) {
  if (obj.hasOwnProperty(key)) {
    console.log(key, obj[key]);
  }
}

// 方法2：Object.entries
Object.entries(obj).forEach(([key, value]) => {
  console.log(key, value);
});
```

**字符串操作**：
```javascript
// 格式化数字
const num = 5;
const formatted = num.toString().padStart(2, '0'); // '05'

// 驼峰转连字符
const camelCase = 'camelCase';
const kebabCase = camelCase.replace(/([a-z0-9]|(?=[A-Z]))([A-Z])/g, '$1-$2').toLowerCase(); // 'camel-case'

// 连字符转驼峰
const kebabCase = 'kebab-case';
const camelCase = kebabCase.replace(/-([a-z])/g, (_, letter) => letter.toUpperCase()); // 'kebabCase'
```

---

## 🌱 七、模块化（ES Module）

### 📖 核心语法

**导出**：
```javascript
// 命名导出
export const x = 1;
export function fn() {};
export class MyClass {};

// 默认导出
export default function defaultFn() {};
export default const defaultVar = 1;
export default {
  name: 'module',
  version: '1.0.0'
};

// 混合导出
export const x = 1;
export default function fn() {};
```

**导入**：
```javascript
// 导入默认导出
import defaultFn from './module.js';
import myModule from './module.js';

// 导入命名导出
import { x, fn } from './module.js';
import { x as myX, fn as myFn } from './module.js';

// 导入所有命名导出
import * as MyModule from './module.js';

// 混合导入
import defaultFn, { x, fn } from './module.js';
```

### 🔍 与 CommonJS 的区别

| 特性 | ES Module | CommonJS |
|------|-----------|----------|
| 语法 | `import`/`export` | `require`/`module.exports` |
| 加载方式 | 静态加载（编译时） | 动态加载（运行时） |
| 适用环境 | 浏览器、Node.js | Node.js |
| 导出方式 | 可以导出多个值 | 导出单个值 |
| 循环依赖 | 处理更好 | 可能有问题 |
| 文件扩展名 | `.mjs` 或 `type: "module"` | `.js` |

### 💡 实用技巧

**条件导入**：
```javascript
if (condition) {
  import('./module.js').then(module => {
    // 使用模块
  });
}
```

**动态导入**：
```javascript
async function loadModule() {
  const module = await import('./module.js');
  // 使用模块
}
```

---

## 🌱 八、事件循环与执行顺序（校招常考）

### 📖 核心概念

| 任务类型 | 包含内容 | 执行时机 |
|----------|----------|----------|
| **宏任务** | script、setTimeout、setInterval、I/O、UI 渲染 | 每轮事件循环执行一个 |
| **微任务** | Promise.then/catch/finally、queueMicrotask、MutationObserver | 每个宏任务执行后清空 |

### 🔍 执行顺序

1. 执行主线程同步代码
2. 执行微任务队列中的所有任务
3. 执行宏任务队列中的一个任务
4. 重复步骤2-3

### 💡 示例分析

```javascript
console.log('1'); // 同步代码

setTimeout(() => {
  console.log('2'); // 宏任务
}, 0);

Promise.resolve().then(() => {
  console.log('3'); // 微任务
});

console.log('4'); // 同步代码

// 输出顺序：1 -> 4 -> 3 -> 2
```

**解析**：
1. 执行同步代码 `console.log('1')`，输出 `1`
2. 执行同步代码 `console.log('4')`，输出 `4`
3. 执行微任务队列，输出 `3`
4. 执行宏任务队列，输出 `2`

### 🎯 面试常见题

**题目**：分析以下代码的输出顺序

```javascript
async function async1() {
  console.log('async1 start');
  await async2();
  console.log('async1 end');
}

async function async2() {
  console.log('async2');
}

console.log('script start');
setTimeout(() => {
  console.log('setTimeout');
}, 0);
async1();
new Promise(resolve => {
  console.log('promise1');
  resolve();
}).then(() => {
  console.log('promise2');
});
console.log('script end');
```

**答案**：
1. script start
2. async1 start
3. async2
4. promise1
5. script end
6. async1 end
7. promise2
8. setTimeout

**解析**：
- 同步代码：script start → async1 start → async2 → promise1 → script end
- 微任务：async1 end → promise2
- 宏任务：setTimeout

---

## 🌱 九、Map、Set、WeakMap、WeakSet

### 📖 核心 API

| 数据结构 | 说明 | 特点 | 应用场景 |
|----------|------|------|----------|
| **Map** | 键值对集合 | 键可以是任意类型，保持插入顺序 | 复杂键值映射 |
| **Set** | 唯一值集合 | 元素唯一，保持插入顺序 | 去重、集合操作 |
| **WeakMap** | 弱引用键值对 | 键必须是对象，垃圾回收时自动清理 | 缓存、私有属性 |
| **WeakSet** | 弱引用值集合 | 值必须是对象，垃圾回收时自动清理 | 对象引用跟踪 |

### 🔍 实用示例

**Map 用法**：
```javascript
const map = new Map();

// 添加元素
map.set('key1', 'value1');
map.set(1, 'value2');
map.set({ id: 1 }, 'value3');

// 获取元素
map.get('key1'); // 'value1'

// 检查元素
map.has('key1'); // true

// 删除元素
map.delete('key1');

// 遍历
for (const [key, value] of map) {
  console.log(key, value);
}

// 转换为数组
const entries = [...map.entries()];
const keys = [...map.keys()];
const values = [...map.values()];
```

**Set 用法**：
```javascript
const set = new Set();

// 添加元素
set.add(1);
set.add(2);
set.add(1); // 重复元素，不会添加

// 检查元素
set.has(1); // true

// 删除元素
set.delete(1);

// 遍历
for (const item of set) {
  console.log(item);
}

// 转换为数组
const array = [...set];

// 去重
const uniqueArray = [...new Set(arrayWithDuplicates)];
```

**WeakMap 用法**：
```javascript
const weakMap = new WeakMap();
const obj = {};

// 添加元素
weakMap.set(obj, 'value');

// 获取元素
weakMap.get(obj); // 'value'

// 检查元素
weakMap.has(obj); // true

// 删除元素
weakMap.delete(obj);

// 注意：WeakMap 不可遍历
```

---

## 🌱 十、正则表达式

### 📖 核心语法

| 语法 | 说明 | 示例 |
|------|------|------|
| **^** | 匹配开始 | `^abc` 匹配以abc开头 |
| **$** | 匹配结束 | `abc$` 匹配以abc结尾 |
| **.** | 匹配任意字符 | `a.c` 匹配abc、adc等 |
| **\d** | 匹配数字 | `\d+` 匹配一个或多个数字 |
| **\D** | 匹配非数字 | `\D+` 匹配一个或多个非数字 |
| **\w** | 匹配字母、数字、下划线 | `\w+` 匹配单词 |
| **\W** | 匹配非字母、数字、下划线 | `\W+` 匹配非单词 |
| **\s** | 匹配空白字符 | `\s+` 匹配一个或多个空白 |
| **\S** | 匹配非空白字符 | `\S+` 匹配一个或多个非空白 |
| **[abc]** | 匹配方括号内的任意字符 | `[aeiou]` 匹配元音字母 |
| **[^abc]** | 匹配方括号外的任意字符 | `[^0-9]` 匹配非数字 |
| **ab** | 匹配a或b | `catdog` 匹配cat或dog |
| **a*` | 匹配0个或多个a | `a*` 匹配空、a、aa等 |
| **a+** | 匹配1个或多个a | `a+` 匹配a、aa等 |
| **a?** | 匹配0个或1个a | `a?` 匹配空或a |
| **a{n}** | 匹配n个a | `a{3}` 匹配aaa |
| **a{n,}** | 匹配至少n个a | `a{2,}` 匹配aa、aaa等 |
| **a{n,m}** | 匹配n到m个a | `a{2,4}` 匹配aa、aaa、aaaa |
| **(abc)** | 捕获组 | `(\d{4})-(\d{2})-(\d{2})` 匹配日期 |
| **(?:abc)** | 非捕获组 | 提高性能 |

### 🔍 实用示例

**邮箱验证**：
```javascript
const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const isValid = emailRegex.test('user@example.com');
```

**手机号验证**：
```javascript
const phoneRegex = /^1[3-9]\d{9}$/;
const isValid = phoneRegex.test('13812345678');
```

**URL验证**：
```javascript
const urlRegex = /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/;
const isValid = urlRegex.test('https://www.example.com');
```

**密码强度验证**：
```javascript
// 至少8位，包含大小写字母和数字
const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$/;
const isValid = passwordRegex.test('MyPass123');
```

---

## 🌱 十一、实战手写题速查

### 📖 防抖与节流

| 类型 | 核心思路 | 关键代码 |
|------|----------|----------|
| **防抖** | 延迟执行，清除定时器重新计时 | `clearTimeout(timer); timer = setTimeout(...)` |
| **节流（时间戳）** | 记录上次执行时间，判断是否到达间隔 | `if (now - lastTime >= delay) { ... }` |
| **节流（定时器）** | 使用定时器控制执行频率 | `if (!timer) { timer = setTimeout(...) }` |

### 📖 深拷贝与浅拷贝

| 类型 | 实现方式 | 特点 |
|------|----------|------|
| **浅拷贝** | 展开运算符、Object.assign、slice | 只拷贝第一层 |
| **深拷贝（JSON）** | `JSON.parse(JSON.stringify(obj))` | 简单但不完善 |
| **深拷贝（递归）** | 递归拷贝 + WeakMap处理循环引用 | 完整但复杂 |

### 📖 数组常用操作

| 操作 | 实现方式 | 代码示例 |
|------|----------|----------|
| **去重** | Set | `[...new Set(arr)]` |
| **扁平化** | flat | `arr.flat(Infinity)` |
| **求和** | reduce | `arr.reduce((a, b) => a + b, 0)` |
| **分组** | reduce | `arr.reduce((acc, item) => { ... }, {})` |
| **排序** | sort | `arr.sort((a, b) => a - b)` |

### 📖 高频手写题

| 题目 | 核心思路 |
|------|----------|
| **Promise** | 状态管理、回调队列、then链式调用 |
| **new** | 创建对象、设置原型、执行构造函数 |
| **call/apply** | 将函数作为对象属性执行 |
| **bind** | 返回新函数，预设参数 |
| **instanceof** | 遍历原型链查找 |
| **curry** | 闭包保存参数，参数足够时执行 |

---

## 🌱 十二、校招面试高频考点

### 📖 核心考点

| 考点 | 核心内容 | 常见问题 |
|------|----------|----------|
| **闭包** | 概念、形成条件、用途、内存泄漏 | 解释闭包、闭包的优缺点、手写闭包 |
| **this 指向** | 默认绑定、隐式绑定、显式绑定、new绑定、箭头函数 | this的指向规则、call/apply/bind的区别 |
| **原型链** | prototype、__proto__、constructor、继承 | 解释原型链、实现继承的方式 |
| **事件循环** | 宏任务、微任务、执行顺序 | 分析代码输出顺序 |
| **Promise** | 状态、链式调用、API使用 | Promise的工作原理、手写Promise |
| **async/await** | 语法、错误处理、与Promise的关系 | async/await的实现原理 |
| **数组操作** | 常用API、手写实现 | 数组去重、扁平化、排序 |
| **对象操作** | 遍历、合并、深拷贝 | 深拷贝的实现、对象遍历方法 |
| **模块化** | ES Module与CommonJS的区别 | 模块化的优点、两种模块系统的区别 |
| **类型判断** | typeof、instanceof、Object.prototype.toString.call | 如何准确判断类型 |

### 📖 面试答题框架

**概念解释类**：
1. 先给出明确定义
2. 说明核心特点/原理
3. 举例说明应用场景
4. 提及注意事项/优缺点

**代码分析类**：
1. 识别同步代码和异步代码
2. 确定宏任务和微任务
3. 按执行顺序逐步分析
4. 给出最终输出结果

**手写实现类**：
1. 明确功能需求
2. 确定核心算法/思路
3. 处理边界条件
4. 考虑特殊情况（循环引用、this绑定等）

### 💡 面试技巧

1. **理解核心概念**：不仅要知道API的用法，还要理解其背后的原理
2. **手写实现**：掌握常见函数的手写实现，如防抖、节流、深拷贝、Promise等
3. **分析问题**：遇到复杂问题时，先理清思路，再逐步解决
4. **实践经验**：结合实际项目经验，说明API的应用场景
5. **持续学习**：关注JavaScript的新特性和最佳实践

---

## 🌱 十三、最佳实践

### 📖 代码规范

1. **变量命名**：使用语义化的变量名，驼峰命名法
2. **函数设计**：函数应单一职责，避免过长函数
3. **错误处理**：使用try/catch或Promise.catch处理错误
4. **代码风格**：保持一致的代码风格，使用ESLint和Prettier
5. **性能优化**：避免频繁DOM操作，合理使用缓存

### 📖 性能优化

1. **减少重排重绘**：批量修改DOM，使用documentFragment
2. **防抖节流**：对频繁触发的事件使用防抖或节流
3. **内存管理**：及时清理引用，避免内存泄漏
4. **网络优化**：使用CDN，压缩资源，合理缓存
5. **代码分割**：使用动态导入，减少初始加载时间

### 📖 安全注意事项

1. **XSS攻击**：对用户输入进行转义
2. **CSRF攻击**：使用CSRF token
3. **注入攻击**：避免使用eval，使用参数化查询
4. **密码安全**：使用bcrypt等算法加密存储密码
5. **敏感信息**：不要在前端存储敏感信息

---

## 🌱 十四、与学习笔记的对应关系

| 学习笔记章节 | 对应速查章节 | 核心内容 |
|--------------|--------------|----------|
| 第1章：JavaScript 概述与运行环境 | 八、事件循环与执行顺序 | 执行机制、宏任务、微任务 |
| 第2章：基础语法与类型 | 一、变量与类型 | 变量声明、类型判断、类型转换 |
| 第3章：函数与闭包 | 二、函数与 this | 箭头函数、this绑定、闭包 |
| 第4章：面向对象与原型 | 六、对象与字符串 | 对象操作、属性描述符 |
| 第5章：异步与 Promise | 四、Promise 与 async/await | Promise API、async/await |
| 第6章：ES6+ 常用特性 | 三、解构与展开、七、模块化 | 解构语法、展开运算符、ES Module |
| 第7章：实战与面试要点 | 十二、实战手写题速查、十三、校招面试高频考点 | 实战技巧、面试重点 |

---

> **总结**：本速查手册涵盖了JavaScript（ES6+）的核心API和使用场景，配合《学习笔记》使用，可帮助你快速掌握JavaScript的关键知识点，应对校招面试和日常开发。
