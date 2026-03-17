# 📘《前端与AI交互常用 API 与使用场景》

> 系统学习见同目录《学习笔记》；本文件为日常开发速查手册。

------

## 1. HTTP客户端

### 1.1 Axios

#### 安装
```bash
npm install axios
```

#### 基本使用
```javascript
import axios from 'axios';

// 基本请求
axios.get('/api/data')
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.error(error);
  });

// POST请求
axios.post('/api/chat', {
  message: 'Hello'
})
  .then(response => {
    console.log(response.data);
  })
  .catch(error => {
    console.error(error);
  });
```

#### 流式请求
```javascript
// 流式请求
axios.post('/api/stream', {
  message: 'Hello'
}, {
  responseType: 'stream'
})
  .then(response => {
    const reader = response.data.getReader();
    const decoder = new TextDecoder();
    
    reader.read().then(function processText({ done, value }) {
      if (done) {
        console.log('Stream complete');
        return;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      console.log(chunk);
      
      return reader.read().then(processText);
    });
  })
  .catch(error => {
    console.error(error);
  });
```

#### 拦截器
```javascript
// 请求拦截器
axios.interceptors.request.use(
  config => {
    // 在发送请求之前做些什么
    config.headers.Authorization = `Bearer ${localStorage.getItem('token')}`;
    return config;
  },
  error => {
    // 处理请求错误
    return Promise.reject(error);
  }
);

// 响应拦截器
axios.interceptors.response.use(
  response => {
    // 对响应数据做点什么
    return response;
  },
  error => {
    // 处理响应错误
    if (error.response.status === 401) {
      // 处理未授权
    }
    return Promise.reject(error);
  }
);
```

### 1.2 Fetch API

#### 基本使用
```javascript
// 基本请求
fetch('/api/data')
  .then(response => response.json())
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error(error);
  });

// POST请求
fetch('/api/chat', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message: 'Hello' })
})
  .then(response => response.json())
  .then(data => {
    console.log(data);
  })
  .catch(error => {
    console.error(error);
  });
```

#### 流式请求
```javascript
// 流式请求
fetch('/api/stream', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ message: 'Hello' })
})
  .then(response => {
    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    
    reader.read().then(function processText({ done, value }) {
      if (done) {
        console.log('Stream complete');
        return;
      }
      
      const chunk = decoder.decode(value, { stream: true });
      console.log(chunk);
      
      return reader.read().then(processText);
    });
  })
  .catch(error => {
    console.error(error);
  });
```

### 1.3 使用场景

- **API调用**：与后端AI服务通信，获取模型推理结果。
- **流式输出**：实现大模型生成内容的实时显示。
- **文件上传**：上传图像、音频等文件到AI服务。
- **认证授权**：处理API密钥和认证令牌。

------

## 2. WebSocket

### 2.1 基本使用

```javascript
// 创建WebSocket连接
const socket = new WebSocket('ws://localhost:8000/ws');

// 连接建立
socket.addEventListener('open', (event) => {
  console.log('WebSocket connected');
  // 发送消息
  socket.send(JSON.stringify({ message: 'Hello' }));
});

// 接收消息
socket.addEventListener('message', (event) => {
  console.log('Message from server:', event.data);
});

// 连接关闭
socket.addEventListener('close', (event) => {
  console.log('WebSocket disconnected');
});

// 连接错误
socket.addEventListener('error', (event) => {
  console.error('WebSocket error:', event);
});
```

### 2.2 心跳机制

```javascript
// 心跳机制
let heartbeatInterval;

function startHeartbeat() {
  heartbeatInterval = setInterval(() => {
    if (socket.readyState === WebSocket.OPEN) {
      socket.send(JSON.stringify({ type: 'ping' }));
    }
  }, 30000); // 30秒发送一次心跳
}

function stopHeartbeat() {
  clearInterval(heartbeatInterval);
}

// 连接建立时启动心跳
socket.addEventListener('open', (event) => {
  console.log('WebSocket connected');
  startHeartbeat();
});

// 连接关闭时停止心跳
socket.addEventListener('close', (event) => {
  console.log('WebSocket disconnected');
  stopHeartbeat();
});
```

### 2.3 重连机制

```javascript
// 重连机制
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;
const reconnectDelay = 1000; // 1秒

function connect() {
  const socket = new WebSocket('ws://localhost:8000/ws');
  
  socket.addEventListener('open', (event) => {
    console.log('WebSocket connected');
    reconnectAttempts = 0;
  });
  
  socket.addEventListener('close', (event) => {
    console.log('WebSocket disconnected');
    if (reconnectAttempts < maxReconnectAttempts) {
      reconnectAttempts++;
      console.log(`Attempting to reconnect... (${reconnectAttempts}/${maxReconnectAttempts})`);
      setTimeout(connect, reconnectDelay * reconnectAttempts);
    } else {
      console.error('Max reconnect attempts reached');
    }
  });
  
  return socket;
}

// 启动连接
const socket = connect();
```

### 2.4 使用场景

- **实时聊天**：实现与AI的实时对话，支持流式输出。
- **多用户协作**：支持多个用户同时与AI交互。
- **游戏和交互应用**：需要实时双向通信的场景。
- **监控和通知**：实时接收系统状态和通知。

------

## 3. Server-Sent Events (SSE)

### 3.1 基本使用

```javascript
// 创建EventSource连接
const eventSource = new EventSource('/api/stream');

// 接收消息
eventSource.addEventListener('message', (event) => {
  console.log('Message from server:', event.data);
});

// 接收错误
eventSource.addEventListener('error', (event) => {
  if (event.readyState === EventSource.CLOSED) {
    console.log('SSE connection closed');
  } else {
    console.error('SSE error:', event);
  }
});

// 接收自定义事件
eventSource.addEventListener('update', (event) => {
  console.log('Update event:', event.data);
});

// 关闭连接
// eventSource.close();
```

### 3.2 后端实现（FastAPI）

```python
from fastapi import FastAPI, Response
import asyncio

app = FastAPI()

@app.get("/api/stream")
async def stream():
    async def event_generator():
        for i in range(5):
            await asyncio.sleep(1)
            yield f"data: {i}\n\n"
    
    return Response(
        event_generator(),
        media_type="text/event-stream"
    )
```

### 3.3 使用场景

- **流式输出**：实现大模型生成内容的实时显示。
- **实时更新**：接收服务器的实时更新，如股票价格、新闻等。
- **监控系统**：实时接收系统状态和告警信息。

------

## 4. 状态管理

### 4.1 React useState

```javascript
import { useState } from 'react';

function ChatComponent() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;

    // 添加用户消息
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // 调用API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: input })
      });
      
      const data = await response.json();
      // 添加AI消息
      const aiMessage = { role: 'assistant', content: data.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = { role: 'assistant', content: 'Sorry, an error occurred.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
          </div>
        ))}
        {isLoading && <div className="loading">Generating...</div>}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
        />
        <button onClick={handleSend} disabled={isLoading}>Send</button>
      </div>
    </div>
  );
}
```

### 4.2 Redux

#### 安装
```bash
npm install @reduxjs/toolkit react-redux
```

#### 基本使用
```javascript
// store.js
import { configureStore, createSlice } from '@reduxjs/toolkit';

const chatSlice = createSlice({
  name: 'chat',
  initialState: {
    messages: [],
    input: '',
    isLoading: false,
    error: null
  },
  reducers: {
    setInput: (state, action) => {
      state.input = action.payload;
    },
    addMessage: (state, action) => {
      state.messages.push(action.payload);
    },
    setLoading: (state, action) => {
      state.isLoading = action.payload;
    },
    setError: (state, action) => {
      state.error = action.payload;
    },
    clearError: (state) => {
      state.error = null;
    }
  }
});

export const { setInput, addMessage, setLoading, setError, clearError } = chatSlice.actions;

export const store = configureStore({
  reducer: {
    chat: chatSlice.reducer
  }
});

// ChatComponent.jsx
import { useSelector, useDispatch } from 'react-redux';
import { setInput, addMessage, setLoading, setError } from './store';

function ChatComponent() {
  const { messages, input, isLoading, error } = useSelector(state => state.chat);
  const dispatch = useDispatch();

  const handleSend = async () => {
    if (!input.trim()) return;

    // 添加用户消息
    dispatch(addMessage({ role: 'user', content: input }));
    dispatch(setInput(''));
    dispatch(setLoading(true));
    dispatch(setError(null));

    try {
      // 调用API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: input })
      });
      
      const data = await response.json();
      // 添加AI消息
      dispatch(addMessage({ role: 'assistant', content: data.response }));
    } catch (error) {
      console.error('Error:', error);
      dispatch(setError('Sorry, an error occurred.'));
      dispatch(addMessage({ role: 'assistant', content: 'Sorry, an error occurred.' }));
    } finally {
      dispatch(setLoading(false));
    }
  };

  return (
    <div>
      {error && <div className="error">{error}</div>}
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.role}`}>
            {message.content}
          </div>
        ))}
        {isLoading && <div className="loading">Generating...</div>}
      </div>
      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => dispatch(setInput(e.target.value))}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Type your message..."
        />
        <button onClick={handleSend} disabled={isLoading}>Send</button>
      </div>
    </div>
  );
}
```

### 4.3 使用场景

- **聊天应用**：管理对话历史、输入状态、加载状态等。
- **复杂应用**：管理多个组件共享的状态。
- **状态持久化**：将状态保存到本地存储，实现页面刷新后状态恢复。

------

## 5. 流式输出实现

### 5.1 文本流式输出

```javascript
// 前端实现
async function streamText() {
  const response = await fetch('/api/stream', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message: 'Write a short story about AI' })
  });

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let result = '';
  const outputElement = document.getElementById('output');

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    const chunk = decoder.decode(value, { stream: true });
    result += chunk;
    outputElement.textContent = result;
  }
}

// 后端实现（FastAPI）
@app.post("/api/stream")
async def stream_text(request: Request):
    data = await request.json()
    message = data.get('message', '')
    
    async def generate():
        # 模拟大模型生成过程
        story = "Once upon a time, there was an AI named Alex... "
        for i in range(len(story)):
            await asyncio.sleep(0.1)
            yield story[:i+1]
    
    return StreamingResponse(generate(), media_type="text/plain")
```

### 5.2 打字动画效果

```javascript
function typeWriter(text, element, speed = 50) {
  let i = 0;
  element.textContent = '';
  
  function type() {
    if (i < text.length) {
      element.textContent += text.charAt(i);
      i++;
      setTimeout(type, speed);
    }
  }
  
  type();
}

// 使用示例
const outputElement = document.getElementById('output');
typeWriter('Hello, this is a typing animation!', outputElement);
```

### 5.3 使用场景

- **聊天机器人**：实现AI回复的实时显示，模拟人类打字效果。
- **内容生成**：实时显示生成的文章、代码等内容。
- **加载状态**：提供更生动的加载反馈。

------

## 6. 多模态交互

### 6.1 图像上传

```javascript
// 前端实现
function ImageUpload() {
  const [image, setImage] = useState(null);
  const [result, setResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setImage(URL.createObjectURL(file));
    }
  };

  const handleSubmit = async () => {
    if (!image) return;

    setIsLoading(true);
    
    const formData = new FormData();
    formData.append('image', document.getElementById('image-input').files[0]);

    try {
      const response = await fetch('/api/image-analysis', {
        method: 'POST',
        body: formData
      });
      
      const data = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        id="image-input"
        accept="image/*"
        onChange={handleImageChange}
      />
      {image && (
        <div>
          <img src={image} alt="Uploaded" style={{ maxWidth: '300px' }} />
          <button onClick={handleSubmit} disabled={isLoading}>
            {isLoading ? 'Analyzing...' : 'Analyze Image'}
          </button>
        </div>
      )}
      {result && (
        <div className="result">
          <h3>Analysis Result:</h3>
          <p>{result.description}</p>
        </div>
      )}
    </div>
  );
}
```

### 6.2 语音识别

```javascript
// 前端实现
function SpeechRecognitionComponent() {
  const [transcript, setTranscript] = useState('');
  const [isListening, setIsListening] = useState(false);

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert('Speech recognition is not supported in this browser.');
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setTranscript(transcript);
    };

    recognition.onend = () => {
      setIsListening(false);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
    };

    recognition.start();
  };

  return (
    <div>
      <button onClick={startListening} disabled={isListening}>
        {isListening ? 'Listening...' : 'Start Listening'}
      </button>
      {transcript && (
        <div className="transcript">
          <h3>Transcript:</h3>
          <p>{transcript}</p>
        </div>
      )}
    </div>
  );
}
```

### 6.3 语音合成

```javascript
// 前端实现
function TextToSpeech() {
  const [text, setText] = useState('Hello, this is a text to speech example.');
  const [isSpeaking, setIsSpeaking] = useState(false);

  const speak = () => {
    if ('speechSynthesis' in window) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 1;
      utterance.pitch = 1;
      utterance.volume = 1;

      utterance.onstart = () => {
        setIsSpeaking(true);
      };

      utterance.onend = () => {
        setIsSpeaking(false);
      };

      speechSynthesis.speak(utterance);
    } else {
      alert('Text-to-speech is not supported in this browser.');
    }
  };

  return (
    <div>
      <textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        cols={50}
      />
      <button onClick={speak} disabled={isSpeaking}>
        {isSpeaking ? 'Speaking...' : 'Speak'}
      </button>
    </div>
  );
}
```

### 6.4 使用场景

- **图像分析**：上传图像进行识别、分类等。
- **语音助手**：通过语音与AI交互。
- **多模态内容生成**：生成包含文本、图像、语音的内容。
- **辅助功能**：为视力或听力障碍用户提供辅助功能。

------

## 7. 性能优化

### 7.1 虚拟列表

#### 安装
```bash
npm install react-window
```

#### 基本使用
```javascript
import { FixedSizeList as List } from 'react-window';

function VirtualList({ items }) {
  const Row = ({ index, style }) => (
    <div style={style} className="message">
      {items[index].content}
    </div>
  );

  return (
    <List
      height={400}
      itemCount={items.length}
      itemSize={50}
      width="100%"
    >
      {Row}
    </List>
  );
}
```

### 7.2 防抖和节流

```javascript
// 防抖
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

// 节流
function throttle(func, limit) {
  let inThrottle;
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}

// 使用示例
const debouncedSearch = debounce((query) => {
  // 搜索API调用
  console.log('Searching for:', query);
}, 300);

// 在输入框 onChange 事件中使用
<input onChange={(e) => debouncedSearch(e.target.value)} />
```

### 7.3 代码分割

```javascript
// React.lazy 和 Suspense
import { lazy, Suspense } from 'react';

const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <div>
      <Suspense fallback={<div>Loading...</div>}>
        <HeavyComponent />
      </Suspense>
    </div>
  );
}
```

### 7.4 使用场景

- **长列表**：使用虚拟列表优化长对话历史的渲染。
- **搜索输入**：使用防抖优化搜索输入，减少API调用次数。
- **大型应用**：使用代码分割减少初始加载时间。
- **资源密集型操作**：使用节流优化滚动、 resize 等事件处理。

------

## 8. 安全考虑

### 8.1 API密钥管理

```javascript
// 错误做法：硬编码API密钥
const API_KEY = 'sk-1234567890abcdef'; // 不安全！

// 正确做法：使用环境变量或后端代理
// 1. 使用环境变量（在构建时注入）
const API_KEY = process.env.REACT_APP_API_KEY;

// 2. 使用后端代理
// 前端调用后端API，后端再调用AI服务
async function callAI(message) {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ message })
  });
  return response.json();
}
```

### 8.2 数据清理

```javascript
// 防止XSS攻击
function sanitizeInput(input) {
  const div = document.createElement('div');
  div.textContent = input;
  return div.innerHTML;
}

// 使用示例
const userInput = sanitizeInput(input);
```

### 8.3 HTTPS

```javascript
// 确保使用HTTPS
if (window.location.protocol !== 'https:') {
  window.location.href = window.location.href.replace('http:', 'https:');
}
```

### 8.4 使用场景

- **API调用**：安全管理API密钥，避免泄露。
- **用户输入**：清理用户输入，防止XSS攻击。
- **数据传输**：使用HTTPS加密传输数据。
- **认证授权**：实现安全的认证和授权机制。

------

## 9. 最佳实践

### 9.1 代码组织

- **组件化**：将UI拆分为可复用的组件。
- **模块化**：将业务逻辑拆分为独立的模块。
- **文件夹结构**：合理组织文件夹结构，提高代码可读性。

### 9.2 错误处理

- **全局错误处理**：实现全局错误处理机制。
- **用户友好的错误提示**：提供清晰、友好的错误提示。
- **错误日志**：记录错误日志，便于问题排查。

### 9.3 用户体验

- **加载状态**：提供明确的加载状态反馈。
- **流式输出**：实现流式输出，提高用户体验。
- **响应式设计**：适配不同屏幕尺寸的设备。
- **可访问性**：确保所有用户都能使用，包括残障用户。

### 9.4 性能优化

- **网络优化**：减少请求次数，使用缓存。
- **渲染优化**：使用虚拟列表，优化渲染性能。
- **资源优化**：压缩资源，减少加载时间。
- **代码优化**：减少代码体积，优化代码结构。

### 9.5 安全最佳实践

- **API密钥管理**：安全存储API密钥，避免硬编码。
- **数据清理**：清理用户输入，防止XSS攻击。
- **HTTPS**：使用HTTPS加密传输数据。
- **CORS**：正确配置CORS，避免跨域安全问题。

------

## 10. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 流式输出卡顿 | 网络延迟高 | 使用WebSocket，优化网络连接 |
|  | 前端渲染慢 | 使用虚拟列表，优化渲染性能 |
| API调用失败 | 网络错误 | 实现错误处理和重试机制 |
|  | API密钥错误 | 安全管理API密钥，避免泄露 |
|  | 速率限制 | 遵守API速率限制，实现请求队列 |
| 状态管理混乱 | 状态设计不合理 | 合理设计状态结构，使用状态管理库 |
|  | 状态更新频繁 | 使用防抖和节流，优化状态更新 |
| 性能问题 | 资源加载慢 | 优化资源加载，使用CDN |
|  | 渲染性能差 | 使用虚拟列表，优化渲染逻辑 |
| 安全问题 | API密钥泄露 | 不在前端存储API密钥，使用后端代理 |
|  | XSS攻击 | 清理用户输入，使用安全的渲染方式 |
| 多模态交互问题 | 浏览器兼容性 | 检查浏览器支持，提供降级方案 |
|  | 文件大小限制 | 限制上传文件大小，提供压缩功能 |

------

## 11. 参考资源

- [Axios 官方文档](https://axios-http.com/docs/intro)
- [Fetch API 官方文档](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)
- [WebSocket 官方文档](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Server-Sent Events 官方文档](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events)
- [Redux 官方文档](https://redux.js.org/)
- [React Window 官方文档](https://react-window.vercel.app/)
- [Web Speech API 官方文档](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [Material UI 官方文档](https://mui.com/)
- [Ant Design 官方文档](https://ant.design/)
