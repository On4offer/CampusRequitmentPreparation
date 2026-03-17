# 📘《模型服务与部署常用 API 与使用场景》

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
  name: model-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: model-service
  template:
    metadata:
      labels:
        app: model-service
    spec:
      containers:
      - name: model-service
        image: model-service:latest
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
  name: model-service

spec:
  selector:
    app: model-service
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
  name: model-service-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: model-service
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

- **模型API服务**：提供模型推理API。
- **微服务**：构建轻量级微服务。
- **实时应用**：支持WebSocket和流式输出。
- **API文档**：自动生成OpenAPI文档。

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

## 5. ONNX Runtime

### 5.1 基本使用

#### 安装
```bash
pip install onnxruntime
```

#### 加载和推理
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

### 5.2 使用场景

- **跨平台推理**：在不同平台上运行模型。
- **性能优化**：提高模型推理速度。
- **模型部署**：将模型部署到生产环境。

------

## 6. TensorRT

### 6.1 基本使用

#### 安装
```bash
pip install tensorrt
```

#### 加载和推理
```python
import tensorrt as trt
import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit

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
input_data = np.random.random((1, 1536)).astype(np.float32)
np.copyto(host_inputs[0], input_data.ravel())
cuda.memcpy_htod(device_inputs[0], host_inputs[0])
context.execute_v2(device_inputs)
cuda.memcpy_dtoh(host_outputs[0], device_outputs[0])
print(host_outputs[0])
```

### 6.2 使用场景

- **高性能推理**：在NVIDIA GPU上实现最高性能。
- **生产部署**：将模型部署到生产环境。
- **边缘设备**：在边缘设备上部署模型。

------

## 7. 云服务部署

### 7.1 AWS SageMaker

#### 部署模型
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

### 7.2 Azure ML

#### 部署模型
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

### 7.3 GCP Vertex AI

#### 部署模型
```python
from google.cloud import aiplatform

# 初始化Vertex AI
aiplatform.init(project="my-project", location="us-central1")

# 上传模型
model = aiplatform.Model.upload(
    display_name="llm-model",
    artifact_uri="gs://my-bucket/model",
    serving_container_image_uri="us-docker.pkg.dev/vertex-ai/prediction/pytorch-cpu.1-12:latest"
)

# 部署模型
endpoint = model.deploy(
    machine_type="n1-standard-4",
    min_replica_count=1,
    max_replica_count=3
)

# 测试模型
response = endpoint.predict([{"input": "Hello world"}])
print(response)
```

### 7.4 使用场景

- **弹性计算**：根据需求自动调整计算资源。
- **托管服务**：使用云提供商的托管服务，简化部署和管理。
- **全球部署**：在多个区域部署服务，提高可用性和降低延迟。
- **成本优化**：使用按需付费和预留实例等定价模式。

------

## 8. 监控工具

### 8.1 Prometheus

#### 基本配置
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'model-service'
    static_configs:
      - targets: ['model-service:8000']

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

### 8.2 Grafana

#### 数据源配置
- **类型**：Prometheus
- **URL**：http://prometheus:9090
- **Access**：Server

#### 面板配置
- **面板类型**：Graph、Gauge、Heatmap等
- **查询**：PromQL查询语句，如 `rate(request_count[5m])`
- **警报**：设置阈值和告警规则

### 8.3 使用场景

- **系统监控**：监控服务器CPU、内存、磁盘等指标。
- **应用监控**：监控API响应时间、错误率等指标。
- **模型监控**：监控模型推理时间、token使用量等指标。
- **告警**：当指标超过阈值时发送告警。

------

## 9. CI/CD工具

### 9.1 GitHub Actions

#### 基本配置
```yaml
# .github/workflows/deploy.yml
name: Deploy Model Service

on:
  push:
    branches:
      - main

jobs:
  build-and-deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1
      
      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: ${{ secrets.DOCKER_HUB_USERNAME }}
          password: ${{ secrets.DOCKER_HUB_TOKEN }}
      
      - name: Build and push
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: ${{ secrets.DOCKER_HUB_USERNAME }}/model-service:latest
      
      - name: Deploy to Kubernetes
        uses: azure/k8s-deploy@v1
        with:
          namespace: default
          manifests: k8s/deployment.yaml
          images: |
            ${{ secrets.DOCKER_HUB_USERNAME }}/model-service:latest
          kubectl-version: 'latest'
```

### 9.2 Jenkins

#### 基本配置
```groovy
// Jenkinsfile
pipeline {
    agent any
    
    stages {
        stage('Build') {
            steps {
                sh 'docker build -t model-service .'
            }
        }
        
        stage('Test') {
            steps {
                sh 'docker run model-service pytest'
            }
        }
        
        stage('Deploy') {
            steps {
                sh 'docker push model-service:latest'
                sh 'kubectl apply -f k8s/deployment.yaml'
            }
        }
    }
}
```

### 9.3 使用场景

- **自动化部署**：实现代码提交后自动构建、测试和部署。
- **持续集成**：确保代码质量，及早发现问题。
- **持续部署**：快速将代码部署到生产环境。
- **版本管理**：管理不同版本的部署。

------

## 10. 最佳实践

### 10.1 部署最佳实践

- **使用容器化**：使用Docker容器化应用，确保环境一致性。
- **自动化部署**：使用CI/CD工具实现自动化部署。
- **监控先行**：在部署前设置好监控系统。
- **灰度发布**：逐步将流量切换到新服务。
- **备份与恢复**：定期备份数据和配置，准备回滚方案。

### 10.2 性能优化

- **模型优化**：使用量化、压缩等技术优化模型。
- **批量处理**：批量处理多个请求，提高效率。
- **缓存策略**：缓存常用请求的结果，减少重复计算。
- **资源管理**：合理分配资源，避免资源浪费。
- **网络优化**：使用CDN、负载均衡等优化网络性能。

### 10.3 安全最佳实践

- **API安全**：使用HTTPS、API密钥、OAuth2等认证授权机制。
- **数据安全**：加密传输和存储敏感数据。
- **模型安全**：防止模型被恶意访问和滥用。
- **定期安全审计**：检查系统安全状况，发现和解决安全问题。
- **最小权限原则**：只授予必要的权限。

### 10.4 成本优化

- **资源管理**：合理分配资源，避免资源浪费。
- **自动扩缩容**：根据流量自动调整资源。
- **缓存策略**：缓存常用请求的结果，减少API调用。
- **批处理**：批量处理请求，提高效率。
- **选择合适的云服务**：根据需求选择合适的云服务和计费方式。

------

## 11. 常见问题与解决方案

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 服务启动失败 | 端口被占用 | 检查并释放占用的端口 |
|  | 依赖缺失 | 确保所有依赖都已安装 |
|  | 配置错误 | 检查配置文件和环境变量 |
| 服务响应慢 | 模型推理时间长 | 优化模型，使用缓存，增加计算资源 |
|  | 网络延迟高 | 使用CDN，选择就近的服务器 |
|  | 数据库查询慢 | 优化数据库查询，使用缓存 |
| 服务不稳定 | 资源不足 | 增加资源，使用自动扩缩容 |
|  | 代码bug | 完善错误处理，增加监控 |
|  | 依赖服务故障 | 实现服务降级和重试机制 |
| 成本过高 | 资源浪费 | 优化资源使用，使用自动扩缩容 |
|  | API调用过多 | 使用缓存，批处理 |
|  | 存储费用高 | 清理无用数据，使用适合的存储类型 |
| 安全问题 | 认证授权不当 | 加强认证授权，使用HTTPS |
|  | 数据泄露 | 加密敏感数据，限制数据访问 |
|  | 容器漏洞 | 使用安全的容器镜像，定期更新依赖 |

------

## 12. 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [Kubernetes 官方文档](https://kubernetes.io/docs/)
- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [vLLM 官方文档](https://vllm.readthedocs.io/en/latest/)
- [ONNX Runtime 官方文档](https://onnxruntime.ai/docs/)
- [TensorRT 官方文档](https://docs.nvidia.com/deeplearning/tensorrt/developer-guide/index.html)
- [AWS SageMaker 官方文档](https://docs.aws.amazon.com/sagemaker/)
- [Azure ML 官方文档](https://docs.microsoft.com/en-us/azure/machine-learning/)
- [GCP Vertex AI 官方文档](https://cloud.google.com/vertex-ai/docs)
- [Prometheus 官方文档](https://prometheus.io/docs/)
- [Grafana 官方文档](https://grafana.com/docs/)
- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [Jenkins 官方文档](https://www.jenkins.io/doc/)
