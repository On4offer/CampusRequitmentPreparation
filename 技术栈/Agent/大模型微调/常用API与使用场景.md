# 📘《大模型微调常用 API 与使用场景》

> 系统学习见同目录《学习笔记》；本文件为日常开发速查手册。

------

## 1. Hugging Face Transformers

### 1.1 模型加载与配置

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

#### 模型配置
```python
from transformers import AutoConfig

# 查看模型配置
config = AutoConfig.from_pretrained(model_name)
print(config)

# 修改配置
config.max_new_tokens = 1024
model = AutoModelForCausalLM.from_pretrained(model_name, config=config)
```

### 1.2 数据处理

#### 基本分词
```python
# 分词
inputs = tokenizer("Hello, how are you?", return_tensors="pt")
print(inputs)

# 解码
output_ids = model.generate(**inputs, max_new_tokens=50)
output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
print(output)
```

#### 批量处理
```python
# 批量分词
batch_texts = ["Hello, how are you?", "What's your name?"]
inputs = tokenizer(batch_texts, padding=True, truncation=True, return_tensors="pt")
print(inputs)
```

### 1.3 全参数微调

#### 基本训练循环
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

#### 使用混合精度训练
```python
training_args = TrainingArguments(
    # 其他参数...
    fp16=True,  # 启用混合精度训练
)
```

------

## 2. PEFT 库

### 2.1 LoRA 微调

#### 基本配置
```python
from peft import LoraConfig, get_peft_model

# 配置LoRA
lora_config = LoraConfig(
    r=8,  # LoRA秩
    lora_alpha=16,  # 缩放因子
    target_modules=["q_proj", "v_proj"],  # 目标模块
    lora_dropout=0.1,  # Dropout概率
    bias="none",  # 是否训练偏置
)

# 创建PEFT模型
peft_model = get_peft_model(model, lora_config)
print(peft_model.print_trainable_parameters())  # 打印可训练参数
```

#### 训练与保存
```python
# 训练（与全参数微调相同）
trainer = Trainer(
    model=peft_model,
    args=training_args,
    train_dataset=train_dataset,
)
trainer.train()

# 保存PEFT模型
peft_model.save_pretrained("./lora-model")

# 加载PEFT模型
from peft import PeftModel
loaded_model = AutoModelForCausalLM.from_pretrained(model_name)
loaded_peft_model = PeftModel.from_pretrained(loaded_model, "./lora-model")
```

### 2.2 QLoRA 微调

#### 基本配置
```python
from peft import LoraConfig, get_peft_model
import bitsandbytes as bnb

# 加载量化模型
model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_8bit=True,  # 8位量化
    device_map="auto",
)

# 配置QLoRA
lora_config = LoraConfig(
    r=64,
    lora_alpha=16,
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
    lora_dropout=0.1,
    bias="none",
)

# 创建PEFT模型
peft_model = get_peft_model(model, lora_config)
print(peft_model.print_trainable_parameters())
```

------

## 3. Accelerate 库

### 3.1 基本使用

#### 配置加速
```python
from accelerate import Accelerator

# 创建加速器
accelerator = Accelerator()

# 准备模型、优化器和数据加载器
optimizer = torch.optim.AdamW(model.parameters(), lr=2e-5)

# 使用accelerator包装
model, optimizer, train_dataloader = accelerator.prepare(
    model, optimizer, train_dataloader
)

# 训练循环
for epoch in range(num_epochs):
    for batch in train_dataloader:
        outputs = model(**batch)
        loss = outputs.loss
        accelerator.backward(loss)
        optimizer.step()
        optimizer.zero_grad()
```

### 3.2 分布式训练

```python
# 配置分布式训练
accelerator = Accelerator(
    gradient_accumulation_steps=4,  # 梯度累积
    mixed_precision="fp16",  # 混合精度
)
```

------

## 4. 指令微调

### 4.1 Alpaca 格式数据处理

```python
import json

# 加载Alpaca格式数据
with open("alpaca_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# 格式化数据
def format_alpaca_example(example):
    instruction = example["instruction"]
    input_text = example.get("input", "")
    output = example["output"]
    
    if input_text:
        prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{input_text}\n\n### Response:\n"
    else:
        prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
    
    return prompt + output

# 处理数据
train_texts = [format_alpaca_example(example) for example in data]
```

### 4.2 自定义指令格式

```python
def format_custom_instruction(instruction, input_text="", output=""):
    prompt = f"指令: {instruction}\n"
    if input_text:
        prompt += f"输入: {input_text}\n"
    prompt += f"输出: {output}"
    return prompt

# 使用示例
train_texts = [format_custom_instruction(
    instruction="总结以下文本",
    input_text="大模型是指参数量巨大、训练数据丰富的人工智能模型...",
    output="大模型是参数量巨大、数据丰富的AI模型，具有强大的语言理解和生成能力。"
)]
```

------

## 5. 评估与验证

### 5.1 自动评估

#### 困惑度计算
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 加载模型和分词器
model = AutoModelForCausalLM.from_pretrained("./fine-tuned-model")
tokenizer = AutoTokenizer.from_pretrained("./fine-tuned-model")
model.to(torch.device("cuda"))
model.eval()

# 计算困惑度
def compute_perplexity(text):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        outputs = model(**inputs, labels=inputs["input_ids"])
        loss = outputs.loss
        perplexity = torch.exp(loss)
    
    return perplexity.item()

# 测试
text = "This is a test sentence to compute perplexity."
perplexity = compute_perplexity(text)
print(f"Perplexity: {perplexity}")
```

#### 生成评估
```python
def generate_response(prompt, max_new_tokens=100):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(model.device) for k, v in inputs.items()}
    
    with torch.no_grad():
        output_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,
            top_p=0.95,
            repetition_penalty=1.1
        )
    
    output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
    return output

# 测试
prompt = "### Instruction:\nExplain what machine learning is.\n\n### Response:\n"
response = generate_response(prompt)
print(response)
```

### 5.2 人工评估

#### 评估问卷设计

| 评估维度 | 评分标准（1-5分） |
|---------|------------------|
| 相关性 | 回答与问题的相关程度 |
| 准确性 | 回答内容的准确程度 |
| 完整性 | 回答是否完整覆盖问题 |
| 清晰度 | 回答表达的清晰程度 |
| 风格一致性 | 回答风格是否符合预期 |

------

## 6. 模型部署

### 6.1 模型格式转换

#### 转换为 ONNX
```python
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

# 加载模型和分词器
model = AutoModelForCausalLM.from_pretrained("./fine-tuned-model")
tokenizer = AutoTokenizer.from_pretrained("./fine-tuned-model")

# 准备示例输入
inputs = tokenizer("Hello, how are you?", return_tensors="pt")

# 导出为ONNX
torch.onnx.export(
    model,
    tuple(inputs.values()),
    "model.onnx",
    input_names=["input_ids", "attention_mask"],
    output_names=["output"],
    dynamic_axes={
        "input_ids": {0: "batch_size", 1: "seq_length"},
        "attention_mask": {0: "batch_size", 1: "seq_length"},
        "output": {0: "batch_size", 1: "seq_length"}
    }
)
```

#### 量化模型
```python
# 使用bitsandbytes量化
from transformers import AutoModelForCausalLM

model = AutoModelForCausalLM.from_pretrained(
    "./fine-tuned-model",
    load_in_8bit=True,
    device_map="auto"
)

# 保存量化模型
model.save_pretrained("./quantized-model")
```

### 6.2 服务部署

#### 使用 FastAPI 部署
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

app = FastAPI()

# 加载模型
model_name = "./fine-tuned-model"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)
model.to(torch.device("cuda"))
model.eval()

# 定义请求体
class GenerateRequest(BaseModel):
    prompt: str
    max_new_tokens: int = 100
    temperature: float = 0.7

# 定义生成接口
@app.post("/generate")
async def generate(request: GenerateRequest):
    try:
        inputs = tokenizer(request.prompt, return_tensors="pt")
        inputs = {k: v.to(model.device) for k, v in inputs.items()}
        
        with torch.no_grad():
            output_ids = model.generate(
                **inputs,
                max_new_tokens=request.max_new_tokens,
                temperature=request.temperature,
                top_p=0.95,
                repetition_penalty=1.1
            )
        
        output = tokenizer.decode(output_ids[0], skip_special_tokens=True)
        return {"response": output}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 运行服务
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

------

## 7. 最佳实践

### 7.1 数据准备

- **数据质量**：确保数据准确、多样、代表性强。
- **数据量**：根据模型大小，通常需要至少1000-10000条数据。
- **数据格式**：使用标准格式，如Alpaca格式。
- **数据分割**：训练集、验证集、测试集比例通常为8:1:1。

### 7.2 微调策略

- **选择合适的微调方法**：
  - 小模型（<1B）：全参数微调
  - 大模型（≥7B）：PEFT方法（如LoRA、QLoRA）
- **学习率**：
  - 全参数微调：1e-5到5e-5
  - PEFT：1e-4到5e-4
- **batch size**：根据GPU内存调整，通常为8-32。
- **训练轮数**：通常为3-10轮，使用早停策略。

### 7.3 评估与优化

- **多维度评估**：结合自动评估和人工评估。
- **A/B测试**：在实际应用中测试不同微调版本。
- **迭代优化**：根据评估结果调整数据和微调参数。

### 7.4 部署建议

- **模型量化**：使用8位或4位量化减少推理成本。
- **服务优化**：使用异步处理、批处理等提高服务性能。
- **监控**：监控模型性能、响应时间和资源使用。

------

## 8. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 内存不足 | 模型太大，batch size过大 | 使用PEFT方法，减小batch size，使用梯度累积 |
| 训练不稳定 | 学习率过高，数据质量差 | 降低学习率，检查数据质量，使用梯度裁剪 |
| 过拟合 | 数据量不足，训练轮数过多 | 增加数据量，使用正则化，早停策略 |
| 性能不佳 | 数据质量差，微调策略不当 | 改进数据质量，调整微调参数，尝试不同的PEFT方法 |
| 推理速度慢 | 模型太大，未量化 | 使用模型量化，优化推理代码，使用更高效的硬件 |

------

## 9. 参考资源

- [Hugging Face Transformers 文档](https://huggingface.co/docs/transformers/index)
- [PEFT 库文档](https://huggingface.co/docs/peft/index)
- [Accelerate 库文档](https://huggingface.co/docs/accelerate/index)
- [bitsandbytes 文档](https://github.com/TimDettmers/bitsandbytes)
- [QLoRA 论文](https://arxiv.org/abs/2305.14314)
- [LoRA 论文](https://arxiv.org/abs/2106.09685)
