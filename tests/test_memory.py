"""
记忆模块测试
"""
import pytest
from src.memory.short_term_memory import ShortTermMemory
from src.memory.long_term_memory import LongTermMemory, UserPreference


def test_short_term_memory():
    """测试短期记忆"""
    memory = ShortTermMemory(user_id="test_user", window_size=5)
    
    # 添加消息
    memory.add_message("你好", "你好！我是小厨神")
    memory.add_message("推荐一道菜", "我推荐番茄炒蛋")
    
    # 获取消息
    messages = memory.get_messages()
    assert len(messages) == 4  # 2对话 = 4条消息
    
    # 获取上下文字符串
    context = memory.get_context_string()
    assert "你好" in context
    assert "小厨神" in context


def test_short_term_memory_window():
    """测试短期记忆窗口"""
    memory = ShortTermMemory(user_id="test_user", window_size=2)
    
    # 添加多条消息
    for i in range(5):
        memory.add_message(f"消息{i}", f"回复{i}")
    
    # 应该只保留最近2条对话（4条消息）
    messages = memory.get_messages()
    assert len(messages) <= 4


def test_user_preference():
    """测试用户偏好数据模型"""
    pref = UserPreference(
        user_id="test_user",
        cuisines=["川菜", "粤菜"],
        allergies=["花生"],
        favorite_ingredients=["鸡蛋", "番茄"]
    )
    
    # 转换为字典
    pref_dict = pref.to_dict()
    assert pref_dict["user_id"] == "test_user"
    assert "川菜" in pref_dict["cuisines"]
    assert "花生" in pref_dict["allergies"]
    
    # 转换为文本
    text = pref.to_text()
    assert "川菜" in text
    assert "花生" in text


def test_long_term_memory():
    """测试长期记忆"""
    ltm = LongTermMemory()
    
    # 创建用户偏好
    pref = UserPreference(
        user_id="test_user_ltm",
        cuisines=["川菜"],
        allergies=["海鲜"]
    )
    
    # 保存偏好
    ltm.save_preference(pref)
    
    # 获取偏好
    retrieved_pref = ltm.get_preference("test_user_ltm")
    assert retrieved_pref is not None
    assert retrieved_pref.user_id == "test_user_ltm"
    assert "川菜" in retrieved_pref.cuisines
    
    # 更新偏好
    updated_pref = ltm.update_preference(
        "test_user_ltm",
        cuisines=["粤菜"],
        favorite_dishes=["宫保鸡丁"]
    )
    assert "川菜" in updated_pref.cuisines  # 原有的保留
    assert "粤菜" in updated_pref.cuisines  # 新的合并进来
    
    # 删除偏好
    ltm.delete_preference("test_user_ltm")
    deleted_pref = ltm.get_preference("test_user_ltm")
    assert deleted_pref is None
