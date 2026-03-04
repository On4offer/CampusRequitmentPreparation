# 📌 Netty 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**日常开发中的核心类、Pipeline 与 Handler**，便于速查与上手。

---

## 一、核心类与启动

### 1.1 服务端

| 类/接口 | 说明 | 常用方法 |
|---------|------|----------|
| **NioEventLoopGroup** | Boss/Worker 线程组 | 构造时指定线程数；bossGroup(1)、workerGroup(n) |
| **ServerBootstrap** | 服务端引导 | group(boss, worker)、channel(NioServerSocketChannel.class)、childHandler(ChannelInitializer) |
| **bind(port)** | 绑定端口 | 返回 ChannelFuture，可 sync() 或 addListener |

### 1.2 客户端

| 类/接口 | 说明 | 常用方法 |
|---------|------|----------|
| **Bootstrap** | 客户端引导 | group(eventLoopGroup)、channel(NioSocketChannel.class)、handler(ChannelInitializer) |
| **connect(host, port)** | 连接 | 返回 ChannelFuture |

### 1.3 示例骨架

```java
// 服务端
EventLoopGroup boss = new NioEventLoopGroup(1);
EventLoopGroup worker = new NioEventLoopGroup();
ServerBootstrap b = new ServerBootstrap();
b.group(boss, worker)
 .channel(NioServerSocketChannel.class)
 .childHandler(new ChannelInitializer<SocketChannel>() {
     @Override
     protected void initChannel(SocketChannel ch) {
         ch.pipeline().addLast(new MyHandler());
     }
 });
ChannelFuture f = b.bind(8080).sync();
```

---

## 二、Channel 与 Pipeline

| 类/概念 | 说明 |
|---------|------|
| **Channel** | 连接抽象，可 read、write、close、获取 Pipeline |
| **ChannelPipeline** | Handler 链，addLast/addFirst 添加 Handler |
| **ChannelHandlerContext** | Handler 在 Pipeline 中的上下文，可 writeAndFlush、fireXxx 传递事件、channel() 取 Channel |
| **ChannelFuture** | 异步结果，addListener、sync()、await() |

---

## 三、Handler 常用类型

| 类型 | 说明 | 常用方法/场景 |
|------|------|----------------|
| **ChannelInboundHandlerAdapter** | 入站（读、连接建立/断开） | channelRead、channelActive、channelInactive、exceptionCaught |
| **SimpleChannelInboundHandler&lt;I&gt;** | 入站且自动释放 msg | channelRead0(ctx, msg)，泛型为消息类型 |
| **ChannelOutboundHandlerAdapter** | 出站（写、connect 等） | write、flush、connect |
| **ChannelInitializer&lt;C&gt;** | 初始化时向 Pipeline 加 Handler | initChannel(ch) 里 ch.pipeline().addLast(...) |

### 3.1 常用回调

- **channelActive**：连接建立；**channelInactive**：连接断开；**channelRead**：读到数据，需处理 **ByteBuf** 并决定是否 release；**exceptionCaught**：异常，一般记录日志并 **ctx.close()**；**ctx.writeAndFlush(msg)**：写出并刷新。

---

## 四、ByteBuf 与编解码

### 4.1 ByteBuf

| 方法/概念 | 说明 |
|-----------|------|
| **readableBytes() / writeableBytes()** | 可读/可写字节数 |
| **readXxx() / writeXxx()** | 读写，会移动索引 |
| **getXxx() / setXxx()** | 读写不移动索引 |
| **release()** | 引用计数减一，池化时回收 |
| **retain()** | 引用计数加一 |

### 4.2 常用解码/编码器

| 类 | 说明 |
|----|------|
| **LengthFieldBasedFrameDecoder** | 按长度域拆包，解决粘包半包 |
| **DelimiterBasedFrameDecoder** | 按分隔符拆包 |
| **StringDecoder / StringEncoder** | 字符串与 ByteBuf 互转（需指定 Charset） |
| **HttpServerCodec** | HTTP 编解码 |
| **WebSocketServerProtocolHandler** | WebSocket 协议处理 |

---

## 五、使用场景对照

| 场景 | 推荐做法 |
|------|----------|
| **Echo / 简单 TCP** | Pipeline：解码（如需）→ 业务 InboundHandler，读后 ctx.writeAndFlush |
| **自定义协议** | LengthFieldBasedFrameDecoder + 自定义 Decoder/Encoder + 业务 Handler |
| **HTTP 服务** | HttpServerCodec + HttpObjectAggregator + 业务 Handler（处理 FullHttpRequest） |
| **WebSocket** | WebSocketServerProtocolHandler + 业务 Handler（处理 WebSocketFrame） |
| **SSL** | Pipeline 最前加 SslHandler |
| **心跳/空闲** | IdleStateHandler + 自定义 Handler 处理 IdleStateEvent |
| **耗时业务** | 在 channelRead 中把任务提交到业务线程池，完成后再用 ctx.executor().execute 回 EventLoop 写回 |

---

## 六、常见问题与注意点

| 问题 | 说明 |
|------|------|
| **ByteBuf 泄漏** | 未 release 或重复 release；用 SimpleChannelInboundHandler 或 finally 中 release |
| **阻塞 EventLoop** | 在 Handler 里做阻塞 I/O 或长时间计算；应提交到线程池 |
| **粘包半包** | 未用 FrameDecoder 或协议未定义长度/分隔符；用 LengthFieldBasedFrameDecoder 等 |
| **跨线程写** | 在非 EventLoop 线程写需 **ctx.channel().eventLoop().execute(() -> ctx.writeAndFlush(msg))**，保证写在同一 EventLoop |

---

## 七、与学习笔记的对应关系

- **概述** → 第 1 章；**架构与组件** → 第 2 章；**通信原理** → 第 3 章；**业务实现** → 第 4 章；**性能优化** → 第 5 章；**与 Spring 等结合** → 第 6 章；**安全与容错** → 第 7 章；**高级特性** → 第 8 章；**总结与最佳实践** → 第 9、10 章及附录。

> 更多原理与面试题见《学习笔记》相应章节。
