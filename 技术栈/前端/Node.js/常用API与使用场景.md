# 📘《Node.js 常用 API 与使用场景速查》

> 配合《学习笔记》使用，侧重**日常开发中的核心模块、API 与常用场景**，便于速查与上手。

---

## 一、核心模块 API

### 1.1 文件系统（fs）

| 方法 | 说明 | 常用参数 |
|------|------|----------|
| **fs.readFile()** | 异步读取文件 | path, encoding, callback |
| **fs.readFileSync()** | 同步读取文件 | path, encoding |
| **fs.writeFile()** | 异步写入文件 | path, data, options, callback |
| **fs.writeFileSync()** | 同步写入文件 | path, data, options |
| **fs.appendFile()** | 追加写入 | path, data, options, callback |
| **fs.mkdir()** | 创建目录 | path, options, callback |
| **fs.readdir()** | 读取目录 | path, options, callback |
| **fs.unlink()** | 删除文件 | path, callback |
| **fs.rmdir()** | 删除目录 | path, options, callback |
| **fs.rename()** | 重命名/移动 | oldPath, newPath, callback |
| **fs.copyFile()** | 复制文件 | src, dest, callback |
| **fs.stat()** | 获取文件状态 | path, callback |

#### Promise API（Node.js 10+）

```javascript
const fs = require('fs').promises;

// 异步读取
const data = await fs.readFile('file.txt', 'utf8');

// 异步写入
await fs.writeFile('file.txt', 'content');

// 异步追加
await fs.appendFile('file.txt', '\nnew line');

// 异步删除
await fs.unlink('file.txt');

// 异步创建目录
await fs.mkdir('dir', { recursive: true });
```

#### 流操作

```javascript
const fs = require('fs');

// 创建读取流
const readStream = fs.createReadStream('input.txt', {
  encoding: 'utf8',
  highWaterMark: 64 * 1024
});

// 创建写入流
const writeStream = fs.createWriteStream('output.txt');

// 管道传输
readStream.pipe(writeStream);

// 使用 pipeline（推荐，自动处理错误）
const { pipeline } = require('stream/promises');
await pipeline(
  fs.createReadStream('input.txt'),
  fs.createWriteStream('output.txt')
);
```

### 1.2 路径处理（path）

| 方法 | 说明 | 示例 |
|------|------|------|
| **path.join()** | 拼接路径 | path.join('/a', 'b', 'c') → '/a/b/c' |
| **path.resolve()** | 解析为绝对路径 | path.resolve('a') → '/current/a' |
| **path.dirname()** | 获取目录名 | path.dirname('/a/b/c.txt') → '/a/b' |
| **path.basename()** | 获取文件名 | path.basename('/a/b/c.txt') → 'c.txt' |
| **path.extname()** | 获取扩展名 | path.extname('c.txt') → '.txt' |
| **path.parse()** | 解析路径对象 | { root, dir, base, ext, name } |
| **path.format()** | 格式化路径 | path.format({ dir, base }) |
| **path.normalize()** | 规范化路径 | path.normalize('/a//b/../c') → '/a/c' |
| **path.isAbsolute()** | 判断绝对路径 | path.isAbsolute('/a') → true |

```javascript
const path = require('path');

// 路径拼接
const fullPath = path.join(__dirname, 'subdir', 'file.txt');

// 绝对路径解析
const absolutePath = path.resolve('./config.json');

// 获取文件名（不含扩展名）
const name = path.basename('file.txt', path.extname('file.txt'));

// 解析路径
const parsed = path.parse('/home/user/documents/file.txt');
// { root: '/', dir: '/home/user/documents', base: 'file.txt', ext: '.txt', name: 'file' }
```

### 1.3 网络操作（http/https）

#### 创建 HTTP 服务器

```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  // req: http.IncomingMessage
  // res: http.ServerResponse

  res.statusCode = 200;
  res.setHeader('Content-Type', 'application/json');
  res.end(JSON.stringify({ message: 'Hello' }));
});

server.listen(3000, () => {
  console.log('Server running on port 3000');
});
```

#### http.IncomingMessage 常用属性与方法

| 属性/方法 | 说明 |
|-----------|------|
| **req.method** | HTTP 方法（GET、POST 等） |
| **req.url** | 请求 URL |
| **req.headers** | 请求头对象 |
| **req.httpVersion** | HTTP 版本 |
| **req.on('data')** | 接收请求体数据 |
| **req.on('end')** | 请求体接收完成 |

#### http.ServerResponse 常用方法

| 方法 | 说明 |
|------|------|
| **res.statusCode** | 设置状态码 |
| **res.statusMessage** | 设置状态消息 |
| **res.setHeader()** | 设置响应头 |
| **res.writeHead()** | 写入状态码和响应头 |
| **res.write()** | 写入响应体 |
| **res.end()** | 结束响应 |

#### 发送 HTTP 请求

```javascript
const http = require('http');

// GET 请求
http.get('http://example.com/data', (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});

// POST 请求
const options = {
  hostname: 'api.example.com',
  port: 80,
  path: '/data',
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  }
};

const req = http.request(options, (res) => {
  let data = '';
  res.on('data', chunk => data += chunk);
  res.on('end', () => console.log(data));
});

req.write(JSON.stringify({ name: 'John' }));
req.end();
```

### 1.4 进程与系统（process/os）

#### process 常用属性

| 属性 | 说明 |
|------|------|
| **process.pid** | 进程 ID |
| **process.ppid** | 父进程 ID |
| **process.version** | Node.js 版本 |
| **process.platform** | 运行平台（win32、linux 等） |
| **process.arch** | 架构（x64、arm64 等） |
| **process.cwd()** | 当前工作目录 |
| **process.env** | 环境变量对象 |
| **process.argv** | 命令行参数数组 |
| **process.uptime()** | 进程运行时间（秒） |
| **process.memoryUsage()** | 内存使用情况 |

#### process 常用方法

| 方法 | 说明 |
|------|------|
| **process.exit(code)** | 退出进程 |
| **process.kill(pid)** | 发送信号 |
| **process.on(event, callback)** | 监听进程事件 |

#### 进程事件

```javascript
// 监听未捕获异常
process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err);
});

// 监听未处理的 Promise 拒绝
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
});

// 监听退出信号
process.on('SIGINT', () => {
  console.log('Received SIGINT, shutting down...');
  process.exit(0);
});
```

#### os 模块常用方法

| 方法 | 说明 |
|------|------|
| **os.platform()** | 操作系统平台 |
| **os.arch()** | 系统架构 |
| **os.cpus()** | CPU 信息数组 |
| **os.totalmem()** | 总内存（字节） |
| **os.freemem()** | 空闲内存（字节） |
| **os.homedir()** | 用户主目录 |
| **os.tmpdir()** | 临时目录 |
| **os.hostname()** | 主机名 |
| **os.networkInterfaces()** | 网络接口信息 |

```javascript
const os = require('os');

console.log('CPU cores:', os.cpus().length);
console.log('Total memory:', (os.totalmem() / 1024 / 1024 / 1024).toFixed(2), 'GB');
console.log('Free memory:', (os.freemem() / 1024 / 1024 / 1024).toFixed(2), 'GB');
console.log('Platform:', os.platform());
```

### 1.5 事件处理（events）

| 类/方法 | 说明 |
|---------|------|
| **EventEmitter** | 事件发射器基类 |
| **emitter.on(event, listener)** | 注册事件监听器 |
| **emitter.once(event, listener)** | 注册单次监听器 |
| **emitter.emit(event, ...args)** | 发射事件 |
| **emitter.off(event, listener)** | 移除监听器 |
| **emitter.removeAllListeners(event)** | 移除所有监听器 |
| **emitter.listenerCount(event)** | 获取监听器数量 |

```javascript
const EventEmitter = require('events');

class MyEmitter extends EventEmitter {}

const emitter = new MyEmitter();

// 注册事件
emitter.on('event', (data) => {
  console.log('Event received:', data);
});

// 单次事件
emitter.once('onceEvent', () => {
  console.log('This will only run once');
});

// 发射事件
emitter.emit('event', { message: 'Hello' });

// 移除监听器
emitter.off('event', listener);
```

### 1.6 工具模块（util）

| 方法 | 说明 |
|------|------|
| **util.format()** | 格式化字符串 |
| **util.inspect()** | 对象检查（调试用） |
| **util.promisify()** | 回调函数转 Promise |
| **util.callbackify()** | Promise 转回调函数 |
| **util.isDeepStrictEqual()** | 深度严格相等比较 |

```javascript
const util = require('util');

// 格式化字符串
util.format('%s: %d', 'Hello', 123); // 'Hello: 123'

// 对象检查
util.inspect({ a: 1, b: { c: 2 } });

// 回调转 Promise
const fs = require('fs');
const readFile = util.promisify(fs.readFile);
const data = await readFile('file.txt', 'utf8');
```

---

## 二、Express 框架 API

### 2.1 应用创建与配置

```javascript
const express = require('express');
const app = express();

// 常用配置
app.set('port', 3000);
app.set('view engine', 'ejs');
```

### 2.2 中间件方法

| 方法 | 说明 |
|------|------|
| **app.use([path], middleware)** | 使用中间件 |
| **app.get(path, handler)** | GET 路由 |
| **app.post(path, handler)** | POST 路由 |
| **app.put(path, handler)** | PUT 路由 |
| **app.delete(path, handler)** | DELETE 路由 |
| **app.patch(path, handler)** | PATCH 路由 |
| **app.all(path, handler)** | 处理所有方法 |
| **app.route(path)** | 链式路由 |

#### 内置中间件

```javascript
// 解析 JSON
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// 静态文件
app.use(express.static('public'));
app.use('/static', express.static('public'));

// 视图渲染
app.set('views', './views');
app.set('view engine', 'ejs');
```

### 2.3 请求对象（req）

| 属性/方法 | 说明 |
|-----------|------|
| **req.method** | 请求方法 |
| **req.path** | 请求路径 |
| **req.url** | 完整 URL |
| **req.params** | 路由参数 |
| **req.query** | 查询参数 |
| **req.body** | 请求体（需中间件解析） |
| **req.headers** | 请求头 |
| **req.cookies** | Cookie（需 cookie-parser） |
| **req.get(header)** | 获取请求头 |
| **req.accepts(types)** | 检查可接受的类型 |

### 2.4 响应对象（res）

| 方法 | 说明 |
|------|------|
| **res.send(body)** | 发送响应 |
| **res.json(obj)** | 发送 JSON |
| **res.status(code)** | 设置状态码 |
| **res.set(header, value)** | 设置响应头 |
| **res.redirect([status], url)** | 重定向 |
| **res.render(view, data)** | 渲染视图 |
| **res.download(path)** | 下载文件 |
| **res.end()** | 结束响应 |

### 2.5 路由参数

```javascript
// 路由参数
app.get('/users/:id', (req, res) => {
  const { id } = req.params;
  res.json({ id });
});

// 查询参数
app.get('/search', (req, res) => {
  const { q, page = 1 } = req.query;
  res.json({ q, page });
});

// 正则表达式参数
app.get('/users/:id([0-9]+)', (req, res) => {
  res.json({ id: req.params.id });
});
```

### 2.6 错误处理

```javascript
// 错误处理中间件（必须放在最后）
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Internal Server Error' });
});

// 异步错误处理
app.get('/async', async (req, res, next) => {
  try {
    const result = await someAsyncOperation();
    res.json(result);
  } catch (err) {
    next(err); // 传递给错误处理中间件
  }
});
```

---

## 三、常用工具模块

### 3.1 加密模块（crypto）

```javascript
const crypto = require('crypto');

// MD5 哈希
const md5 = crypto.createHash('md5').update('data').digest('hex');

// SHA-256 哈希
const sha256 = crypto.createHash('sha256').update('data').digest('hex');

// AES 加密
const key = crypto.scryptSync('password', 'salt', 32);
const iv = crypto.randomBytes(16);
const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
let encrypted = cipher.update('data', 'utf8', 'hex');
encrypted += cipher.final('hex');

// AES 解密
const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
let decrypted = decipher.update(encrypted, 'hex', 'utf8');
decrypted += decipher.final('utf8');
```

### 3.2 压缩模块（zlib）

```javascript
const zlib = require('zlib');

// Gzip 压缩
const gzip = zlib.createGzip();
const readStream = fs.createReadStream('file.txt');
const writeStream = fs.createWriteStream('file.txt.gz');
readStream.pipe(gzip).pipe(writeStream);

// 解压
const gunzip = zlib.createGunzip();
fs.createReadStream('file.txt.gz').pipe(gunzip).pipe(fs.createWriteStream('file.txt'));

// 同步压缩
const compressed = zlib.gzipSync Buffer.from('data');
```

### 3.3 断言模块（assert）

```javascript
const assert = require('assert');

// 严格相等
assert.strictEqual(actual, expected);

// 深度相等
assert.deepStrictEqual(actual, expected);

// 抛出错误
assert.throws(() => {
  throw new Error('Error');
});

// 条件断言
assert(condition, 'Message');
```

### 3.4 查询字符串（querystring）

```javascript
const querystring = require('querystring');

// 解析
const parsed = querystring.parse('name=John&age=30');
// { name: 'John', age: '30' }

// 序列化
const str = querystring.stringify({ name: 'John', age: 30 });
// 'name=John&age=30'

// URLSearchParams
const params = new URLSearchParams('name=John&age=30');
params.get('name'); // 'John'
params.append('city', 'Beijing');
```

### 3.5 URL 模块

```javascript
const url = require('url');

// 解析 URL
const parsed = new URL('http://user:pass@example.com:8080/path?query=value#hash');
// protocol: 'http:', host: 'example.com:8080', pathname: '/path', etc.

// 解析查询字符串
const { URL } = require('url');
const u = new URL('http://example.com?a=1&b=2');
u.searchParams.get('a'); // '1'
u.searchParams.set('c', '3');
u.toString(); // 'http://example.com?a=1&b=2&c=3'
```

---

## 四、常用场景对照

| 场景 | 推荐做法 |
|------|----------|
| **读取配置文件** | 使用 require() 或 fs.readFile + JSON.parse |
| **创建 HTTP API** | Express + 中间件 + 路由模块化 |
| **处理文件上传** | Multer 中间件 |
| **实时通信** | Socket.io 或 ws（WebSocket） |
| **数据库操作** | Mongoose（MongoDB）或 mysql2/sequelize |
| **缓存数据** | Redis（ioredis） |
| **日志记录** | Winston 或 Bunyan |
| **环境配置** | dotenv |
| **用户认证** | JWT + bcrypt |
| **API 验证** | Joi 或 express-validator |
| **跨域请求** | cors 中间件 |
| **HTTPS** | 使用 https 模块或 Nginx 反向代理 |
| **PM2 进程管理** | pm2 start ecosystem.config.js |

### 4.1 文件操作场景

```javascript
// 读取 JSON 配置
const config = require('./config.json');

// 写入 JSON 文件
await fs.writeFile('data.json', JSON.stringify(data, null, 2));

// 复制文件
await fs.copyFile('src.txt', 'dest.txt');

// 批量处理文件
const files = await fs.readdir('./dir');
for (const file of files) {
  // 处理每个文件
}
```

### 4.2 HTTP API 场景

```javascript
// RESTful API 骨架
const express = require('express');
const app = express();
app.use(express.json());

// GET 列表
app.get('/api/users', async (req, res) => {
  const { page = 1, limit = 10 } = req.query;
  const users = await User.find().skip((page-1)*limit).limit(+limit);
  res.json(users);
});

// GET 单条
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) return res.status(404).json({ error: 'Not found' });
  res.json(user);
});

// POST 创建
app.post('/api/users', async (req, res) => {
  const user = new User(req.body);
  await user.save();
  res.status(201).json(user);
});

// PUT 更新
app.put('/api/users/:id', async (req, res) => {
  const user = await User.findByIdAndUpdate(req.params.id, req.body, { new: true });
  res.json(user);
});

// DELETE 删除
app.delete('/api/users/:id', async (req, res) => {
  await User.findByIdAndDelete(req.params.id);
  res.status(204).send();
});
```

### 4.3 实时通信场景

```javascript
// Socket.io 服务端
const io = require('socket.io')(server);

io.on('connection', (socket) => {
  console.log('Client connected:', socket.id);

  // 接收消息
  socket.on('chat message', (msg) => {
    // 广播给所有人
    io.emit('chat message', msg);
    // 或者只发给发送者
    socket.emit('chat message', msg);
  });

  // 加入房间
  socket.join('room1');
  io.to('room1').emit('message', 'Hello room1');

  // 离开房间
  socket.leave('room1');

  // 断开连接
  socket.on('disconnect', () => {
    console.log('Client disconnected');
  });
});

// 客户端
const socket = io();
socket.emit('chat message', 'Hello');
socket.on('chat message', (msg) => {
  console.log(msg);
});
```

### 4.4 异步编程场景

```javascript
// 串行执行
async function serial() {
  const a = await fetchA();
  const b = await fetchB(a);
  const c = await fetchC(b);
  return c;
}

// 并行执行
async function parallel() {
  const [a, b, c] = await Promise.all([
    fetchA(),
    fetchB(),
    fetchC()
  ]);
  return { a, b, c };
}

// 竞态处理（race）
async function withTimeout(promise, ms) {
  return Promise.race([
    promise,
    new Promise((_, reject) => 
      setTimeout(() => reject(new Error('Timeout')), ms)
    )
  ]);
}
```

---

## 五、常见问题与注意点

| 问题 | 说明 |
|------|------|
| **req.body 为 undefined** | 确保使用 express.json() 或 express.urlencoded() 中间件 |
| **静态文件 404** | 检查 express.static() 路径配置 |
| **路由顺序** | 具体路由在前，通配路由在后 |
| **异步错误未捕获** | 使用 try/catch 或 Promise.catch() |
| **文件路径跨平台** | 使用 path.join() 而非字符串拼接 |
| **回调地狱** | 使用 async/await 或 Promise |
| **内存泄漏** | 及时移除事件监听器，关闭流和连接 |
| **进程崩溃** | 使用 PM2 自动重启，捕获 uncaughtException |
| **CORS 错误** | 使用 cors 中间件配置允许的来源 |
| **环境变量泄露** | 不提交 .env 到版本控制，使用 dotenv |

---

## 六、与学习笔记的对应关系

- **核心概念** → 第 1 章；**模块系统与 API** → 第 2 章；**Express 框架** → 第 3 章；**异步编程与高级特性** → 第 4 章；**实战技巧** → 第 5 章；**面试要点** → 第 6 章。

> 更多原理与深入内容见《学习笔记》相应章节。
