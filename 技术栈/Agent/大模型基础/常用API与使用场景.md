# 📘《大模型基础常用 API 与使用场景》

> 系统学习见同目录《学习笔记》；本文件为日常开发速查手册。

------

## 1. Hugging Face Transformers

### 1.1 模型加载与使用

#### 安装
```bash
pip install transformers torch
```

#### 加载预训练模型
```python
from transformers import AutoModelForCausalLM, AutoTokenizer

# 加载模型和分词器
model_name = "meta-llama/Llama-2-7b-hf"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# 加载模型到GPU
import torch
model = model.to(torch.device("cuda"))
```

#### 文本生成
```python
# 生成文本
prompt = "Once upon a time,"
inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

# 生成配置
outputs = model.generate(
    **inputs,
    max_new_tokens=100,  # 生成的最大token数
    temperature=0.7,  # 温度参数，控制生成的随机性
    top_p=0.95,  #  nucleus sampling参数
    repetition_penalty=1.1,  # 重复惩罚
    num_return_sequences=1  # 返回的序列数
)

# 解码输出
output = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(output)
```

### 1.2 模型微调

#### 基本微调
```python
from transformers import Trainer, TrainingArguments

# 准备数据集
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, texts, tokenizer, max_length=512):
        self.texts = texts
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        inputs = self.tokenizer(
            text,
            max_length=self.max_length,
            padding="max_length",
            truncation=True,
            return_tensors="pt"
        )
        inputs["labels"] = inputs["input_ids"]
        return {k: v.squeeze() for k, v in inputs.items()}

# 创建数据集
train_texts = ["This is a sample text for training.", "Another sample text."]
train_dataset = CustomDataset(train_texts, tokenizer)

# 配置训练参数
training_args = TrainingArguments(
    output_dir="./results",
    per_device_train_batch_size=2,
    num_train_epochs=3,
    learning_rate=2e-5,
    weight_decay=0.01,
    logging_dir="./logs",
    logging_steps=10,
    save_steps=100,
    save_total_limit=2,
)

# 创建训练器
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
)

# 开始训练
trainer.train()

# 保存模型
trainer.save_model("./fine-tuned-model")
tokenizer.save_pretrained("./fine-tuned-model")
```

### 1.3 使用场景

- **文本生成**：生成文章、故事、代码等。
- **文本分类**：情感分析、主题分类等。
- **问答系统**：基于模型的问答。
- **翻译**：文本翻译。
- **摘要**：文本摘要生成。

------

## 2. OpenAI API

### 2.1 基本使用

#### 安装
```bash
pip install openai
```

#### 配置
```python
import openai

# 设置API密钥
openai.api_key = "your-api-key"
```

#### 文本生成
```python
# 生成文本
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short story about AI."}
    ],
    temperature=0.7,
    max_tokens=150,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
)

print(response["choices"][0]["message"]["content"])
```

#### 流式输出
```python
# 流式输出
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Write a short story about AI."}
    ],
    temperature=0.7,
    max_tokens=150,
    stream=True
)

for chunk in response:
    if "content" in chunk["choices"][0]["delta"]:
        print(chunk["choices"][0]["delta"]["content"], end="")
```

### 2.2 使用场景

- **聊天机器人**：构建基于GPT的聊天机器人。
- **内容生成**：生成文章、邮件、代码等。
- **问答系统**：基于GPT的问答系统。
- **辅助写作**：语法检查、风格调整等。
- **教育辅助**：辅导、答疑等。

------

## 3. LangChain

### 3.1 基本使用

#### 安装
```bash
pip install langchain
```

#### 链式调用
```python
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# 初始化LLM
llm = ChatOpenAI(model_name="gpt-3.5-turbo", temperature=0.7)

# 创建Prompt模板
prompt = ChatPromptTemplate.from_template(
    "Write a {genre} story about {topic}."
)

# 创建链
chain = LLMChain(llm=llm, prompt=prompt)

# 运行链
result = chain.run(genre="science fiction", topic="artificial intelligence")
print(result)
```

#### 与工具集成
```python
from langchain.agents import AgentType, initialize_agent, load_tools

# 加载工具
tools = load_tools(["serpapi", "llm-math"], llm=llm)

# 初始化代理
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 运行代理
agent.run("What's the current temperature in New York? And what's 25 Celsius in Fahrenheit?")
```

### 3.2 使用场景

- **复杂任务自动化**：结合多个工具完成复杂任务。
- **RAG系统**：构建检索增强生成系统。
- **对话系统**：构建多轮对话系统。
- **知识管理**：管理和利用知识库。
- **工作流自动化**：自动化办公流程。

------

## 4. vLLM

### 4.1 基本使用

#### 安装
```bash
pip install vllm
```

#### 启动服务
```bash
# 启动vLLM服务
python -m vllm.entrypoints.api_server --model meta-llama/Llama-2-7b-hf --port 8000
```

#### 客户端调用
```python
import requests

# 发送请求
response = requests.post(
    "http://localhost:8000/generate",
    json={
        "prompt": "Once upon a time,",
        "max_tokens": 100,
        "temperature": 0.7
    }
)

# 处理响应
result = response.json()
print(result["text"][0])
```

### 4.2 使用场景

- **高并发推理**：处理大量并发请求。
- **低延迟生成**：减少生成延迟，提高用户体验。
- **模型服务**：部署大模型作为服务。
- **批量推理**：高效处理批量推理请求。

------

## 5. PyTorch

### 5.1 基本使用

#### 安装
```bash
pip install torch torchvision torchaudio
```

#### 张量操作
```python
import torch

# 创建张量
t = torch.tensor([1, 2, 3])
print(t)

# 张量运算
t1 = torch.tensor([1, 2, 3])
t2 = torch.tensor([4, 5, 6])
print(t1 + t2)
print(t1 * t2)

# 自动微分
x = torch.tensor(2.0, requires_grad=True)
y = x**2
y.backward()
print(x.grad)
```

#### 模型定义
```python
import torch.nn as nn
import torch.nn.functional as F

class SimpleModel(nn.Module):
    def __init__(self):
        super(SimpleModel, self).__init__()
        self.fc1 = nn.Linear(10, 50)
        self.fc2 = nn.Linear(50, 1)
    
    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        return x

# 创建模型
model = SimpleModel()
print(model)
```

### 5.2 使用场景

- **模型训练**：训练自定义模型。
- **模型微调**：微调预训练模型。
- **模型部署**：将模型部署到生产环境。
- **研究实验**：进行深度学习研究实验。

------

## 6. TensorFlow

### 6.1 基本使用

#### 安装
```bash
pip install tensorflow
```

#### 张量操作
```python
import tensorflow as tf

# 创建张量
t = tf.constant([1, 2, 3])
print(t)

# 张量运算
t1 = tf.constant([1, 2, 3])
t2 = tf.constant([4, 5, 6])
print(tf.add(t1, t2))
print(tf.multiply(t1, t2))

# 自动微分
x = tf.Variable(2.0)
with tf.GradientTape() as tape:
    y = x**2
grad = tape.gradient(y, x)
print(grad)
```

#### 模型定义
```python
from tensorflow.keras import layers, models

model = models.Sequential([
    layers.Dense(50, activation='relu', input_shape=(10,)),
    layers.Dense(1)
])

model.summary()
```

### 6.2 使用场景

- **模型训练**：训练自定义模型。
- **模型微调**：微调预训练模型。
- **模型部署**：将模型部署到生产环境。
- **研究实验**：进行深度学习研究实验。
- **移动端部署**：将模型部署到移动设备。

------

## 7. 大模型评估工具

### 7.1 EleutherAI LM Eval Harness

#### 安装
```bash
pip install lm_eval
```

#### 使用
```python
from lm_eval import evaluator, tasks

# 评估模型
results = evaluator.simple_evaluate(
    model="gpt2",
    tasks=["hellaswag", "piqa"],
    batch_size=1
)

print(results)
```

### 7.2 Hugging Face Evaluate

#### 安装
```bash
pip install evaluate
```

#### 使用
```python
import evaluate

# 加载评估指标
accuracy = evaluate.load("accuracy")

# 计算准确率
predictions = [0, 1, 1, 0]
references = [0, 1, 0, 0]
results = accuracy.compute(predictions=predictions, references=references)
print(results)
```

### 7.3 使用场景

- **模型评估**：评估模型在各种任务上的性能。
- **模型选择**：比较不同模型的性能。
- **微调监控**：监控微调过程中的模型性能。
- **研究实验**：评估新方法的效果。

------

## 8. 最佳实践

### 8.1 模型选择

- **根据任务选择**：不同任务适合不同模型，如文本生成适合GPT类模型，文本理解适合BERT类模型。
- **根据资源选择**：资源有限时选择较小的模型，资源充足时选择较大的模型。
- **根据场景选择**：实时应用选择推理速度快的模型，非实时应用选择性能好的模型。

### 8.2 性能优化

- **模型量化**：使用INT8或FP16量化，减少模型大小和推理时间。
- **模型压缩**：使用剪枝、知识蒸馏等方法，减小模型大小。
- **批量推理**：批量处理多个输入，提高推理效率。
- **缓存机制**：缓存中间计算结果，加速自回归生成。
- **硬件优化**：使用GPU、TPU等硬件加速推理。

### 8.3 提示工程

- **清晰指令**：明确告诉模型要做什么。
- **示例引导**：提供示例，引导模型输出格式和风格。
- **上下文管理**：合理组织上下文，提供必要的信息。
- **格式约束**：指定输出格式，如JSON、列表等。
- **迭代优化**：根据模型输出，不断优化提示。

### 8.4 部署建议

- **云服务**：使用AWS、Azure、GCP等云服务，快速部署模型。
- **容器化**：使用Docker容器化模型，确保环境一致性。
- **自动扩缩容**：根据流量自动调整资源，优化成本。
- **监控与日志**：监控模型性能和使用情况，及时发现问题。
- **安全措施**：保护API密钥，防止滥用。

------

## 9. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 模型加载失败 | 模型路径错误 | 检查模型路径是否正确 |
|  | 内存不足 | 使用更小的模型或增加内存 |
| 推理速度慢 | 模型太大 | 使用模型量化或压缩 |
|  | 硬件性能不足 | 使用GPU或TPU加速 |
|  | 批量大小不当 | 调整批量大小，平衡速度和内存 |
| 生成内容质量差 | 提示设计不当 | 优化提示，提供更清晰的指令 |
|  | 模型不适合任务 | 选择更适合任务的模型 |
|  | 温度参数不当 | 调整温度参数，平衡随机性和准确性 |
| 显存不足 | 模型太大 | 使用更小的模型或模型量化 |
|  | 批量大小过大 | 减小批量大小 |
| API调用失败 | API密钥错误 | 检查API密钥是否正确 |
|  | 速率限制 | 遵守API速率限制，实现请求队列 |
|  | 网络问题 | 检查网络连接，实现重试机制 |

------

## 10. 参考资源

- [Hugging Face Transformers 文档](https://huggingface.co/docs/transformers/index)
- [OpenAI API 文档](https://platform.openai.com/docs/introduction)
- [LangChain 文档](https://python.langchain.com/docs/get_started/introduction)
- [vLLM 文档](https://vllm.readthedocs.io/en/latest/)
- [PyTorch 文档](https://pytorch.org/docs/stable/)
- [TensorFlow 文档](https://www.tensorflow.org/docs)
- [EleutherAI LM Eval Harness](https://github.com/EleutherAI/lm-evaluation-harness)
- [Hugging Face Evaluate](https://huggingface.co/docs/evaluate/index)
