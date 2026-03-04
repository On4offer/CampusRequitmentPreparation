Web 浏览器和 Web 服务器之间通信的基础协议主要包括以下几种：

1. **HTTP（HyperText Transfer Protocol，超文本传输协议）**
   - 最常用的基础协议，是浏览器与服务器之间进行通信的核心协议。当前主流版本有 HTTP/1.1、HTTP/2 和逐渐推广中的 HTTP/3。
   - 它是一个无状态、基于请求-响应模型的协议。
2. **HTTPS（HTTP Secure）**
   - 是在 HTTP 的基础上加入了 SSL/TLS 加密层的安全通信协议。
   - 保障了数据在传输过程中的机密性、完整性和身份验证。
3. **TCP（Transmission Control Protocol）**
   - 是 HTTP 和 HTTPS 通信所依赖的传输层协议，提供可靠的数据传输。
   - 保证数据按顺序、无差错地到达目标主机。
4. **TLS（Transport Layer Security）/SSL（Secure Sockets Layer）**
   - 是 HTTPS 中的加密协议，用于在 Web 通信中提供安全连接。TLS 是 SSL 的后续版本，目前广泛使用的是 TLS 1.2 和 TLS 1.3。
5. **WebSocket**
   - 是一种在单个 TCP 连接上进行全双工通信的协议，适用于实时通信场景（如在线聊天、实时推送）。
   - 与 HTTP 不同，WebSocket 建立后，客户端和服务器可以随时互发消息。

需要注意的是：

- 通常浏览网页是通过 HTTP 或 HTTPS。
- WebSocket 则多用于交互性较强的 Web 应用中。
- 所有这些协议底层都依赖 TCP/IP 协议栈。

如果你需要更技术性或详细的说明（比如报文结构或端口号等），我也可以继续补充。