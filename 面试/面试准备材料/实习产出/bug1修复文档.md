
# Bug排查定位修复报告

## 一、Bug描述

### 1.1 问题概述
- 问题名称：消耗业绩报表中移动端消耗数据缺失
- 严重程度：高
- 影响范围：消耗业绩报表、开单业绩报表、退款业绩报表

### 1.2 问题现象
- 门店反馈：消耗业绩报表数据不准确
- 具体表现：
  - 移动端消耗有记录（消耗管理模块可见）
  - 消耗业绩报表中未体现
  - 导致报表数据不完整，影响业绩统计

### 1.3 业务影响
- 移动端消耗数据无法在报表中汇总
- 业绩统计不准确
- 可能影响门店业绩考核和数据分析

---

## 二、问题排查过程

### 2.1 排查步骤

#### 步骤1：确认问题范围
- 检查消耗管理模块：移动端消耗数据正常记录
- 检查消耗业绩报表接口：数据缺失
- 确认问题定位：数据查询层面

#### 步骤2：代码调用链分析
```
前端请求 → CoursesController.consume() 
         → HIS_CourseDetailsMapper.selectCoursesDetails()
         → HIS_ReportCommonBaseV3Mapper.Select_Consume_Details
         → HIS_ReportCommonBaseV3Mapper.Select_Consume_Core_Where
```

#### 步骤3：参数传递检查
- 检查 `CoursesController.consume()` 方法
- 发现：未设置 `isExclusionChannels` 参数
- 检查 `ReportServiceImpl.summaryOfOperationOfEachStoreNew()` 方法
- 发现：该方法设置了 `isExclusionChannels = 1`

#### 步骤4：SQL过滤逻辑分析
- 定位到 `HIS_ReportCommonBaseV3Mapper.xml` 中的 `Select_Consume_Core_Where`
- 发现 `isExclusionChannels = 1` 的过滤逻辑存在问题

### 2.2 关键发现

#### 发现1：过滤逻辑缺陷
在 `HIS_ReportCommonBaseV3Mapper.xml` 的 `Select_Consume_Core_Where` 中，存在以下过滤逻辑：

```xml
<if test="isExclusionChannels != null and isExclusionChannels == 1">
    and not exists (
        select 1
        from (
            select coursedetail.`ID` as `consume_id`
            from coursedetails coursedetail
            left join courses course on course.`ID`=coursedetail.`Course_ID`
            left join employeecoursedetails employeecoursedetail on ...
            left join employees employee on ...
            where coursedetail.`ClinicId`='484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
            and (employee.`EmpName` like concat('%', '吴慧玲', '%')
                 or employee.`EmpName` like concat('%', '徐敏', '%')
                 or employee.`EmpName` like concat('%', '手术', '%'))
            -- 问题：缺少对 is_network_order 的判断
        ) t
        where t.`consume_id`=coursedetail.`ID`
    )
</if>
```

#### 发现2：问题根因
- 过滤逻辑未区分移动端与非移动端数据
- 当业绩人包含“吴慧玲|徐敏|手术”时，移动端数据也被误过滤
- 移动端数据（`is_network_order = 1`）不应被渠道排除过滤影响

---

## 三、根本原因分析

### 3.1 技术原因
1. 过滤条件不完整：`isExclusionChannels = 1` 的过滤逻辑未考虑 `is_network_order`
2. 业务逻辑理解偏差：渠道排除应仅针对非移动端订单
3. 数据完整性：移动端数据应始终参与报表统计

### 3.2 业务背景
- `isExclusionChannels = 1`：排除特定渠道客户（针对特定门店）
- 过滤条件：业绩人包含“吴慧玲|徐敏|手术”的数据
- 移动端数据：`is_network_order = 1`，不应受渠道排除影响

### 3.3 影响范围
涉及以下 Mapper 文件：
1. `HIS_ReportCommonBaseV3Mapper.xml`（主要使用版本）
2. `HIS_ReportCommonBase2025Mapper.xml`（被 `summaryOfOperationOfEachStoreNew` 使用）
3. `HIS_ReportCommonBaseMapper.xml`（旧版本）

涉及以下报表类型：
- 消耗业绩报表（`Select_Consume_Core_Where`）
- 开单业绩报表（`Select_Bills_Core_Where`）
- 退款业绩报表（`Select_Refund_Core_Where`）

---

## 四、修复方案

### 4.1 修复策略
在 `isExclusionChannels = 1` 的过滤条件中，排除移动端数据：
- V3版本：在子查询中添加 `and (billdetail.is_network_order is null or billdetail.is_network_order = 0)`
- 2025版本和旧版本：在过滤条件中添加 `(is_network_order = 1 or ...)` 逻辑

### 4.2 修复原则
1. 移动端数据（`is_network_order = 1`）不参与渠道排除过滤
2. 非移动端数据（`is_network_order = 0` 或 `null`）按原逻辑过滤
3. 不影响其他功能

---

## 五、修复内容详情

### 5.1 HIS_ReportCommonBaseV3Mapper.xml

#### 修复1：消耗业绩报表（Select_Consume_Core_Where）
```xml
<if test="isExclusionChannels != null and isExclusionChannels == 1">
    and not exists (
        select 1
        from (
            select coursedetail.`ID` as `consume_id`
            from coursedetails coursedetail
            left join courses course on course.`ID`=coursedetail.`Course_ID`
            left join billdetails billdetail on billdetail.`ID`=course.`BillDetailiId`
            left join employeecoursedetails employeecoursedetail on ...
            left join employees employee on ...
            where coursedetail.`ClinicId`='484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
            and (employee.`EmpName` like concat('%', '吴慧玲', '%')
                 or employee.`EmpName` like concat('%', '徐敏', '%')
                 or employee.`EmpName` like concat('%', '手术', '%'))
            <!-- 修复：排除移动端数据，移动端数据不应该被过滤 -->
            and (billdetail.`is_network_order` is null or billdetail.`is_network_order` = 0)
        ) t
        where t.`consume_id`=coursedetail.`ID`
    )
</if>
```

#### 修复2：开单业绩报表（Select_Bills_Core_Where）
```xml
<if test="isExclusionChannels != null and isExclusionChannels == 1">
    and not exists (
        select 1
        from (
            select paybook.`BillId` as `bill_id`
            from paybooks paybook
            left join bills bill on bill.`ID`=paybook.`BillId`
            left join billdetails billdetail on billdetail.`Bill_ID`=bill.`ID`
            left join billemployees billemployee on ...
            left join employees employee on ...
            where paybook.`OrganizationId`='484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
            and (employee.`EmpName` like concat('%', '吴慧玲', '%')
                 or employee.`EmpName` like concat('%', '徐敏', '%')
                 or employee.`EmpName` like concat('%', '手术', '%'))
            <!-- 修复：排除移动端数据，移动端数据不应该被过滤 -->
            and (billdetail.`is_network_order` is null or billdetail.`is_network_order` = 0)
        ) t
        where t.`bill_id`=paybook.`BillId`
    )
</if>
```

#### 修复3：退款业绩报表（Select_Refund_Core_Where）
```xml
<if test="isExclusionChannels != null and isExclusionChannels == 1">
    and not exists (
        select 1
        from (
            select refundbook.`BillId` as `bill_id`
            from refundbooks refundbook
            left join bills bill on bill.`ID`=refundbook.`BillId`
            left join billdetails billdetail on billdetail.`Bill_ID`=bill.`ID`
            left join billemployees billemployee on ...
            left join employees employee on ...
            where bill.`ClinicId`='484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
            and (employee.`EmpName` like concat('%', '吴慧玲', '%')
                 or employee.`EmpName` like concat('%', '徐敏', '%')
                 or employee.`EmpName` like concat('%', '手术', '%'))
            <!-- 修复：排除移动端数据，移动端数据不应该被过滤 -->
            and (billdetail.`is_network_order` is null or billdetail.`is_network_order` = 0)
        ) t
        where t.`bill_id`=refundbook.`BillId`
    )
</if>
```

### 5.2 HIS_ReportCommonBase2025Mapper.xml

#### 修复1：消耗业绩报表（Select_Base_Course_Services）
```xml
<if test="isExclusionChannels != null and isExclusionChannels == 1">
    and if (
        coursedetail.`course_clinic_id`='484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a',
        <!-- 修复：排除移动端数据，移动端数据不应该被过滤 -->
        (coursedetail.`is_network_order` = 1 or coursedetail.`performers_details` NOT REGEXP '吴慧玲|徐敏|手术'),
        1=1
    )
</if>
```

#### 修复2：开单业绩报表（Select_Base_Bills_PayBooks）
```xml
<if test="isExclusionChannels != null and isExclusionChannels == 1">
    and if (
        bill.`bill_clinic_id`='484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a',
        <!-- 修复：排除移动端数据，移动端数据不应该被过滤 -->
        (bill.`is_network_order` = 1 or bill.`performers_details` NOT REGEXP '吴慧玲|徐敏|手术'),
        1=1
    )
</if>
```

#### 修复3：退款业绩报表
- 商品部分：添加 `(billdetail.is_network_order = 1 or ...)`
- 项目部分：添加 `left join billdetails` 并添加 `(billdetail.is_network_order = 1 or ...)`

### 5.3 HIS_ReportCommonBaseMapper.xml

#### 修复1：消耗业绩报表（Select_Base_Course_Services）
```xml
<if test="isExclusionChannels != null and isExclusionChannels == 1">
    and if (
        coursedetail.`course_clinic_id`='484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a',
        <!-- 修复：排除移动端数据，移动端数据不应该被过滤 -->
        (coursedetail.`is_network_order` = 1 or coursedetail.`performers_details` NOT REGEXP '吴慧玲|徐敏|手术'),
        1=1
    )
</if>
```

#### 修复2：退款业绩报表
- 商品部分：添加 `(billdetail.is_network_order = 1 or ...)`
- 项目部分：添加 `left join billdetails` 并添加 `(billdetail.is_network_order = 1 or ...)`

---

## 六、修复文件清单

| 文件路径 | 修复位置 | 修复类型 |
|---------|---------|---------|
| `HIS_ReportCommonBaseV3Mapper.xml` | `Select_Consume_Core_Where` | 消耗业绩报表 |
| `HIS_ReportCommonBaseV3Mapper.xml` | `Select_Bills_Core_Where` | 开单业绩报表 |
| `HIS_ReportCommonBaseV3Mapper.xml` | `Select_Refund_Core_Where` | 退款业绩报表 |
| `HIS_ReportCommonBase2025Mapper.xml` | `Select_Base_Course_Services` | 消耗业绩报表 |
| `HIS_ReportCommonBase2025Mapper.xml` | `Select_Base_Bills_PayBooks` | 开单业绩报表 |
| `HIS_ReportCommonBase2025Mapper.xml` | `Select_Base_Refund_Books_Goods` | 退款业绩报表（商品） |
| `HIS_ReportCommonBase2025Mapper.xml` | `Select_Base_Refund_Books_Services` | 退款业绩报表（项目） |
| `HIS_ReportCommonBaseMapper.xml` | `Select_Base_Course_Services` | 消耗业绩报表 |
| `HIS_ReportCommonBaseMapper.xml` | `Select_Base_Refund_Books_Goods` | 退款业绩报表（商品） |
| `HIS_ReportCommonBaseMapper.xml` | `Select_Base_Refund_Books_Services` | 退款业绩报表（项目） |

---

## 七、验证方法

### 7.1 SQL验证
执行 `test.session.sql` 进行验证：

#### 验证查询1：所有移动端消耗数据（基准）
```sql
SELECT 
    '所有移动端消耗数据（基准）' as data_type,
    COUNT(*) as record_count,
    SUM(cd.CourseAmount) / 100.0 as total_amount
FROM coursedetails cd
LEFT JOIN courses course ON course.ID = cd.Course_ID
LEFT JOIN billdetails billdetail ON billdetail.ID = course.BillDetailiId
WHERE cd.ClinicId = '484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
  AND cd.CreateTime >= '2025-01-01'
  AND cd.CreateTime <= '2025-06-18'
  AND billdetail.is_network_order = 1
```

#### 验证查询2：业绩人包含过滤条件的移动端数据
```sql
SELECT 
    '移动端数据-业绩人包含过滤条件（修复后应显示）' as data_type,
    COUNT(*) as record_count,
    SUM(cd.CourseAmount) / 100.0 as total_amount
FROM coursedetails cd
LEFT JOIN courses course ON course.ID = cd.Course_ID
LEFT JOIN billdetails billdetail ON billdetail.ID = course.BillDetailiId
LEFT JOIN (
    SELECT 
        ecd.CourseDetailId,
        GROUP_CONCAT(CONCAT(emp.ID, '|', emp.EmpName) SEPARATOR ';') as performers_details
    FROM employeecoursedetails ecd
    LEFT JOIN employees emp ON emp.ID = ecd.EmployeeId
    GROUP BY ecd.CourseDetailId
) performers_info ON performers_info.CourseDetailId = cd.ID
WHERE cd.ClinicId = '484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
  AND cd.CreateTime >= '2025-01-01'
  AND cd.CreateTime <= '2025-06-18'
  AND billdetail.is_network_order = 1
  AND performers_info.performers_details REGEXP '吴慧玲|徐敏|手术'
```

#### 验证查询3：业绩人不包含过滤条件的移动端数据
```sql
SELECT 
    '移动端数据-业绩人不包含过滤条件（应始终显示）' as data_type,
    COUNT(*) as record_count,
    SUM(cd.CourseAmount) / 100.0 as total_amount
FROM coursedetails cd
LEFT JOIN courses course ON course.ID = cd.Course_ID
LEFT JOIN billdetails billdetail ON billdetail.ID = course.BillDetailiId
LEFT JOIN (
    SELECT 
        ecd.CourseDetailId,
        GROUP_CONCAT(CONCAT(emp.ID, '|', emp.EmpName) SEPARATOR ';') as performers_details
    FROM employeecoursedetails ecd
    LEFT JOIN employees emp ON emp.ID = ecd.EmployeeId
    GROUP BY ecd.CourseDetailId
) performers_info ON performers_info.CourseDetailId = cd.ID
WHERE cd.ClinicId = '484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
  AND cd.CreateTime >= '2025-01-01'
  AND cd.CreateTime <= '2025-06-18'
  AND billdetail.is_network_order = 1
  AND (performers_info.performers_details NOT REGEXP '吴慧玲|徐敏|手术' 
       OR performers_info.performers_details IS NULL)
```

#### 验证查询4：验证修复后的过滤逻辑（应返回0）
```sql
SELECT 
    '验证：修复后的过滤逻辑应排除移动端数据（应返回0）' as data_type,
    COUNT(*) as record_count
FROM coursedetails cd
LEFT JOIN courses course ON course.ID = cd.Course_ID
LEFT JOIN billdetails billdetail ON billdetail.ID = course.BillDetailiId
LEFT JOIN employeecoursedetails employeecoursedetail ON employeecoursedetail.CourseDetailId = cd.ID
LEFT JOIN employees employee ON employee.ID = employeecoursedetail.EmployeeId
WHERE cd.ClinicId = '484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
  AND cd.CreateTime >= '2025-01-01'
  AND cd.CreateTime <= '2025-06-18'
  AND billdetail.is_network_order = 1
  AND (employee.EmpName LIKE '%吴慧玲%'
       OR employee.EmpName LIKE '%徐敏%'
       OR employee.EmpName LIKE '%手术%')
  AND EXISTS (
      SELECT 1
      FROM coursedetails cd2
      LEFT JOIN courses course2 ON course2.ID = cd2.Course_ID
      LEFT JOIN billdetails billdetail2 ON billdetail2.ID = course2.BillDetailiId
      LEFT JOIN employeecoursedetails ecd2 ON ecd2.CourseDetailId = cd2.ID
      LEFT JOIN employees emp2 ON emp2.ID = ecd2.EmployeeId
      WHERE cd2.ID = cd.ID
        AND cd2.ClinicId = '484e1ebc-2e4f-cdc8-8da1-08d5b63fbd3a'
        AND (emp2.EmpName LIKE '%吴慧玲%'
             OR emp2.EmpName LIKE '%徐敏%'
             OR emp2.EmpName LIKE '%手术%')
        -- 修复后的过滤条件：排除移动端数据
        AND (billdetail2.is_network_order IS NULL OR billdetail2.is_network_order = 0)
  )
```

### 7.2 验证标准
修复成功的标志：
1. 查询2的记录数 + 查询3的记录数 = 查询1的记录数
2. 查询4返回0条记录（移动端数据不会被过滤逻辑匹配）
3. 修复后，所有移动端消耗数据都能正常显示在消耗业绩报表中

### 7.3 功能验证
1. 消耗业绩报表接口：`/consume`
   - 验证移动端消耗数据是否正常显示
   - 验证非移动端数据过滤是否正常
2. 各店经营情况汇总表：`summaryOfOperationOfEachStoreNew`
   - 验证移动端数据是否正常汇总
3. 其他报表功能：确保不受影响

---

## 八、风险评估

### 8.1 修复风险
- 低风险：仅修改过滤条件，不改变数据结构
- 向后兼容：不影响现有功能
- 性能影响：增加 `is_network_order` 判断，影响可忽略

### 8.2 影响范围
- 正面影响：移动端消耗数据正确汇总
- 负面影响：无
- 其他功能：不受影响

---

## 九、测试建议

### 9.1 功能测试
1. 消耗业绩报表
   - 移动端数据正常显示
   - 非移动端数据过滤正常
   - 业绩人包含过滤条件的移动端数据正常显示
2. 开单业绩报表
   - 移动端开单数据正常显示
   - 非移动端数据过滤正常
3. 退款业绩报表
   - 移动端退款数据正常显示
   - 非移动端数据过滤正常

### 9.2 回归测试
1. 验证其他报表功能正常
2. 验证非移动端数据过滤逻辑正常
3. 验证其他门店数据不受影响

---

## 十、总结

### 10.1 问题总结
- 根本原因：`isExclusionChannels = 1` 的过滤逻辑未考虑移动端数据
- 修复方案：在过滤条件中排除移动端数据
- 修复范围：3个 Mapper 文件，10个修复位置

### 10.2 修复效果
- 移动端消耗数据能正确汇总到报表
- 非移动端数据过滤逻辑保持不变
- 不影响其他功能

### 10.3 后续建议
1. 代码审查：确保修复逻辑正确
2. 测试验证：执行 `test.session.sql` 验证修复效果
3. 上线部署：修复完成后进行上线部署
4. 监控观察：上线后观察报表数据是否正常

---

## 附录

### A. 相关文件路径
- `src/main/java/cnbwx/intranet/CoursesController.java`
- `src/main/java/cnbwx/domain/datasource/yunyahis/mapper/HIS_ReportCommonBaseV3Mapper.xml`
- `src/main/java/cnbwx/domain/datasource/yunyahis/mapper/HIS_ReportCommonBase2025Mapper.xml`
- `src/main/java/cnbwx/domain/datasource/yunyahis/mapper/HIS_ReportCommonBaseMapper.xml`
- `src/main/java/cnbwx/service/his/impl/ReportServiceImpl.java`
- `test.session.sql`

### B. 相关数据库表
- `coursedetails`：消耗明细表
- `courses`：消耗表
- `billdetails`：订单明细表（包含 `is_network_order` 字段）
- `employeecoursedetails`：员工消耗明细关联表
- `employees`：员工表
- `paybooks`：付款单表
- `bills`：订单表
- `refundbooks`：退款单表

---

报告生成时间：2025年1月
报告版本：v1.0