"""
使用示例脚本
演示如何使用AI食谱推荐官的各种功能
"""
import asyncio
from src.agents.recipe_agent import RecipeRecommenderAgent
from src.retrievers.recipe_retriever import recipe_retriever
from src.utils.helpers import format_recipe_display


async def example_basic_chat():
    """示例1: 基本对话"""
    print("\n" + "="*60)
    print("示例1: 基本对话")
    print("="*60)
    
    agent = RecipeRecommenderAgent(user_id="example_user", streaming=False)
    
    # 简单问候
    response = await agent.arun("你好，小厨神！")
    print(f"用户: 你好，小厨神！")
    print(f"小厨神: {response}\n")


async def example_preference_management():
    """示例2: 偏好管理"""
    print("\n" + "="*60)
    print("示例2: 管理用户偏好")
    print("="*60)
    
    agent = RecipeRecommenderAgent(user_id="preference_user", streaming=False)
    
    # 告诉偏好
    queries = [
        "我喜欢川菜和粤菜",
        "我对海鲜过敏",
        "我不喜欢香菜",
        "我喜欢的食材有鸡蛋、番茄、土豆"
    ]
    
    for query in queries:
        response = await agent.arun(query)
        print(f"用户: {query}")
        print(f"小厨神: {response}\n")
    
    # 查看档案
    profile = agent.get_user_profile()
    print("用户档案:")
    print(f"  偏好: {profile.get('preferences')}")


async def example_fridge_management():
    """示例3: 冰箱管理"""
    print("\n" + "="*60)
    print("示例3: 虚拟冰箱管理")
    print("="*60)
    
    agent = RecipeRecommenderAgent(user_id="fridge_user", streaming=False)
    
    # 添加食材
    response = await agent.arun("我冰箱有鸡蛋、番茄、葱、姜、蒜、盐、油")
    print(f"用户: 我冰箱有鸡蛋、番茄、葱、姜、蒜、盐、油")
    print(f"小厨神: {response}\n")
    
    # 查看冰箱
    response = await agent.arun("查看冰箱")
    print(f"用户: 查看冰箱")
    print(f"小厨神: {response}\n")
    
    # 设置模式
    response = await agent.arun("设置冰箱模式为strict")
    print(f"用户: 设置冰箱模式为strict")
    print(f"小厨神: {response}\n")


async def example_recipe_recommendation():
    """示例4: 食谱推荐"""
    print("\n" + "="*60)
    print("示例4: 智能食谱推荐")
    print("="*60)
    
    # 加载食谱数据
    recipe_retriever.load_recipes_from_json("data/recipes/sample_recipes.json")
    
    agent = RecipeRecommenderAgent(user_id="recommendation_user", streaming=False)
    
    # 设置偏好和冰箱
    await agent.arun("我喜欢川菜，喜欢吃辣的")
    await agent.arun("我冰箱有鸡胸肉、花生米、干辣椒、花椒、葱、姜、蒜")
    
    # 请求推荐
    response = await agent.arun("根据我冰箱的食材，推荐一道川菜")
    print(f"用户: 根据我冰箱的食材，推荐一道川菜")
    print(f"小厨神: {response}\n")


async def example_streaming():
    """示例5: 流式输出"""
    print("\n" + "="*60)
    print("示例5: 流式对话（实时输出）")
    print("="*60)
    
    agent = RecipeRecommenderAgent(user_id="stream_user", streaming=True)
    
    print("用户: 推荐一道简单快手的菜")
    print("小厨神: ", end="", flush=True)
    
    async for token in agent.stream_response("推荐一道简单快手的菜"):
        print(token, end="", flush=True)
    
    print("\n")


async def example_recipe_search():
    """示例6: 直接搜索食谱"""
    print("\n" + "="*60)
    print("示例6: 直接搜索食谱数据库")
    print("="*60)
    
    # 加载食谱
    count = recipe_retriever.load_recipes_from_json("data/recipes/sample_recipes.json")
    print(f"已加载 {count} 个食谱\n")
    
    # 按菜系搜索
    print("搜索川菜:")
    recipes = recipe_retriever.search_by_cuisine("川菜", k=2)
    for recipe in recipes:
        print(f"  - {recipe.name} (难度: {recipe.difficulty}, 时间: {recipe.cooking_time}分钟)")
    print()
    
    # 按食材搜索
    print("搜索包含'鸡蛋'的菜:")
    recipes = recipe_retriever.search_by_ingredients(["鸡蛋"], k=2)
    for recipe in recipes:
        print(f"  - {recipe.name}")
        print(f"    食材: {', '.join(recipe.ingredients[:5])}...")
    print()


async def example_conversation_flow():
    """示例7: 完整对话流程"""
    print("\n" + "="*60)
    print("示例7: 完整对话流程演示")
    print("="*60)
    
    # 加载食谱
    recipe_retriever.load_recipes_from_json("data/recipes/sample_recipes.json")
    
    agent = RecipeRecommenderAgent(user_id="flow_user", streaming=False)
    
    conversation = [
        "你好，我想做饭但不知道做什么",
        "我喜欢吃辣的，特别喜欢川菜",
        "我对花生过敏，需要避免",
        "我冰箱有豆腐、牛肉末、豆瓣酱、花椒",
        "推荐一道菜吧",
        "听起来不错！具体怎么做？",
        "谢谢！下次再咨询你"
    ]
    
    for user_msg in conversation:
        response = await agent.arun(user_msg)
        print(f"👤 用户: {user_msg}")
        print(f"🤖 小厨神: {response}\n")
        await asyncio.sleep(1)  # 模拟思考时间


async def main():
    """运行所有示例"""
    print("\n" + "🍳"*30)
    print("AI食谱推荐官 - 使用示例演示")
    print("🍳"*30)
    
    examples = [
        ("基本对话", example_basic_chat),
        ("偏好管理", example_preference_management),
        ("冰箱管理", example_fridge_management),
        ("食谱推荐", example_recipe_recommendation),
        ("流式输出", example_streaming),
        ("食谱搜索", example_recipe_search),
        ("对话流程", example_conversation_flow),
    ]
    
    print("\n可用示例:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    
    print("\n选择要运行的示例 (输入数字，或'all'运行全部, 'q'退出): ", end="")
    choice = input().strip().lower()
    
    if choice == 'q':
        print("退出")
        return
    
    if choice == 'all':
        for name, func in examples:
            print(f"\n{'='*60}")
            print(f"运行示例: {name}")
            print(f"{'='*60}")
            try:
                await func()
            except Exception as e:
                print(f"❌ 示例运行出错: {e}")
            
            print("\n按Enter继续...")
            input()
    
    elif choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(examples):
            name, func = examples[idx]
            print(f"\n运行示例: {name}")
            try:
                await func()
            except Exception as e:
                print(f"❌ 示例运行出错: {e}")
        else:
            print("无效的选择")
    
    else:
        print("无效的输入")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n程序已退出")
