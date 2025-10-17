# 🚀 运行说明

## 前提条件

确保你有：
1. Python 3.9 或更高版本
2. OpenAI API Key

## 快速启动（3步）

### 步骤 1: 安装依赖

```bash
pip install -r requirements.txt
```

### 步骤 2: 配置环境变量

创建 `.env` 文件：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的 OpenAI API Key：

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

### 步骤 3: 运行程序

```bash
python main.py
```

## 就是这么简单！

启动后，你会看到欢迎界面，然后就可以开始对话了：

```
🍳 欢迎使用AI食谱推荐官 - 小厨神 🍳
请输入你的用户名: 

# 输入你的名字，比如: Alice

Alice > 你好
小厨神 > 你好！我是小厨神...
```

## 常用操作

```bash
# 告诉偏好
"我喜欢川菜"
"我对花生过敏"

# 管理冰箱
"我冰箱有鸡蛋、番茄、葱"

# 获取推荐
"今天吃什么？"
"推荐一道川菜"

# 查看信息
profile   # 查看个人档案
fridge    # 查看冰箱
help      # 查看帮助

# 退出
exit
```

## 运行API服务器

如果想要使用API而不是CLI：

```bash
python api_server.py
```

然后访问 http://localhost:8000/docs 查看API文档

## 运行示例

```bash
python example_usage.py
```

选择示例查看不同功能演示。

## 故障排除

### 问题: "OpenAI API key not found"
**解决**: 确保 `.env` 文件中设置了 `OPENAI_API_KEY=sk-...`

### 问题: 依赖安装失败
**解决**: 
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 问题: 端口被占用
**解决**: 修改 `api_server.py` 中的端口号，或关闭占用8000端口的程序

## 需要帮助？

查看以下文档：
- [README.md](README.md) - 完整项目说明
- [QUICK_START.md](QUICK_START.md) - 快速开始指南
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构设计

祝使用愉快！🍳
