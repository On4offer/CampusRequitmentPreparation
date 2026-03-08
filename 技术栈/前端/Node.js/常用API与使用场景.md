# 📘《Node.js 常用 API 与使用场景》

> 系统学习见同目录《学习笔记》，本文档为速查手册。

------

## 核心模块 API

### 文件系统（fs）

#### 读取文件
```javascript
// 异步读取
fs.readFile('file.txt', 'utf8', (err, data) => {
  if (err) throw err;
  console.log(data);
});

// 同步读取
const data = fs.readFileSync('file.txt', 'utf8');
console.log(data);
```

#### 写入文件
```javascript
// 异步写入
fs.writeFile('file.txt', 'content', (err) => {
  if (err) throw err;
  console.log('File written');
});

// 同步写入
fs.writeFileSync('file.txt', 'content');
console.log('File written');
```

#### 目录操作
```javascript
// 创建目录
fs.mkdirSync('newDir');

// 读取目录
fs.readdirSync('dir', (err, files) => {
  if (err) throw err;
  console.log(files);
});
```

### 路径处理（path）

```javascript
// 路径拼接
const fullPath = path.join(__dirname, 'subdir', 'file.txt');

// 绝对路径
const absolutePath = path.resolve('file.txt');

// 获取文件名
const filename = path.basename('path/to/file.txt');

// 获取扩展名
const ext = path.extname('file.txt');
```

### 网络操作（http）

#### 创建服务器
```javascript
const http = require('http');

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello World\n');
});

server.listen(3000, '127.0.0.1', () => {
  console.log('Server running at http://127.0.0.1:3000/');
});
```

#### 发送请求
```javascript
const http = require('http');

const options = {
  hostname: 'api.example.com',
  port: 80,
  path: '/data',
  method: 'GET'
};

const req = http.request(options, (res) => {
  res.on('data', (chunk) => {
    console.log(chunk.toString());
  });
});

req.end();
```

------

## 常用场景

### 命令行工具

```javascript
// 读取命令行参数
const args = process.argv.slice(2);
console.log('Arguments:', args);

// 环境变量
const port = process.env.PORT || 3000;

// 进程退出
process.exit(0);
```

### 简单 HTTP 服务器

```javascript
const http = require('http');
const fs = require('fs');
const path = require('path');

const server = http.createServer((req, res) => {
  let filePath = path.join(__dirname, 'public', req.url === '/' ? 'index.html' : req.url);
  const extname = path.extname(filePath);
  let contentType = 'text/html';

  switch (extname) {
    case '.js': contentType = 'text/javascript'; break;
    case '.css': contentType = 'text/css'; break;
    case '.json': contentType = 'application/json'; break;
    case '.png': contentType = 'image/png'; break;
    case '.jpg': contentType = 'image/jpg'; break;
  }

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        fs.readFile(path.join(__dirname, 'public', '404.html'), (err, content) => {
          res.writeHead(404, { 'Content-Type': 'text/html' });
          res.end(content, 'utf8');
        });
      } else {
        res.writeHead(500);
        res.end(`Server Error: ${err.code}`);
      }
    } else {
      res.writeHead(200, { 'Content-Type': contentType });
      res.end(content, 'utf8');
    }
  });
});

const PORT = process.env.PORT || 3000;
server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
```

### 文件监控

```javascript
const fs = require('fs');

fs.watch('file.txt', (eventType, filename) => {
  console.log(`File ${filename} changed: ${eventType}`);
});
```

### 数据流处理

```javascript
const fs = require('fs');

// 读取流
const readStream = fs.createReadStream('input.txt');
// 写入流
const writeStream = fs.createWriteStream('output.txt');

// 管道传输
readStream.pipe(writeStream);

readStream.on('end', () => {
  console.log('File copied');
});
```