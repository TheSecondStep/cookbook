"""
Agent测试
"""
import pytest
import asyncio
from src.agents.recipe_agent import RecipeRecommenderAgent


@pytest.fixture
def agent():
    """创建测试Agent"""
    return RecipeRecommenderAgent(user_id="test_user", streaming=False)


@pytest.mark.asyncio
async def test_agent_initialization(agent):
    """测试Agent初始化"""
    assert agent.user_id == "test_user"
    assert agent.llm is not None
    assert agent.tools is not None


@pytest.mark.asyncio
async def test_agent_chat(agent):
    """测试基本对话"""
    response = await agent.arun("你好")
    assert isinstance(response, str)
    assert len(response) > 0


@pytest.mark.asyncio
async def test_agent_preference_save(agent):
    """测试保存偏好"""
    response = await agent.arun("我喜欢川菜，对花生过敏")
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_agent_fridge_management(agent):
    """测试冰箱管理"""
    response = await agent.arun("我冰箱有鸡蛋、番茄、葱")
    assert isinstance(response, str)
    
    # 验证冰箱中有食材
    assert len(agent.fridge.ingredients) > 0


@pytest.mark.asyncio
async def test_agent_memory(agent):
    """测试记忆功能"""
    # 第一轮对话
    await agent.arun("我喜欢吃辣的")
    
    # 第二轮对话应该记住之前的内容
    response = await agent.arun("推荐一道菜")
    assert isinstance(response, str)
    
    # 验证对话历史
    history = agent.get_conversation_history()
    assert len(history) >= 2


def test_agent_profile(agent):
    """测试用户档案"""
    profile = agent.get_user_profile()
    assert profile["user_id"] == "test_user"
    assert "preferences" in profile
    assert "fridge" in profile


def test_agent_clear_session(agent):
    """测试清空会话"""
    agent.short_memory.add_message("test", "response")
    assert len(agent.short_memory.get_messages()) > 0
    
    agent.clear_session()
    assert len(agent.short_memory.get_messages()) == 0
