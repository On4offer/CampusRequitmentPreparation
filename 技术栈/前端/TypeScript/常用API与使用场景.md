# 📌 TypeScript 常用API与核心使用场景速查大全

> **说明**：本文档作为《TypeScript 学习笔记》的强力补充，侧重于**高频 API 的语法速查、典型实战场景的直接复用（可作为项目开发代码片段库）、以及面试常考的“类型体操”手写指北**。内容严格对标一线大厂在前端工程化对 TS 的深度要求。

---

## 一、基础类型与特殊类型速查

| 类型 | 语法示例 | 使用场景与说明 |
|---|---|---|
| **基本数据类型** | `let n: number = 1; let s: string = 'A'; let b: boolean = true;` | 常规变量声明，通常建议让 TS **自动推断**。 |
| **数组** | `let arr: number[] = [1, 2];` <br> `let arr2: Array<string> = ['A'];` | 存储同类型数据的集合。 |
| **元组 (Tuple)** | `let point: [number, number] = [10, 20];` | 已知元素数量和类型的数组。常用于表示坐标，或者 React 的 `useState` 返回值。 |
| **联合类型** | `let id: string \| number = 10;` | 变量可能是多种类型中的一种。 |
| **字面量类型** | `type Direction = 'left' \| 'right' \| 'top' \| 'bottom';` | 限制变量只能是特定的几个值，常用于配置项、状态枚举。 |
| **`any`** | `let data: any = res;` | 放弃类型检查。**极度不推荐**。 |
| **`unknown`** | `let data: unknown = res;` | 安全的 `any`。使用前必须进行**类型收窄**（如 `typeof` 或断言）。用于不确定的外部数据（如 API 返回，`try/catch` 的 `error`）。 |
| **`void`** | `function log(): void { console.log('hi'); }` | 表示函数没有返回值。 |
| **`never`** | `function throwError(): never { throw new Error(); }` | 永不返回的函数（抛错、死循环），或在条件类型 / 联合类型中表示“不可能到达的底部”。 |

### 💡 常见坑与避坑指南

| 错误写法 / 危险操作 | 正确写法 / 规范操作 | 备注 |
|---------------------|---------------------|------|
| `let data: any = fetch(); data.forEach();` | `let data: unknown = fetch(); if (Array.isArray(data)) { data.forEach(); }` | 避免 AnyScript 蔓延。 |
| 遇到 `error` 不知道类型直接 `.message` | `catch (e: unknown) { if (e instanceof Error) console.log(e.message) }` | 在 TS 4.4 之后，catch 的默认类型是 `unknown`，必须缩小类型。 |

---

## 二、接口 (Interface) 与 类型别名 (Type)

### 2.1 Interface 核心语法

```typescript
// 1. 基本与可选/只读属性
interface User {
  id: number;
  name: string;
  avatar?: string;         // 可选属性
  readonly createdAt: number; // 只读属性
}

// 2. 索引签名（当不知道会有哪些额外属性时）
interface Config {
  env: string;
  [key: string]: any; // 允许任意数量的其他属性
}

// 3. 接口继承
interface Admin extends User {
  role: 'admin' | 'superadmin';
  permissions: string[];
}
```

### 2.2 Type 核心语法

```typescript
// 1. 基本定义
type ID = string | number; // 联合类型只能用 type

// 2. 交叉类型（类似于接口继承）
type Timestamp = { createdAt: number; updatedAt: number };
type Article = { title: string; content: string } & Timestamp;
```

### 2.3 `interface` vs `type` 选型指南

- **用 `interface` 的场景**：定义对象的形状、组件的 `Props` / `State`、向外暴露的 API 响应结构。原因：**支持声明合并（Declaration Merging）**，对第三方库扩展更友好，且错误提示更直接。
- **用 `type` 的场景**：定义基础类型的别名、**联合类型**（如 `'a' | 'b'`）、**交叉类型**、提取对象的 `keyof` 映射、手写复杂的**条件类型**（类型体操）。

---

## 三、泛型 (Generics) 与类型约束

泛型是 TS 进阶的核心，相当于“**类型的参数**”。

### 3.1 泛型函数与接口

```typescript
// 1. 泛型函数
function wrapInArray<T>(value: T): T[] {
  return [value];
}
const strArr = wrapInArray('hello'); // 自动推断 T 为 string，返回 string[]

// 2. 泛型接口 (非常常用的 API 响应体封装)
interface ApiResponse<T = any> { // 默认类型为 any
  code: number;
  message: string;
  data: T;
}

// 使用场景
interface UserInfo { name: string; age: number; }
const res: ApiResponse<UserInfo> = await fetchUser();
console.log(res.data.name); // 完美推断出 name
```

### 3.2 泛型约束 (`extends`)

如果我们想保证传入的泛型必须具备某些属性（比如必须有 `.length` 属性）：

```typescript
interface Lengthwise {
  length: number;
}

// T 必须具备 Lengthwise 的特征
function logLength<T extends Lengthwise>(arg: T): T {
  console.log(arg.length);
  return arg;
}

logLength("hello"); // OK，string 有 length
logLength([1, 2, 3]); // OK，数组 有 length
// logLength(123); // Error: number 没有 length
```

### 3.3 `keyof` 与对象属性约束

获取对象上的特定键对应的值，是最常见的高级用法。

```typescript
// K 必须是 T 所有的 key 的集合中的一个
function getProperty<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}

const user = { name: "Alice", age: 25 };
const age = getProperty(user, "age"); // 推断为 number
// getProperty(user, "address"); // Error: Argument of type '"address"' is not assignable to parameter of type '"name" | "age"'.
```

---

## 四、内置高级工具类型 (Utility Types) 必背

TypeScript 提供了全局可用的泛型工具，利用它们可以大量减少冗余的接口定义。

| 工具类型 | 作用与解析 | 实战场景示例 |
|----------|------------|--------------|
| **`Partial<T>`** | 将 `T` 的所有属性变成**可选** (`?`)。 | **更新接口**：`updateUser(id: number, data: Partial<User>)`，不需要传完整对象。 |
| **`Required<T>`** | 将 `T` 的所有属性变成**必选**。 | 消除上游传来的数据的可选状态，强制全量校验。 |
| **`Readonly<T>`** | 将 `T` 的所有属性变成**只读**。 | 防止传入的配置对象/状态在函数内部被意外修改（如 Redux 的 State）。 |
| **`Pick<T, K>`** | 从 `T` 中**提取**一部分属性 `K`。 | **组件开发**：一个大接口有 10 个字段，当前卡片组件只需 3 个：`type CardProps = Pick<User, 'id' | 'name' | 'avatar'>`。 |
| **`Omit<T, K>`** | 从 `T` 中**剔除**一部分属性 `K`。 | **新增接口**：提交给后端的数据往往不需要自带 `id`，`type CreateUserDTO = Omit<User, 'id'>`。 |
| **`Record<K, T>`** | 构造一个键类型为 `K`，值类型为 `T` 的对象类型。 | **字典/映射表**：`const map: Record<string, User> = { 'uuid1': user1 }`。 |
| **`Exclude<T, U>`**| 从联合类型 `T` 中**排除**可分配给 `U` 的类型。 | 操作联合类型：`type T0 = Exclude<"a" | "b" | "c", "a">` -> `"b" | "c"`。 |
| **`Extract<T, U>`**| 从联合类型 `T` 中**提取**可分配给 `U` 的类型。 | 与 `Exclude` 相反：`Extract<"a" | "b" | "c", "a" | "f">` -> `"a"`。 |
| **`ReturnType<T>`**| 获取**函数的返回值**类型。 | 获取某些未导出返回类型的第三方函数的产物类型：`type State = ReturnType<typeof store.getState>`。 |
| **`Parameters<T>`**| 获取函数的**参数类型**（返回元组）。 | 拦截/代理某个函数时，推导其入参类型。 |
| **`Awaited<T>`** | (TS 4.5+) 递归提取 `Promise` 内部的类型。 | 配合 `ReturnType`：`type Data = Awaited<ReturnType<typeof fetchUser>>`。 |

---

## 五、断言 (Assertion) 与类型守卫 (Type Guards)

在实际业务中，TS 经常会报“类型不匹配”或“可能为 null”，此时需要断言和守卫来缩小类型。

### 5.1 类型断言 (`as` / `!`)

- **`as` 断言**：强制告诉编译器变量的类型。（注意：它只能骗过编译器，如果运行时真实数据与断言不符，仍然会引发 bug）。
- **`!` 非空断言**：告诉编译器“这个东西绝对不为 null 或 undefined”。

```typescript
// 1. as 断言获取确切 DOM 元素
const input = document.getElementById('my-input') as HTMLInputElement;
console.log(input.value); 

// 2. 非空断言（慎用，尽量用可选链 ?. 替代）
const config: { host?: string } = {};
// console.log(config.host!.length); // 编译不报错，但运行时因为 host 是 undefined 会崩溃
console.log(config.host?.length);    // 推荐做法（安全）
```

### 5.2 常用类型守卫 (Type Guards)

为了安全地缩小 `unknown` 或联合类型的范围，应该在运行时进行判断：

```typescript
// 1. typeof 守卫（适合基础类型）
function printId(id: string | number) {
  if (typeof id === 'string') {
    console.log(id.toUpperCase()); // 此块内 id 必为 string
  }
}

// 2. instanceof 守卫（适合类、内置对象）
function handleDate(date: Date | string) {
  if (date instanceof Date) {
    console.log(date.getTime()); // 此块内 date 必为 Date
  }
}

// 3. in 守卫（适合检查对象属性）
interface Fish { swim: () => void; }
interface Bird { fly: () => void; }
function move(animal: Fish | Bird) {
  if ('swim' in animal) {
    animal.swim(); // 此块内 animal 必为 Fish
  } else {
    animal.fly();
  }
}

// 4. 自定义类型谓词（is）
// 返回 boolean，告诉 TS "如果返回 true，参数就是特定的类型"
function isString(val: any): val is string {
  return typeof val === 'string';
}
```

---

## 六、高级类型与类型体操 (进阶/面试必考)

面试中常考手写简单的 `Utility Types`，这涉及到**条件类型**、**映射类型**和 **`infer`**。

### 6.1 条件类型 (`T extends U ? X : Y`)

```typescript
// 如果 T 是 string，则类型为 true，否则为 false
type IsString<T> = T extends string ? true : false;
type A = IsString<"hello">; // true
```

### 6.2 `infer` (在条件类型中推断)

`infer` 相当于在匹配模式时声明一个局部变量，把匹配到的类型“抠出来”。

```typescript
// 面试题：手写 ReturnType
// 解析：如果 T 是一个函数，则把它返回的类型提取出来放到 R 中，结果返回 R；否则返回 any
type MyReturnType<T> = T extends (...args: any[]) => infer R ? R : any;

// 面试题：手写获取 Promise 内部的类型（基础版）
type UnpackPromise<T> = T extends Promise<infer U> ? U : T;
```

### 6.3 映射类型 (`[K in keyof T]`)

对现有对象的键值进行遍历映射，通常配合修饰符（如 `-?` 移除可选，`+readonly` 添加只读）。

```typescript
// 面试题：手写 Partial
type MyPartial<T> = {
  [K in keyof T]?: T[K]; // 遍历 T 的每一个键，并在后面加上 ?
};

// 面试题：手写 Readonly
type MyReadonly<T> = {
  readonly [K in keyof T]: T[K];
};
```

---

## 七、主流框架结合实战场景速查

这是目前企业开发中最核心的应用，涵盖 React 和 Vue 3 的标准 TS 写法。

### 7.1 React + TypeScript 最佳实践

#### 1. 组件 Props 与 FC 声明
```tsx
import React, { ReactNode } from 'react';

// 推荐使用普通函数 + Props 接口的写法（React 18+ 不再推荐 React.FC）
interface ButtonProps {
  type?: 'primary' | 'default';
  onClick: (e: React.MouseEvent<HTMLButtonElement>) => void;
  children: ReactNode; // React 18 需要显式声明 children
}

function Button({ type = 'default', onClick, children }: ButtonProps) {
  return <button className={`btn-${type}`} onClick={onClick}>{children}</button>;
}
```

#### 2. Hooks 常用类型
```tsx
import { useState, useRef, useReducer } from 'react';

// useState
// 初始值为 null 时，必须显式泛型
const [user, setUser] = useState<User | null>(null);
// 简单类型可推断
const [count, setCount] = useState(0); 

// useRef 获取 DOM
// 必须赋予初始值 null，并指明元素类型
const inputRef = useRef<HTMLInputElement>(null);
const focus = () => inputRef.current?.focus();

// useRef 存变量（不变的 Ref）
const timerRef = useRef<number>(0);
```

#### 3. 常见事件类型映射
| 事件场景 | TypeScript 类型 |
|---|---|
| 表单输入 (`onChange`) | `React.ChangeEvent<HTMLInputElement>` |
| 按钮点击 (`onClick`) | `React.MouseEvent<HTMLButtonElement>` |
| 表单提交 (`onSubmit`) | `React.FormEvent<HTMLFormElement>` |
| 键盘事件 (`onKeyDown`) | `React.KeyboardEvent<HTMLInputElement>` |

### 7.2 Vue 3 (Composition API) + TypeScript 最佳实践

#### 1. ref 与 reactive
```ts
import { ref, reactive } from 'vue';

// ref 复杂类型
const list = ref<User[]>([]);
const el = ref<HTMLElement | null>(null); // DOM ref

// reactive（通常不需要显式泛型，靠初始值推断）
const state = reactive({
  user: null as User | null, // 局部断言
  loading: false
});
```

#### 2. defineProps 与 defineEmits (基于类型的声明)
```vue
<script setup lang="ts">
// Props
// 使用 withDefaults 定义默认值
export interface Props {
  msg: string;
  labels?: string[];
}
const props = withDefaults(defineProps<Props>(), {
  labels: () => ['one', 'two'] // 对象和数组需要用工厂函数返回
});

// Emits
const emit = defineEmits<{
  (e: 'change', id: number): void;
  (e: 'update', value: string): void;
}>();
</script>
```

#### 3. 获取子组件实例 (Template Refs)
```vue
<script setup lang="ts">
import { ref } from 'vue';
import MyChild from './MyChild.vue';

// 使用 InstanceType 提取组件的实例类型
const childRef = ref<InstanceType<typeof MyChild> | null>(null);

const callChildMethod = () => {
  childRef.value?.someMethod();
};
</script>
```

---

## 八、企业级典型业务场景模板

可以直接在业务代码中复用的 TS 模板。

### 8.1 Axios 通用请求封装模板

```typescript
import axios, { AxiosRequestConfig, AxiosResponse } from 'axios';

// 1. 定义后端统一返回结构
export interface BaseResponse<T = any> {
  code: number;
  message: string;
  data: T;
}

// 2. 封装带泛型的通用请求方法
export const request = <T>(config: AxiosRequestConfig): Promise<BaseResponse<T>> => {
  return new Promise((resolve, reject) => {
    axios.request<BaseResponse<T>>(config)
      .then((res: AxiosResponse<BaseResponse<T>>) => {
        if (res.data.code === 200) {
          resolve(res.data);
        } else {
          // 统一错误处理
          reject(new Error(res.data.message));
        }
      })
      .catch(err => reject(err));
  });
};

// 3. 业务调用示例
interface UserInfo { id: string; name: string; }

export const fetchUserInfo = (id: string) => {
  // 调用时指明希望返回的 data 类型是 UserInfo
  return request<UserInfo>({ url: `/api/user/${id}`, method: 'GET' });
};
```

### 8.2 枚举与字典维护模板

推荐使用 **常量对象 + typeof** 的组合，而不是直接使用 `enum`（因为原生 `enum` 编译后会生成额外的对象，增加包体积，且有双向映射的坑）。

```typescript
// 1. 定义常量字典 (使用 as const 把它冻结为字面量类型)
export const STATUS_MAP = {
  PENDING: 0,
  SUCCESS: 1,
  FAILED: 2,
} as const;

// 2. 提取值类型（常用：提取 0 | 1 | 2）
// typeof STATUS_MAP => 获取对象类型
// [keyof typeof STATUS_MAP] => 获取所有的 value 类型
export type StatusValue = typeof STATUS_MAP[keyof typeof STATUS_MAP];

// 3. 业务使用
function handleStatus(status: StatusValue) {
  if (status === STATUS_MAP.SUCCESS) {
    // ...
  }
}
```

---

## 九、总结与复习指引

- **日常开发中**：把**内置工具类型**（`Partial/Pick/Omit`等）当成肌肉记忆；熟练掌握**组件的 Props 与 Emits 泛型定义**。
- **排查报错时**：第一反应判断是类型过窄还是过宽，如果是 `unknown` 要先写 `if`（类型守卫）；如果是外部不可控类型考虑 `as`。
- **校招面试时**：重点复习 `interface` vs `type` 的异同、`any` vs `unknown` 的区别，并尝试在演草纸上默写基础的**类型体操**（如 `ReturnType`、`Partial`）。
