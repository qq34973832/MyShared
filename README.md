# MyShared

多商家电商平台后台系统，基于 **FastAPI + SQLAlchemy + Redis + Celery + SQLAdmin** 构建。

当前仓库包含：

- 用户注册、登录、权限控制
- 消费者档案与订阅
- 商家入驻、分类、商品与竞价
- 广告活动与匿名广告池
- 评论、聊天、Webhook、开放 API Token
- SQLAdmin 管理后台
- 本地内置 API 文档页 `/docs`

## 代码框架

```text
MyShared
├── app/
│   ├── admin/           # SQLAdmin 后台认证、视图注册
│   ├── core/            # 配置、数据库、缓存、安全、文档、初始化测试数据
│   ├── dependencies/    # 登录用户与角色校验依赖
│   ├── models/          # SQLAlchemy 数据模型
│   ├── routers/         # FastAPI 路由
│   ├── schemas/         # Pydantic 请求/响应模型
│   ├── services/        # 广告、订阅、通知等业务服务
│   ├── shared/          # 共享模型/公共结构
│   ├── tasks/           # Celery 异步任务
│   ├── utils/           # 工具函数
│   ├── websocket/       # WebSocket 管理
│   └── main.py          # 应用入口
├── alembic/             # 数据库迁移配置
├── scripts/             # 数据库初始化脚本
├── tests/               # pytest 测试
├── docker-compose.yml   # PostgreSQL / Redis / Web / Celery 一键启动
├── requirements.txt     # 运行依赖
└── pyproject.toml       # 项目与开发依赖配置
```

## 环境要求

- Python 3.10+
- 可选：PostgreSQL 15+
- 可选：Redis 7+

如果只想快速本地跑通接口，使用 SQLite 也可以。

## 本地启动（推荐）

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

如果需要跑测试和 lint：

```bash
pip install -e '.[dev]'
```

### 2. 准备配置

```bash
cp .env.example .env
```

最小可运行配置示例（SQLite）：

```env
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-dev-secret-key-123456
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
WEBHOOK_SECRET=webhook-secret
AUTO_SEED_DATA=True
```

> `AUTO_SEED_DATA=True` 时，服务启动后会自动补充默认演示数据。

### 3. 初始化数据库

```bash
alembic upgrade head
```

### 4. 启动服务

```bash
uvicorn app.main:app --reload
```

启动后可访问：

- API 根路径：`http://127.0.0.1:8000/`
- API 文档：`http://127.0.0.1:8000/docs`
- 管理后台：`http://127.0.0.1:8000/admin/`

## 启动完整服务（含 Redis / PostgreSQL / Celery）

```bash
docker-compose up -d
```

容器会启动：

- PostgreSQL
- Redis
- FastAPI Web
- Celery Worker
- Celery Beat

## 默认测试数据

当 `AUTO_SEED_DATA=True` 时，首次启动会自动创建演示数据：

### 管理员

- 用户名：`admin`
- 邮箱：`admin@example.com`
- 密码：`1234`

### 演示商家

- 用户名：`merchant-demo`
- 邮箱：`merchant@example.com`
- 密码：`123456`
- 默认店铺：`演示共享店铺`
- 默认分类：`演示数码`
- 默认商品：`演示蓝牙耳机`
- 默认广告：`默认演示广告`

### 演示消费者

- 用户名：`consumer-demo`
- 邮箱：`consumer@example.com`
- 密码：`123456`
- 默认评价：已自动写入一条评论数据

## 测试

运行单元测试：

```bash
pytest -q
```

运行 lint：

```bash
ruff check .
```

> 当前仓库仍有一批历史遗留 Ruff 告警；本次修复已保证核心接口测试通过。

## 本次已验证内容

- 用户登录 JWT 鉴权修复
- 匿名广告池在无 Redis 场景下可退化到内存缓存
- `/docs` 页面改为本地内置文档，不再依赖外部 CDN
- 管理后台可用默认账号 `admin / 1234` 登录
