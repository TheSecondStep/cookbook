"""
RAG检索增强模块
检索本地食谱数据库
"""
from typing import List, Dict, Any, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers.document_compressors import LLMChainExtractor
from langchain_openai import ChatOpenAI
import json
import os
from config.settings import settings


class Recipe:
    """食谱数据模型"""
    
    def __init__(
        self,
        name: str,
        cuisine: str,
        ingredients: List[str],
        steps: List[str],
        difficulty: str,
        cooking_time: int,
        tags: Optional[List[str]] = None,
        nutrition: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.cuisine = cuisine
        self.ingredients = ingredients
        self.steps = steps
        self.difficulty = difficulty
        self.cooking_time = cooking_time
        self.tags = tags or []
        self.nutrition = nutrition or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "cuisine": self.cuisine,
            "ingredients": self.ingredients,
            "steps": self.steps,
            "difficulty": self.difficulty,
            "cooking_time": self.cooking_time,
            "tags": self.tags,
            "nutrition": self.nutrition
        }
    
    def to_text(self) -> str:
        """转换为文本描述（用于向量化）"""
        text = f"""
菜名: {self.name}
菜系: {self.cuisine}
食材: {', '.join(self.ingredients)}
难度: {self.difficulty}
时间: {self.cooking_time}分钟
标签: {', '.join(self.tags)}
做法: {' '.join(self.steps)}
        """.strip()
        return text
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipe':
        """从字典创建"""
        return cls(
            name=data["name"],
            cuisine=data["cuisine"],
            ingredients=data["ingredients"],
            steps=data["steps"],
            difficulty=data["difficulty"],
            cooking_time=data["cooking_time"],
            tags=data.get("tags", []),
            nutrition=data.get("nutrition", {})
        )


class RecipeRetriever:
    """
    食谱检索器
    使用RAG技术检索相关食谱
    """
    
    def __init__(
        self,
        persist_directory: Optional[str] = None,
        collection_name: str = "recipes"
    ):
        """
        初始化检索器
        
        Args:
            persist_directory: 向量数据库持久化目录
            collection_name: 集合名称
        """
        self.persist_directory = persist_directory or settings.chroma_persist_directory
        self.collection_name = collection_name
        
        # 初始化Embedding模型
        self.embeddings = OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key
        )
        
        # 初始化向量存储
        self.vectorstore = None
        self._init_vectorstore()
    
    def _init_vectorstore(self):
        """初始化向量存储"""
        try:
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
        except Exception as e:
            print(f"初始化向量存储失败: {e}")
            # 创建新的向量存储
            self.vectorstore = Chroma(
                persist_directory=self.persist_directory,
                collection_name=self.collection_name,
                embedding_function=self.embeddings
            )
    
    def add_recipe(self, recipe: Recipe) -> None:
        """
        添加食谱到向量数据库
        
        Args:
            recipe: 食谱对象
        """
        doc = Document(
            page_content=recipe.to_text(),
            metadata={
                "name": recipe.name,
                "cuisine": recipe.cuisine,
                "difficulty": recipe.difficulty,
                "cooking_time": recipe.cooking_time,
                "data": json.dumps(recipe.to_dict(), ensure_ascii=False)
            }
        )
        self.vectorstore.add_documents([doc])
    
    def add_recipes(self, recipes: List[Recipe]) -> None:
        """
        批量添加食谱
        
        Args:
            recipes: 食谱列表
        """
        docs = [
            Document(
                page_content=recipe.to_text(),
                metadata={
                    "name": recipe.name,
                    "cuisine": recipe.cuisine,
                    "difficulty": recipe.difficulty,
                    "cooking_time": recipe.cooking_time,
                    "data": json.dumps(recipe.to_dict(), ensure_ascii=False)
                }
            )
            for recipe in recipes
        ]
        self.vectorstore.add_documents(docs)
    
    def search(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Recipe]:
        """
        搜索食谱
        
        Args:
            query: 搜索查询
            k: 返回结果数量
            filter_dict: 过滤条件，如 {"cuisine": "川菜"}
        
        Returns:
            食谱列表
        """
        if filter_dict:
            docs = self.vectorstore.similarity_search(
                query, 
                k=k, 
                filter=filter_dict
            )
        else:
            docs = self.vectorstore.similarity_search(query, k=k)
        
        recipes = []
        for doc in docs:
            try:
                data = json.loads(doc.metadata["data"])
                recipes.append(Recipe.from_dict(data))
            except:
                continue
        
        return recipes
    
    def search_by_ingredients(
        self,
        ingredients: List[str],
        k: int = 5
    ) -> List[Recipe]:
        """
        根据食材搜索食谱
        
        Args:
            ingredients: 食材列表
            k: 返回结果数量
        
        Returns:
            食谱列表
        """
        query = f"使用食材: {', '.join(ingredients)}"
        return self.search(query, k=k)
    
    def search_by_cuisine(
        self,
        cuisine: str,
        k: int = 5
    ) -> List[Recipe]:
        """
        根据菜系搜索食谱
        
        Args:
            cuisine: 菜系名称
            k: 返回结果数量
        
        Returns:
            食谱列表
        """
        return self.search(
            query=f"{cuisine}的菜",
            k=k,
            filter_dict={"cuisine": cuisine}
        )
    
    def get_contextual_retriever(self, llm: Optional[ChatOpenAI] = None):
        """
        创建带上下文压缩的检索器
        提高检索质量
        
        Args:
            llm: 语言模型
        
        Returns:
            上下文压缩检索器
        """
        if not llm:
            llm = ChatOpenAI(
                model=settings.openai_model,
                temperature=0,
                openai_api_key=settings.openai_api_key
            )
        
        compressor = LLMChainExtractor.from_llm(llm)
        return ContextualCompressionRetriever(
            base_compressor=compressor,
            base_retriever=self.vectorstore.as_retriever(search_kwargs={"k": 10})
        )
    
    def load_recipes_from_json(self, filepath: str) -> int:
        """
        从JSON文件加载食谱
        
        Args:
            filepath: JSON文件路径
        
        Returns:
            加载的食谱数量
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            recipes = [Recipe.from_dict(r) for r in data]
            self.add_recipes(recipes)
            return len(recipes)
        except Exception as e:
            print(f"加载食谱失败: {e}")
            return 0


# 创建全局检索器实例
recipe_retriever = RecipeRetriever()
