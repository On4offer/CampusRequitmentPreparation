# 📌 Python 面向对象与进阶特性常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**类、装饰器、生成器、异常、上下文**，便于速查与校招面试。

---

## 一、类与继承

| 语法/方法 | 说明 |
|-----------|------|
| **class C:** / **class C(Parent):** | 定义类、继承 |
| **def __init__(self, ...):** | 构造方法 |
| **self.attr** | 实例属性 |
| **@classmethod** / **@staticmethod** | 类方法（cls）、静态方法（无 self/cls） |
| **super().method()** | 调用父类方法 |
| **cls.mro()** | 方法解析顺序（多重继承） |
| **_name** / **__name** | 约定“内部”、名称改写（mangling） |

```python
class A:
    def __init__(self, x):
        self.x = x
class B(A):
    def __init__(self, x, y):
        super().__init__(x)
        self.y = y
```

---

## 二、魔术方法（常用）

| 方法 | 触发场景 |
|------|----------|
| **__str__** / **__repr__** | str(obj)、print、repr(obj) |
| **__len__** | len(obj) |
| **__getitem__(self, key)** | obj[key] |
| **__iter__** / **__next__** | for、iter()、next() |
| **__enter__** / **__exit__** | with 语句 |
| **__call__(self, ...)** | obj() 调用实例 |
| **__eq__** / **__lt__** 等 | ==、< 等比较 |

---

## 三、装饰器

```python
# 无参装饰器
def deco(func):
    from functools import wraps
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 前
        res = func(*args, **kwargs)
        # 后
        return res
    return wrapper

@deco
def f(): pass

# 带参装饰器
def deco_param(flag):
    def deco(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    return deco
```

| 内置/常用 | 说明 |
|-----------|------|
| **functools.wraps(func)** | 保留原函数 __name__ 等，避免包装后元信息丢失 |
| **functools.lru_cache(maxsize=None)** | 缓存函数结果，适合纯函数 |
| **@property** | 将方法当作属性访问；可配合 setter |
| **@classmethod** / **@staticmethod** | 类方法、静态方法 |

---

## 四、生成器与迭代器

| 概念 | 说明 |
|------|------|
| **可迭代** | 有 __iter__，可用于 for；如 list、dict、range |
| **迭代器** | 有 __iter__ 与 __next__，可 next()；迭代器一定是可迭代的 |
| **生成器** | 含 yield 的函数，返回生成器对象（即迭代器）；惰性求值 |

```python
# 生成器函数
def gen():
    yield 1
    yield 2
g = gen()  # next(g) -> 1, 2, 再 next 抛 StopIteration

# 生成器表达式
(x for x in range(5))  # 惰性，不立即生成列表
```

---

## 五、异常

| 语法 | 说明 |
|------|------|
| **try: ... except E: ...** | 捕获异常 E |
| **except E as e:** | 绑定异常实例 |
| **except (E1, E2):** | 捕获多种 |
| **else:** | try 无异常时执行 |
| **finally:** | 无论如何都执行（清理资源） |
| **raise E** / **raise E from e** | 抛出、链式 |
| **assert cond, msg** | 断言（可被 -O 关掉） |

| 常见异常 | 说明 |
|----------|------|
| **ValueError** | 值错误 |
| **TypeError** | 类型错误 |
| **KeyError** / **IndexError** | 键/索引不存在 |
| **AttributeError** | 属性不存在 |
| **FileNotFoundError** | 文件未找到 |

---

## 六、上下文管理器与 with

```python
# 类实现
class Ctx:
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        return False  # False 不抑制异常

# contextmanager
from contextlib import contextmanager
@contextmanager
def ctx():
    # __enter__
    yield
    # __exit__
```

| 要点 | 说明 |
|------|------|
| **with obj as x:** | 调用 obj.__enter__()，返回值赋给 x；退出时调用 __exit__ |
| **__exit__ 返回 True** | 抑制异常，外部不再收到 |
| **内置** | open()、threading.Lock() 等均支持 with |

---

## 七、面试一句话总结

- **继承与 super**：子类重写方法，super() 调父类；多重继承看 MRO。
- **装饰器**：函数包装函数，@ 语法糖；wraps 保留元信息；带参需两层闭包。
- **生成器**：yield 惰性；与列表推导区别在内存与惰性；迭代器协议 __iter__ + __next__。
- **异常**：具体异常在前；finally 必执行；raise from 保留链。
- **with**：__enter__ / __exit__；保证资源释放；contextmanager 用 yield 简写。

---

## 八、与学习笔记的对应关系

- 第 1 章 → 一；第 2 章 → 一；第 3 章 → 二；第 4 章 → 三；第 5 章 → 四；第 6 章 → 五；第 7 章 → 六、七。
