"""
长期记忆模块
使用向量数据库(ChromaDB)存储用户偏好和历史记录
"""
from typing import List, Dict, Any, Optional
import json
import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from datetime import datetime
from config.settings import settings
import os


class UserPreference:
    """用户偏好数据模型"""
    
    def __init__(
        self,
        user_id: str,
        cuisines: Optional[List[str]] = None,
        allergies: Optional[List[str]] = None,
        dislikes: Optional[List[str]] = None,
        favorite_ingredients: Optional[List[str]] = None,
        favorite_dishes: Optional[List[str]] = None,
        dietary_restrictions: Optional[List[str]] = None,
        spice_level: str = "medium"
    ):
        self.user_id = user_id
        self.cuisines = cuisines or []
        self.allergies = allergies or []
        self.dislikes = dislikes or []
        self.favorite_ingredients = favorite_ingredients or []
        self.favorite_dishes = favorite_dishes or []
        self.dietary_restrictions = dietary_restrictions or []
        self.spice_level = spice_level
        self.updated_at = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "user_id": self.user_id,
            "cuisines": self.cuisines,
            "allergies": self.allergies,
            "dislikes": self.dislikes,
            "favorite_ingredients": self.favorite_ingredients,
            "favorite_dishes": self.favorite_dishes,
            "dietary_restrictions": self.dietary_restrictions,
            "spice_level": self.spice_level,
            "updated_at": self.updated_at
        }
    
    def to_text(self) -> str:
        """转换为文本描述（用于向量化）"""
        parts = []
        if self.cuisines:
            parts.append(f"喜欢的菜系: {', '.join(self.cuisines)}")
        if self.allergies:
            parts.append(f"过敏: {', '.join(self.allergies)}")
        if self.dislikes:
            parts.append(f"不喜欢: {', '.join(self.dislikes)}")
        if self.favorite_ingredients:
            parts.append(f"喜欢的食材: {', '.join(self.favorite_ingredients)}")
        if self.favorite_dishes:
            parts.append(f"喜欢的菜品: {', '.join(self.favorite_dishes)}")
        if self.dietary_restrictions:
            parts.append(f"饮食限制: {', '.join(self.dietary_restrictions)}")
        parts.append(f"辣度偏好: {self.spice_level}")
        
        return " | ".join(parts)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'UserPreference':
        """从字典创建"""
        return cls(
            user_id=data["user_id"],
            cuisines=data.get("cuisines", []),
            allergies=data.get("allergies", []),
            dislikes=data.get("dislikes", []),
            favorite_ingredients=data.get("favorite_ingredients", []),
            favorite_dishes=data.get("favorite_dishes", []),
            dietary_restrictions=data.get("dietary_restrictions", []),
            spice_level=data.get("spice_level", "medium")
        )


class LongTermMemory:
    """
    长期记忆管理器
    使用ChromaDB向量数据库存储用户偏好
    """
    
    def __init__(self, persist_directory: Optional[str] = None):
        """
        初始化长期记忆
        
        Args:
            persist_directory: 持久化目录
        """
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        
        # 确保目录存在
        os.makedirs(self.persist_directory, exist_ok=True)
        
        # 初始化Embedding模型
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # 初始化ChromaDB客户端
        self.chroma_client = chromadb.PersistentClient(
            path=self.persist_directory
        )
        
        # 用户偏好集合
        self.preference_collection = "user_preferences"
        self._init_preference_store()
    
    def _init_preference_store(self):
        """初始化偏好存储"""
        try:
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.preference_collection,
                embedding_function=self.embeddings,
            )
        except Exception as e:
            print(f"初始化向量存储时出错: {e}")
            # 如果集合不存在，创建它
            self.vectorstore = Chroma(
                client=self.chroma_client,
                collection_name=self.preference_collection,
                embedding_function=self.embeddings,
            )
    
    def save_preference(self, preference: UserPreference) -> None:
        """
        保存用户偏好
        
        Args:
            preference: 用户偏好对象
        """
        # 创建文档
        doc = Document(
            page_content=preference.to_text(),
            metadata={
                "user_id": preference.user_id,
                "type": "preference",
                "data": json.dumps(preference.to_dict(), ensure_ascii=False),
                "updated_at": preference.updated_at
            }
        )
        
        # 删除旧的偏好（如果存在）
        try:
            self.vectorstore._collection.delete(
                where={"user_id": preference.user_id, "type": "preference"}
            )
        except:
            pass
        
        # 添加新偏好
        self.vectorstore.add_documents([doc])
    
    def get_preference(self, user_id: str) -> Optional[UserPreference]:
        """
        获取用户偏好
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户偏好对象，如果不存在返回None
        """
        try:
            results = self.vectorstore._collection.get(
                where={"user_id": user_id, "type": "preference"},
                limit=1
            )
            
            if results and results['metadatas']:
                metadata = results['metadatas'][0]
                data = json.loads(metadata['data'])
                return UserPreference.from_dict(data)
        except Exception as e:
            print(f"获取用户偏好时出错: {e}")
        
        return None
    
    def update_preference(
        self, 
        user_id: str, 
        **updates
    ) -> UserPreference:
        """
        更新用户偏好
        
        Args:
            user_id: 用户ID
            **updates: 要更新的字段
            
        Returns:
            更新后的用户偏好
        """
        # 获取现有偏好或创建新的
        preference = self.get_preference(user_id)
        if not preference:
            preference = UserPreference(user_id=user_id)
        
        # 更新字段（合并列表）
        for key, value in updates.items():
            if hasattr(preference, key):
                current_value = getattr(preference, key)
                if isinstance(current_value, list) and isinstance(value, list):
                    # 合并列表并去重
                    merged = list(set(current_value + value))
                    setattr(preference, key, merged)
                else:
                    setattr(preference, key, value)
        
        preference.updated_at = datetime.now().isoformat()
        
        # 保存
        self.save_preference(preference)
        return preference
    
    def delete_preference(self, user_id: str) -> None:
        """删除用户偏好"""
        try:
            self.vectorstore._collection.delete(
                where={"user_id": user_id, "type": "preference"}
            )
        except Exception as e:
            print(f"删除用户偏好时出错: {e}")
    
    def search_similar_preferences(
        self, 
        query: str, 
        k: int = 5
    ) -> List[UserPreference]:
        """
        搜索相似的用户偏好（用于推荐相似用户喜欢的菜品）
        
        Args:
            query: 查询文本
            k: 返回数量
            
        Returns:
            相似的用户偏好列表
        """
        docs = self.vectorstore.similarity_search(query, k=k)
        preferences = []
        
        for doc in docs:
            if doc.metadata.get("type") == "preference":
                try:
                    data = json.loads(doc.metadata["data"])
                    preferences.append(UserPreference.from_dict(data))
                except:
                    continue
        
        return preferences


# 全局长期记忆实例
long_term_memory = LongTermMemory()
