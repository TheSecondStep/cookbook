"""
短期记忆模块
使用LangChain的ConversationBufferWindowMemory实现会话上下文管理
"""
from typing import Optional, List, Dict, Any
from langchain.memory import ConversationBufferWindowMemory, ConversationSummaryBufferMemory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from config.settings import settings
import json


class ShortTermMemory:
    """
    短期记忆管理器
    负责维护当前会话的对话历史
    """
    
    def __init__(
        self, 
        user_id: str,
        max_token_limit: int = 2000,
        window_size: Optional[int] = None
    ):
        """
        初始化短期记忆
        
        Args:
            user_id: 用户ID
            max_token_limit: 最大token限制
            window_size: 窗口大小（消息数量）
        """
        self.user_id = user_id
        self.window_size = window_size or settings.max_memory_messages
        
        # 使用ConversationBufferWindowMemory保持最近N条消息
        self.memory = ConversationBufferWindowMemory(
            k=self.window_size,
            memory_key="chat_history",
            return_messages=True,
            input_key="input",
            output_key="output"
        )
        
        # 可选：使用SummaryMemory进行更智能的压缩
        self.summary_memory = None
        if max_token_limit:
            llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0.3,
                openai_api_key=settings.openai_api_key
            )
            self.summary_memory = ConversationSummaryBufferMemory(
                llm=llm,
                max_token_limit=max_token_limit,
                memory_key="chat_history",
                return_messages=True
            )
    
    def add_message(self, user_message: str, ai_message: str) -> None:
        """
        添加对话消息
        
        Args:
            user_message: 用户消息
            ai_message: AI回复
        """
        self.memory.save_context(
            {"input": user_message},
            {"output": ai_message}
        )
        
        if self.summary_memory:
            self.summary_memory.save_context(
                {"input": user_message},
                {"output": ai_message}
            )
    
    def get_messages(self) -> List[BaseMessage]:
        """获取历史消息"""
        return self.memory.load_memory_variables({})["chat_history"]
    
    def get_summary(self) -> Optional[str]:
        """获取对话摘要（如果使用了summary memory）"""
        if self.summary_memory:
            memory_vars = self.summary_memory.load_memory_variables({})
            return memory_vars.get("history", "")
        return None
    
    def clear(self) -> None:
        """清空短期记忆"""
        self.memory.clear()
        if self.summary_memory:
            self.summary_memory.clear()
    
    def get_context_string(self) -> str:
        """获取格式化的上下文字符串"""
        messages = self.get_messages()
        context_lines = []
        
        for msg in messages:
            if isinstance(msg, HumanMessage):
                context_lines.append(f"用户: {msg.content}")
            elif isinstance(msg, AIMessage):
                context_lines.append(f"小厨神: {msg.content}")
        
        return "\n".join(context_lines)
    
    def export_to_dict(self) -> Dict[str, Any]:
        """导出为字典格式"""
        messages = self.get_messages()
        return {
            "user_id": self.user_id,
            "messages": [
                {
                    "role": "user" if isinstance(msg, HumanMessage) else "assistant",
                    "content": msg.content
                }
                for msg in messages
            ],
            "summary": self.get_summary()
        }


class SessionMemoryManager:
    """
    会话记忆管理器
    管理多个用户的短期记忆
    """
    
    def __init__(self):
        self._sessions: Dict[str, ShortTermMemory] = {}
    
    def get_or_create_session(self, user_id: str) -> ShortTermMemory:
        """获取或创建用户会话"""
        if user_id not in self._sessions:
            self._sessions[user_id] = ShortTermMemory(user_id)
        return self._sessions[user_id]
    
    def remove_session(self, user_id: str) -> None:
        """删除用户会话"""
        if user_id in self._sessions:
            del self._sessions[user_id]
    
    def list_active_sessions(self) -> List[str]:
        """列出活跃会话"""
        return list(self._sessions.keys())
    
    def clear_all(self) -> None:
        """清空所有会话"""
        self._sessions.clear()


# 全局会话管理器实例
session_manager = SessionMemoryManager()
