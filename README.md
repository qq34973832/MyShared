# MyShared - 多商家电商平台后台系统

完整的 Python FastAPI 后台系统，支持：
- 用户管理和权限控制
- 消费者订阅管理
- 多商家入驻和店铺管理
- 无限层级商品分类
- 商家竞价和最低价机制
- 匿名广告池和广告效果评估
- 商品评论和评分
- 实时聊天功能
- WebHook 和开放 API
- 分布式架构支持

## 快速开始

### 环境准备
```bash
pip install -r requirements.txt
cp .env.example .env
# 修改 .env 中的配置
```

### 运行项目
```bash
# 数据库迁移
alembic upgrade head

# 启动 FastAPI 服务
uvicorn app.main:app --reload

# 启动 Celery Worker
celery -A app.tasks worker --loglevel=info

# 启动 Celery Beat（定时任务）
celery -A app.tasks beat --loglevel=info
```

### Docker 方式运行
```bash
docker-compose up -d
```

## 项目结构

- `app/core/` - 核心配置（数据库、Redis、安全）
- `app/models/` - SQLAlchemy 数据库模型
- `app/schemas/` - Pydantic 请求/响应模型
- `app/crud/` - 数据访问层
- `app/routers/` - API 路由
- `app/services/` - 业务逻辑层
- `app/tasks/` - Celery 异步任务
- `app/websocket/` - WebSocket 实现
- `app/dependencies/` - 依赖注入
- `app/utils/` - 工具函数
- `alembic/` - 数据库迁移脚本
- `tests/` - 测试用例
