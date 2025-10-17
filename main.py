"""
主程序入口
提供CLI交互界面
"""
import asyncio
import sys
from typing import Optional
from src.agents.recipe_agent import RecipeRecommenderAgent
from src.retrievers.recipe_retriever import recipe_retriever
from src.utils.logger import app_logger
from src.utils.helpers import format_recipe_display
from config.settings import settings
import os


class RecipeAssistantCLI:
    """命令行交互界面"""
    
    def __init__(self):
        self.agent: Optional[RecipeRecommenderAgent] = None
        self.user_id: Optional[str] = None
    
    def print_welcome(self):
        """打印欢迎信息"""
        print("\n" + "="*60)
        print("🍳 欢迎使用AI食谱推荐官 - 小厨神 🍳")
        print("="*60)
        print("\n我可以帮你:")
        print("  📝 记录你的饮食偏好（菜系、忌口、喜好等）")
        print("  🥘 管理你的虚拟冰箱（添加/删除食材）")
        print("  🔍 根据偏好和食材推荐食谱")
        print("  👨‍🍳 提供详细的烹饪指导")
        print("\n特色功能:")
        print("  💡 支持两种模式: strict(仅用现有食材) / flexible(可建议补充)")
        print("  🧠 长期记忆你的偏好，越用越懂你")
        print("  ⚡ 流式输出，实时响应")
        print("\n常用命令:")
        print("  'help' - 查看帮助")
        print("  'profile' - 查看个人档案")
        print("  'fridge' - 查看冰箱")
        print("  'clear' - 清空当前会话")
        print("  'exit' 或 'quit' - 退出程序")
        print("="*60 + "\n")
    
    def print_help(self):
        """打印帮助信息"""
        print("\n" + "="*60)
        print("📚 使用指南")
        print("="*60)
        print("\n🔸 记录偏好:")
        print("  - '我喜欢川菜和粤菜'")
        print("  - '我对花生过敏'")
        print("  - '我不吃香菜'")
        print("  - '我喜欢鸡蛋和番茄'")
        print("\n🔸 管理冰箱:")
        print("  - '我冰箱有鸡蛋、番茄、土豆'")
        print("  - '添加食材: 牛肉、洋葱'")
        print("  - '删除食材: 鸡蛋'")
        print("  - '查看冰箱' 或 'fridge'")
        print("  - '设置冰箱模式为strict/flexible'")
        print("\n🔸 获取推荐:")
        print("  - '今天吃什么？'")
        print("  - '推荐一道川菜'")
        print("  - '用现有食材能做什么？'")
        print("  - '推荐简单快手的菜'")
        print("\n🔸 系统命令:")
        print("  - 'profile' - 查看你的偏好和冰箱状态")
        print("  - 'clear' - 清空当前对话记录")
        print("  - 'exit' / 'quit' - 退出程序")
        print("="*60 + "\n")
    
    async def initialize(self):
        """初始化系统"""
        print("🔧 正在初始化...")
        
        # 加载食谱数据
        recipe_file = "data/recipes/sample_recipes.json"
        if os.path.exists(recipe_file):
            try:
                count = recipe_retriever.load_recipes_from_json(recipe_file)
                print(f"✅ 已加载 {count} 个食谱")
            except Exception as e:
                print(f"⚠️  加载食谱失败: {e}")
        
        # 获取用户ID
        self.user_id = input("\n请输入你的用户名（用于识别和记忆你的偏好）: ").strip()
        if not self.user_id:
            self.user_id = "default_user"
        
        # 创建Agent
        try:
            self.agent = RecipeRecommenderAgent(
                user_id=self.user_id,
                streaming=settings.stream_enabled
            )
            print(f"✅ 欢迎回来, {self.user_id}!\n")
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            sys.exit(1)
    
    def handle_command(self, command: str) -> bool:
        """
        处理系统命令
        
        Returns:
            True表示继续运行，False表示退出
        """
        command = command.lower().strip()
        
        if command in ['exit', 'quit', '退出']:
            print("\n👋 再见！期待下次为你服务~")
            return False
        
        elif command == 'help' or command == '帮助':
            self.print_help()
        
        elif command == 'profile' or command == '档案':
            profile = self.agent.get_user_profile()
            print("\n" + "="*60)
            print("👤 个人档案")
            print("="*60)
            print(f"用户ID: {profile['user_id']}")
            print(f"\n📋 偏好信息:")
            if profile['preferences']:
                pref = profile['preferences']
                if pref.get('cuisines'):
                    print(f"  喜欢的菜系: {', '.join(pref['cuisines'])}")
                if pref.get('allergies'):
                    print(f"  过敏食材: {', '.join(pref['allergies'])}")
                if pref.get('dislikes'):
                    print(f"  不喜欢: {', '.join(pref['dislikes'])}")
                if pref.get('favorite_ingredients'):
                    print(f"  喜欢的食材: {', '.join(pref['favorite_ingredients'])}")
                if pref.get('favorite_dishes'):
                    print(f"  喜欢的菜品: {', '.join(pref['favorite_dishes'])}")
                print(f"  辣度偏好: {pref.get('spice_level', 'medium')}")
            else:
                print("  暂无偏好信息")
            
            print(f"\n📦 冰箱状态:")
            fridge = profile['fridge']
            print(f"  模式: {fridge['mode']}")
            if fridge['ingredients']:
                ingredients = [ing['name'] for ing in fridge['ingredients']]
                print(f"  食材({len(ingredients)}): {', '.join(ingredients)}")
            else:
                print("  冰箱是空的")
            
            print(f"\n💬 对话轮次: {profile['conversation_count']}")
            print("="*60 + "\n")
        
        elif command == 'fridge' or command == '冰箱':
            fridge = self.agent.fridge
            print(f"\n📦 {fridge}")
        
        elif command == 'clear' or command == '清空':
            self.agent.clear_session()
            print("✅ 已清空当前会话记录\n")
        
        else:
            print("❌ 未知命令，输入 'help' 查看帮助\n")
        
        return True
    
    async def chat_loop(self):
        """主对话循环"""
        while True:
            try:
                # 获取用户输入
                user_input = input(f"{self.user_id} > ").strip()
                
                if not user_input:
                    continue
                
                # 检查是否是系统命令
                if user_input.lower() in ['exit', 'quit', 'help', 'profile', 'fridge', 'clear', '退出', '帮助', '档案', '冰箱', '清空']:
                    should_continue = self.handle_command(user_input)
                    if not should_continue:
                        break
                    continue
                
                # 处理用户输入
                print("\n小厨神 > ", end="", flush=True)
                
                if settings.stream_enabled:
                    # 流式输出
                    full_response = ""
                    async for token in self.agent.stream_response(user_input):
                        print(token, end="", flush=True)
                        full_response += token
                    print("\n")
                else:
                    # 非流式输出
                    response = await self.agent.arun(user_input)
                    print(response + "\n")
            
            except KeyboardInterrupt:
                print("\n\n👋 再见！期待下次为你服务~")
                break
            
            except Exception as e:
                app_logger.error(f"对话循环出错: {e}")
                print(f"\n❌ 出错了: {e}\n")
    
    async def run(self):
        """运行CLI程序"""
        self.print_welcome()
        await self.initialize()
        await self.chat_loop()


async def main():
    """主函数"""
    # 确保必要的目录存在
    os.makedirs("data/vectordb", exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 运行CLI
    cli = RecipeAssistantCLI()
    await cli.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 程序已退出")
        sys.exit(0)
