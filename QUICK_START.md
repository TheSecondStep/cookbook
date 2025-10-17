# 🚀 快速开始指南

## 5分钟上手AI食谱推荐官

### 1️⃣ 准备工作

#### 必需条件
- Python 3.9+
- OpenAI API Key

#### 获取代码
```bash
git clone <repository-url>
cd cookbook
```

### 2️⃣ 安装依赖

```bash
# 推荐使用虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

### 3️⃣ 配置环境

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑.env文件，填入你的API Key
# 必须设置: OPENAI_API_KEY=sk-...
```

最小配置示例：
```bash
OPENAI_API_KEY=sk-your-key-here
OPENAI_MODEL=gpt-4-turbo-preview
```

### 4️⃣ 启动程序

#### 方式1: 命令行交互（推荐新手）

```bash
python main.py
```

启动后你会看到：
```
🍳 欢迎使用AI食谱推荐官 - 小厨神 🍳
请输入你的用户名: Alice
✅ 欢迎回来, Alice!

Alice > 
```

#### 方式2: API服务器

```bash
python api_server.py
```

访问 http://localhost:8000/docs 查看API文档

#### 方式3: Docker

```bash
docker-compose up -d
```

### 5️⃣ 开始使用

#### 第一次对话

```
Alice > 你好
小厨神 > 你好！我是小厨神...

Alice > 我喜欢川菜
小厨神 > 好的，我已记录你喜欢川菜...

Alice > 我冰箱有鸡蛋、番茄
小厨神 > 已添加2种食材到冰箱...

Alice > 推荐一道菜
小厨神 > 根据你的偏好和现有食材，我推荐...
```

#### 常用命令

```bash
# 系统命令
help      # 查看帮助
profile   # 查看个人档案
fridge    # 查看冰箱
clear     # 清空会话
exit      # 退出

# 自然对话示例
"我喜欢吃辣的"
"我对花生过敏"
"我冰箱有..."
"推荐一道川菜"
"今天吃什么？"
```

### 6️⃣ 运行示例脚本

```bash
python example_usage.py
```

选择要运行的示例，体验不同功能。

## 🎯 快速场景

### 场景1: 基于现有食材做饭

```
1. 告诉冰箱有什么: "我冰箱有鸡蛋、番茄、葱"
2. 请求推荐: "用这些食材能做什么？"
3. 查看详细做法: "番茄炒蛋怎么做？"
```

### 场景2: 记录饮食偏好

```
1. "我喜欢川菜和粤菜"
2. "我对海鲜过敏"
3. "我不吃香菜"
4. 查看档案: "profile"
```

### 场景3: 指定菜系推荐

```
1. "我想做一道川菜"
2. "推荐一道简单的粤菜"
3. "有什么家常菜推荐？"
```

## 🔧 API使用

### REST API

```bash
# 聊天
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"user_id": "alice", "message": "推荐一道川菜"}'

# 设置偏好
curl -X POST http://localhost:8000/preferences \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "cuisines": ["川菜"],
    "allergies": ["花生"]
  }'

# 管理冰箱
curl -X POST http://localhost:8000/fridge \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "alice",
    "action": "add",
    "ingredients": ["鸡蛋", "番茄"]
  }'
```

### Python客户端

```python
import requests

# 聊天
response = requests.post(
    "http://localhost:8000/chat",
    json={"user_id": "alice", "message": "推荐一道菜"}
)
print(response.json()["response"])
```

## ❓ 常见问题

### Q: 提示"OpenAI API key not found"

A: 确保在`.env`文件中设置了`OPENAI_API_KEY=sk-...`

### Q: 向量数据库初始化失败

A: 确保`data/vectordb`目录存在，或删除后重新创建：
```bash
rm -rf data/vectordb
python main.py
```

### Q: 没有食谱推荐结果

A: 确保已加载示例食谱。程序首次运行会自动加载`data/recipes/sample_recipes.json`

### Q: 如何添加自己的食谱？

A: 编辑`data/recipes/sample_recipes.json`，按照格式添加食谱，或通过代码：
```python
from src.retrievers.recipe_retriever import recipe_retriever, Recipe

recipe = Recipe(
    name="我的菜",
    cuisine="家常菜",
    ingredients=["食材1", "食材2"],
    steps=["步骤1", "步骤2"],
    difficulty="简单",
    cooking_time=20
)
recipe_retriever.add_recipe(recipe)
```

### Q: 如何清空所有数据？

A: 删除相关目录：
```bash
rm -rf data/vectordb
rm -rf logs
```

## 📚 下一步

- 阅读 [完整文档](README.md)
- 查看 [架构设计](ARCHITECTURE.md)
- 运行 [测试](tests/)
- 自定义 [Prompt模板](src/prompts/templates.py)

## 💡 提示

1. **首次使用**: 先告诉系统你的偏好和冰箱食材，会得到更好的推荐
2. **流式输出**: 启用后响应更快，设置`STREAM_ENABLED=true`
3. **冰箱模式**: 
   - `strict`: 严格模式，只推荐能用现有食材做的
   - `flexible`: 灵活模式，可建议补充食材
4. **多轮对话**: 系统会记住对话历史，可以连续提问

## 🎉 开始你的烹饪之旅！

现在你已经准备好使用AI食谱推荐官了！尝试问问它：

- "今天吃什么？"
- "用鸡蛋能做什么菜？"
- "推荐一道适合新手的菜"
- "我想吃辣的"

祝你使用愉快！ 🍳👨‍🍳
