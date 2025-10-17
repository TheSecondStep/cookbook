"""
辅助工具函数
"""
from typing import List, Dict, Any
import json
import re


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """
    从文本中提取JSON
    
    Args:
        text: 包含JSON的文本
        
    Returns:
        解析后的字典
    """
    # 尝试直接解析
    try:
        return json.loads(text)
    except:
        pass
    
    # 尝试提取JSON代码块
    json_pattern = r'```json\s*(.*?)\s*```'
    matches = re.findall(json_pattern, text, re.DOTALL)
    if matches:
        try:
            return json.loads(matches[0])
        except:
            pass
    
    # 尝试提取花括号内容
    brace_pattern = r'\{.*?\}'
    matches = re.findall(brace_pattern, text, re.DOTALL)
    for match in matches:
        try:
            return json.loads(match)
        except:
            continue
    
    return {}


def format_recipe_display(recipe: Dict[str, Any]) -> str:
    """
    格式化食谱显示
    
    Args:
        recipe: 食谱字典
        
    Returns:
        格式化的文本
    """
    output = f"""
╔══════════════════════════════════════╗
║  📖 {recipe['name']}
╚══════════════════════════════════════╝

🏷️  菜系: {recipe['cuisine']}
⏱️  时间: {recipe['cooking_time']}分钟
📊 难度: {recipe['difficulty']}

🥘 食材:
"""
    for i, ingredient in enumerate(recipe['ingredients'], 1):
        output += f"   {i}. {ingredient}\n"
    
    output += "\n👨‍🍳 步骤:\n"
    for i, step in enumerate(recipe['steps'], 1):
        output += f"   {i}. {step}\n"
    
    if recipe.get('tags'):
        output += f"\n🏷️  标签: {', '.join(recipe['tags'])}\n"
    
    return output


def calculate_match_score(
    recipe_ingredients: List[str],
    available_ingredients: List[str],
    user_preferences: Dict[str, Any]
) -> float:
    """
    计算食谱匹配分数
    
    Args:
        recipe_ingredients: 食谱所需食材
        available_ingredients: 可用食材
        user_preferences: 用户偏好
        
    Returns:
        匹配分数 (0-1)
    """
    score = 0.0
    
    # 食材匹配度 (权重40%)
    ingredient_match = len(set(recipe_ingredients) & set(available_ingredients)) / len(recipe_ingredients)
    score += ingredient_match * 0.4
    
    # 用户偏好匹配度 (权重60%)
    if user_preferences:
        # 检查是否有过敏或不喜欢的食材
        allergies = user_preferences.get('allergies', [])
        dislikes = user_preferences.get('dislikes', [])
        
        if any(allergy in recipe_ingredients for allergy in allergies):
            return 0.0  # 包含过敏食材，直接返回0
        
        dislike_penalty = sum(1 for dislike in dislikes if dislike in recipe_ingredients)
        score -= dislike_penalty * 0.1
        
        # 检查是否有喜欢的食材
        favorites = user_preferences.get('favorite_ingredients', [])
        favorite_bonus = sum(1 for fav in favorites if fav in recipe_ingredients)
        score += min(favorite_bonus * 0.2, 0.6)
    
    return max(0.0, min(1.0, score))


def parse_ingredient_quantity(ingredient_text: str) -> Dict[str, Any]:
    """
    解析食材数量
    
    Args:
        ingredient_text: 食材文本，如"鸡蛋 3个"
        
    Returns:
        包含name, quantity, unit的字典
    """
    # 正则匹配：名称 + 数量 + 单位
    pattern = r'^(.*?)\s*(\d+(?:\.\d+)?)\s*(\S+)?$'
    match = re.match(pattern, ingredient_text.strip())
    
    if match:
        return {
            "name": match.group(1).strip(),
            "quantity": match.group(2),
            "unit": match.group(3) or ""
        }
    
    return {
        "name": ingredient_text.strip(),
        "quantity": None,
        "unit": None
    }


def sanitize_input(text: str, max_length: int = 500) -> str:
    """
    清理用户输入
    
    Args:
        text: 输入文本
        max_length: 最大长度
        
    Returns:
        清理后的文本
    """
    # 移除多余空白
    text = ' '.join(text.split())
    
    # 限制长度
    if len(text) > max_length:
        text = text[:max_length]
    
    return text.strip()
