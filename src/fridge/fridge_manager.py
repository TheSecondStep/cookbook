"""
冰箱管理模块
虚拟冰箱，管理用户现有食材
"""
from typing import List, Dict, Set, Optional
from datetime import datetime
import json
from enum import Enum


class FridgeMode(Enum):
    """冰箱模式枚举"""
    STRICT = "strict"  # 仅使用现有食材
    FLEXIBLE = "flexible"  # 可扩展建议补充食材


class Ingredient:
    """食材数据模型"""
    
    def __init__(
        self,
        name: str,
        quantity: Optional[str] = None,
        unit: Optional[str] = None,
        added_at: Optional[str] = None
    ):
        self.name = name
        self.quantity = quantity
        self.unit = unit
        self.added_at = added_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "quantity": self.quantity,
            "unit": self.unit,
            "added_at": self.added_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Ingredient':
        return cls(
            name=data["name"],
            quantity=data.get("quantity"),
            unit=data.get("unit"),
            added_at=data.get("added_at")
        )
    
    def __str__(self) -> str:
        if self.quantity and self.unit:
            return f"{self.name} ({self.quantity}{self.unit})"
        return self.name


class VirtualFridge:
    """
    虚拟冰箱类
    管理用户的食材库存
    """
    
    def __init__(self, user_id: str, mode: FridgeMode = FridgeMode.FLEXIBLE):
        """
        初始化虚拟冰箱
        
        Args:
            user_id: 用户ID
            mode: 冰箱模式
        """
        self.user_id = user_id
        self.mode = mode
        self.ingredients: Dict[str, Ingredient] = {}
        self.updated_at = datetime.now().isoformat()
    
    def add_ingredient(
        self, 
        name: str, 
        quantity: Optional[str] = None, 
        unit: Optional[str] = None
    ) -> Ingredient:
        """
        添加食材
        
        Args:
            name: 食材名称
            quantity: 数量
            unit: 单位
            
        Returns:
            添加的食材对象
        """
        ingredient = Ingredient(name, quantity, unit)
        self.ingredients[name] = ingredient
        self.updated_at = datetime.now().isoformat()
        return ingredient
    
    def add_ingredients(self, names: List[str]) -> List[Ingredient]:
        """
        批量添加食材
        
        Args:
            names: 食材名称列表
            
        Returns:
            添加的食材列表
        """
        added = []
        for name in names:
            ingredient = self.add_ingredient(name)
            added.append(ingredient)
        return added
    
    def remove_ingredient(self, name: str) -> bool:
        """
        移除食材
        
        Args:
            name: 食材名称
            
        Returns:
            是否成功移除
        """
        if name in self.ingredients:
            del self.ingredients[name]
            self.updated_at = datetime.now().isoformat()
            return True
        return False
    
    def remove_ingredients(self, names: List[str]) -> int:
        """
        批量移除食材
        
        Args:
            names: 食材名称列表
            
        Returns:
            成功移除的数量
        """
        count = 0
        for name in names:
            if self.remove_ingredient(name):
                count += 1
        return count
    
    def has_ingredient(self, name: str) -> bool:
        """检查是否有某个食材"""
        return name in self.ingredients
    
    def has_all_ingredients(self, names: List[str]) -> bool:
        """检查是否有所有指定的食材"""
        return all(name in self.ingredients for name in names)
    
    def get_ingredient(self, name: str) -> Optional[Ingredient]:
        """获取食材"""
        return self.ingredients.get(name)
    
    def list_ingredients(self) -> List[Ingredient]:
        """列出所有食材"""
        return list(self.ingredients.values())
    
    def get_ingredient_names(self) -> List[str]:
        """获取所有食材名称"""
        return list(self.ingredients.keys())
    
    def clear(self) -> None:
        """清空冰箱"""
        self.ingredients.clear()
        self.updated_at = datetime.now().isoformat()
    
    def set_mode(self, mode: FridgeMode) -> None:
        """设置冰箱模式"""
        self.mode = mode
        self.updated_at = datetime.now().isoformat()
    
    def check_recipe_compatibility(
        self, 
        recipe_ingredients: List[str]
    ) -> Dict[str, any]:
        """
        检查食谱兼容性
        
        Args:
            recipe_ingredients: 食谱所需食材列表
            
        Returns:
            包含匹配信息的字典
        """
        available = []
        missing = []
        
        for ingredient in recipe_ingredients:
            if self.has_ingredient(ingredient):
                available.append(ingredient)
            else:
                missing.append(ingredient)
        
        match_rate = len(available) / len(recipe_ingredients) if recipe_ingredients else 0
        
        result = {
            "compatible": len(missing) == 0 if self.mode == FridgeMode.STRICT else match_rate > 0.5,
            "match_rate": match_rate,
            "available_ingredients": available,
            "missing_ingredients": missing,
            "mode": self.mode.value
        }
        
        return result
    
    def to_dict(self) -> Dict:
        """导出为字典"""
        return {
            "user_id": self.user_id,
            "mode": self.mode.value,
            "ingredients": [ing.to_dict() for ing in self.ingredients.values()],
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'VirtualFridge':
        """从字典创建"""
        fridge = cls(
            user_id=data["user_id"],
            mode=FridgeMode(data.get("mode", "flexible"))
        )
        for ing_data in data.get("ingredients", []):
            ingredient = Ingredient.from_dict(ing_data)
            fridge.ingredients[ingredient.name] = ingredient
        fridge.updated_at = data.get("updated_at", datetime.now().isoformat())
        return fridge
    
    def __str__(self) -> str:
        """字符串表示"""
        if not self.ingredients:
            return "冰箱是空的"
        
        ingredients_str = ", ".join(str(ing) for ing in self.ingredients.values())
        return f"冰箱食材 ({self.mode.value}模式): {ingredients_str}"


class FridgeManager:
    """
    冰箱管理器
    管理多个用户的虚拟冰箱
    """
    
    def __init__(self):
        self._fridges: Dict[str, VirtualFridge] = {}
    
    def get_or_create_fridge(
        self, 
        user_id: str, 
        mode: FridgeMode = FridgeMode.FLEXIBLE
    ) -> VirtualFridge:
        """获取或创建用户冰箱"""
        if user_id not in self._fridges:
            self._fridges[user_id] = VirtualFridge(user_id, mode)
        return self._fridges[user_id]
    
    def get_fridge(self, user_id: str) -> Optional[VirtualFridge]:
        """获取用户冰箱"""
        return self._fridges.get(user_id)
    
    def remove_fridge(self, user_id: str) -> None:
        """删除用户冰箱"""
        if user_id in self._fridges:
            del self._fridges[user_id]
    
    def save_to_file(self, filepath: str) -> None:
        """保存所有冰箱到文件"""
        data = {
            user_id: fridge.to_dict() 
            for user_id, fridge in self._fridges.items()
        }
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_from_file(self, filepath: str) -> None:
        """从文件加载冰箱"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self._fridges = {
                user_id: VirtualFridge.from_dict(fridge_data)
                for user_id, fridge_data in data.items()
            }
        except FileNotFoundError:
            pass


# 全局冰箱管理器实例
fridge_manager = FridgeManager()
