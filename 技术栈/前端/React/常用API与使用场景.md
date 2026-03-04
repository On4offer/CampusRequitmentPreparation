# 📌 React 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重 **React 18 函数组件、Hooks、常用模式与场景**，便于速查。

---

## 一、创建应用与挂载

```js
import { createRoot } from 'react-dom/client'
import App from './App'
createRoot(document.getElementById('root')).render(<App />)
```

---

## 二、常用 Hooks

| Hook | 说明 | 示例 |
|------|------|------|
| **useState** | 状态，不可变更新 | const [n, setN] = useState(0); setN(v => v + 1) |
| **useEffect** | 副作用，依赖与清理 | useEffect(() => { ...; return () => {} }, [deps]) |
| **useContext** | 消费 Context | const value = useContext(MyContext) |
| **useRef** | DOM 引用或持久化值 | const ref = useRef(null); ref.current |
| **useMemo** | 缓存计算结果 | const x = useMemo(() => compute(a), [a]) |
| **useCallback** | 缓存函数引用 | const fn = useCallback(() => {}, [deps]) |

---

## 三、JSX 与基础写法

| 用法 | 说明 |
|------|------|
| **条件渲染** | {flag && <A />} 或 {flag ? <A /> : <B />} |
| **列表** | list.map(item => <li key={item.id}>...</li>) |
| **类名** | className={cls} 或 className={`btn ${active ? 'active' : ''}`} |
| **样式** | style={{ width: 100, marginTop: 8 }}（驼峰） |
| **事件** | onClick={fn}、onChange={e => setVal(e.target.value)} |
| **受控输入** | value={val} onChange={e => setVal(e.target.value)} |

---

## 四、组件与 Props

| 用法 | 说明 |
|------|------|
| **函数组件** | function Comp({ title, children }) { return <div>...</div> } |
| **Props 只读** | 不直接修改 props，通过回调通知父组件 |
| **children** | 组件标签内的内容会作为 props.children 传入 |
| **默认值** | 解构时 default：function Comp({ name = 'guest' }) {} |

---

## 五、Context

| 步骤 | 说明 |
|------|------|
| **createContext** | const Ctx = createContext(defaultValue) |
| **Provider** | <Ctx.Provider value={v}>...</Ctx.Provider> |
| **消费** | useContext(Ctx) 或 <Ctx.Consumer>{v => ...}</Ctx.Consumer> |

---

## 六、路由（React Router v6）

| 用法 | 说明 |
|------|------|
| **BrowserRouter** | 根组件包裹，使用 history 模式 |
| **Routes / Route** | <Route path="/" element={<Home />} />、嵌套 Route |
| **useNavigate** | const nav = useNavigate(); nav('/path')、nav(-1) |
| **useParams** | 动态段：path="/user/:id" → useParams().id |
| **useSearchParams** | [params, setParams] = useSearchParams(); params.get('q') |
| **懒加载** | const Page = lazy(() => import('./Page')); <Suspense fallback={...}><Page /></Suspense> |

---

## 七、状态管理速记

| 方案 | 说明 |
|------|------|
| **useState 提升** | 共享状态放到共同父组件，通过 props 与回调传递 |
| **Context** | 轻量全局数据（主题、语言、用户信息） |
| **Redux** | store、reducer、useSelector、useDispatch；适合大型应用 |
| **Zustand** | 轻量 store，useXxxStore() 直接读写，无 Provider |

---

## 八、使用场景对照

| 场景 | 推荐做法 |
|------|----------|
| 列表渲染 | map + 稳定 key（如 id）；长列表用虚拟滚动 |
| 表单 | 受控：value + onChange，状态由 state 管理 |
| 请求数据 | useEffect 中 fetch/axios，用 useState 存 data/loading/error |
| 鉴权 | 路由层判断 token，无则重定向登录；请求拦截器带 token |
| 全局状态 | Context 或 Zustand/Redux 存用户、主题等 |
| 父子通信 | props 下传、回调上传；跨层级用 Context 或状态库 |
| AI 对话/流式 | 使用 Vercel AI SDK 的 useChat 等 React 生态 hooks（若选 React 技术栈） |

---

## 九、与学习笔记的对应关系

- 概述与特点 → 第 1 章；JSX 与基础 → 第 2 章；Hooks 与状态 → 第 3 章；组件化与数据流 → 第 4 章；路由与状态管理 → 第 5 章；工程化与面试 → 第 6 章及附录。
