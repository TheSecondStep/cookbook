# 🍳 AI食谱推荐官 - 小厨神

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![LangChain](https://img.shields.io/badge/LangChain-v0.1.0-green.svg)](https://python.langchain.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-production%20ready-brightgreen.svg)](PROJECT_SUMMARY.md)

基于LangChain v1和OpenAI构建的智能食谱推荐Agent，提供个性化的烹饪建议和食谱推荐。

> ✅ **项目已完成**: 包含完整的Agent实现、记忆系统、RAG检索、流式传输、API服务等功能。查看 [项目总结](PROJECT_SUMMARY.md) 了解详情。

## 🎯 快速开始

**只需3步即可启动：**

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置API Key（编辑.env文件）
cp .env.example .env

# 3. 运行程序
python main.py
```

详细说明请查看 [运行说明](RUN_INSTRUCTIONS.md) 或 [快速开始指南](QUICK_START.md)

## ✨ 核心特性

### 🎯 智能Agent能力
- **个性化偏好管理**：记录并学习用户的菜系偏好、忌口、喜好食材等
- **虚拟冰箱**：管理现有食材，智能匹配可做菜品
- **双模式推荐**：
  - `strict`模式：仅使用现有食材推荐
  - `flexible`模式：可建议补充少量关键食材
- **RAG检索增强**：基于向量数据库检索相关食谱，提高推荐准确度

### 🧠 记忆系统
- **短期记忆**：维护会话上下文，支持多轮对话
- **长期记忆**：持久化用户偏好，越用越懂你

### ⚡ 高级功能
- **流式传输**：实时响应，提升用户体验
- **异步处理**：支持高并发多用户访问
- **人机交互**：智能确认用户偏好信息
- **工具系统**：模块化工具设计，易于扩展

## 🏗️ 架构设计

```
AI食谱推荐官
├── 对话大模型 (ChatOpenAI)
│   └── 负责理解用户意图和生成回复
├── Agent核心 (OpenAI Functions Agent)
│   └── 协调各模块，执行推理和决策
├── 工具系统 (Tools)
│   ├── 偏好管理工具
│   ├── 冰箱管理工具
│   └── 兼容性检查工具
├── 记忆系统 (Memory)
│   ├── 短期记忆 (ConversationBufferWindowMemory)
│   └── 长期记忆 (ChromaDB向量数据库)
├── RAG检索 (Retrieval)
│   ├── Embedding模型 (OpenAI Embeddings)
│   ├── 向量存储 (ChromaDB)
│   └── 食谱检索器
└── 虚拟冰箱 (Fridge)
    ├── 食材管理
    └── 兼容性分析
```

## 📦 安装部署

### 环境要求
- Python 3.9+
- OpenAI API Key

### 快速开始

1. **克隆项目**
```bash
git clone <repository-url>
cd cookbook
```

2. **安装依赖**
```bash
pip install -r requirements.txt
```

3. **配置环境变量**
```bash
cp .env.example .env
# 编辑.env文件，填入你的OpenAI API Key
```

4. **运行CLI版本**
```bash
python main.py
```

5. **运行API服务器**
```bash
python api_server.py
# 访问 http://localhost:8000/docs 查看API文档
```

## 🎮 使用指南

### CLI交互模式

启动后，你可以：

```
🔸 记录偏好
  "我喜欢川菜和粤菜"
  "我对花生过敏"
  "我不吃香菜"

🔸 管理冰箱
  "我冰箱有鸡蛋、番茄、土豆"
  "添加食材: 牛肉、洋葱"
  "查看冰箱"

🔸 获取推荐
  "今天吃什么？"
  "推荐一道川菜"
  "用现有食材能做什么？"

🔸 系统命令
  help - 查看帮助
  profile - 查看个人档案
  fridge - 查看冰箱
  clear - 清空会话
  exit - 退出
```

### API接口

#### REST API

```bash
# 聊天
POST /chat
{
  "user_id": "user123",
  "message": "推荐一道川菜"
}

# 设置偏好
POST /preferences
{
  "user_id": "user123",
  "cuisines": ["川菜", "粤菜"],
  "allergies": ["花生"]
}

# 管理冰箱
POST /fridge
{
  "user_id": "user123",
  "action": "add",
  "ingredients": ["鸡蛋", "番茄"]
}

# 搜索食谱
POST /recipes/search
{
  "query": "鸡蛋",
  "k": 5
}
```

#### WebSocket（流式对话）

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/user123');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.type === 'token') {
    console.log(data.content);  // 实时接收响应token
  }
};

ws.send(JSON.stringify({
  message: "推荐一道菜"
}));
```

## 🧪 测试

运行测试套件：

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_agent.py

# 查看覆盖率
pytest --cov=src
```

## 📁 项目结构

```
cookbook/
├── config/                 # 配置模块
│   ├── __init__.py
│   └── settings.py        # 环境配置
├── src/                   # 核心源码
│   ├── agents/           # Agent实现
│   │   ├── __init__.py
│   │   └── recipe_agent.py
│   ├── tools/            # 工具模块
│   │   ├── __init__.py
│   │   └── recipe_tools.py
│   ├── memory/           # 记忆系统
│   │   ├── __init__.py
│   │   ├── short_term_memory.py
│   │   └── long_term_memory.py
│   ├── retrievers/       # 检索器
│   │   ├── __init__.py
│   │   └── recipe_retriever.py
│   ├── fridge/           # 冰箱模块
│   │   ├── __init__.py
│   │   └── fridge_manager.py
│   ├── prompts/          # Prompt模板
│   │   ├── __init__.py
│   │   └── templates.py
│   └── utils/            # 工具函数
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── data/                  # 数据目录
│   ├── recipes/          # 食谱数据
│   │   └── sample_recipes.json
│   └── vectordb/         # 向量数据库
├── tests/                 # 测试文件
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_memory.py
│   ├── test_fridge.py
│   └── test_retriever.py
├── main.py               # CLI入口
├── api_server.py         # API服务器
├── requirements.txt      # 依赖列表
├── pytest.ini           # 测试配置
├── .env.example         # 环境变量示例
├── .gitignore
└── README.md
```

## 🎨 Prompt工程最佳实践

本项目采用的Prompt设计原则：

1. **简洁清晰**：每个Prompt都有明确的目的和结构
2. **角色定位**：为Agent设定专业的"小厨神"角色
3. **上下文管理**：合理使用对话历史和用户偏好
4. **格式化输出**：使用JSON等结构化格式便于解析
5. **Few-shot示例**：在关键场景提供示例引导

示例Prompt结构：
```python
系统角色 + 当前状态（冰箱/偏好） + 对话历史 + 用户输入 + 预期输出格式
```

## 🔧 LangChain v1 API使用

### Agent创建
```python
from langchain.agents import create_openai_functions_agent, AgentExecutor

agent = create_openai_functions_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)
```

### 记忆管理
```python
from langchain.memory import ConversationBufferWindowMemory

memory = ConversationBufferWindowMemory(
    k=50,  # 保留最近50条消息
    memory_key="chat_history",
    return_messages=True
)
```

### 向量检索
```python
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings

vectorstore = Chroma(
    collection_name="recipes",
    embedding_function=OpenAIEmbeddings()
)

results = vectorstore.similarity_search(query, k=5)
```

## 🚀 扩展建议

1. **添加更多工具**：
   - 营养计算工具
   - 食材替换建议工具
   - 菜谱评分系统

2. **增强RAG**：
   - 使用Rerank提高检索质量
   - 添加混合检索（关键词+语义）
   - 实现Query重写优化

3. **UI界面**：
   - 开发Web前端
   - 移动端应用
   - 语音交互

4. **多模态**：
   - 图片识别食材
   - 生成菜品图片
   - 视频烹饪指导

## 📝 配置说明

环境变量配置（`.env`）：

```bash
# OpenAI配置
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4-turbo-preview
OPENAI_TEMPERATURE=0.7

# 向量数据库
CHROMA_PERSIST_DIRECTORY=./data/vectordb

# 应用设置
LOG_LEVEL=INFO
MAX_MEMORY_MESSAGES=50
STREAM_ENABLED=true
FRIDGE_MODE=flexible
```

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

开发建议：
1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 License

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [LangChain](https://python.langchain.com/) - 强大的LLM应用框架
- [OpenAI](https://openai.com/) - 提供优秀的语言模型
- [ChromaDB](https://www.trychroma.com/) - 高效的向量数据库

## 📞 联系方式

如有问题或建议，欢迎通过Issue联系我们！

---

⭐ 如果这个项目对你有帮助，欢迎Star支持！
