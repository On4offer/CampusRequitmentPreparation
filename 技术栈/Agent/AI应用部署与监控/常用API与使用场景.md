# 📘《AI应用部署与监控常用 API 与使用场景》

> 系统学习见同目录《学习笔记》；本文件为日常开发速查手册。

------

## 1. Docker

### 1.1 基本操作

#### 构建镜像
```bash
# 构建镜像
docker build -t <image-name> .

# 指定Dockerfile路径
docker build -t <image-name> -f <dockerfile-path> .

# 构建时指定参数
docker build -t <image-name> --build-arg <arg-name>=<arg-value> .
```

#### 运行容器
```bash
# 运行容器
docker run -d --name <container-name> -p <host-port>:<container-port> <image-name>

# 运行容器并挂载卷
docker run -d --name <container-name> -v <host-path>:<container-path> <image-name>

# 运行容器并设置环境变量
docker run -d --name <container-name> -e <env-name>=<env-value> <image-name>

# 运行容器并设置资源限制
docker run -d --name <container-name> --memory <memory-limit> --cpus <cpu-limit> <image-name>
```

#### 管理容器
```bash
# 列出容器
docker ps

# 列出所有容器（包括停止的）
docker ps -a

# 停止容器
docker stop <container-name>

# 启动容器
docker start <container-name>

# 删除容器
docker rm <container-name>

# 查看容器日志
docker logs <container-name>

# 进入容器
docker exec -it <container-name> /bin/bash
```

#### 管理镜像
```bash
# 列出镜像
docker images

# 删除镜像
docker rmi <image-name>

# 推送镜像到仓库
docker push <image-name>

# 从仓库拉取镜像
docker pull <image-name>
```

### 1.2 Docker Compose

#### 基本配置
```yaml
# docker-compose.yml
version: '3'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - MODEL_NAME=llama2
    depends_on:
      - vector-db
  vector-db:
    image: milvusdb/milvus:latest
    ports:
      - "19530:19530"
    volumes:
      - milvus-data:/var/lib/milvus
volumes:
  milvus-data:
```

#### 运行
```bash
# 启动服务
docker-compose up -d

# 停止服务
docker-compose down

# 查看服务状态
docker-compose ps

# 查看服务日志
docker-compose logs
```

### 1.3 使用场景

- **本地开发环境**：快速搭建和隔离开发环境。
- **持续集成/持续部署**：在CI/CD流程中构建和部署应用。
- **微服务部署**：将不同服务打包为容器，实现独立部署和扩展。
- **环境一致性**：确保开发、测试和生产环境的一致性。

------

## 2. Kubernetes

### 2.1 基本操作

#### 部署应用
```bash
# 应用部署配置
kubectl apply -f <deployment-file.yaml>

# 查看部署状态
kubectl get deployments

# 查看pod状态
kubectl get pods

# 查看服务状态
kubectl get services
```

#### 资源管理
```bash
# 查看资源使用情况
kubectl top pod

# 查看节点状态
kubectl get nodes

# 查看集群信息
kubectl cluster-info
```

#### 配置管理
```bash
# 创建配置映射
kubectl create configmap <config-name> --from-file=<config-file>

# 创建密钥
kubectl create secret generic <secret-name> --from-literal=<key>=<value>

# 查看配置映射
kubectl get configmaps

# 查看密钥
kubectl get secrets
```

### 2.2 部署配置示例

#### Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: llm-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: llm-api
  template:
    metadata:
      labels:
        app: llm-api
    spec:
      containers:
      - name: llm-api
        image: llm-api:latest
        ports:
        - containerPort: 8000
        resources:
          limits:
            cpu: "1"
            memory: "2Gi"
          requests:
            cpu: "500m"
            memory: "1Gi"
        env:
        - name: MODEL_NAME
          value: "llama2"
        - name: API_KEY
          valueFrom:
            secretKeyRef:
              name: api-secrets
              key: openai-api-key
```

#### Service
```yaml
apiVersion: v1
kind: Service
metadata:
  name: llm-api-service
spec:
  selector:
    app: llm-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

#### Horizontal Pod Autoscaler
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: llm-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: llm-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### 2.3 使用场景

- **大规模应用部署**：管理和编排多个容器。
- **自动扩缩容**：根据负载自动调整实例数量。
- **高可用部署**：通过副本集确保服务可用性。
- **服务发现与负载均衡**：自动发现服务并分发请求。

------

## 3. FastAPI

### 3.1 基本使用

#### 安装
```bash
pip install fastapi uvicorn
```

#### 基本API
```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}

# 运行服务
# uvicorn main:app --host 0.0.0.0 --port 8000
```

#### 异步API
```python
from fastapi import FastAPI
import asyncio

app = FastAPI()

@app.get("/async")
async def async_endpoint():
    await asyncio.sleep(1)
    return {"message": "Async response"}
```

#### 流式输出
```python
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
import asyncio

app = FastAPI()

async def generate_response():
    for i in range(5):
        await asyncio.sleep(1)
        yield f"Message {i}\n"

@app.get("/stream")
def stream_response():
    return StreamingResponse(generate_response(), media_type="text/plain")
```

### 3.2 请求与响应模型

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    description: str = None
    price: float
    tax: float = None

@app.post("/items/")
def create_item(item: Item):
    return {"item": item}
```

### 3.3 使用场景

- **AI API服务**：提供模型推理、向量搜索等API。
- **微服务**：构建轻量级微服务。
- **实时应用**：支持WebSocket和流式输出。
- **API文档**：自动生成OpenAPI文档。

------

## 4. Prometheus & Grafana

### 4.1 Prometheus 配置

#### 基本配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'llm-api'
    static_configs:
      - targets: ['llm-api:8000']

  - job_name: 'vector-db'
    static_configs:
      - targets: ['vector-db:19530']
```

#### 暴露指标
```python
from fastapi import FastAPI
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

app = FastAPI()

# 定义指标
REQUEST_COUNT = Counter('request_count', 'Total request count')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency')

@app.middleware("http")
async def metrics_middleware(request, call_next):
    REQUEST_COUNT.inc()
    with REQUEST_LATENCY.time():
        response = await call_next(request)
    return response

@app.get("/metrics")
def metrics():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )
```

### 4.2 Grafana 配置

#### 数据源配置
- **类型**：Prometheus
- **URL**：http://prometheus:9090
- **Access**：Server

#### 面板配置
- **面板类型**：Graph、Gauge、Heatmap等
- **查询**：PromQL查询语句，如 `rate(request_count[5m])`
- **警报**：设置阈值和告警规则

### 4.3 使用场景

- **系统监控**：监控服务器CPU、内存、磁盘等指标。
- **应用监控**：监控API响应时间、错误率等指标。
- **AI服务监控**：监控模型推理时间、token使用量等指标。
- **告警**：当指标超过阈值时发送告警。

------

## 5. ELK Stack

### 5.1 基本配置

#### Docker Compose配置
```yaml
version: '3'
services:
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:7.17.0
    environment:
      - discovery.type=single-node
    ports:
      - "9200:9200"
  logstash:
    image: docker.elastic.co/logstash/logstash:7.17.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"
  kibana:
    image: docker.elastic.co/kibana/kibana:7.17.0
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
```

#### Logstash配置
```conf
# logstash.conf
input {
  beats {
    port => 5044
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:loglevel} %{GREEDYDATA:message}" }
  }
}

output {
  elasticsearch {
    hosts => ["elasticsearch:9200"]
    index => "logs-%{+YYYY.MM.dd}"
  }
}
```

### 5.2 日志收集

#### 使用Filebeat
```yaml
# filebeat.yml
filebeat.inputs:
- type: log
  paths:
    - /var/log/app/*.log

output.logstash:
  hosts: ["logstash:5044"]
```

#### Python日志集成
```python
import logging
from elasticsearch import Elasticsearch
from elastichsearch_logger import ElasticsearchHandler

# 配置日志
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# 连接Elasticsearch
es = Elasticsearch(["http://elasticsearch:9200"])

# 添加Elasticsearch处理器
handler = ElasticsearchHandler(
    es_client=es,
    index_name="app-logs"
)
logger.addHandler(handler)

# 记录日志
logger.info("Application started")
logger.error("An error occurred", exc_info=True)
```

### 5.3 使用场景

- **日志收集**：集中收集和管理应用日志。
- **日志分析**：通过Kibana分析和可视化日志。
- **故障排查**：快速定位和解决问题。
- **安全审计**：记录和分析安全相关事件。

------

## 6. 云服务部署

### 6.1 AWS

#### EC2部署
```bash
# 启动EC2实例
aws ec2 run-instances \
    --image-id ami-0c55b159cbfafe1f0 \
    --instance-type t2.micro \
    --key-name MyKeyPair \
    --security-group-ids sg-0abcdef1234567890 \
    --subnet-id subnet-0abcdef1234567890

# 连接EC2实例
ssh -i MyKeyPair.pem ec2-user@ec2-198-51-100-1.compute-1.amazonaws.com
```

#### Lambda部署
```python
# lambda_function.py
import json

def lambda_handler(event, context):
    # 处理请求
    body = json.loads(event['body'])
    # 调用模型
    result = process_request(body)
    # 返回响应
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

#### SageMaker部署
```python
import boto3
from sagemaker.pytorch import PyTorchModel

# 创建SageMaker模型
model = PyTorchModel(
    model_data='s3://my-bucket/model.tar.gz',
    role='arn:aws:iam::123456789012:role/SageMakerRole',
    framework_version='1.12.0',
    entry_point='inference.py'
)

# 部署模型
predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large'
)

# 测试模型
result = predictor.predict({'input': 'Hello world'})
print(result)
```

### 6.2 Azure

#### VM部署
```bash
# 创建VM
az vm create \
    --resource-group myResourceGroup \
    --name myVM \
    --image UbuntuLTS \
    --admin-username azureuser \
    --generate-ssh-keys

# 连接VM
ssh azureuser@public-ip-address
```

#### Functions部署
```python
# __init__.py
import azure.functions as func
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    # 处理请求
    body = req.get_json()
    # 调用模型
    result = process_request(body)
    # 返回响应
    return func.HttpResponse(
        json.dumps(result),
        mimetype="application/json"
    )
```

#### Azure ML部署
```python
from azureml.core import Workspace
from azureml.core.model import Model
from azureml.core.webservice import AciWebservice, Webservice

# 加载工作区
ws = Workspace.from_config()

# 注册模型
model = Model.register(
    workspace=ws,
    model_path="./model",
    model_name="llm-model"
)

# 部署配置
aciconfig = AciWebservice.deploy_configuration(
    cpu_cores=1,
    memory_gb=2,
    tags={"model": "llm"},
    description="LLM inference service"
)

# 部署模型
service = Model.deploy(
    workspace=ws,
    name="llm-service",
    models=[model],
    inference_config=inference_config,
    deployment_config=aciconfig
)

service.wait_for_deployment(show_output=True)
```

### 6.3 使用场景

- **弹性计算**：根据需求自动调整计算资源。
- **托管服务**：使用云提供商的托管服务，如SageMaker、Azure ML等。
- **全球部署**：在多个区域部署服务，提高可用性和降低延迟。
- **成本优化**：使用按需付费和预留实例等定价模式。

------

## 7. 模型优化工具

### 7.1 ONNX Runtime

#### 安装
```bash
pip install onnxruntime
```

#### 使用
```python
import onnxruntime as rt
import numpy as np

# 加载模型
session = rt.InferenceSession("model.onnx")

# 获取输入和输出名称
input_name = session.get_inputs()[0].name
output_name = session.get_outputs()[0].name

# 准备输入数据
input_data = np.random.random((1, 1536)).astype(np.float32)

# 推理
output = session.run([output_name], {input_name: input_data})
print(output)
```

### 7.2 TensorRT

#### 安装
```bash
pip install tensorrt
```

#### 使用
```python
import tensorrt as trt
import numpy as np

# 创建TensorRT引擎
logger = trt.Logger(trt.Logger.WARNING)
builder = trt.Builder(logger)
network = builder.create_network()

# 解析ONNX模型
parser = trt.OnnxParser(network, logger)
with open("model.onnx", "rb") as f:
    parser.parse(f.read())

# 构建引擎
config = builder.create_builder_config()
config.max_workspace_size = 1 << 30  # 1GB
engine = builder.build_engine(network, config)

# 创建执行上下文
context = engine.create_execution_context()

# 准备输入输出缓冲区
host_inputs = []
host_outputs = []
device_inputs = []
device_outputs = []

for binding in range(engine.num_bindings):
    size = trt.volume(engine.get_binding_shape(binding)) * engine.max_batch_size * np.dtype(np.float32).itemsize
    device_mem = cuda.mem_alloc(size)
    host_mem = np.zeros(size, dtype=np.float32)
    if engine.binding_is_input(binding):
        host_inputs.append(host_mem)
        device_inputs.append(device_mem)
    else:
        host_outputs.append(host_mem)
        device_outputs.append(device_mem)

# 推理
cuda.memcpy_htod(device_inputs[0], input_data)
context.execute_v2(device_inputs)
cuda.memcpy_dtoh(host_outputs[0], device_outputs[0])
print(host_outputs[0])
```

### 7.3 使用场景

- **模型推理加速**：提高模型推理速度，降低延迟。
- **资源优化**：减少模型内存使用，适合边缘设备。
- **部署优化**：简化模型部署，提高兼容性。

------

## 8. 最佳实践

### 8.1 部署最佳实践

- **使用容器化**：使用Docker容器化应用，确保环境一致性。
- **自动化部署**：使用CI/CD工具实现自动化部署。
- **监控先行**：在部署前设置好监控系统。
- **灰度发布**：逐步将流量切换到新服务。
- **备份与恢复**：定期备份数据和配置，准备回滚方案。

### 8.2 监控最佳实践

- **全面监控**：监控系统、应用和业务指标。
- **设置合理的告警阈值**：避免过多的误告警。
- **可视化**：使用Grafana等工具可视化监控数据。
- **日志管理**：集中管理和分析日志。
- **性能分析**：定期分析性能瓶颈，优化系统。

### 8.3 安全最佳实践

- **使用HTTPS**：加密传输数据。
- **认证授权**：实现API密钥、OAuth2等认证机制。
- **最小权限原则**：只授予必要的权限。
- **定期安全审计**：检查系统安全状况。
- **漏洞扫描**：定期扫描系统漏洞。

### 8.4 成本优化最佳实践

- **资源管理**：合理分配资源，避免资源浪费。
- **自动扩缩容**：根据流量自动调整资源。
- **缓存策略**：缓存常用请求的结果。
- **批处理**：批量处理请求，提高效率。
- **选择合适的云服务**：根据需求选择合适的云服务和计费方式。

------

## 9. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 服务启动失败 | 端口被占用 | 检查并释放占用的端口 |
|  | 依赖缺失 | 确保所有依赖都已安装 |
|  | 配置错误 | 检查配置文件和环境变量 |
| 服务响应慢 | 模型推理时间长 | 优化模型、使用缓存、增加计算资源 |
|  | 网络延迟高 | 使用CDN、选择就近的服务器 |
|  | 数据库查询慢 | 优化数据库查询、使用缓存 |
| 服务不稳定 | 资源不足 | 增加资源、使用自动扩缩容 |
|  | 代码bug | 完善错误处理、增加监控 |
|  | 依赖服务故障 | 实现服务降级和重试机制 |
| 成本过高 | 资源浪费 | 优化资源使用、使用自动扩缩容 |
|  | API调用过多 | 使用缓存、批处理 |
|  | 存储费用高 | 清理无用数据、使用适合的存储类型 |
| 安全问题 | 认证授权不当 | 加强认证授权、使用HTTPS |
|  | 数据泄露 | 加密敏感数据、限制数据访问 |
|  | 容器漏洞 | 使用安全的容器镜像，定期更新依赖 |

------

## 10. 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [ELK Stack 官方文档](https://www.elastic.co/guide/index.html)
- [AWS 官方文档](https://docs.aws.amazon.com/)
- [Azure 官方文档](https://docs.microsoft.com/en-us/azure/)
- [ONNX Runtime 官方文档](https://onnxruntime.ai/docs/)
- [TensorRT 官方文档](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html)
