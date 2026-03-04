# 📌 Vue 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重 **Vue 3 Composition API、常用指令与场景**，便于速查。

---

## 一、创建应用与挂载

```js
import { createApp } from 'vue'
import App from './App.vue'
createApp(App).mount('#app')
```

---

## 二、响应式与组合式 API（script setup）

| API | 说明 | 示例 |
|-----|------|------|
| **ref** | 基本类型响应式，.value 读写 | const count = ref(0); count.value++ |
| **reactive** | 对象响应式，直接改属性 | const state = reactive({ name: 'a' }); state.name = 'b' |
| **computed** | 计算属性 | const double = computed(() => count.value * 2) |
| **watch** | 侦听 | watch(count, (n) => console.log(n)) |
| **watchEffect** | 自动收集依赖并执行 | watchEffect(() => console.log(count.value)) |

---

## 三、常用模板指令

| 指令 | 说明 | 示例 |
|------|------|------|
| **v-if / v-else-if / v-else** | 条件渲染 | v-if="show" |
| **v-for** | 列表渲染 | v-for="(item, i) in list" :key="item.id" |
| **v-bind** 或 **:** | 绑定属性 | :class="cls" :style="sty" |
| **v-on** 或 **@** | 绑定事件 | @click="fn" @submit.prevent="fn" |
| **v-model** | 双向绑定 | v-model="text"（input/textarea/组件） |
| **v-show** | 切换 display | v-show="visible" |
| **v-slot** 或 **#** | 插槽 | #default="{ row }" |

---

## 四、组件（script setup）

| 用法 | 说明 |
|------|------|
| **defineProps&lt;T&gt;()** | 定义 props，无需 return |
| **defineEmits&lt;E&gt;([])** | 定义事件，emit('event', payload) |
| **defineExpose({ ... })** | 暴露给父组件 ref 调用的方法/属性 |
| **useSlots() / useAttrs()** | 插槽与未声明属性 |

---

## 五、生命周期（Composition API）

| 钩子 | 说明 |
|------|------|
| **onMounted** | 组件挂载完成 |
| **onUnmounted** | 组件卸载前 |
| **onUpdated** | 响应式数据变更导致 DOM 更新后 |
| **onBeforeMount / onBeforeUnmount** | 挂载/卸载前 |

---

## 六、路由（Vue Router）

| 用法 | 说明 |
|------|------|
| **useRouter()** | router.push、replace、go、back |
| **useRoute()** | route.params、query、path、name |
| **router.beforeEach** | 全局前置守卫（鉴权、重定向） |
| **&lt;RouterView&gt;** | 路由出口；**&lt;RouterLink to="..."&gt;** 声明式导航 |

---

## 七、状态管理（Pinia）

| 用法 | 说明 |
|------|------|
| **defineStore(id, fn)** | 定义 store（state、getters、actions） |
| **useXxxStore()** | 在组件中使用 store，直接读 state、调 actions |
| **storeToRefs(store)** | 解构 state/getters 保持响应式 |

---

## 八、使用场景对照

| 场景 | 推荐做法 |
|------|----------|
| 列表渲染 | v-for + :key 唯一；大列表考虑虚拟滚动 |
| 表单 | v-model + 校验（手动或 VeeValidate 等） |
| 请求后端 | axios，在 onMounted 或事件里调用，配合 ref/reactive 存数据 |
| 鉴权 | 路由 beforeEach 查 token，无则跳登录；axios 拦截器带 token |
| 全局状态 | Pinia 存用户信息、主题等 |
| 父子通信 | props 下传，emit 上传；跨层级可用 provide/inject 或 Pinia |

---

## 九、与学习笔记的对应关系

- 概述与基础 → 第 1、2 章；组件 → 第 3 章；路由与状态 → 第 4 章；工程化 → 第 5 章；实战与面试 → 第 6 章及附录。
