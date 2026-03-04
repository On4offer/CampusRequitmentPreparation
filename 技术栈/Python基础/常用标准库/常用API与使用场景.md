# 📌 Python 常用标准库常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**文件、re、json、datetime、collections**，便于速查与校招笔试。

---

## 一、文件与路径

| 用法 | 说明 |
|------|------|
| **open(path, mode, encoding='utf-8')** | 常用 mode：r、w、a、rb、wb；文本模式指定 encoding |
| **with open(...) as f:** | 自动关闭文件 |
| **f.read()** / **f.readline()** / **f.readlines()** | 读全部/一行/多行 |
| **f.write(s)** / **f.writelines(lines)** | 写 |
| **for line in f:** | 按行迭代，省内存 |
| **Path('a/b')** | pathlib，跨平台 |
| **p.exists()** / **p.is_file()** / **p.read_text()** / **p.write_text()** | 存在、是否文件、读写文本 |
| **p.iterdir()** / **p.glob('*.py')** | 遍历目录、通配 |
| **os.path.join(a, b)** / **os.listdir(path)** | 拼接路径、列目录 |
| **os.environ** | 环境变量 |

---

## 二、正则（re）

| 函数 | 说明 |
|------|------|
| **re.search(pat, s)** | 找首个匹配，返回 Match 或 None |
| **re.match(pat, s)** | 从字符串**开头**匹配 |
| **re.findall(pat, s)** | 全部匹配，返回列表 |
| **re.sub(pat, repl, s)** | 替换；repl 可为函数 |
| **re.split(pat, s)** | 按模式切分 |
| **re.compile(pat)** | 编译后多次使用 |
| **m.group()** / **m.groups()** | 匹配内容、分组元组 |
| **re.IGNORECASE** / **re.DOTALL** | 忽略大小写、. 匹配换行 |

| 常用元字符 | 说明 |
|------------|------|
| **\d \w \s** | 数字、单词字符、空白 |
| **. * + ?** | 任意、0+、1+、0或1 |
| **[] [^]** | 字符类、否定 |
| **^ $** | 开头、结尾 |
| **() (?: )** | 捕获组、非捕获组 |
| **\b** | 单词边界 |

- **贪婪与非贪婪**：*、+ 贪婪；*?、+? 非贪婪。

---

## 三、json

| 函数 | 说明 |
|------|------|
| **json.dumps(obj)** | 对象→JSON 字符串 |
| **json.loads(s)** | 字符串→对象 |
| **json.dump(obj, fp)** | 写入文件 |
| **json.load(fp)** | 从文件读取 |
| **ensure_ascii=False** | 不转义中文 |
| **indent=2** | 美化输出 |
| **default=fn** / **object_hook=fn** | 自定义序列化/反序列化 |

---

## 四、datetime

| 用法 | 说明 |
|------|------|
| **datetime.datetime.now()** | 当前时间 |
| **datetime.date.today()** | 当前日期 |
| **datetime.timedelta(days=1)** | 时间差，用于加减 |
| **dt.strftime('%Y-%m-%d %H:%M:%S')** | 格式化为字符串 |
| **datetime.strptime(s, '%Y-%m-%d')** | 字符串解析为 datetime |
| **dt.timestamp()** | 转时间戳 |
| **datetime.fromtimestamp(ts)** | 时间戳转 datetime |

---

## 五、collections

| 类型 | 说明 | 典型用法 |
|------|------|----------|
| **defaultdict(factory)** | 无键时用 factory() 生成默认值 | defaultdict(list)、defaultdict(int) |
| **Counter(iterable)** | 计数；.most_common(n) 前 n 多 | 词频、统计 |
| **deque** | 双端队列；.popleft()、.appendleft() | 队列、滑动窗口、BFS |
| **namedtuple('Name', 'a b')** | 命名元组，按名访问 | 轻量结构体 |
| **OrderedDict** | 有序字典（3.7+ dict 已有序，少用） | 需强调顺序时 |

```python
from collections import defaultdict, Counter, deque
d = defaultdict(list)
d['k'].append(1)
c = Counter('hello')  # Counter({'l':2,'h':1,'e':1,'o':1})
q = deque([1,2,3])
q.popleft(); q.append(4)
```

---

## 六、itertools 与 functools（常用）

| 模块 | 函数 | 说明 |
|------|------|------|
| **itertools** | **chain(*iters)** | 串联多个可迭代对象 |
| | **islice(it, n)** | 取前 n 个 |
| | **permutations(lst, r)** | 排列 |
| | **combinations(lst, r)** | 组合 |
| | **groupby(it, key)** | 按 key 分组（需先排序） |
| **functools** | **reduce(fn, it [, init])** | 归约 |
| | **lru_cache(maxsize=None)** | 缓存函数结果 |
| | **partial(fn, *a, **k)** | 固定部分参数 |
| | **wraps(func)** | 装饰器保留元信息 |

---

## 七、random 与 math

| random | 说明 |
|--------|------|
| **random.random()** | [0, 1) 浮点 |
| **random.randint(a, b)** | [a, b] 整数 |
| **random.choice(seq)** | 随机选一个 |
| **random.shuffle(lst)** | 原地打乱 |
| **random.sample(pop, k)** | 无放回抽 k 个 |

| math | 说明 |
|------|------|
| **math.ceil / floor / sqrt / log** | 取整、开方、对数 |
| **math.pow(x, y)** | 幂 |

---

## 八、内置函数（速记）

| 类别 | 函数 |
|------|------|
| **序列** | len、range、enumerate、zip、sorted、reversed、sum、min、max |
| **函数式** | map、filter、any、all |
| **类型** | int、float、str、list、dict、set、tuple、bool |
| **其它** | isinstance、hasattr、getattr、setattr、open、input、print、type |

---

## 九、与学习笔记的对应关系

- 第 1 章 → 概述；第 2 章 → 一；第 3 章 → 二；第 4 章 → 三；第 5 章 → 四；第 6 章 → 五、六；第 7 章 → 七、八。
