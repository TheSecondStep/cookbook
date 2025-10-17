"""
工具模块
定义Agent可以使用的各种工具
"""
from typing import Optional, List, Dict, Any
from langchain.tools import BaseTool, StructuredTool, tool
from langchain.pydantic_v1 import BaseModel, Field
from src.memory.long_term_memory import long_term_memory, UserPreference
from src.fridge.fridge_manager import fridge_manager, FridgeMode
import json


# ============= 工具输入Schema =============

class PreferenceSaveInput(BaseModel):
    """保存偏好工具的输入"""
    user_id: str = Field(description="用户ID")
    cuisines: Optional[List[str]] = Field(default=None, description="菜系偏好列表")
    allergies: Optional[List[str]] = Field(default=None, description="过敏食材列表")
    dislikes: Optional[List[str]] = Field(default=None, description="不喜欢的食材列表")
    favorite_ingredients: Optional[List[str]] = Field(default=None, description="喜欢的食材列表")
    favorite_dishes: Optional[List[str]] = Field(default=None, description="喜欢的菜品列表")
    dietary_restrictions: Optional[List[str]] = Field(default=None, description="饮食限制列表")
    spice_level: Optional[str] = Field(default="medium", description="辣度偏好: mild/medium/hot")


class FridgeOperationInput(BaseModel):
    """冰箱操作工具的输入"""
    user_id: str = Field(description="用户ID")
    action: str = Field(description="操作类型: add/remove/list/clear")
    ingredients: Optional[List[str]] = Field(default=None, description="食材名称列表")


class FridgeModeInput(BaseModel):
    """冰箱模式设置的输入"""
    user_id: str = Field(description="用户ID")
    mode: str = Field(description="冰箱模式: strict/flexible")


# ============= 工具函数实现 =============

@tool
def save_user_preference(
    user_id: str,
    cuisines: Optional[List[str]] = None,
    allergies: Optional[List[str]] = None,
    dislikes: Optional[List[str]] = None,
    favorite_ingredients: Optional[List[str]] = None,
    favorite_dishes: Optional[List[str]] = None,
    dietary_restrictions: Optional[List[str]] = None,
    spice_level: str = "medium"
) -> str:
    """
    保存或更新用户的饮食偏好。
    
    Args:
        user_id: 用户ID
        cuisines: 喜欢的菜系，如["川菜", "粤菜"]
        allergies: 过敏的食材，如["花生", "海鲜"]
        dislikes: 不喜欢的食材或口味
        favorite_ingredients: 喜欢的食材
        favorite_dishes: 喜欢的菜品
        dietary_restrictions: 饮食限制，如["素食", "清真"]
        spice_level: 辣度偏好，mild/medium/hot
    
    Returns:
        操作结果描述
    """
    try:
        updates = {}
        if cuisines:
            updates["cuisines"] = cuisines
        if allergies:
            updates["allergies"] = allergies
        if dislikes:
            updates["dislikes"] = dislikes
        if favorite_ingredients:
            updates["favorite_ingredients"] = favorite_ingredients
        if favorite_dishes:
            updates["favorite_dishes"] = favorite_dishes
        if dietary_restrictions:
            updates["dietary_restrictions"] = dietary_restrictions
        if spice_level:
            updates["spice_level"] = spice_level
        
        preference = long_term_memory.update_preference(user_id, **updates)
        
        return f"✅ 已保存用户偏好: {preference.to_text()}"
    except Exception as e:
        return f"❌ 保存偏好失败: {str(e)}"


@tool
def get_user_preference(user_id: str) -> str:
    """
    获取用户的饮食偏好信息。
    
    Args:
        user_id: 用户ID
    
    Returns:
        用户偏好的JSON字符串或提示信息
    """
    try:
        preference = long_term_memory.get_preference(user_id)
        if preference:
            return json.dumps(preference.to_dict(), ensure_ascii=False, indent=2)
        return "该用户还没有保存偏好信息"
    except Exception as e:
        return f"❌ 获取偏好失败: {str(e)}"


@tool
def manage_fridge(
    user_id: str,
    action: str,
    ingredients: Optional[List[str]] = None
) -> str:
    """
    管理用户的虚拟冰箱食材。
    
    Args:
        user_id: 用户ID
        action: 操作类型 - "add"(添加), "remove"(移除), "list"(列出), "clear"(清空)
        ingredients: 食材名称列表（add和remove时需要）
    
    Returns:
        操作结果描述
    """
    try:
        fridge = fridge_manager.get_or_create_fridge(user_id)
        
        if action == "add":
            if not ingredients:
                return "❌ 请提供要添加的食材列表"
            added = fridge.add_ingredients(ingredients)
            return f"✅ 已添加 {len(added)} 种食材到冰箱: {', '.join(ingredients)}\n当前冰箱: {fridge}"
        
        elif action == "remove":
            if not ingredients:
                return "❌ 请提供要移除的食材列表"
            count = fridge.remove_ingredients(ingredients)
            return f"✅ 已移除 {count} 种食材: {', '.join(ingredients)}\n当前冰箱: {fridge}"
        
        elif action == "list":
            if not fridge.ingredients:
                return "冰箱目前是空的，请先添加食材"
            return f"📦 {fridge}"
        
        elif action == "clear":
            fridge.clear()
            return "✅ 已清空冰箱"
        
        else:
            return f"❌ 未知操作: {action}。支持的操作: add, remove, list, clear"
    
    except Exception as e:
        return f"❌ 冰箱操作失败: {str(e)}"


@tool
def set_fridge_mode(user_id: str, mode: str) -> str:
    """
    设置用户冰箱的工作模式。
    
    Args:
        user_id: 用户ID
        mode: 冰箱模式 - "strict"(仅用现有食材) 或 "flexible"(可建议补充食材)
    
    Returns:
        操作结果描述
    """
    try:
        fridge = fridge_manager.get_or_create_fridge(user_id)
        
        if mode.lower() == "strict":
            fridge.set_mode(FridgeMode.STRICT)
            return "✅ 冰箱模式已设置为 STRICT - 仅使用现有食材推荐"
        elif mode.lower() == "flexible":
            fridge.set_mode(FridgeMode.FLEXIBLE)
            return "✅ 冰箱模式已设置为 FLEXIBLE - 可建议补充少量食材"
        else:
            return f"❌ 未知模式: {mode}。支持的模式: strict, flexible"
    
    except Exception as e:
        return f"❌ 设置模式失败: {str(e)}"


@tool
def check_recipe_compatibility(
    user_id: str,
    recipe_ingredients: List[str]
) -> str:
    """
    检查食谱与冰箱食材的兼容性。
    
    Args:
        user_id: 用户ID
        recipe_ingredients: 食谱所需的食材列表
    
    Returns:
        兼容性分析结果的JSON字符串
    """
    try:
        fridge = fridge_manager.get_or_create_fridge(user_id)
        result = fridge.check_recipe_compatibility(recipe_ingredients)
        
        # 格式化输出
        output = {
            "兼容性": "✅ 兼容" if result["compatible"] else "⚠️ 不兼容",
            "匹配度": f"{result['match_rate'] * 100:.1f}%",
            "已有食材": result["available_ingredients"],
            "需补充食材": result["missing_ingredients"],
            "冰箱模式": result["mode"]
        }
        
        return json.dumps(output, ensure_ascii=False, indent=2)
    
    except Exception as e:
        return f"❌ 检查兼容性失败: {str(e)}"


# ============= 工具列表 =============

def get_recipe_tools() -> List[BaseTool]:
    """获取所有食谱相关工具"""
    return [
        save_user_preference,
        get_user_preference,
        manage_fridge,
        set_fridge_mode,
        check_recipe_compatibility
    ]
