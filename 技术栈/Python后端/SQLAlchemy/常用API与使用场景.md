# 📌 SQLAlchemy 常用 API 与使用场景速查

> 配合《学习笔记》使用，侧重**Engine、Session、CRUD、常用查询**等日常开发速查。

---

## 一、Engine 与 Session 创建

### 1.1 同步

| API | 说明 | 使用场景 |
|-----|------|----------|
| `create_engine("dialect+driver://user:pass@host/db")` | 创建引擎 | 应用启动 |
| `sessionmaker(bind=engine, autocommit=False, autoflush=False)` | 创建 Session 工厂 | 全局或请求级 |
| `with Session() as session:` | 上下文内使用 Session | 自动 commit/rollback |
| `session.commit()` | 提交事务 | 写操作后 |
| `session.rollback()` | 回滚 | 异常时 |
| `session.close()` | 关闭（归还连接） | 请求结束 |

### 1.2 异步（2.0）

| API | 说明 |
|-----|------|
| `create_async_engine("postgresql+asyncpg://...")` | 异步引擎 |
| `async_sessionmaker(..., class_=AsyncSession)` | 异步 Session 工厂 |
| `async with AsyncSession() as session:` | 异步上下文 |

---

## 二、模型定义（2.0 风格）

| 写法 | 说明 |
|------|------|
| `class User(Base): __tablename__ = "users"` | 表名 |
| `id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)` | 主键 |
| `name: Mapped[str] = mapped_column(String(64))` | 字符串 |
| `created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)` | 默认值 |
| `relationship("Order", back_populates="user")` | 一对多等关系 |

---

## 三、CRUD 与查询（2.0 风格）

### 3.1 查询

| API | 说明 | 使用场景 |
|-----|------|----------|
| `select(Model)` | 全表查询 | `session.execute(select(User))` |
| `select(Model).where(Model.id == 1)` | 条件 | 单条/列表 |
| `session.scalars(select(User).where(...)).first()` | 单条或 None | 按 id 查 |
| `session.scalars(select(User).where(...)).all()` | 列表 | 列表页 |
| `session.get(Model, pk)` | 按主键取（2.0 推荐） | 简单主键查询 |

### 3.2 写操作

| API | 说明 |
|-----|------|
| `session.add(instance)` | 添加一条 |
| `session.add_all([...])` | 批量添加 |
| `session.delete(instance)` | 删除（需先查询或 attach） |
| `session.merge(instance)` | 合并（存在则更新） |

### 3.3 常用过滤与排序

| 写法 | 说明 |
|------|------|
| `.where(Model.field == value)` | 等值 |
| `.where(Model.field.in_([...]))` | IN |
| `.where(Model.field.like("%x%"))` | LIKE |
| `.order_by(Model.created_at.desc())` | 排序 |
| `.limit(n).offset(m)` | 分页 |

---

## 四、关系加载

| API | 说明 |
|-----|------|
| `selectinload(User.orders)` | 子查询加载关联（避免 N+1） |
| `joinedload(User.orders)` | JOIN 加载 |
| `session.execute(select(User).options(selectinload(User.orders)))` | 配合 select 使用 |

---

## 五、常用场景速查

| 场景 | 示例 |
|------|------|
| 按 id 查一条 | `session.get(User, user_id)` |
| 分页列表 | `select(User).order_by(...).limit(10).offset((page-1)*10)` |
| 条件过滤 | `select(User).where(User.name == "xxx")` |
| 新增并提交 | `session.add(user); session.commit()` |
| 更新 | 查出来改属性后 `session.commit()` |
