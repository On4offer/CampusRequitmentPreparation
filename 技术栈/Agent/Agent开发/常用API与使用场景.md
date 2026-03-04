# 📌 Agent 开发常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重 **工具定义、ReAct/Tool Use、LangChain/LangGraph** 的常用写法与场景。

---

## 一、工具定义（OpenAI 兼容 Function / Tool）

| 字段 | 说明 | 示例 |
|------|------|------|
| **name** | 工具名，模型据此选择 | get_weather |
| **description** | 模型用来说明“何时用这个工具” | 根据城市名查询当前天气。 |
| **parameters** | JSON Schema：type、properties、required | type: object, properties: { city: { type: "string" } }, required: ["city"] |

- 描述越清晰，模型选对工具、填对参数的概率越高；可写清参数单位、枚举值。

---

## 二、ReAct / Tool Use 流程速记

1. **用户输入** → 拼进 messages（含历史）。
2. **调用 LLM** → 若返回 tool_calls，解析 name + arguments。
3. **执行工具** → 本地函数或 HTTP，得到 result。
4. **把结果塞回** → 追加 tool 消息：role=tool，content=result。
5. **再次调用 LLM** → 根据观察继续推理或输出最终答案；若再无 tool_calls 则结束。

---

## 三、LangChain 常用抽象速查

| 概念 | 说明 |
|------|------|
| **Tool** | 用 @tool 或 StructuredTool 定义，带 name、description、schema |
| **Agent** | create_react_agent（ReAct）、create_tool_calling_agent 等 |
| **AgentExecutor** | agent.invoke(input)，内部循环：LLM → 解析 tool_calls → 执行 → 再调 LLM |
| **Memory** | ChatMessageHistory、BufferWindowMemory 等，注入到 chain/agent |
| **LCEL** | pipe：prompt \| llm \| output_parser，链式组合 |

---

## 四、LangGraph 要点速记

| 概念 | 说明 |
|------|------|
| **State** | 图节点间传递的 TypedDict，如 messages、current_step |
| **节点** | 函数：state → 新 state（或 partial update） |
| **边** | add_edge(from, to)；conditional_edges 根据 state 选下一节点 |
| **入口/出口** | add_node、set_entry_point、set_finish_point |
| **编译** | graph.compile() 得到可执行的 runnable，invoke(state) 运行 |

- 多 Agent：不同节点调用不同 Agent，通过 state 传消息或任务描述。

---

## 五、使用场景对照

| 场景 | 推荐做法 |
|------|----------|
| 问答 + 查库 | 工具：query_database(sql)；描述写清“执行只读 SQL，返回表格”。 |
| 问答 + 检索 | RAG：先检索再注入 context；或工具 search_docs(query)，把结果给模型总结。 |
| 多步任务 | LangGraph 建图：规划 → 执行工具 → 判断是否完成 → 汇总或再规划。 |
| 与后端联调 | 工具实现里调后端 REST：requests.post(url, json=params)；后端提供清晰 API 与鉴权。 |
| 人工介入 | LangGraph 某节点“等待人工输入”，state 中写入 pending_human_input，恢复时再继续。 |

---

## 六、与学习笔记的对应关系

- Agent 概念与 ReAct/Tool Use → 第 1 章；工具定义与调用 → 第 2 章；LangChain/LangGraph → 第 3、4 章；记忆与生产 → 第 5 章；实战与面试 → 第 6 章及附录。
