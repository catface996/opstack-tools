# AIOps Tools

LLM Tool Management System - 创建、管理和执行 LLM 工具的平台。

## 架构概览

![AIOps Tools Architecture](doc/images/op-stack-tools-architecture.png)

## 功能特性

- **分类管理**: 创建工具分类，组织和管理工具
- **工具管理**: 工具的增删改查、启用/禁用
- **LLM 兼容 API**: 提供 OpenAI function calling 格式的接口，供 LLM 发现和调用工具
- **Python 脚本执行**: 安全沙箱环境执行 Python 脚本，30 秒超时保护
- **版本控制**: 工具更新时自动增加版本号
- **Swagger 文档**: 内置 API 文档，方便开发调试

## 快速开始

### 使用 Docker Compose

```bash
# 启动所有服务 (API, PostgreSQL, Redis)
docker-compose up -d

# 查看日志
docker-compose logs -f api
```

### 访问地址

| 服务 | 地址 |
|------|------|
| API | http://localhost:6060 |
| Swagger UI | http://localhost:6060/docs |
| ReDoc | http://localhost:6060/redoc |

## API 接口

所有接口均使用 **POST** 方法，请求体为 JSON 格式。

### Categories - 分类管理

| 接口 | 描述 |
|------|------|
| `POST /api/tools/v1/categories/create` | 创建分类 |
| `POST /api/tools/v1/categories/list` | 分类列表 |
| `POST /api/tools/v1/categories/get` | 获取分类详情 |
| `POST /api/tools/v1/categories/update` | 更新分类 |
| `POST /api/tools/v1/categories/delete` | 删除分类 |

### Tools - 工具管理

| 接口 | 描述 |
|------|------|
| `POST /api/tools/v1/tools/create` | 创建工具 |
| `POST /api/tools/v1/tools/list` | 工具列表（支持分页、搜索、筛选） |
| `POST /api/tools/v1/tools/get` | 获取工具详情 |
| `POST /api/tools/v1/tools/update` | 更新工具 |
| `POST /api/tools/v1/tools/delete` | 删除工具 |
| `POST /api/tools/v1/tools/activate` | 启用工具 |
| `POST /api/tools/v1/tools/deactivate` | 禁用工具 |

### LLM - LLM 工具调用

| 接口 | 描述 |
|------|------|
| `POST /api/tools/v1/llm/list` | 获取工具列表（OpenAI function calling 格式） |
| `POST /api/tools/v1/llm/get` | 获取单个工具详情 |
| `POST /api/tools/v1/llm/invoke` | 执行工具 |

## 项目结构

```
.
├── src/aiops_tools/          # 源码
│   ├── api/v1/endpoints/     # API 端点
│   │   ├── tools.py          # 工具和分类管理
│   │   └── llm.py            # LLM 兼容接口
│   ├── core/                 # 核心配置
│   │   ├── config.py         # 应用配置
│   │   ├── database.py       # 数据库连接
│   │   └── redis.py          # Redis 连接
│   ├── models/               # 数据模型
│   │   └── tool.py           # Tool, ToolCategory, ToolExecution
│   ├── schemas/              # Pydantic 模型
│   │   ├── tool.py           # 请求/响应模型
│   │   └── llm.py            # LLM 格式模型
│   ├── services/             # 业务服务
│   │   ├── tool_executor.py  # 脚本执行器
│   │   └── tool_validator.py # 工具验证器
│   └── main.py               # 应用入口
├── alembic/                  # 数据库迁移
├── docker-compose.yml        # Docker 编排
├── Dockerfile                # Docker 镜像
└── pyproject.toml            # Python 依赖
```

## 数据模型

### ToolCategory (工具分类)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | UUID | 主键 |
| name | string | 分类名称 |
| description | string | 分类描述 |
| parent_id | UUID | 父分类 ID（支持层级） |

### Tool (工具)

| 字段 | 类型 | 描述 |
|------|------|------|
| id | UUID | 主键 |
| name | string | 工具名称（唯一标识，如 `get_weather`） |
| display_name | string | 显示名称 |
| description | string | 工具描述 |
| status | enum | 状态：draft/active/deprecated/disabled |
| category_id | UUID | 所属分类 |
| input_schema | JSON | 输入参数 JSON Schema |
| output_schema | JSON | 输出参数 JSON Schema |
| script_content | string | Python 脚本内容 |
| executor_type | string | 执行器类型：python/http/shell |
| version | int | 版本号（自动递增） |

## 使用示例

### 1. 创建工具

```bash
curl -X POST http://localhost:6060/api/tools/v1/tools/create \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_weather",
    "display_name": "获取天气",
    "description": "根据城市名称获取天气信息",
    "executor_type": "python",
    "input_schema": {
      "type": "object",
      "properties": {
        "city": {"type": "string", "description": "城市名称"}
      },
      "required": ["city"]
    },
    "script_content": "def main(args):\n    return {\"weather\": \"sunny\", \"city\": args[\"city\"]}"
  }'
```

### 2. 启用工具

```bash
curl -X POST http://localhost:6060/api/tools/v1/tools/activate \
  -H "Content-Type: application/json" \
  -d '{"tool_id": "your-tool-uuid"}'
```

### 3. LLM 发现工具

```bash
curl -X POST http://localhost:6060/api/tools/v1/llm/list
```

返回 OpenAI function calling 格式：
```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "get_weather",
        "description": "根据城市名称获取天气信息",
        "parameters": {
          "type": "object",
          "properties": {
            "city": {"type": "string", "description": "城市名称"}
          },
          "required": ["city"]
        }
      }
    }
  ]
}
```

### 4. 执行工具

```bash
curl -X POST http://localhost:6060/api/tools/v1/llm/invoke \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_weather",
    "arguments": {"city": "北京"}
  }'
```

## 本地开发

### 环境要求

- Python 3.11+
- PostgreSQL 16+
- Redis 7+

### 启动服务

```bash
# 安装依赖
pip install -e .

# 启动服务（需要 PostgreSQL 和 Redis）
uvicorn aiops_tools.main:app --host 0.0.0.0 --port 6060 --reload
```

### 环境变量

| 变量 | 默认值 | 描述 |
|------|--------|------|
| `HOST` | 0.0.0.0 | 服务监听地址 |
| `PORT` | 6060 | 服务端口 |
| `DATABASE_URL` | postgresql+asyncpg://... | PostgreSQL 连接 URL |
| `REDIS_URL` | redis://localhost:6379/0 | Redis 连接 URL |
| `DEBUG` | false | 调试模式 |

## 技术栈

- **FastAPI** - Web 框架
- **SQLModel** - ORM
- **PostgreSQL** - 数据库
- **Redis** - 缓存
- **Pydantic** - 数据验证
- **Docker** - 容器化部署

## License

MIT
