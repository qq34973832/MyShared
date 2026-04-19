# MyShared

多商家电商平台系统，基于 **FastAPI + SQLAlchemy + SQLAdmin** 构建，提供管理后台、商户门户、消费者门户三套界面。

## 系统架构

```
┌─────────────────────────────────────────────────────────┐
│                      MyShared 平台                       │
├──────────────┬──────────────┬───────────────────────────┤
│  /admin      │  /portal     │  REST API                 │
│  管理后台     │  商户/消费者  │  /users /products         │
│  (SQLAdmin)  │  Web 门户    │  /merchants /consumers    │
│  仅管理员    │  登录+仪表盘  │  /ads /comments /chat ... │
├──────────────┴──────────────┴───────────────────────────┤
│  FastAPI + JWT Auth + Role-based Access Control         │
├─────────────────────────────────────────────────────────┤
│  SQLAlchemy ORM + SQLite (开发) / PostgreSQL (生产)      │
├─────────────────────────────────────────────────────────┤
│  Redis (可选缓存) + Celery (可选异步任务)                 │
└─────────────────────────────────────────────────────────┘
```

## 功能模块

### 三套用户界面

| 入口 | 地址 | 说明 |
|------|------|------|
| 管理后台 | `/admin` | SQLAdmin，仅 admin 角色可登录，管理所有数据 |
| 商户/消费者门户 | `/portal/login` | 统一登录页，根据角色自动跳转对应仪表盘 |
| REST API | `/docs` | Swagger 文档，支持所有 API 调试 |

### 商户门户功能 (`/portal/merchant`)

- 📊 **概览仪表盘** — 商品总数、店铺评分、认证状态、最近商品
- 🏪 **店铺管理** — 注册店铺、查看/编辑店铺信息
- 📦 **商品管理** — 添加、编辑商品，查看完整商品列表（名称、SKU、价格、库存、销量、状态）
- 💰 **竞价管理** — 浏览平台所有商品并出价竞价，查看竞价记录和竞价详情，支持商品搜索
- 📂 **分类管理** — 创建和查看商品分类
- 👤 **个人设置** — 查看账户信息
- 🔌 **开放接口** — 在门户中申请 API Token、查看/撤销 Token、创建/查看/删除 Webhook

### 消费者门户功能 (`/portal/consumer`)

- 📊 **概览仪表盘** — 订阅数、兴趣标签、推荐商品（带一键订阅按钮）
- 🛒 **浏览商品** — 按分类分组展示，支持关键词搜索和分类筛选，可直接订阅商品或商户
- 🏪 **商户列表** — 查看所有商户信息，一键订阅商户或查看其商品
- 🔔 **我的订阅** — 查看所有订阅（商户/分类/商品），支持取消订阅
- 👤 **消费者档案** — 创建/编辑档案（昵称、头像、兴趣标签）
- ⚙️ **个人设置** — 查看账户信息
- 🔌 **开放接口** — 在门户中申请 API Token、查看/撤销 Token、创建/查看/删除 Webhook

### 核心业务功能

- **用户系统** — 注册、登录（JWT）、角色管理（admin/merchant/consumer/guest）
- **商家入驻** — 注册店铺、管理商品、管理分类
- **共享商品竞价** — 多商家对同一商品出价，平台取最低价，竞价记录透明可查
- **消费者订阅** — 订阅商户、分类或商品，获取更新通知
- **广告系统** — 广告活动创建、匿名广告池（保护消费者隐私）、效果分析
- **评论系统** — 商品评论、评分
- **聊天系统** — 用户间消息
- **Webhook** — 事件推送
- **API Token** — 开放 API 访问令牌

## 代码结构

```
MyShared/
├── app/
│   ├── admin/           # SQLAdmin 后台（认证、视图注册）
│   ├── core/            # 配置、数据库、缓存、安全、种子数据
│   ├── dependencies/    # FastAPI 依赖注入（认证、角色校验）
│   ├── models/          # SQLAlchemy 数据模型
│   ├── routers/         # FastAPI 路由
│   │   ├── portal.py    # 商户/消费者 Web 门户（登录、注册、仪表盘）
│   │   ├── users.py     # 用户注册、登录、个人信息
│   │   ├── merchants.py # 商户注册、店铺管理、分类
│   │   ├── consumers.py # 消费者档案、订阅
│   │   ├── shared_products.py  # 商品 CRUD、竞价出价、竞价记录
│   │   ├── ads.py       # 广告活动
│   │   ├── comments.py  # 评论
│   │   ├── chat.py      # 聊天消息
│   │   ├── webhooks.py  # Webhook 管理
│   │   ├── categories.py # 公开分类列表
│   │   └── openapi.py   # OpenAPI 文档
│   ├── schemas/         # Pydantic 请求/响应模型
│   ├── services/        # 业务服务（竞价、订阅、广告池、分析、通知）
│   ├── templates/       # HTML 模板（登录页、商户仪表盘、消费者仪表盘）
│   ├── tasks/           # Celery 异步任务
│   └── main.py          # 应用入口
├── alembic/             # 数据库迁移
├── tests/               # pytest 测试
├── requirements.txt     # 运行依赖
├── docker-compose.yml   # Docker 一键部署
└── pyproject.toml       # 项目配置
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 准备配置

```bash
cp .env.example .env
```

最小可运行配置（SQLite，无需 PostgreSQL/Redis）：

```env
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=dev-secret-key-dev-secret-key-123456
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
WEBHOOK_SECRET=webhook-secret
AUTO_SEED_DATA=True
```

### 3. 启动服务

```bash
uvicorn app.main:app --reload
```

启动后自动创建数据库表和演示数据，访问：

| 地址 | 说明 |
|------|------|
| http://127.0.0.1:8000/ | API 根路径 |
| http://127.0.0.1:8000/portal/login | **商户/消费者登录** |
| http://127.0.0.1:8000/admin | 管理后台 |
| http://127.0.0.1:8000/docs | API 文档 |

## 测试账号

`AUTO_SEED_DATA=True` 时自动创建：

| 角色 | 用户名 | 邮箱 | 密码 | 登录地址 |
|------|--------|------|------|----------|
| 管理员 | admin | admin@example.com | 1234 | `/admin` |
| 商户 | lily | lily@example.com | 1234 | `/portal/login` |
| 消费者 | alice | alice@example.com | 1234 | `/portal/login` |
| 商户(演示) | merchant-demo | merchant@example.com | 123456 | `/portal/login` |
| 消费者(演示) | consumer-demo | consumer@example.com | 123456 | `/portal/login` |

## API 端点一览

### 用户 `/users`
- `POST /users/register` — 注册
- `POST /users/login` — 登录（返回 JWT）
- `GET /users/me` — 当前用户信息
- `PUT /users/me` — 更新个人信息

### 商户 `/merchants`
- `GET /merchants` — 商户列表（公开）
- `POST /merchants/register` — 注册店铺
- `GET /merchants/me` — 我的店铺
- `PUT /merchants/me` — 更新店铺
- `POST /merchants/categories` — 创建分类
- `GET /merchants/categories` — 我的分类列表

### 商品 `/products`
- `GET /products` — 商品列表（支持 `category_id`、`merchant_id`、`keyword` 筛选）
- `GET /products/my` — 我的商品列表（商户）
- `POST /products` — 创建商品（商户）
- `GET /products/{id}` — 商品详情
- `PUT /products/{id}` — 更新商品（商户）

### 竞价 `/products/bids`
- `POST /products/bids` — 出价竞价（商户）
- `GET /products/bids/my` — 我的出价记录（商户）
- `GET /products/bids/{product_id}` — 商品竞价详情

### 消费者 `/consumers`
- `POST /consumers/profile` — 创建消费者档案
- `GET /consumers/profile` — 获取档案
- `PUT /consumers/profile` — 更新档案
- `POST /consumers/subscriptions` — 创建订阅
- `GET /consumers/subscriptions` — 订阅列表
- `DELETE /consumers/subscriptions/{id}` — 取消订阅

### 其他
- `GET /categories` — 分类列表（公开）
- `POST /ads/campaigns` — 创建广告活动
- `POST /comments` — 创建评论
- `GET /comments/product/{id}` — 商品评论列表

### 开放接口 `/openapi` 与 `/webhooks`
- `POST /openapi/tokens` — 创建 API Token
- `GET /openapi/tokens` — 当前用户的 Token 列表（返回脱敏 token）
- `DELETE /openapi/tokens/{id}` — 撤销 Token
- `POST /openapi/tokens/{id}/refresh` — 刷新 Token
- `GET /openapi/tokens/{id}/check?token=...` — 检查 Token 是否有效
- `POST /webhooks` — 创建 Webhook
- `GET /webhooks` — 当前用户自己的 Webhook 列表
- `PUT /webhooks/{id}` — 更新 Webhook
- `DELETE /webhooks/{id}` — 删除 Webhook
- `GET /webhooks/logs/{id}` — 查看该 Webhook 的投递日志

> 当前版本中，商户和消费者都可以在门户页面直接管理 Token 与 Webhook。

## Docker 部署

```bash
docker-compose up -d
```

启动 PostgreSQL、Redis、FastAPI Web、Celery Worker、Celery Beat 全套服务。

## 测试

```bash
pytest -q
```

## 本次已验证能力

- 商户门户“开放接口”页可正常打开与提交
- 消费者门户“开放接口”页可正常打开与提交
- 商户可成功申请 API Token
- 消费者可成功申请 API Token
- Token 可通过 `/openapi/tokens/{id}/check` 校验有效性
- 已撤销 Token 会返回 `403 Token is revoked`
- 商户可成功创建、查看、删除自己的 Webhook
- 消费者可成功创建、查看、删除自己的 Webhook
- Webhook 列表已按当前登录用户隔离，互相不可见

## 技术栈

- **后端**: FastAPI 0.104 + Uvicorn
- **ORM**: SQLAlchemy 2.0
- **数据库**: SQLite (开发) / PostgreSQL (生产)
- **认证**: JWT (PyJWT) + 角色权限
- **密码**: passlib + bcrypt
- **管理后台**: SQLAdmin 0.24
- **缓存**: Redis（可选，无 Redis 时自动降级内存缓存）
- **异步任务**: Celery（可选）
- **前端**: 原生 HTML/CSS/JS（无框架依赖）
