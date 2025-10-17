# 🏗️ 架构设计文档

## 系统概述

AI食谱推荐官是一个基于LangChain v1框架构建的智能Agent系统，采用模块化设计，支持多用户并发访问。

## 技术栈

- **框架**: LangChain v1 (0.1.0)
- **LLM**: OpenAI GPT-4-turbo
- **Embedding**: OpenAI text-embedding-3-small
- **向量数据库**: ChromaDB
- **API框架**: FastAPI
- **异步处理**: asyncio, aiohttp
- **日志**: Loguru

## 架构分层

### 1. 接口层 (Interface Layer)

#### CLI接口 (`main.py`)
- 命令行交互界面
- 实时流式输出
- 命令处理系统

#### REST API (`api_server.py`)
- RESTful接口
- 多用户并发支持
- WebSocket流式传输

### 2. Agent层 (Agent Layer)

#### RecipeRecommenderAgent (`src/agents/recipe_agent.py`)
核心Agent实现，负责：
- 协调各模块工作
- 执行推理和决策
- 管理对话流程
- 整合RAG检索结果

**关键方法**：
```python
async def arun(user_input: str) -> str
    # 异步处理用户输入，返回响应

async def stream_response(user_input: str) -> AsyncIterator[str]
    # 流式生成响应

async def _retrieve_relevant_recipes(query: str) -> List[Dict]
    # 检索相关食谱

async def _enhance_with_rag(response: str, recipes: List[Dict]) -> str
    # 使用RAG增强响应
```

### 3. 工具层 (Tools Layer)

#### 工具系统 (`src/tools/recipe_tools.py`)

采用LangChain的Tool接口，实现以下工具：

1. **save_user_preference**
   - 保存/更新用户偏好
   - 支持菜系、忌口、喜好等维度

2. **get_user_preference**
   - 获取用户偏好信息
   - 返回JSON格式数据

3. **manage_fridge**
   - 管理虚拟冰箱
   - 支持add/remove/list/clear操作

4. **set_fridge_mode**
   - 设置冰箱模式
   - strict/flexible两种模式

5. **check_recipe_compatibility**
   - 检查食谱与冰箱的兼容性
   - 返回匹配度和缺失食材

### 4. 记忆层 (Memory Layer)

#### 短期记忆 (`src/memory/short_term_memory.py`)

**设计模式**: 滑动窗口 + 摘要压缩

```python
class ShortTermMemory:
    - memory: ConversationBufferWindowMemory  # 保留最近N条消息
    - summary_memory: ConversationSummaryBufferMemory  # 智能压缩
```

**特性**：
- 保持会话上下文
- 自动清理旧消息
- 支持摘要生成

#### 长期记忆 (`src/memory/long_term_memory.py`)

**存储方案**: ChromaDB向量数据库

```python
class LongTermMemory:
    - vectorstore: Chroma  # 向量存储
    - embeddings: OpenAIEmbeddings  # 向量化
```

**存储内容**：
- 用户偏好（菜系、忌口、喜好）
- 向量化存储，支持语义搜索
- 持久化到磁盘

### 5. 检索层 (Retrieval Layer)

#### RAG检索器 (`src/retrievers/recipe_retriever.py`)

**检索流程**：
```
用户查询 -> 查询优化 -> 向量化 -> 相似度搜索 -> 结果排序 -> 返回Top-K
```

**优化策略**：
1. **查询增强**: 结合用户偏好优化查询
2. **过滤机制**: 根据冰箱食材过滤
3. **重排序**: 按匹配度重新排序
4. **模式感知**: strict模式只返回兼容食谱

**关键方法**：
```python
def search(query: str, k: int, filter_dict: Optional[Dict]) -> List[Recipe]
    # 通用搜索

def search_by_ingredients(ingredients: List[str], k: int) -> List[Recipe]
    # 按食材搜索

def search_by_cuisine(cuisine: str, k: int) -> List[Recipe]
    # 按菜系搜索
```

### 6. 业务层 (Business Layer)

#### 冰箱管理 (`src/fridge/fridge_manager.py`)

**数据模型**：
```python
Ingredient:  # 食材
    - name: str
    - quantity: Optional[str]
    - unit: Optional[str]

VirtualFridge:  # 虚拟冰箱
    - user_id: str
    - mode: FridgeMode (STRICT/FLEXIBLE)
    - ingredients: Dict[str, Ingredient]
```

**核心功能**：
- 食材增删改查
- 兼容性检查
- 匹配度计算
- 模式切换

### 7. Prompt层 (Prompt Layer)

#### Prompt模板设计 (`src/prompts/templates.py`)

**设计原则**：
1. **简洁性**: 避免冗余，突出重点
2. **结构化**: 清晰的层次结构
3. **可扩展**: 易于添加新功能
4. **格式化**: 使用JSON等结构化输出

**主要Prompt**：

1. **系统角色Prompt**
```python
SYSTEM_ROLE_PROMPT = """
你是专业的AI食谱推荐官...
职责: 1. 理解用户偏好 2. 管理冰箱 3. 智能推荐 4. 友好交互
"""
```

2. **偏好收集Prompt**
```python
PREFERENCE_COLLECTION_PROMPT = """
提取用户的饮食偏好信息
输出格式: JSON {cuisines, allergies, dislikes, ...}
"""
```

3. **推荐生成Prompt**
```python
RECIPE_RECOMMENDATION_PROMPT = """
基于: 用户偏好 + 冰箱食材 + 检索结果
输出: 1-3个推荐 + 理由 + 匹配度
"""
```

## 数据流

### 1. 用户请求处理流程

```
用户输入
  ↓
接口层接收
  ↓
Agent解析意图
  ↓
判断是否需要工具调用
  ↓ (是)
执行相应工具
  ↓
判断是否需要推荐
  ↓ (是)
RAG检索增强
  ↓
生成最终响应
  ↓
保存到短期记忆
  ↓
返回给用户
```

### 2. 食谱推荐流程

```
用户查询
  ↓
加载用户偏好（长期记忆）
  ↓
获取冰箱食材
  ↓
优化查询语句
  ↓
向量检索Top-K食谱
  ↓
计算兼容性和匹配度
  ↓
根据模式过滤
  ↓
重排序
  ↓
生成推荐响应
  ↓
流式返回给用户
```

### 3. 偏好学习流程

```
用户表达偏好
  ↓
Agent识别意图
  ↓
调用preference工具
  ↓
提取结构化信息
  ↓
征求用户确认
  ↓ (确认)
更新长期记忆
  ↓
向量化存储
```

## 并发处理

### AgentManager设计

```python
class AgentManager:
    - agents: Dict[str, RecipeRecommenderAgent]  # 用户ID -> Agent实例
    - locks: Dict[str, asyncio.Lock]  # 用户级锁
    
    def get_agent(user_id: str) -> RecipeRecommenderAgent:
        # 懒加载，首次访问时创建
    
    def get_lock(user_id: str) -> asyncio.Lock:
        # 获取用户锁，确保串行处理同一用户请求
```

**并发策略**：
- 用户级隔离：每个用户独立的Agent实例
- 异步处理：使用asyncio实现并发
- 锁机制：防止同一用户的并发请求冲突

## 性能优化

### 1. 缓存策略
- 向量数据库持久化
- Agent实例复用
- 偏好信息缓存

### 2. 异步处理
- 所有IO操作异步化
- 流式输出减少等待时间
- 并行处理多用户请求

### 3. 向量检索优化
- 预计算Embedding
- 使用过滤器减少搜索空间
- Top-K限制返回数量

## 扩展性

### 1. 新增工具
```python
@tool
def new_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result

# 添加到get_recipe_tools()
```

### 2. 新增Prompt
```python
NEW_PROMPT = """..."""

def create_new_prompt():
    return PromptTemplate(template=NEW_PROMPT, ...)
```

### 3. 新增存储后端
实现相应接口即可替换：
- Memory: 实现BaseChatMessageHistory
- VectorStore: 实现VectorStore接口

## 安全性

### 1. 输入验证
- 最大长度限制
- 特殊字符过滤
- 类型检查

### 2. API安全
- CORS配置
- 用户隔离
- 错误处理

### 3. 数据隐私
- 用户级数据隔离
- 不共享个人偏好
- 可删除个人数据

## 监控和日志

### 日志系统
```python
from src.utils.logger import app_logger

app_logger.info("信息日志")
app_logger.error("错误日志")
```

### 监控指标
- 请求响应时间
- Agent执行步骤
- 工具调用次数
- 错误率

## 部署建议

### 开发环境
```bash
python main.py  # CLI模式
python api_server.py  # API服务
```

### 生产环境
```bash
# 使用Gunicorn + Uvicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker

# 或使用Docker
docker build -t recipe-agent .
docker run -p 8000:8000 recipe-agent
```

### 配置建议
- 使用环境变量管理配置
- 分离开发/生产配置
- 敏感信息使用密钥管理服务

## 总结

本系统采用模块化、分层的架构设计，充分利用LangChain v1的Agent、Memory、Tools等特性，实现了一个功能完整、易于扩展的智能食谱推荐系统。

关键设计亮点：
- ✅ 完整的Agent工作流
- ✅ 短期+长期双记忆系统
- ✅ RAG检索增强
- ✅ 流式异步处理
- ✅ 多用户并发支持
- ✅ 清晰的Prompt工程
- ✅ 模块化可扩展设计
