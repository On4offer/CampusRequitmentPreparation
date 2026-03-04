# 📌 Python 语法与基础常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**类型、控制流、函数、列表/字典/集合**，便于速查与校招笔试。

---

## 一、类型与转换

| 类型 | 说明 | 示例 |
|------|------|------|
| **int / float** | 整数、浮点 | 3, 3.14；除法 / 得 float，// 整除 |
| **str** | 字符串，不可变 | "a", 'b', """c"""；f"{x}" 格式化 |
| **list** | 可变有序序列 | [1,2,3], list(range(5)) |
| **tuple** | 不可变有序 | (1,2), 单元素 (1,) |
| **dict** | 键值对 | {"a":1}, dict(a=1) |
| **set** | 无序不重复 | {1,2}, set([1,2,2]) |
| **bool** | True / False | 非零、非空为 True |
| **None** | 空值 | 无 return 时默认返回 None |

| 转换 | 说明 |
|------|------|
| **int(x)** / **float(x)** / **str(x)** | 数值与字符串互转 |
| **list(it)** / **dict(it)** / **set(it)** | 从可迭代对象构造 |
| **type(x)** / **isinstance(x, type)** | 类型判断 |

---

## 二、字符串常用

| 方法/语法 | 说明 |
|-----------|------|
| **s[i]** / **s[start:stop:step]** | 索引与切片 |
| **s.strip()** / **s.split(sep)** | 去空白、按分隔符切分 |
| **s.replace(old, new)** | 替换 |
| **s.join(iterable)** | 用 s 连接可迭代元素 |
| **s.format(...)** / **f"{x}"** | 格式化 |
| **s.startswith()** / **s.endswith()** / **s.find()** | 前后缀与查找 |
| **s.upper()** / **s.lower()** | 大小写 |

---

## 三、列表与序列

| 操作 | 说明 |
|------|------|
| **lst.append(x)** | 尾部追加 |
| **lst.extend(it)** | 追加多个元素 |
| **lst.insert(i, x)** | 指定位置插入 |
| **lst.remove(x)** | 删除首个等于 x 的元素 |
| **lst.pop([i])** | 删除并返回（默认最后一个） |
| **lst.sort()** / **sorted(lst)** | 排序（sort 原地，sorted 返回新列表） |
| **lst.reverse()** / **reversed(lst)** | 反转 |
| **len(lst)** / **lst.index(x)** / **x in lst** | 长度、索引、成员 |

- **切片**：lst[:]、lst[::2]、lst[::-1] 反转；切片为浅拷贝。

---

## 四、字典

| 操作 | 说明 |
|------|------|
| **d[key]** / **d.get(key [, default])** | 取值，get 无键返回 default |
| **d[key] = value** / **d.update(other)** | 赋值、批量更新 |
| **d.keys()** / **d.values()** / **d.items()** | 键、值、键值对（遍历用） |
| **key in d** | 键是否存在 |
| **d.setdefault(key, default)** | 无键则设 default 并返回 |
| **d.pop(key [, default])** | 删除并返回值 |
| **dict.fromkeys(keys, value)** | 用键列表建字典，同一 value |

---

## 五、集合

| 操作 | 说明 |
|------|------|
| **s.add(x)** / **s.remove(x)** | 添加、删除（无则报错） |
| **s.discard(x)** | 删除，无则忽略 |
| **s & t** / **s \| t** / **s - t** | 交、并、差 |
| **x in s** | 成员 O(1) |
| **set(lst)** | 列表去重 |

---

## 六、控制流与推导式

```python
# 条件
y = x if x > 0 else 0
# for
for i, v in enumerate(lst):
    pass
for k, v in d.items():
    pass
# 列表推导
[x*2 for x in lst]
[x for x in lst if x > 0]
# 字典推导
{k: v*2 for k, v in d.items()}
# 集合推导
{x for x in lst}
```

---

## 七、函数

| 语法 | 说明 |
|------|------|
| **def f(a, b=0, *args, **kwargs):** | 位置、默认、可变位置、可变关键字 |
| **return x** / **return a, b** | 多值返回实为元组 |
| **lambda x: x*2** | 匿名函数 |
| **global x** / **nonlocal x** | 声明全局/闭包变量 |
| **type hints** | def f(x: int) -> str: 可选注解 |

---

## 八、模块与运行

| 用法 | 说明 |
|------|------|
| **import m** / **from m import f** | 导入模块或成员 |
| **if __name__ == "__main__":** | 仅直接运行该文件时执行 |
| **range(n)** / **range(s, e, step)** | 整数序列，常用于 for |

---

## 九、与学习笔记的对应关系

- 第 1 章 → 环境；第 2 章 → 一、二；第 3 章 → 六；第 4 章 → 七；第 5 章 → 三、四、五；第 6 章 → 八。
