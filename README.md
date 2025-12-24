# AIOps Tools

Agent Tools 管理平台 - 管理 AI Agent 可调用的工具，包括工具注册、执行、监控和日志等功能。

## 技术栈

| 组件 | 技术 | 说明 |
|------|------|------|
| Web 框架 | FastAPI | 高性能异步框架，自动生成 OpenAPI 文档 |
| ORM | SQLAlchemy 2.0 + SQLModel | 类型安全的 ORM，与 Pydantic 深度集成 |
| 数据库 | PostgreSQL | 支持 JSONB 存储工具 schema |
| 缓存 | Redis | 工具执行状态缓存 |
| 任务队列 | Celery | 异步执行工具，支持超时控制 |
| 迁移 | Alembic | 数据库版本管理 |

## 项目结构

```
aiops-tools/
├── src/aiops_tools/
│   ├── api/v1/           # API 路由
│   │   └── endpoints/    # 具体端点
│   ├── core/             # 核心配置
│   │   ├── config.py     # 应用配置
│   │   ├── database.py   # 数据库连接
│   │   └── redis.py      # Redis 连接
│   ├── models/           # 数据库模型
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # 业务逻辑
│   └── main.py           # 应用入口
├── tests/                # 测试
├── alembic/              # 数据库迁移
├── docker-compose.yml    # Docker 编排
└── pyproject.toml        # 项目配置
```

## 快速开始

### 使用 Docker Compose（推荐）

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f api
```

API 文档: http://localhost:8000/api/v1/docs

### 本地开发

```bash
# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows

# 安装依赖
pip install -e ".[dev]"

# 复制环境变量配置
cp .env.example .env

# 启动 PostgreSQL 和 Redis（使用 Docker）
docker-compose up -d db redis

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn aiops_tools.main:app --reload
```

## API 端点

### 工具管理

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/tools | 创建工具 |
| GET | /api/v1/tools | 获取工具列表 |
| GET | /api/v1/tools/{id} | 获取工具详情 |
| PATCH | /api/v1/tools/{id} | 更新工具 |
| DELETE | /api/v1/tools/{id} | 删除工具 |
| POST | /api/v1/tools/{id}/activate | 激活工具 |
| POST | /api/v1/tools/{id}/deactivate | 停用工具 |

### 工具分类

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/tools/categories | 创建分类 |
| GET | /api/v1/tools/categories | 获取分类列表 |
| GET | /api/v1/tools/categories/{id} | 获取分类详情 |
| PATCH | /api/v1/tools/categories/{id} | 更新分类 |
| DELETE | /api/v1/tools/categories/{id} | 删除分类 |

### 工具执行

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | /api/v1/tools/{id}/execute | 执行工具 |
| GET | /api/v1/tools/{id}/executions | 获取执行历史 |
| GET | /api/v1/tools/executions/{id} | 获取执行详情 |
| POST | /api/v1/tools/executions/{id}/cancel | 取消执行 |

## 下一步

- [ ] 实现 Celery Worker 执行逻辑
- [ ] 添加用户认证 (JWT)
- [ ] 实现工具版本管理
- [ ] 添加执行日志和监控
- [ ] 支持 MCP (Model Context Protocol) 工具
- [ ] 添加单元测试和集成测试
