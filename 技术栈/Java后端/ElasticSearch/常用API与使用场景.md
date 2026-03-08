# 📋 Elasticsearch - 常用API与使用场景速查

> 日常开发Elasticsearch常用REST API、DSL查询、Java客户端与场景速查，配合《学习笔记.md》系统学习使用。

---

## 🚀 快速开始

### REST API基础格式

```bash
# 基本格式
curl -X <METHOD> "http://localhost:9200/<index>/<endpoint>" -H 'Content-Type: application/json' -d '<body>'

# 常用HTTP方法
GET     # 查询
POST    # 创建/搜索
PUT     # 更新（全量）
PATCH   # 更新（部分）
DELETE  # 删除
```

### 集群健康检查

```bash
# 查看集群健康状态
curl -X GET "localhost:9200/_cluster/health"

# 查看集群状态（详细）
curl -X GET "localhost:9200/_cluster/health?pretty"

# 查看所有节点
curl -X GET "localhost:9200/_cat/nodes?v"

# 查看所有索引
curl -X GET "localhost:9200/_cat/indices?v"

# 查看集群统计
curl -X GET "localhost:9200/_cluster/stats"
```

---

## 📚 索引操作

### 创建索引

```bash
# 创建简单索引
curl -X PUT "localhost:9200/products" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1
  }
}'

# 创建带Mapping的索引
curl -X PUT "localhost:9200/products" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 3,
    "number_of_replicas": 1,
    "analysis": {
      "analyzer": {
        "ik_smart": {
          "type": "custom",
          "tokenizer": "ik_smart"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "name": {
        "type": "text",
        "analyzer": "ik_smart",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ik_max_word"
      },
      "price": {
        "type": "float"
      },
      "stock": {
        "type": "integer"
      },
      "category": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "create_time": {
        "type": "date",
        "format": "yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||epoch_millis"
      },
      "is_on_sale": {
        "type": "boolean"
      },
      "location": {
        "type": "geo_point"
      }
    }
  }
}'
```

### 查看索引

```bash
# 查看索引设置
curl -X GET "localhost:9200/products/_settings"

# 查看索引Mapping
curl -X GET "localhost:9200/products/_mapping"

# 查看索引统计
curl -X GET "localhost:9200/products/_stats"

# 判断索引是否存在
curl -X HEAD "localhost:9200/products"
```

### 修改索引

```bash
# 修改副本数
curl -X PUT "localhost:9200/products/_settings" -H 'Content-Type: application/json' -d'
{
  "number_of_replicas": 2
}'

# 添加字段（只能添加，不能修改或删除）
curl -X PUT "localhost:9200/products/_mapping" -H 'Content-Type: application/json' -d'
{
  "properties": {
    "brand": {
      "type": "keyword"
    }
  }
}'
```

### 删除索引

```bash
# 删除单个索引
curl -X DELETE "localhost:9200/products"

# 删除多个索引
curl -X DELETE "localhost:9200/products,orders"

# 删除所有索引（危险！）
curl -X DELETE "localhost:9200/_all"
```

---

## 📝 文档操作

### 添加文档

```bash
# 指定ID添加
curl -X PUT "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d'
{
  "name": "iPhone 15 Pro",
  "description": "苹果最新旗舰手机",
  "price": 7999.00,
  "stock": 100,
  "category": "手机",
  "tags": ["苹果", "5G", "旗舰"],
  "create_time": "2024-01-15 10:30:00",
  "is_on_sale": true
}'

# 自动生成ID
curl -X POST "localhost:9200/products/_doc" -H 'Content-Type: application/json' -d'
{
  "name": "MacBook Pro",
  "price": 14999.00
}'

# 批量添加（_bulk）
curl -X POST "localhost:9200/products/_bulk" -H 'Content-Type: application/json' -d'
{ "index": { "_id": "2" } }
{ "name": "iPad Air", "price": 4999.00, "category": "平板" }
{ "index": { "_id": "3" } }
{ "name": "AirPods Pro", "price": 1999.00, "category": "耳机" }
{ "index": { "_id": "4" } }
{ "name": "Apple Watch", "price": 2999.00, "category": "手表" }
'
```

### 查询文档

```bash
# 根据ID查询
curl -X GET "localhost:9200/products/_doc/1"

# 批量查询（_mget）
curl -X GET "localhost:9200/products/_mget" -H 'Content-Type: application/json' -d'
{
  "ids": ["1", "2", "3"]
}'

# 判断文档是否存在
curl -X HEAD "localhost:9200/products/_doc/1"
```

### 更新文档

```bash
# 全量更新（替换）
curl -X PUT "localhost:9200/products/_doc/1" -H 'Content-Type: application/json' -d'
{
  "name": "iPhone 15 Pro Max",
  "price": 9999.00
}'

# 部分更新（_update）
curl -X POST "localhost:9200/products/_update/1" -H 'Content-Type: application/json' -d'
{
  "doc": {
    "price": 7499.00,
    "stock": 50
  }
}'

# 使用脚本更新
curl -X POST "localhost:9200/products/_update/1" -H 'Content-Type: application/json' -d'
{
  "script": {
    "source": "ctx._source.stock += params.quantity",
    "lang": "painless",
    "params": {
      "quantity": 10
    }
  }
}'
```

### 删除文档

```bash
# 根据ID删除
curl -X DELETE "localhost:9200/products/_doc/1"

# 条件删除（_delete_by_query）
curl -X POST "localhost:9200/products/_delete_by_query" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "category": "停产"
    }
  }
}'
```

---

## 🔍 搜索DSL

### 基础查询

```bash
# 搜索所有
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_all": {}
  }
}'

# 分页
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "from": 0,
  "size": 10,
  "query": {
    "match_all": {}
  }
}'

# 指定返回字段
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "_source": ["name", "price", "category"],
  "query": {
    "match_all": {}
  }
}'

# 排序
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "sort": [
    { "price": "asc" },
    { "create_time": "desc" }
  ]
}'
```

### 全文搜索

```bash
# match查询（分词）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "name": "苹果手机"
    }
  }
}'

# multi_match查询（多字段）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "multi_match": {
      "query": "苹果",
      "fields": ["name^3", "description"],
      "type": "best_fields"
    }
  }
}'

# match_phrase查询（短语匹配）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match_phrase": {
      "description": "最新旗舰"
    }
  }
}'

# query_string查询（支持Lucene语法）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "query_string": {
      "query": "name:苹果 AND price:[5000 TO 10000]"
    }
  }
}'
```

### 精确查询

```bash
# term查询（精确匹配）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "term": {
      "category": "手机"
    }
  }
}'

# terms查询（多值匹配）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "terms": {
      "category": ["手机", "平板"]
    }
  }
}'

# range查询（范围）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "range": {
      "price": {
        "gte": 1000,
        "lte": 5000
      }
    }
  }
}'

# exists查询（字段存在）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "exists": {
      "field": "description"
    }
  }
}'
```

### 复合查询

```bash
# bool查询（must/should/must_not/filter）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "must": [
        { "match": { "name": "苹果" } },
        { "range": { "price": { "lte": 8000 } } }
      ],
      "filter": [
        { "term": { "is_on_sale": true } },
        { "range": { "stock": { "gt": 0 } } }
      ]
    }
  }
}'

# should查询（或关系，可指定minimum_should_match）
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "bool": {
      "should": [
        { "match": { "name": "苹果" } },
        { "match": { "name": "华为" } },
        { "match": { "name": "小米" } }
      ],
      "minimum_should_match": 1
    }
  }
}'
```

### 聚合查询

```bash
# 指标聚合：平均值
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "aggs": {
    "avg_price": {
      "avg": {
        "field": "price"
      }
    }
  }
}'

# 桶聚合：按类别分组统计
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": {
        "field": "category"
      }
    }
  }
}'

# 嵌套聚合
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "by_category": {
      "terms": {
        "field": "category"
      },
      "aggs": {
        "avg_price": {
          "avg": {
            "field": "price"
          }
        },
        "max_price": {
          "max": {
            "field": "price"
          }
        }
      }
    }
  }
}'

# 范围聚合
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "price_ranges": {
      "range": {
        "field": "price",
        "ranges": [
          { "to": 1000, "key": "under_1000" },
          { "from": 1000, "to": 5000, "key": "1000_to_5000" },
          { "from": 5000, "key": "over_5000" }
        ]
      }
    }
  }
}'

# 日期直方图聚合
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "size": 0,
  "aggs": {
    "sales_over_time": {
      "date_histogram": {
        "field": "create_time",
        "calendar_interval": "month",
        "format": "yyyy-MM"
      }
    }
  }
}'
```

### 高亮搜索

```bash
curl -X GET "localhost:9200/products/_search" -H 'Content-Type: application/json' -d'
{
  "query": {
    "match": {
      "name": "苹果"
    }
  },
  "highlight": {
    "fields": {
      "name": {
        "pre_tags": ["<em>"],
        "post_tags": ["</em>"]
      },
      "description": {}
    }
  }
}'
```

---

## ☕ Java客户端（RestHighLevelClient / Elasticsearch Java API Client）

### 客户端配置

```java
// RestHighLevelClient配置（7.x）
@Configuration
public class ElasticsearchConfig {
    
    @Bean
    public RestHighLevelClient elasticsearchClient() {
        RestClientBuilder builder = RestClient.builder(
            new HttpHost("localhost", 9200, "http")
        );
        
        builder.setRequestConfigCallback(requestConfigBuilder ->
            requestConfigBuilder
                .setConnectTimeout(5000)
                .setSocketTimeout(60000)
        );
        
        builder.setHttpClientConfigCallback(httpClientBuilder ->
            httpClientBuilder
                .setMaxConnTotal(100)
                .setMaxConnPerRoute(10)
        );
        
        return new RestHighLevelClient(builder);
    }
}

// Elasticsearch Java API Client（8.x推荐）
@Bean
public ElasticsearchClient elasticsearchClient() {
    RestClient restClient = RestClient.builder(
        new HttpHost("localhost", 9200)).build();
    
    ElasticsearchTransport transport = new RestClientTransport(
        restClient, new JacksonJsonpMapper());
    
    return new ElasticsearchClient(transport);
}
```

### 索引操作

```java
@Service
public class IndexService {
    
    @Autowired
    private RestHighLevelClient client;
    
    // 创建索引
    public boolean createIndex(String indexName) throws IOException {
        CreateIndexRequest request = new CreateIndexRequest(indexName);
        
        // 设置Settings
        request.settings(Settings.builder()
            .put("index.number_of_shards", 3)
            .put("index.number_of_replicas", 1)
        );
        
        // 设置Mapping
        XContentBuilder builder = XContentFactory.jsonBuilder();
        builder.startObject();
        {
            builder.startObject("properties");
            {
                builder.startObject("name");
                builder.field("type", "text");
                builder.field("analyzer", "ik_smart");
                builder.endObject();
                
                builder.startObject("price");
                builder.field("type", "float");
                builder.endObject();
                
                builder.startObject("category");
                builder.field("type", "keyword");
                builder.endObject();
            }
            builder.endObject();
        }
        builder.endObject();
        request.mapping(builder);
        
        CreateIndexResponse response = client.indices().create(request, RequestOptions.DEFAULT);
        return response.isAcknowledged();
    }
    
    // 删除索引
    public boolean deleteIndex(String indexName) throws IOException {
        DeleteIndexRequest request = new DeleteIndexRequest(indexName);
        AcknowledgedResponse response = client.indices().delete(request, RequestOptions.DEFAULT);
        return response.isAcknowledged();
    }
    
    // 判断索引是否存在
    public boolean indexExists(String indexName) throws IOException {
        GetIndexRequest request = new GetIndexRequest(indexName);
        return client.indices().exists(request, RequestOptions.DEFAULT);
    }
}
```

### 文档操作

```java
@Service
public class DocumentService {
    
    @Autowired
    private RestHighLevelClient client;
    
    // 添加/更新文档
    public IndexResponse saveDocument(String index, String id, Object document) throws IOException {
        IndexRequest request = new IndexRequest(index);
        request.id(id);
        request.source(JSON.toJSONString(document), XContentType.JSON);
        
        return client.index(request, RequestOptions.DEFAULT);
    }
    
    // 批量添加
    public BulkResponse bulkSave(String index, List<Product> products) throws IOException {
        BulkRequest request = new BulkRequest();
        
        for (Product product : products) {
            IndexRequest indexRequest = new IndexRequest(index)
                .id(product.getId())
                .source(JSON.toJSONString(product), XContentType.JSON);
            request.add(indexRequest);
        }
        
        return client.bulk(request, RequestOptions.DEFAULT);
    }
    
    // 根据ID查询
    public GetResponse getDocument(String index, String id) throws IOException {
        GetRequest request = new GetRequest(index, id);
        return client.get(request, RequestOptions.DEFAULT);
    }
    
    // 更新文档
    public UpdateResponse updateDocument(String index, String id, Map<String, Object> updates) throws IOException {
        UpdateRequest request = new UpdateRequest(index, id);
        request.doc(updates);
        return client.update(request, RequestOptions.DEFAULT);
    }
    
    // 删除文档
    public DeleteResponse deleteDocument(String index, String id) throws IOException {
        DeleteRequest request = new DeleteRequest(index, id);
        return client.delete(request, RequestOptions.DEFAULT);
    }
}
```

### 搜索操作

```java
@Service
public class SearchService {
    
    @Autowired
    private RestHighLevelClient client;
    
    // 简单搜索
    public SearchResponse search(String index, String keyword) throws IOException {
        SearchRequest request = new SearchRequest(index);
        
        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
        sourceBuilder.query(QueryBuilders.matchQuery("name", keyword));
        sourceBuilder.from(0);
        sourceBuilder.size(10);
        
        request.source(sourceBuilder);
        return client.search(request, RequestOptions.DEFAULT);
    }
    
    // 复合搜索
    public SearchResponse complexSearch(SearchParam param) throws IOException {
        SearchRequest request = new SearchRequest("products");
        
        BoolQueryBuilder boolQuery = QueryBuilders.boolQuery();
        
        // must条件
        if (StringUtils.isNotBlank(param.getKeyword())) {
            boolQuery.must(QueryBuilders.multiMatchQuery(param.getKeyword())
                .field("name", 3.0f)
                .field("description"));
        }
        
        // filter条件
        if (StringUtils.isNotBlank(param.getCategory())) {
            boolQuery.filter(QueryBuilders.termQuery("category", param.getCategory()));
        }
        
        if (param.getMinPrice() != null || param.getMaxPrice() != null) {
            RangeQueryBuilder rangeQuery = QueryBuilders.rangeQuery("price");
            if (param.getMinPrice() != null) {
                rangeQuery.gte(param.getMinPrice());
            }
            if (param.getMaxPrice() != null) {
                rangeQuery.lte(param.getMaxPrice());
            }
            boolQuery.filter(rangeQuery);
        }
        
        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
        sourceBuilder.query(boolQuery);
        
        // 分页
        sourceBuilder.from((param.getPageNum() - 1) * param.getPageSize());
        sourceBuilder.size(param.getPageSize());
        
        // 排序
        if (StringUtils.isNotBlank(param.getSortField())) {
            sourceBuilder.sort(param.getSortField(), 
                "asc".equals(param.getSortOrder()) ? SortOrder.ASC : SortOrder.DESC);
        }
        
        // 高亮
        HighlightBuilder highlightBuilder = new HighlightBuilder();
        highlightBuilder.field("name");
        highlightBuilder.preTags("<em>");
        highlightBuilder.postTags("</em>");
        sourceBuilder.highlighter(highlightBuilder);
        
        // 聚合
        TermsAggregationBuilder categoryAgg = AggregationBuilders
            .terms("by_category")
            .field("category");
        sourceBuilder.aggregation(categoryAgg);
        
        request.source(sourceBuilder);
        return client.search(request, RequestOptions.DEFAULT);
    }
    
    // 处理搜索结果
    public List<Product> processSearchResponse(SearchResponse response) {
        List<Product> products = new ArrayList<>();
        
        for (SearchHit hit : response.getHits().getHits()) {
            Product product = JSON.parseObject(hit.getSourceAsString(), Product.class);
            
            // 处理高亮
            Map<String, HighlightField> highlightFields = hit.getHighlightFields();
            if (highlightFields.containsKey("name")) {
                String highlightedName = highlightFields.get("name").fragments()[0].string();
                product.setName(highlightedName);
            }
            
            products.add(product);
        }
        
        return products;
    }
}
```

---

## 🎯 常用代码场景

### 1. 商品搜索服务

```java
@Service
public class ProductSearchService {
    
    @Autowired
    private RestHighLevelClient client;
    
    public SearchResult<Product> searchProducts(ProductSearchParam param) {
        try {
            SearchRequest request = buildSearchRequest(param);
            SearchResponse response = client.search(request, RequestOptions.DEFAULT);
            return parseSearchResponse(response, param);
        } catch (IOException e) {
            log.error("Search failed", e);
            throw new SearchException("搜索失败");
        }
    }
    
    private SearchRequest buildSearchRequest(ProductSearchParam param) {
        SearchRequest request = new SearchRequest("products");
        SearchSourceBuilder sourceBuilder = new SearchSourceBuilder();
        
        BoolQueryBuilder boolQuery = QueryBuilders.boolQuery();
        
        // 关键词搜索
        if (StringUtils.isNotBlank(param.getKeyword())) {
            boolQuery.must(QueryBuilders.boolQuery()
                .should(QueryBuilders.matchQuery("name", param.getKeyword()).boost(3.0f))
                .should(QueryBuilders.matchQuery("description", param.getKeyword()))
                .should(QueryBuilders.matchQuery("brand", param.getKeyword()).boost(2.0f)));
        }
        
        // 分类过滤
        if (CollectionUtils.isNotEmpty(param.getCategories())) {
            boolQuery.filter(QueryBuilders.termsQuery("category", param.getCategories()));
        }
        
        // 品牌过滤
        if (CollectionUtils.isNotEmpty(param.getBrands())) {
            boolQuery.filter(QueryBuilders.termsQuery("brand", param.getBrands()));
        }
        
        // 价格范围
        if (param.getMinPrice() != null || param.getMaxPrice() != null) {
            RangeQueryBuilder rangeQuery = QueryBuilders.rangeQuery("price");
            if (param.getMinPrice() != null) rangeQuery.gte(param.getMinPrice());
            if (param.getMaxPrice() != null) rangeQuery.lte(param.getMaxPrice());
            boolQuery.filter(rangeQuery);
        }
        
        // 属性过滤（nested query）
        if (MapUtils.isNotEmpty(param.getAttributes())) {
            param.getAttributes().forEach((key, values) -> {
                BoolQueryBuilder attrBool = QueryBuilders.boolQuery();
                attrBool.must(QueryBuilders.termQuery("attributes.key", key));
                attrBool.must(QueryBuilders.termsQuery("attributes.value", values));
                boolQuery.filter(QueryBuilders.nestedQuery("attributes", attrBool, ScoreMode.None));
            });
        }
        
        // 库存过滤
        if (param.getInStock() != null && param.getInStock()) {
            boolQuery.filter(QueryBuilders.rangeQuery("stock").gt(0));
        }
        
        sourceBuilder.query(boolQuery);
        
        // 分页
        int from = (param.getPageNum() - 1) * param.getPageSize();
        sourceBuilder.from(from).size(param.getPageSize());
        
        // 排序
        if ("price_asc".equals(param.getSort())) {
            sourceBuilder.sort("price", SortOrder.ASC);
        } else if ("price_desc".equals(param.getSort())) {
            sourceBuilder.sort("price", SortOrder.DESC);
        } else if ("sales".equals(param.getSort())) {
            sourceBuilder.sort("sales", SortOrder.DESC);
        } else {
            sourceBuilder.sort("_score", SortOrder.DESC);
        }
        
        // 高亮
        HighlightBuilder highlight = new HighlightBuilder()
            .field("name", 100, 1)
            .preTags("<span class='highlight'>")
            .postTags("</span>");
        sourceBuilder.highlighter(highlight);
        
        // 聚合
        sourceBuilder.aggregation(AggregationBuilders.terms("categories").field("category"));
        sourceBuilder.aggregation(AggregationBuilders.terms("brands").field("brand"));
        sourceBuilder.aggregation(AggregationBuilders.range("price_ranges").field("price")
            .addRange(0, 1000)
            .addRange(1000, 5000)
            .addRange(5000, 10000)
            .addUnboundedFrom(10000));
        
        request.source(sourceBuilder);
        return request;
    }
}
```

### 2. 数据同步（MySQL到ES）

```java
@Component
@Slf4j
public class DataSyncService {
    
    @Autowired
    private ProductMapper productMapper;
    
    @Autowired
    private RestHighLevelClient esClient;
    
    // 全量同步
    public void fullSync() {
        log.info("Starting full sync...");
        
        int pageSize = 1000;
        int pageNum = 1;
        
        while (true) {
            PageHelper.startPage(pageNum, pageSize);
            List<Product> products = productMapper.selectAll();
            
            if (products.isEmpty()) {
                break;
            }
            
            bulkIndex(products);
            log.info("Synced page {} with {} products", pageNum, products.size());
            
            pageNum++;
        }
        
        log.info("Full sync completed");
    }
    
    // 增量同步（基于更新时间）
    public void incrementalSync(LocalDateTime lastSyncTime) {
        log.info("Starting incremental sync from {}", lastSyncTime);
        
        List<Product> products = productMapper.selectByUpdateTimeAfter(lastSyncTime);
        
        if (!products.isEmpty()) {
            bulkIndex(products);
            log.info("Incremental synced {} products", products.size());
        }
    }
    
    private void bulkIndex(List<Product> products) {
        BulkRequest bulkRequest = new BulkRequest();
        
        for (Product product : products) {
            IndexRequest indexRequest = new IndexRequest("products")
                .id(product.getId().toString())
                .source(JSON.toJSONString(product), XContentType.JSON);
            bulkRequest.add(indexRequest);
        }
        
        try {
            BulkResponse response = esClient.bulk(bulkRequest, RequestOptions.DEFAULT);
            if (response.hasFailures()) {
                log.error("Bulk index has failures: {}", response.buildFailureMessage());
            }
        } catch (IOException e) {
            log.error("Bulk index failed", e);
            throw new RuntimeException("数据同步失败");
        }
    }
}
```

---

## ⚠️ 常见坑点速查

| 坑点 | 说明 | 正确做法 |
|------|------|----------|
| 深度分页性能差 | from+size超过10000会报错 | 用scroll或search_after |
| 字段类型错误 | text类型不能用于排序和聚合 | 用fields定义keyword子字段 |
| 分词不匹配 | term查询text字段无结果 | text用match，keyword用term |
| 批量请求过大 | bulk一次提交太多数据 | 控制每批5-15MB |
| 映射冲突 | 同一字段不同类型 | 提前规划mapping，避免动态映射冲突 |
| 脑裂问题 | 网络分区导致多master | 配置discovery.zen.minimum_master_nodes |
| 刷新频率 | 默认1秒刷新，实时性要求高的场景 | 调整refresh_interval |
| 副本数设置 | 单节点设置副本会unassigned | 单节点时副本设为0 |

---

> 💡 **提示**：本文档用于日常速查，系统学习请查看《学习笔记.md》
