# 📘《RAG 常用 API 与使用场景》

> 系统学习见同目录《学习笔记》；本文件为日常开发速查手册。

------

## 1. LangChain

### 1.1 核心 API

#### 文档加载
```python
from langchain.document_loaders import TextLoader, PyPDFLoader, DirectoryLoader

# 加载单个文本文件
loader = TextLoader("path/to/file.txt")
documents = loader.load()

# 加载PDF文件
loader = PyPDFLoader("path/to/file.pdf")
documents = loader.load()

# 加载目录下所有文件
loader = DirectoryLoader("path/to/directory")
documents = loader.load()
```

#### 分块
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter, CharacterTextSplitter

# 递归字符分块（推荐）
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", " ", ""]
)
chunks = splitter.split_documents(documents)

# 字符分块
splitter = CharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)
chunks = splitter.split_documents(documents)
```

#### 嵌入
```python
from langchain.embeddings import OpenAIEmbeddings, HuggingFaceEmbeddings

# OpenAI 嵌入
embeddings = OpenAIEmbeddings(api_key="your-api-key")

# HuggingFace 嵌入
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-small-en-v1.5"
)
```

#### 向量存储
```python
from langchain.vectorstores import Chroma, FAISS

# Chroma 向量存储
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory="path/to/chroma"
)

# FAISS 向量存储
vectorstore = FAISS.from_documents(
    documents=chunks,
    embedding=embeddings
)
# 保存到文件
vectorstore.save_local("path/to/faiss")
# 从文件加载
vectorstore = FAISS.load_local("path/to/faiss", embeddings)
```

#### 检索
```python
# 相似度检索
docs = vectorstore.similarity_search(
    query="你的问题",
    k=3  # 返回前3个结果
)

# 带分数的检索
docs_with_score = vectorstore.similarity_search_with_score(
    query="你的问题",
    k=3
)

# 带元数据过滤的检索
docs = vectorstore.similarity_search(
    query="你的问题",
    k=3,
    filter={"source": "特定文档"}
)
```

#### 链与 Prompt
```python
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.chat_models import ChatOpenAI

# 构建 Prompt
prompt_template = """
你是一个专业的问答助手，负责基于提供的文档回答用户问题。

请严格按照以下要求回答：
1. 仅基于提供的文档内容回答，不要使用外部知识
2. 回答要准确、简洁、有条理
3. 对于需要引用的内容，请在回答末尾标注来源

文档：
{context}

用户问题：
{question}

回答：
"""

prompt = PromptTemplate(
    template=prompt_template,
    input_variables=["context", "question"]
)

# 构建检索问答链
qa_chain = RetrievalQA.from_chain_type(
    llm=ChatOpenAI(model_name="gpt-3.5-turbo"),
    chain_type="stuff",  # 其他选项：map_reduce, refine, map_rerank
    retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    chain_type_kwargs={"prompt": prompt}
)

# 执行问答
result = qa_chain.run("你的问题")
```

### 1.2 使用场景

- **企业知识库问答**：加载企业文档，构建向量存储，提供智能问答。
- **文档问答**：针对特定文档（如PDF、Word）进行问答。
- **客户服务**：基于产品手册、FAQ 等提供客户支持。
- **教育辅助**：基于教材、课件等提供学习辅助。

------

## 2. LlamaIndex

### 2.1 核心 API

#### 文档加载
```python
from llama_index import SimpleDirectoryReader

# 加载目录下所有文件
reader = SimpleDirectoryReader("path/to/directory")
documents = reader.load_data()
```

#### 索引构建
```python
from llama_index import VectorStoreIndex, ServiceContext
from llama_index.embeddings import OpenAIEmbedding

# 配置服务上下文
service_context = ServiceContext.from_defaults(
    embedding=OpenAIEmbedding(api_key="your-api-key")
)

# 构建向量索引
index = VectorStoreIndex.from_documents(
    documents,
    service_context=service_context
)

# 保存索引
index.storage_context.persist("path/to/storage")

# 加载索引
from llama_index import StorageContext, load_index_from_storage
storage_context = StorageContext.from_defaults(persist_dir="path/to/storage")
index = load_index_from_storage(storage_context)
```

#### 查询
```python
# 创建查询引擎
query_engine = index.as_query_engine()

# 执行查询
response = query_engine.query("你的问题")
print(response)

# 带参数的查询
query_engine = index.as_query_engine(
    similarity_top_k=3,  # 返回前3个结果
    response_mode="compact"  # 其他选项：tree_summarize, refine, accumulate
)
```

#### 自定义 Prompt
```python
from llama_index import PromptTemplate

# 自定义查询 Prompt
custom_prompt = PromptTemplate(
    """
    你是一个专业的问答助手，负责基于提供的文档回答用户问题。
    
    请严格按照以下要求回答：
    1. 仅基于提供的文档内容回答，不要使用外部知识
    2. 回答要准确、简洁、有条理
    3. 对于需要引用的内容，请在回答末尾标注来源
    
    文档：
    {context_str}
    
    用户问题：
    {query_str}
    
    回答：
    """
)

# 应用自定义 Prompt
query_engine = index.as_query_engine(
    text_qa_template=custom_prompt
)
```

### 2.2 使用场景

- **复杂文档处理**：处理长文档、多文档的问答。
- **结构化数据集成**：结合结构化数据（如数据库）与非结构化数据。
- **多模态 RAG**：处理文本、图像等多模态数据。

------

## 3. 向量数据库 API

### 3.1 Pinecone

```python
import pinecone
from langchain.vectorstores import Pinecone

# 初始化 Pinecone
pinecone.init(
    api_key="your-api-key",
    environment="your-environment"
)

# 创建或连接索引
index_name = "your-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # 嵌入维度
        metric="cosine"
    )

# 构建向量存储
vectorstore = Pinecone.from_documents(
    documents=chunks,
    embedding=embeddings,
    index_name=index_name
)

# 检索
docs = vectorstore.similarity_search(
    query="你的问题",
    k=3
)
```

### 3.2 Milvus

```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# 连接 Milvus
connections.connect("default", host="localhost", port="19530")

# 定义 schema
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
    FieldSchema(name="metadata", dtype=DataType.JSON)
]
schema = CollectionSchema(fields, "RAG collection")

# 创建或加载集合
collection_name = "rag_collection"
if collection_name not in connections.list_collections():
    collection = Collection(collection_name, schema)
else:
    collection = Collection(collection_name)

# 创建索引
index_params = {
    "index_type": "HNSW",
    "metric_type": "COSINE",
    "params": {"M": 8, "efConstruction": 64}
}
collection.create_index("embedding", index_params)

# 插入数据
data = [
    ["id1", "id2"],  # id
    [[0.1, 0.2, ...], [0.3, 0.4, ...]],  # embedding
    ["text1", "text2"],  # text
    [{"source": "doc1"}, {"source": "doc2"}]  # metadata
]
collection.insert(data)

# 搜索
query_embedding = [0.1, 0.2, ...]  # 查询嵌入
search_params = {"metric_type": "COSINE", "params": {"ef": 64}}
results = collection.search(
    data=[query_embedding],
    anns_field="embedding",
    param=search_params,
    limit=3,
    output_fields=["text", "metadata"]
)
```

### 3.3 使用场景

- **大规模知识库**：处理百万级文档的检索。
- **实时更新**：支持知识库的实时更新与检索。
- **多租户**：为不同用户或应用提供隔离的向量存储。

------

## 4. 重排序 API

### 4.1 Cohere Rerank

```python
import cohere

# 初始化 Cohere
co = cohere.Client("your-api-key")

# 重排序
results = co.rerank(
    model="rerank-english-v2.0",
    query="你的问题",
    documents=[doc.page_content for doc in retrieved_docs],
    top_n=3
)

# 获取重排序结果
reranked_docs = [retrieved_docs[result.index] for result in results.results]
```

### 4.2 Hugging Face 交叉编码器

```python
from sentence_transformers import CrossEncoder

# 加载交叉编码器
model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")

# 构建查询-文档对
pairs = [(query, doc.page_content) for doc in retrieved_docs]

# 计算相关性分数
scores = model.predict(pairs)

# 按分数排序
sorted_docs = [doc for _, doc in sorted(zip(scores, retrieved_docs), key=lambda x: x[0], reverse=True)]
```

### 4.3 使用场景

- **高精度检索**：提升检索结果的相关性。
- **复杂查询**：处理多意图、模糊查询等复杂场景。
- **领域特定**：针对特定领域优化检索结果。

------

## 5. 最佳实践

### 5.1 性能优化

- **批处理**：批量处理文档分块与嵌入生成。
- **缓存**：缓存热门查询的检索结果与生成回答。
- **异步处理**：使用异步API提高并发能力。
- **索引优化**：根据数据特征选择合适的索引类型。

### 5.2 质量优化

- **混合检索**：结合关键词检索与向量检索。
- **多轮交互**：通过多轮对话澄清用户意图。
- **主动学习**：基于用户反馈优化检索与生成。
- **知识图谱**：结合知识图谱增强语义理解。

### 5.3 部署建议

- **云服务**：小规模应用可使用云向量数据库服务。
- **本地部署**：大规模应用或对数据隐私要求高的场景可本地部署。
- **边缘部署**：对延迟要求高的场景可考虑边缘部署。

------

## 6. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 检索结果不相关 | 分块策略不当 | 调整分块大小与策略，使用语义分块 |
|  | 嵌入模型不合适 | 选择更适合的嵌入模型，或微调模型 |
|  | 检索参数不当 | 调整 k 值、相似度阈值 |
| 上下文过长 | 分块过大 | 减小分块大小，使用重叠分块 |
|  | 模型窗口限制 | 使用摘要压缩，滑动窗口技术 |
| 生成内容不准确 | Prompt 设计不当 | 改进 Prompt，加强引用要求 |
|  | 检索结果质量差 | 优化检索策略，使用重排序 |
| 响应时间长 | 检索速度慢 | 优化向量数据库索引，使用批处理 |
|  | 生成速度慢 | 使用流式输出，选择更快的模型 |

------

## 7. 参考资源

- [LangChain 官方文档](https://python.langchain.com/docs/get_started/introduction)
- [LlamaIndex 官方文档](https://docs.llamaindex.ai/en/stable/)
- [Pinecone 官方文档](https://docs.pinecone.io/docs/quickstart)
- [Milvus 官方文档](https://milvus.io/docs/overview.md)
- [Hugging Face 嵌入模型](https://huggingface.co/models?pipeline_tag=embeddings)
