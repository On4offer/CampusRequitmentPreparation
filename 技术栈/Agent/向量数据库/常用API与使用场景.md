# 📘《向量数据库常用 API 与使用场景》

> 系统学习见同目录《学习笔记》；本文件为日常开发速查手册。

------

## 1. Pinecone

### 1.1 基本操作

#### 初始化
```python
import pinecone

# 初始化 Pinecone
pinecone.init(
    api_key="your-api-key",
    environment="your-environment"  # 如 gcp-starter
)
```

#### 创建索引
```python
# 创建索引
index_name = "your-index"
if index_name not in pinecone.list_indexes():
    pinecone.create_index(
        name=index_name,
        dimension=1536,  # 嵌入维度，根据模型调整
        metric="cosine",  # 相似度度量：cosine, euclidean, dotproduct
        pods=1,  # 节点数
        pod_type="p1.x1"  # 节点类型
    )

# 连接索引
index = pinecone.Index(index_name)
```

#### 插入数据
```python
# 单条插入
index.upsert(
    vectors=[
        ("vec1", [0.1, 0.2, ..., 0.9], {"text": "示例文本1", "source": "doc1"})
    ]
)

# 批量插入
batch_size = 100
vectors = []
for i, (text, embedding) in enumerate(zip(texts, embeddings)):
    vectors.append((f"vec{i}", embedding, {"text": text, "source": f"doc{i}"}))
    if len(vectors) >= batch_size:
        index.upsert(vectors=vectors)
        vectors = []
if vectors:
    index.upsert(vectors=vectors)
```

#### 搜索
```python
# 基本搜索
query_vector = [0.1, 0.2, ..., 0.9]  # 查询向量
results = index.query(
    vector=query_vector,
    top_k=5,  # 返回前5个结果
    include_metadata=True  # 包含元数据
)

# 带元数据过滤的搜索
results = index.query(
    vector=query_vector,
    top_k=5,
    include_metadata=True,
    filter={"source": {"$eq": "doc1"}}  # 过滤条件
)

# 带命名空间的搜索
results = index.query(
    vector=query_vector,
    top_k=5,
    namespace="namespace1"  # 命名空间
)
```

#### 更新数据
```python
# 更新向量
index.update(
    id="vec1",
    values=[0.2, 0.3, ..., 1.0],  # 新向量
    set_metadata={"text": "更新后的文本", "source": "doc1"}  # 更新元数据
)
```

#### 删除数据
```python
# 删除单个向量
index.delete(ids=["vec1"])

# 删除命名空间内所有向量
index.delete(delete_all=True, namespace="namespace1")
```

#### 获取索引信息
```python
# 获取索引统计信息
stats = index.describe_index_stats()
print(stats)

# 获取向量
vector = index.fetch(ids=["vec1"])
print(vector)
```

### 1.2 使用场景

- **RAG系统**：存储文档嵌入向量，用于语义搜索。
- **推荐系统**：存储用户和物品嵌入向量，用于相似性匹配。
- **图像搜索**：存储图像嵌入向量，用于相似图像检索。
- **实时应用**：需要低延迟、高并发的生产环境。

------

## 2. Milvus

### 2.1 基本操作

#### 连接与创建集合
```python
from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType

# 连接 Milvus
connections.connect("default", host="localhost", port="19530")

# 定义字段
fields = [
    FieldSchema(name="id", dtype=DataType.VARCHAR, max_length=64, is_primary=True),
    FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
    FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=4096),
    FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=256)
]

# 定义集合 schema
schema = CollectionSchema(fields, "RAG collection")

# 创建集合
collection_name = "rag_collection"
if collection_name not in connections.list_collections():
    collection = Collection(collection_name, schema)
else:
    collection = Collection(collection_name)

# 加载集合到内存
collection.load()
```

#### 创建索引
```python
# 定义索引参数
index_params = {
    "index_type": "HNSW",  # 索引类型：HNSW, IVF_FLAT, IVF_PQ等
    "metric_type": "COSINE",  # 相似度度量
    "params": {"M": 8, "efConstruction": 64}  # HNSW参数
}

# 创建索引
collection.create_index(
    field_name="embedding",
    index_params=index_params
)
```

#### 插入数据
```python
# 准备数据
data = [
    ["id1", "id2", "id3"],  # id
    [[0.1, 0.2, ...], [0.3, 0.4, ...], [0.5, 0.6, ...]],  # embedding
    ["text1", "text2", "text3"],  # text
    ["source1", "source2", "source3"]  # source
]

# 插入数据
collection.insert(data)

# 刷新集合，确保数据可搜索
collection.flush()
```

#### 搜索
```python
# 准备查询向量
query_vectors = [[0.1, 0.2, ..., 0.9]]

# 定义搜索参数
search_params = {
    "metric_type": "COSINE",
    "params": {"ef": 64}  # HNSW搜索参数
}

# 执行搜索
results = collection.search(
    data=query_vectors,
    anns_field="embedding",  # 搜索的字段
    param=search_params,
    limit=5,  # 返回前5个结果
    expr="source == 'source1'",  # 过滤条件
    output_fields=["text", "source"]  # 返回的字段
)

# 处理搜索结果
for result in results[0]:
    print(f"ID: {result.id}, Distance: {result.distance}, Text: {result.entity.get('text')}")
```

#### 更新数据
```python
# Milvus 2.0+ 支持部分更新
collection.update(
    expr="id == 'id1'",  # 更新条件
    partition_name="",  # 分区名（可选）
    update_dict={"text": "更新后的文本"}  # 更新内容
)
```

#### 删除数据
```python
# 删除符合条件的数据
collection.delete(expr="source == 'source1'")

# 删除指定ID的数据
collection.delete(expr="id in ['id1', 'id2']")
```

#### 获取集合信息
```python
# 获取集合统计信息
stats = collection.num_entities
print(f"集合中的实体数: {stats}")

# 获取集合schema
print(collection.schema)
```

### 2.2 使用场景

- **大规模RAG系统**：处理百万级文档的检索。
- **多租户应用**：支持命名空间隔离。
- **高并发场景**：支持水平扩展，处理高并发请求。
- **需要自定义部署**：本地部署，完全控制数据。

------

## 3. FAISS

### 3.1 基本操作

#### 安装
```bash
pip install faiss-cpu  # CPU版本
# 或
pip install faiss-gpu  # GPU版本
```

#### 创建索引
```python
import faiss
import numpy as np

# 准备向量数据
dimension = 1536
vectors = np.random.random((1000, dimension)).astype('float32')

# 创建索引
# 方法1：暴力搜索（精确但慢）
index = faiss.IndexFlatL2(dimension)  # L2距离
# 或
index = faiss.IndexFlatIP(dimension)  # 内积（余弦相似度）

# 方法2：IVF索引（更快，近似）
nlist = 100  # 聚类数
index = faiss.IndexIVFFlat(
    faiss.IndexFlatL2(dimension),  # 基础索引
    dimension,  # 向量维度
    nlist,  # 聚类数
    faiss.METRIC_L2  # 距离度量
)

# 训练索引（仅IVF等需要）
index.train(vectors)

# 添加向量
index.add(vectors)
```

#### 搜索
```python
# 准备查询向量
query_vector = np.random.random((1, dimension)).astype('float32')

# 搜索
k = 5  # 返回前5个结果
distances, indices = index.search(query_vector, k)

print("距离:", distances)
print("索引:", indices)
```

#### 保存和加载索引
```python
# 保存索引
faiss.write_index(index, "index.faiss")

# 加载索引
index = faiss.read_index("index.faiss")
```

### 3.2 使用场景

- **离线搜索**：嵌入到应用中，无需独立服务。
- **小规模数据**：适合万级到十万级数据。
- **原型开发**：快速构建原型，验证概念。
- **资源受限环境**：轻量级，内存使用可控。

------

## 4. Chroma

### 4.1 基本操作

#### 安装
```bash
pip install chromadb
```

#### 创建客户端和集合
```python
import chromadb

# 创建客户端
client = chromadb.Client()
# 或持久化存储
# client = chromadb.PersistentClient(path="./chroma_db")

# 创建集合
collection = client.create_collection(name="my-collection")
# 或获取现有集合
# collection = client.get_collection(name="my-collection")
```

#### 添加数据
```python
# 添加数据
collection.add(
    documents=["这是文档1", "这是文档2"],  # 文档内容
    metadatas=[{"source": "doc1"}, {"source": "doc2"}],  # 元数据
    ids=["id1", "id2"]  # 唯一ID
)

# 自动生成嵌入（使用默认模型）
# 也可以手动提供嵌入
# collection.add(
#     embeddings=[[0.1, 0.2, ...], [0.3, 0.4, ...]],
#     documents=["这是文档1", "这是文档2"],
#     metadatas=[{"source": "doc1"}, {"source": "doc2"}],
#     ids=["id1", "id2"]
# )
```

#### 搜索
```python
# 基本搜索
results = collection.query(
    query_texts=["查询文本"],  # 查询文本
    n_results=5,  # 返回前5个结果
    include=["documents", "metadatas", "distances"]  # 包含的内容
)

# 带元数据过滤的搜索
results = collection.query(
    query_texts=["查询文本"],
    n_results=5,
    where={"source": {"$eq": "doc1"}},  # 过滤条件
    include=["documents", "metadatas", "distances"]
)

print(results)
```

#### 更新数据
```python
# 更新数据
collection.update(
    ids=["id1"],
    documents=["更新后的文档1"],
    metadatas=[{"source": "doc1-updated"}]
)
```

#### 删除数据
```python
# 删除数据
collection.delete(ids=["id1"])

# 删除集合
client.delete_collection(name="my-collection")
```

### 4.2 使用场景

- **快速原型开发**：API友好，易于使用。
- **小型应用**：适合中小规模数据。
- **开发和测试**：轻量级，适合开发环境。
- **嵌入式应用**：可以嵌入到应用中，无需独立服务。

------

## 5. Qdrant

### 5.1 基本操作

#### 安装
```bash
pip install qdrant-client
```

#### 连接和创建集合
```python
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance

# 连接Qdrant
client = QdrantClient(host="localhost", port=6333)
# 或使用云服务
# client = QdrantClient(url="https://your-qdrant-instance.cloud.qdrant.io", api_key="your-api-key")

# 创建集合
collection_name = "my-collection"
client.recreate_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(
        size=1536,  # 向量维度
        distance=Distance.COSINE  # 距离度量
    )
)
```

#### 插入数据
```python
# 准备数据
points = [
    {
        "id": 1,
        "vector": [0.1, 0.2, ..., 0.9],
        "payload": {"text": "文档1", "source": "doc1"}
    },
    {
        "id": 2,
        "vector": [0.3, 0.4, ..., 0.8],
        "payload": {"text": "文档2", "source": "doc2"}
    }
]

# 插入数据
client.upsert(
    collection_name=collection_name,
    points=points
)
```

#### 搜索
```python
# 准备查询向量
query_vector = [0.1, 0.2, ..., 0.9]

# 基本搜索
results = client.search(
    collection_name=collection_name,
    query_vector=query_vector,
    limit=5,  # 返回前5个结果
    with_payload=True  # 包含payload
)

# 带过滤条件的搜索
from qdrant_client.http.models import Filter, FieldCondition, MatchValue

filter_condition = Filter(
    must=[
        FieldCondition(
            key="source",
            match=MatchValue(value="doc1")
        )
    ]
)

results = client.search(
    collection_name=collection_name,
    query_vector=query_vector,
    limit=5,
    with_payload=True,
    query_filter=filter_condition
)

# 处理搜索结果
for result in results:
    print(f"ID: {result.id}, Score: {result.score}, Text: {result.payload.get('text')}")
```

#### 更新数据
```python
# 更新数据
client.upsert(
    collection_name=collection_name,
    points=[
        {
            "id": 1,
            "vector": [0.2, 0.3, ..., 1.0],
            "payload": {"text": "更新后的文档1", "source": "doc1"}
        }
    ]
)
```

#### 删除数据
```python
# 删除单个点
client.delete(
    collection_name=collection_name,
    points_selector={"ids": [1]}
)

# 根据过滤条件删除
client.delete(
    collection_name=collection_name,
    points_selector={"filter": filter_condition}
)
```

### 5.2 使用场景

- **需要元数据过滤**：支持复杂的过滤条件。
- **地理位置搜索**：支持基于地理位置的搜索。
- **实时应用**：性能优异，支持高并发。
- **灵活部署**：可本地部署或使用云服务。

------

## 6. Elasticsearch

### 6.1 基本操作

#### 安装依赖
```bash
pip install elasticsearch
```

#### 连接和创建索引
```python
from elasticsearch import Elasticsearch

# 连接Elasticsearch
es = Elasticsearch(["http://localhost:9200"])

# 创建索引
index_name = "vector-index"
mapping = {
    "mappings": {
        "properties": {
            "text": {
                "type": "text"
            },
            "embedding": {
                "type": "dense_vector",
                "dims": 1536,  # 向量维度
                "index": True,
                "similarity": "cosine"  # 相似度度量
            },
            "source": {
                "type": "keyword"
            }
        }
    }
}

if not es.indices.exists(index=index_name):
    es.indices.create(index=index_name, body=mapping)
```

#### 插入数据
```python
# 插入单条数据
document = {
    "text": "示例文档",
    "embedding": [0.1, 0.2, ..., 0.9],
    "source": "doc1"
}

es.index(
    index=index_name,
    id="1",
    body=document
)

# 批量插入
from elasticsearch.helpers import bulk

documents = [
    {
        "_index": index_name,
        "_id": "2",
        "_source": {
            "text": "文档2",
            "embedding": [0.3, 0.4, ..., 0.8],
            "source": "doc2"
        }
    },
    {
        "_index": index_name,
        "_id": "3",
        "_source": {
            "text": "文档3",
            "embedding": [0.5, 0.6, ..., 0.7],
            "source": "doc3"
        }
    }
]

bulk(es, documents)
```

#### 搜索
```python
# 向量搜索
query_vector = [0.1, 0.2, ..., 0.9]

search_body = {
    "query": {
        "knn": {
            "embedding": {
                "vector": query_vector,
                "k": 5  # 返回前5个结果
            }
        }
    },
    "fields": ["text", "source"],
    "size": 5
}

results = es.search(index=index_name, body=search_body)

# 带过滤条件的搜索
search_body = {
    "query": {
        "bool": {
            "must": [
                {
                    "knn": {
                        "embedding": {
                            "vector": query_vector,
                            "k": 5
                        }
                    }
                },
                {
                    "term": {
                        "source": "doc1"
                    }
                }
            ]
        }
    },
    "fields": ["text", "source"],
    "size": 5
}

results = es.search(index=index_name, body=search_body)

# 处理搜索结果
for hit in results["hits"]["hits"]:
    print(f"ID: {hit['_id']}, Score: {hit['_score']}, Text: {hit['_source']['text']}")
```

#### 更新数据
```python
# 更新数据
update_body = {
    "doc": {
        "text": "更新后的文档",
        "source": "doc1-updated"
    }
}

es.update(index=index_name, id="1", body=update_body)
```

#### 删除数据
```python
# 删除单个文档
es.delete(index=index_name, id="1")

# 删除索引
es.indices.delete(index=index_name)
```

### 6.2 使用场景

- **需要全文搜索**：同时支持全文搜索和向量搜索。
- **现有Elasticsearch用户**：集成到现有Elasticsearch生态系统。
- **复杂查询**：支持复杂的查询组合。
- **企业级应用**：成熟的生态系统，支持大规模部署。

------

## 7. 最佳实践

### 7.1 性能优化

- **批量操作**：使用批量插入和批量查询提高效率。
- **索引选择**：根据数据特点选择合适的索引类型。
- **参数调优**：根据实际情况调优索引参数，如HNSW的M值、IVF的聚类数等。
- **硬件优化**：使用高性能硬件，如SSD存储、足够的内存。
- **缓存策略**：缓存热门查询结果，减少重复计算。

### 7.2 数据管理

- **数据预处理**：对原始数据进行清洗和标准化，提高嵌入质量。
- **嵌入模型选择**：选择适合任务的嵌入模型，确保向量质量。
- **元数据设计**：合理设计元数据，便于过滤和查询。
- **数据更新策略**：定期更新向量数据，保持数据新鲜度。
- **备份与恢复**：定期备份数据，确保数据安全。

### 7.3 部署建议

- **云服务 vs 本地部署**：根据数据规模、预算和技术能力选择。
- **水平扩展**：对于大规模数据，使用支持水平扩展的向量数据库。
- **监控与告警**：监控数据库性能，设置合理的告警机制。
- **安全措施**：设置访问控制，保护敏感数据。

### 7.4 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 搜索速度慢 | 索引类型不合适 | 选择更适合的索引类型，如HNSW |
|  | 数据量过大 | 增加硬件资源，使用水平扩展 |
|  | 查询参数不当 | 优化查询参数，如减少k值 |
| 搜索结果不相关 | 嵌入模型不合适 | 选择更适合任务的嵌入模型 |
|  | 索引参数不当 | 调优索引参数 |
|  | 数据质量差 | 改进数据预处理，提高数据质量 |
| 内存使用高 | 索引类型内存消耗大 | 选择内存效率更高的索引类型，如PQ |
|  | 数据量过大 | 增加内存，或使用量化技术 |
| 部署复杂 | 依赖项多 | 选择易于部署的向量数据库，如Chroma |
|  | 配置复杂 | 参考官方文档，使用容器化部署 |

------

## 8. 参考资源

- [Pinecone 官方文档](https://docs.pinecone.io/docs/quickstart)
- [Milvus 官方文档](https://milvus.io/docs/overview.md)
- [FAISS 官方文档](https://github.com/facebookresearch/faiss/wiki)
- [Chroma 官方文档](https://docs.trychroma.com/)
- [Qdrant 官方文档](https://qdrant.tech/documentation/)
- [Elasticsearch 向量搜索文档](https://www.elastic.co/guide/en/elasticsearch/reference/current/knn-search.html)
