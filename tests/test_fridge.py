"""
冰箱模块测试
"""
import pytest
from src.fridge.fridge_manager import VirtualFridge, FridgeMode, Ingredient


def test_ingredient():
    """测试食材模型"""
    ing = Ingredient(name="鸡蛋", quantity="3", unit="个")
    assert ing.name == "鸡蛋"
    assert ing.quantity == "3"
    assert ing.unit == "个"
    assert "鸡蛋" in str(ing)


def test_virtual_fridge_add():
    """测试添加食材"""
    fridge = VirtualFridge(user_id="test_user")
    
    # 添加单个食材
    fridge.add_ingredient("鸡蛋", "3", "个")
    assert fridge.has_ingredient("鸡蛋")
    assert len(fridge.ingredients) == 1
    
    # 批量添加
    fridge.add_ingredients(["番茄", "葱", "姜"])
    assert len(fridge.ingredients) == 4


def test_virtual_fridge_remove():
    """测试移除食材"""
    fridge = VirtualFridge(user_id="test_user")
    fridge.add_ingredients(["鸡蛋", "番茄", "葱"])
    
    # 移除单个
    result = fridge.remove_ingredient("鸡蛋")
    assert result is True
    assert not fridge.has_ingredient("鸡蛋")
    
    # 批量移除
    count = fridge.remove_ingredients(["番茄", "姜"])  # 姜不存在
    assert count == 1  # 只移除了番茄


def test_virtual_fridge_compatibility():
    """测试食谱兼容性检查"""
    fridge = VirtualFridge(user_id="test_user", mode=FridgeMode.STRICT)
    fridge.add_ingredients(["鸡蛋", "番茄", "盐", "油"])
    
    # 完全匹配
    recipe_ingredients = ["鸡蛋", "番茄", "盐"]
    result = fridge.check_recipe_compatibility(recipe_ingredients)
    assert result["compatible"] is True
    assert result["match_rate"] == 1.0
    
    # 部分匹配（strict模式下不兼容）
    recipe_ingredients = ["鸡蛋", "番茄", "糖", "醋"]
    result = fridge.check_recipe_compatibility(recipe_ingredients)
    assert result["compatible"] is False
    assert "糖" in result["missing_ingredients"]


def test_virtual_fridge_modes():
    """测试冰箱模式"""
    fridge = VirtualFridge(user_id="test_user", mode=FridgeMode.STRICT)
    assert fridge.mode == FridgeMode.STRICT
    
    # 切换模式
    fridge.set_mode(FridgeMode.FLEXIBLE)
    assert fridge.mode == FridgeMode.FLEXIBLE
    
    # flexible模式下，部分匹配也兼容
    fridge.add_ingredients(["鸡蛋", "番茄"])
    recipe_ingredients = ["鸡蛋", "番茄", "糖", "盐"]
    result = fridge.check_recipe_compatibility(recipe_ingredients)
    assert result["compatible"] is True  # 匹配率>50%


def test_virtual_fridge_persistence():
    """测试冰箱数据持久化"""
    fridge = VirtualFridge(user_id="test_user")
    fridge.add_ingredients(["鸡蛋", "番茄", "葱"])
    
    # 导出
    data = fridge.to_dict()
    assert data["user_id"] == "test_user"
    assert len(data["ingredients"]) == 3
    
    # 导入
    restored_fridge = VirtualFridge.from_dict(data)
    assert restored_fridge.user_id == "test_user"
    assert len(restored_fridge.ingredients) == 3
    assert restored_fridge.has_ingredient("鸡蛋")
