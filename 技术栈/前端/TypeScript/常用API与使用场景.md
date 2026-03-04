# 📌 TypeScript 常用语法与使用场景速查

> 配合《学习笔记》使用，侧重 **类型、接口、泛型与常用语法**，便于速查与校招复习。

---

## 一、基础类型

```ts
let n: number = 1;
let s: string = 'a';
let b: boolean = true;
let u: undefined = undefined;
let nu: null = null;
let arr: number[] = [1, 2];
let tuple: [string, number] = ['a', 1];
let union: string | number = 1;
let literal: 'a' | 'b' = 'a';
```

| 语法 | 说明 |
|------|------|
| **as Type** | 类型断言 |
| **value!** | 非空断言（排除 null/undefined） |
| **?** | 可选属性或可选参数 |

---

## 二、接口与类型别名

```ts
interface User {
  id: number;
  name: string;
  readonly createdAt: Date;
  age?: number;
  [key: string]: unknown; // 索引签名
}
interface Admin extends User {
  role: 'admin';
}

type ID = string | number;
type Point = { x: number; y: number };
type Callback = (err: Error | null, data: string) => void;
```

| 对比 | interface | type |
|------|------------|------|
| 扩展 | extends | 交叉 & |
| 声明合并 | 支持同名合并 | 不支持 |
| 联合/复杂 | 不直接写联合 | 可写联合、映射等 |

---

## 三、泛型

```ts
function identity<T>(x: T): T {
  return x;
}
function first<T>(arr: T[]): T | undefined {
  return arr[0];
}
interface Box<T> {
  value: T;
}
// 约束
function getProp<T, K extends keyof T>(obj: T, key: K): T[K] {
  return obj[key];
}
```

| 写法 | 说明 |
|------|------|
| **&lt;T&gt;** | 泛型参数 |
| **T extends U** | 泛型约束 |
| **keyof T** | 键的联合类型 |
| **T[K]** | 索引访问类型 |

---

## 四、常用工具类型

| 类型 | 说明 | 示例 |
|------|------|------|
| **Partial&lt;T&gt;** | 所有属性可选 | Partial&lt;User&gt; |
| **Required&lt;T&gt;** | 所有属性必选 | Required&lt;User&gt; |
| **Readonly&lt;T&gt;** | 只读 | Readonly&lt;User&gt; |
| **Pick&lt;T, K&gt;** | 选取部分键 | Pick&lt;User, 'id' \| 'name'&gt; |
| **Omit&lt;T, K&gt;** | 排除部分键 | Omit&lt;User, 'id'&gt; |
| **Record&lt;K, V&gt;** | 键值类型构造 | Record&lt;string, number&gt; |
| **ReturnType&lt;F&gt;** | 函数返回值类型 | ReturnType&lt;typeof fn&gt; |

---

## 五、函数类型

```ts
type Fn = (a: number, b?: string) => boolean;
function fn(a: number, b: string = 'x'): number {
  return a;
}
// 重载
function overload(x: string): number;
function overload(x: number): string;
function overload(x: string | number): number | string {
  return typeof x === 'string' ? 1 : 'a';
}
```

---

## 六、类与模块

```ts
class Animal {
  constructor(public name: string, private age: number) {}
  greet(): string {
    return this.name;
  }
}
class Dog extends Animal {
  override greet(): string {
    return super.greet() + '!';
  }
}
```

- **声明文件**：`.d.ts` 中 `declare const x: string`、`declare function f(): void`；使用 `@types/xxx` 安装库类型。

---

## 七、Vue / React 中常用

| 场景 | 示例/要点 |
|------|-----------|
| **Vue Props** | `defineProps<{ id: number; name?: string }>()` |
| **Vue Emits** | `defineEmits<{ (e: 'submit', id: number): void }>()` |
| **Vue ref** | `ref<HTMLElement \| null>(null)`、`ref<User[]>([])` |
| **React useState** | `useState<number>(0)`、`useState<User \| null>(null)` |
| **React 事件** | `React.ChangeEvent<HTMLInputElement>`、`React.MouseEvent` |
| **React FC** | `const Comp: FC<Props> = ({ name }) => ...` |

---

## 八、与学习笔记的对应关系

- 第 1 章 → 环境；第 2 章 → 一；第 3 章 → 二、四；第 4 章 → 三、五；第 5 章 → 六；第 6 章 → 七及面试要点。
