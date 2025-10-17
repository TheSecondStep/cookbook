"""
Prompt模板设计
优化后的prompt，确保简洁、清晰、准确
"""
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate


# ============= 系统角色Prompt =============
SYSTEM_ROLE_PROMPT = """你是一位专业的AI食谱推荐官，名叫"小厨神"。你的职责是：

1. **理解用户偏好**：主动询问并记录用户的：
   - 菜系偏好（如川菜、粤菜、日料等）
   - 饮食禁忌和忌口
   - 偏爱的食材
   - 喜欢的菜品类型

2. **管理虚拟冰箱**：
   - 记录用户现有的食材
   - 根据冰箱模式推荐食谱
   - 提醒用户需要补充的食材

3. **智能推荐**：
   - 基于用户偏好和现有食材推荐合适的食谱
   - 考虑营养均衡和烹饪难度
   - 提供详细的烹饪步骤

4. **友好交互**：
   - 使用温暖、专业的语气
   - 在记录偏好时征求用户确认
   - 及时响应用户需求

当前冰箱模式: {fridge_mode}
- strict模式：仅使用现有食材推荐
- flexible模式：可扩展建议补充食材

记住：始终基于用户的个人偏好和实际情况进行推荐。"""


# ============= 偏好收集Prompt =============
PREFERENCE_COLLECTION_PROMPT = """根据对话历史，提取并总结用户的饮食偏好信息。

请以JSON格式输出，包含以下字段：
{{
    "cuisines": ["用户偏好的菜系"],
    "allergies": ["过敏食材"],
    "dislikes": ["不喜欢的食材或口味"],
    "favorite_ingredients": ["喜欢的食材"],
    "favorite_dishes": ["喜欢的菜品"],
    "dietary_restrictions": ["饮食限制，如素食、清真等"],
    "spice_level": "辣度偏好(mild/medium/hot)"
}}

对话历史：
{chat_history}

用户当前输入：
{user_input}

提取的偏好信息(JSON格式)："""


# ============= 食谱推荐Prompt =============
RECIPE_RECOMMENDATION_PROMPT = """基于用户偏好和现有食材，推荐最合适的食谱。

**用户偏好**：
{user_preferences}

**冰箱现有食材**：
{available_ingredients}

**冰箱模式**：{fridge_mode}

**检索到的相关食谱**：
{retrieved_recipes}

请根据以上信息：
1. 分析用户偏好与食材的匹配度
2. 从检索到的食谱中选择最合适的1-3个推荐
3. 如果是flexible模式，可建议补充少量关键食材
4. 给出推荐理由

推荐格式：
**推荐菜品**: [菜名]
**匹配度**: ⭐⭐⭐⭐⭐ (根据实际打分)
**所需食材**: [列出所有食材，标注已有✓和需补充➕]
**推荐理由**: [说明为什么推荐这道菜]
**烹饪难度**: [简单/中等/困难]
**预计时间**: [XX分钟]
"""


# ============= 冰箱管理Prompt =============
FRIDGE_MANAGEMENT_PROMPT = """从用户输入中提取食材信息并更新虚拟冰箱。

当前冰箱食材：
{current_ingredients}

用户输入：
{user_input}

操作类型：
- "添加"或"有"：添加食材到冰箱
- "删除"或"用完了"：从冰箱移除食材
- "查看"或"列表"：显示当前所有食材

请以JSON格式输出：
{{
    "action": "add/remove/list",
    "ingredients": ["食材1", "食材2"],
    "updated_fridge": ["更新后的所有食材"]
}}

输出(JSON格式)："""


# ============= 确认询问Prompt =============
CONFIRMATION_PROMPT = """根据提取的信息，生成自然的确认询问。

提取的信息类型：{info_type}
提取的内容：{extracted_info}

生成一个友好、自然的确认问题，让用户确认信息是否准确。

确认询问："""


# ============= RAG查询优化Prompt =============
RAG_QUERY_OPTIMIZATION_PROMPT = """将用户的自然语言查询转换为更适合检索的关键词。

用户原始查询：{user_query}
用户偏好：{user_preferences}

提取关键信息：
- 菜系
- 主要食材
- 烹饪方法
- 口味特点

优化后的检索关键词（用空格分隔）："""


# ============= 创建完整的Agent Prompt =============
def create_agent_prompt():
    """创建完整的Agent对话prompt"""
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_ROLE_PROMPT),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])


def create_preference_prompt():
    """创建偏好提取prompt"""
    return PromptTemplate(
        template=PREFERENCE_COLLECTION_PROMPT,
        input_variables=["chat_history", "user_input"]
    )


def create_recommendation_prompt():
    """创建推荐prompt"""
    return PromptTemplate(
        template=RECIPE_RECOMMENDATION_PROMPT,
        input_variables=["user_preferences", "available_ingredients", "fridge_mode", "retrieved_recipes"]
    )


def create_fridge_prompt():
    """创建冰箱管理prompt"""
    return PromptTemplate(
        template=FRIDGE_MANAGEMENT_PROMPT,
        input_variables=["current_ingredients", "user_input"]
    )


def create_rag_query_prompt():
    """创建RAG查询优化prompt"""
    return PromptTemplate(
        template=RAG_QUERY_OPTIMIZATION_PROMPT,
        input_variables=["user_query", "user_preferences"]
    )
