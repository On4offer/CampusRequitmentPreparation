查看项目根目录结构，梳理整体框架。


[4 tools called]


继续查看关键文件以了解项目结构：


[6 tools called]


继续查看关键配置和结构：


[4 tools called]


查看一些关键的服务和工具类：


[3 tools called]


## 项目概述

基于 Spring Boot 2.3.7 的 HIS（医院信息系统）API 后端，采用 Java 8，支持多数据源、JPA 与 MyBatis 双 ORM、JWT 认证等。

## 技术栈

### 核心框架
- Spring Boot 2.3.7.RELEASE
- Spring Data JPA
- MyBatis 2.1.2
- Spring Web MVC

### 数据库与连接池
- MySQL（多数据源）
- Druid 1.1.6
- JPA/Hibernate

### 缓存与消息
- Redis（Redisson 3.6.5）
- Spring Data Redis

### 认证与安全
- JWT（io.jsonwebtoken 0.9.1、java-jwt 3.4.0）
- BouncyCastle（加密）

### 工具库
- Lombok
- FastJSON 1.2.44
- Hutool 5.1.1
- Apache Commons（fileupload、codec、io、lang3、httpclient、net）
- Google ZXing（二维码）

### 文档与模板
- FreeMarker
- iText PDF（PDF 生成）
- JFreeChart（图表）
- Apache POI / EasyExcel（Excel）

### 其他
- Apache CXF（WebService）
- Spring Mail
- Spring Validation

## 项目结构

```
cnbwx/
├── config/              # 配置类
│   ├── db/             # 多数据源配置
│   ├── exception/      # 全局异常处理
│   └── filter/         # 过滤器配置
├── constant/           # 常量定义
├── domain/             # 领域模型层
│   ├── datasource/     # 多数据源Mapper（MyBatis）
│   ├── dto/            # 数据传输对象
│   └── model/          # 实体模型
├── dto/                # 通用DTO
├── exception/          # 异常定义
├── intranet/           # 内网API控制器（49个Controller）
├── manager/            # 管理端控制器
├── model/              # JPA实体模型（109个）
├── redis/              # Redis配置和工具
├── repository/         # JPA数据访问层（59个Repository）
├── service/            # 业务逻辑层（174个Service）
│   ├── his/           # HIS业务服务接口和实现
│   ├── impl/          # 服务实现类
│   ├── external/      # 外部服务集成
│   ├── mail/          # 邮件服务
│   ├── yesskin/       # YesSkin相关服务
│   └── ywy/           # YWY相关服务
├── task/               # 定时任务
├── util/               # 工具类（36个）
├── vo/                 # 视图对象
└── zhongxinUtil/       # 中信银行工具类
```

## 核心架构设计

### 1. 多数据源配置

项目支持多个数据源：

```12:37:src/main/java/cnbwx/config/db/DataSourcesConfig.java
@Configuration
public class DataSourcesConfig {
    @Primary
    @Bean(name = "primaryDataSource")
    @Qualifier("primaryDataSource")
    @ConfigurationProperties(prefix="olddatasource.primary")
    public DataSource yunYaHisDataSource() {
        System.out.println("yunyahis db built");
        return DataSourceBuilder.create().build();
    }
```

支持的数据源：
- yunyahis（云雅HIS，主数据源）
- yesskinhis（YesSkin HIS）
- yesskinmagicbox（YesSkin魔盒）
- yesskinywy（YesSkin YWY）
- cskin（CSkin）

### 2. 双 ORM 架构

- JPA/Hibernate：主数据源，用于核心业务实体（`cnbwx.model`、`cnbwx.repository`）
- MyBatis：多数据源，用于复杂查询和报表（`cnbwx.domain.datasource.*`）

```29:32:src/main/java/cnbwx/HisApplication.java
@MapperScan(basePackages = {"cnbwx.domain.datasource.yesskinhis.mapper", "cnbwx.domain.datasource.yunyahis.mapper", "cnbwx.domain.datasource.yesskinmagicbox.mapper"})
public class HisApplication extends SpringBootServletInitializer {
```

### 3. 控制器层设计

采用继承基类的方式统一管理：

```25:31:src/main/java/cnbwx/intranet/InformedConsentController.java
public class InformedConsentController extends BaseAdminController<TblInformedConsent> {

    @Autowired
    public void setService(InformedConsentService service) {
        this.service = service;
        this.isOpenInterface(true, true, true, true, true);
    }
```

`BaseAdminController` 提供：
- CRUD（save、update、delete、deletes、show）
- 分页（pageNumber、pageSize）
- 排序（sort、order）
- JWT 认证
- 接口权限控制（isAdd、isUpdate、isDelete 等）

### 4. 认证与授权

- JWT Token：请求头 `Constants.TokenName`
- Token 解析：`JwtHisUtil` 解析用户信息（ClinicId、EmpId、Compid、roleids 等）
- 权限控制：基于角色和接口开关

```41:50:src/main/java/cnbwx/intranet/InformedConsentController.java
        String token = request.getHeader(Constants.TokenName);
        if (token == null || token.equals("null") || token.equals("")) {
            r.setApiErrDesc(ApiErrDesc.ERR_TOKEN);
            return r;
        }
        String ClinicId = JwtHisUtil.getVal(token, Constants.yunya_encryKey, "ClinicId");
        String EmpId = JwtHisUtil.getVal(token, Constants.yunya_encryKey, "EmpId");
        String Compid = JwtHisUtil.getVal(token, Constants.yunya_encryKey, "Compid");
        boolean IsGeneral = JwtHisUtil.getBoolVal(token, Constants.yunya_encryKey, "IsGeneral");
        String roleids = JwtHisUtil.getVal(token, Constants.yunya_encryKey, "roleids");
```

### 5. 环境配置

多环境配置文件：
- `application.yml`（主配置，激活 test）
- `application-test.yml`
- `application-dev.yml`
- `application-pro.yml`
- `application-yunya.yml`
- `application-yanxing.yml`
- `application-sh.yml`
- `application-build.yml`

### 6. 定时任务

```15:16:src/main/java/cnbwx/HisApplication.java
@EnableJpaAuditing
@EnableScheduling
```

定时任务：
- `CommonTask.java`：通用定时任务
- `CacheDataDailyRefreshTask.java`：缓存数据每日刷新
- `CacheDataSyncTask.java`：缓存数据同步

### 7. 异常处理

全局异常处理：

```1:3:src/main/java/cnbwx/exception/ExceptionHandlerAdvice.java
```

异常类型：
- `CnbwxException`：自定义业务异常
- `CommonException`：通用异常
- `GlobalExceptionHandler`：全局异常处理器

### 8. 业务模块

主要业务模块（`intranet` 包下 49 个 Controller）：
- 客户管理（CustomerController）
- 预约管理（AppointmentsController、PendingAppointmentsController）
- 处方管理（PrescriptionsController、PendingPrescriptionsController）
- 库存管理（RepertoryController、RepertoryenterController、RepertoryoutController）
- 账单管理（BillsController、PaybooksController）
- 员工管理（EmployeesController）
- 诊所管理（ClinicsController）
- 商品管理（GoodsController）
- 报告管理（ReportController、FaceReportController）
- 知情同意（InformedConsentController）
- 退款管理（RefundsController、ZhongxinRefundController）
- 其他业务模块

### 9. 工具类

`util` 包提供：
- 日期工具（DateUtils、DateZoneUtil）
- Excel 工具（ExcelUtils、EasyExcel）
- 文件工具（file 包）
- HTTP 工具（HttpSMSUtil）
- 加密工具（rsa 包）
- 微信工具（WeixinUtil、WeixinVo）
- 图表工具（jfreechart 包）
- 其他工具

### 10. 数据访问层

- Repository（JPA）：59 个，继承 JPA Repository
- Mapper（MyBatis）：多数据源，133 个 XML 映射文件，128 个 Mapper 接口

## 特色功能

1. 多数据源：支持多个 HIS 系统数据源
2. 双 ORM：JPA 与 MyBatis 并存
3. 统一基类：控制器统一继承 `BaseAdminController`
4. JWT 认证：基于 Token 的认证
5. 接口权限控制：可配置接口开关
6. 定时任务：支持定时数据同步和缓存刷新
7. 文件上传：支持大文件上传（最大 100MB）
8. PDF 生成：支持报告和文档生成
9. Excel 导入导出：支持 Excel 处理
10. 微信集成：支持微信相关功能

## 部署方式

支持两种部署：
1. JAR：Spring Boot 内嵌 Tomcat
2. WAR：可部署到外部 Tomcat（继承 `SpringBootServletInitializer`）

这是一个功能完整的医院信息系统 API 后端，采用分层架构，支持多数据源和多种业务场景。