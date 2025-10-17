"""
检索器测试
"""
import pytest
from src.retrievers.recipe_retriever import Recipe, RecipeRetriever


def test_recipe_model():
    """测试食谱模型"""
    recipe = Recipe(
        name="番茄炒蛋",
        cuisine="家常菜",
        ingredients=["鸡蛋", "番茄", "盐"],
        steps=["打蛋", "切番茄", "炒制"],
        difficulty="简单",
        cooking_time=10,
        tags=["快手菜"]
    )
    
    assert recipe.name == "番茄炒蛋"
    assert len(recipe.ingredients) == 3
    
    # 转换为字典
    recipe_dict = recipe.to_dict()
    assert recipe_dict["name"] == "番茄炒蛋"
    
    # 转换为文本
    text = recipe.to_text()
    assert "番茄炒蛋" in text
    assert "鸡蛋" in text


def test_recipe_retriever_add():
    """测试添加食谱"""
    retriever = RecipeRetriever(collection_name="test_recipes")
    
    recipe = Recipe(
        name="测试菜",
        cuisine="测试",
        ingredients=["食材1"],
        steps=["步骤1"],
        difficulty="简单",
        cooking_time=10
    )
    
    # 添加单个食谱
    retriever.add_recipe(recipe)
    
    # 搜索
    results = retriever.search("测试菜", k=1)
    assert len(results) > 0


@pytest.mark.skip(reason="需要实际的OpenAI API")
def test_recipe_retriever_search():
    """测试搜索功能"""
    retriever = RecipeRetriever(collection_name="test_recipes_search")
    
    # 添加测试食谱
    recipes = [
        Recipe(
            name="宫保鸡丁",
            cuisine="川菜",
            ingredients=["鸡肉", "花生", "辣椒"],
            steps=["切肉", "炒制"],
            difficulty="中等",
            cooking_time=25,
            tags=["辣"]
        ),
        Recipe(
            name="番茄炒蛋",
            cuisine="家常菜",
            ingredients=["鸡蛋", "番茄"],
            steps=["打蛋", "炒制"],
            difficulty="简单",
            cooking_time=10,
            tags=["快手"]
        )
    ]
    
    retriever.add_recipes(recipes)
    
    # 搜索川菜
    results = retriever.search_by_cuisine("川菜", k=2)
    assert len(results) > 0
    assert any(r.name == "宫保鸡丁" for r in results)
    
    # 根据食材搜索
    results = retriever.search_by_ingredients(["鸡蛋", "番茄"], k=2)
    assert len(results) > 0
