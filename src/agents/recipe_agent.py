"""
Agent核心逻辑
基于LangChain实现智能食谱推荐Agent
"""
from typing import List, Dict, Any, Optional, AsyncIterator
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, SystemMessage
from langchain.callbacks.base import BaseCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import asyncio
import json

from src.prompts.templates import create_agent_prompt, create_recommendation_prompt, create_preference_prompt
from src.tools.recipe_tools import get_recipe_tools
from src.memory.short_term_memory import ShortTermMemory, session_manager
from src.memory.long_term_memory import long_term_memory
from src.fridge.fridge_manager import fridge_manager, FridgeMode
from src.retrievers.recipe_retriever import recipe_retriever
from config.settings import settings


class StreamingCallbackHandler(BaseCallbackHandler):
    """流式输出回调处理器"""
    
    def __init__(self):
        self.tokens = []
        self.is_streaming = False
    
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        """处理新token"""
        self.tokens.append(token)
        self.is_streaming = True
    
    def get_full_response(self) -> str:
        """获取完整响应"""
        return "".join(self.tokens)
    
    def clear(self) -> None:
        """清空tokens"""
        self.tokens = []
        self.is_streaming = False


class RecipeRecommenderAgent:
    """
    AI食谱推荐Agent
    整合所有模块，提供智能食谱推荐服务
    """
    
    def __init__(
        self,
        user_id: str,
        streaming: bool = True,
        temperature: float = 0.7
    ):
        """
        初始化Agent
        
        Args:
            user_id: 用户ID
            streaming: 是否启用流式输出
            temperature: 模型温度
        """
        self.user_id = user_id
        self.streaming = streaming
        
        # 初始化LLM
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=temperature,
            openai_api_key=settings.openai_api_key,
            streaming=streaming
        )
        
        # 初始化记忆
        self.short_memory = session_manager.get_or_create_session(user_id)
        
        # 获取长期记忆（用户偏好）
        self.user_preference = long_term_memory.get_preference(user_id)
        
        # 获取或创建冰箱
        self.fridge = fridge_manager.get_or_create_fridge(
            user_id, 
            FridgeMode(settings.fridge_mode)
        )
        
        # 初始化工具
        self.tools = get_recipe_tools()
        
        # 创建Agent
        self.agent = self._create_agent()
        
        # 创建Agent执行器
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True,
            max_iterations=5,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def _create_agent(self):
        """创建OpenAI Functions Agent"""
        prompt = create_agent_prompt()
        return create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=prompt
        )
    
    def _get_fridge_mode_text(self) -> str:
        """获取冰箱模式文本"""
        if self.fridge.mode == FridgeMode.STRICT:
            return "strict (仅使用现有食材)"
        return "flexible (可建议补充食材)"
    
    async def arun(self, user_input: str) -> str:
        """
        异步运行Agent（支持流式输出）
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent响应
        """
        # 检索相关食谱
        relevant_recipes = await self._retrieve_relevant_recipes(user_input)
        
        # 构建输入
        agent_input = {
            "input": user_input,
            "chat_history": self.short_memory.get_messages(),
            "fridge_mode": self._get_fridge_mode_text()
        }
        
        # 执行Agent
        try:
            result = await self.agent_executor.ainvoke(agent_input)
            response = result["output"]
            
            # 如果涉及推荐，整合检索结果
            if "推荐" in user_input or "做什么" in user_input or "菜" in user_input:
                response = await self._enhance_with_rag(response, relevant_recipes)
            
            # 保存到短期记忆
            self.short_memory.add_message(user_input, response)
            
            return response
        
        except Exception as e:
            error_msg = f"抱歉，处理您的请求时出错了: {str(e)}"
            self.short_memory.add_message(user_input, error_msg)
            return error_msg
    
    def run(self, user_input: str) -> str:
        """
        同步运行Agent
        
        Args:
            user_input: 用户输入
            
        Returns:
            Agent响应
        """
        return asyncio.run(self.arun(user_input))
    
    async def _retrieve_relevant_recipes(self, query: str) -> List[Dict]:
        """
        检索相关食谱
        
        Args:
            query: 查询文本
            
        Returns:
            食谱列表
        """
        try:
            # 优化查询
            optimized_query = query
            if self.user_preference:
                # 结合用户偏好优化查询
                pref_text = f"{' '.join(self.user_preference.cuisines)} {' '.join(self.user_preference.favorite_ingredients)}"
                optimized_query = f"{query} {pref_text}"
            
            # 检索食谱
            recipes = recipe_retriever.search(optimized_query, k=5)
            
            # 根据冰箱食材过滤
            if self.fridge.ingredients:
                scored_recipes = []
                for recipe in recipes:
                    compatibility = self.fridge.check_recipe_compatibility(
                        recipe.ingredients
                    )
                    scored_recipes.append({
                        "recipe": recipe,
                        "match_rate": compatibility["match_rate"],
                        "compatible": compatibility["compatible"]
                    })
                
                # 按匹配度排序
                scored_recipes.sort(key=lambda x: x["match_rate"], reverse=True)
                
                # 如果是strict模式，只返回兼容的
                if self.fridge.mode == FridgeMode.STRICT:
                    scored_recipes = [r for r in scored_recipes if r["compatible"]]
                
                return [r["recipe"].to_dict() for r in scored_recipes[:3]]
            
            return [r.to_dict() for r in recipes[:3]]
        
        except Exception as e:
            print(f"检索食谱失败: {e}")
            return []
    
    async def _enhance_with_rag(
        self, 
        response: str, 
        recipes: List[Dict]
    ) -> str:
        """
        使用RAG增强响应
        
        Args:
            response: 原始响应
            recipes: 检索到的食谱
            
        Returns:
            增强后的响应
        """
        if not recipes:
            return response
        
        # 构建推荐提示
        user_pref_text = "无特定偏好"
        if self.user_preference:
            user_pref_text = self.user_preference.to_text()
        
        fridge_ingredients = self.fridge.get_ingredient_names()
        
        # 格式化食谱信息
        recipes_text = "\n\n".join([
            f"【{recipe['name']}】\n"
            f"菜系: {recipe['cuisine']}\n"
            f"食材: {', '.join(recipe['ingredients'])}\n"
            f"难度: {recipe['difficulty']}\n"
            f"时间: {recipe['cooking_time']}分钟\n"
            f"做法: {' -> '.join(recipe['steps'][:3])}..."
            for recipe in recipes
        ])
        
        # 使用推荐prompt
        recommendation_prompt = create_recommendation_prompt()
        formatted_prompt = recommendation_prompt.format(
            user_preferences=user_pref_text,
            available_ingredients=", ".join(fridge_ingredients) if fridge_ingredients else "冰箱为空",
            fridge_mode=self._get_fridge_mode_text(),
            retrieved_recipes=recipes_text
        )
        
        # 生成增强推荐
        try:
            enhanced_response = await self.llm.ainvoke([
                SystemMessage(content="你是专业的食谱推荐助手"),
                HumanMessage(content=formatted_prompt)
            ])
            
            return enhanced_response.content
        except:
            return response
    
    async def stream_response(self, user_input: str) -> AsyncIterator[str]:
        """
        流式输出响应
        
        Args:
            user_input: 用户输入
            
        Yields:
            响应的token流
        """
        callback = StreamingCallbackHandler()
        
        # 创建支持流式的LLM
        streaming_llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.7,
            openai_api_key=settings.openai_api_key,
            streaming=True,
            callbacks=[callback]
        )
        
        # 构建输入
        agent_input = {
            "input": user_input,
            "chat_history": self.short_memory.get_messages(),
            "fridge_mode": self._get_fridge_mode_text()
        }
        
        try:
            # 异步执行
            response_task = asyncio.create_task(
                self.agent_executor.ainvoke(agent_input)
            )
            
            # 流式输出tokens
            while not response_task.done():
                if callback.tokens:
                    token = callback.tokens.pop(0)
                    yield token
                await asyncio.sleep(0.01)
            
            # 输出剩余tokens
            while callback.tokens:
                yield callback.tokens.pop(0)
            
            # 获取完整结果
            result = await response_task
            full_response = result["output"]
            
            # 保存到记忆
            self.short_memory.add_message(user_input, full_response)
            
        except Exception as e:
            error_msg = f"流式输出时出错: {str(e)}"
            yield error_msg
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        return self.short_memory.export_to_dict()["messages"]
    
    def clear_session(self) -> None:
        """清空会话"""
        self.short_memory.clear()
    
    def get_user_profile(self) -> Dict[str, Any]:
        """获取用户画像"""
        profile = {
            "user_id": self.user_id,
            "preferences": self.user_preference.to_dict() if self.user_preference else None,
            "fridge": self.fridge.to_dict(),
            "conversation_count": len(self.short_memory.get_messages())
        }
        return profile
