"""
FastAPI服务器
提供RESTful API和WebSocket接口
支持多用户并发访问
"""
from fastapi import FastAPI, WebSocket, HTTPException, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
from datetime import datetime

from src.agents.recipe_agent import RecipeRecommenderAgent
from src.retrievers.recipe_retriever import recipe_retriever
from src.memory.long_term_memory import long_term_memory
from src.fridge.fridge_manager import fridge_manager
from src.utils.logger import app_logger
from config.settings import settings


# 创建FastAPI应用
app = FastAPI(
    title="AI食谱推荐官 API",
    description="智能食谱推荐系统API",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============= 数据模型 =============

class ChatRequest(BaseModel):
    """聊天请求"""
    user_id: str
    message: str


class ChatResponse(BaseModel):
    """聊天响应"""
    user_id: str
    response: str
    timestamp: str


class PreferenceRequest(BaseModel):
    """偏好设置请求"""
    user_id: str
    cuisines: Optional[List[str]] = None
    allergies: Optional[List[str]] = None
    dislikes: Optional[List[str]] = None
    favorite_ingredients: Optional[List[str]] = None
    favorite_dishes: Optional[List[str]] = None
    dietary_restrictions: Optional[List[str]] = None
    spice_level: Optional[str] = "medium"


class FridgeRequest(BaseModel):
    """冰箱操作请求"""
    user_id: str
    action: str  # add, remove, list, clear
    ingredients: Optional[List[str]] = None


class RecipeSearchRequest(BaseModel):
    """食谱搜索请求"""
    query: str
    cuisine: Optional[str] = None
    k: int = 5


# ============= Agent管理 =============

class AgentManager:
    """Agent管理器，管理多用户并发"""
    
    def __init__(self):
        self.agents: Dict[str, RecipeRecommenderAgent] = {}
        self.locks: Dict[str, asyncio.Lock] = {}
    
    def get_agent(self, user_id: str) -> RecipeRecommenderAgent:
        """获取或创建用户Agent"""
        if user_id not in self.agents:
            self.agents[user_id] = RecipeRecommenderAgent(
                user_id=user_id,
                streaming=False
            )
            self.locks[user_id] = asyncio.Lock()
        return self.agents[user_id]
    
    def get_lock(self, user_id: str) -> asyncio.Lock:
        """获取用户锁"""
        if user_id not in self.locks:
            self.locks[user_id] = asyncio.Lock()
        return self.locks[user_id]
    
    async def remove_agent(self, user_id: str):
        """移除用户Agent"""
        if user_id in self.agents:
            del self.agents[user_id]
        if user_id in self.locks:
            del self.locks[user_id]


agent_manager = AgentManager()


# ============= API端点 =============

@app.on_event("startup")
async def startup_event():
    """启动时加载食谱数据"""
    app_logger.info("正在启动API服务器...")
    
    # 加载示例食谱
    try:
        count = recipe_retriever.load_recipes_from_json("data/recipes/sample_recipes.json")
        app_logger.info(f"已加载 {count} 个食谱")
    except Exception as e:
        app_logger.warning(f"加载食谱失败: {e}")


@app.get("/")
async def root():
    """根路径"""
    return {
        "message": "AI食谱推荐官 API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    聊天接口
    """
    try:
        agent = agent_manager.get_agent(request.user_id)
        lock = agent_manager.get_lock(request.user_id)
        
        async with lock:
            response = await agent.arun(request.message)
        
        return ChatResponse(
            user_id=request.user_id,
            response=response,
            timestamp=datetime.now().isoformat()
        )
    
    except Exception as e:
        app_logger.error(f"聊天处理失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/preferences")
async def set_preferences(request: PreferenceRequest):
    """
    设置用户偏好
    """
    try:
        updates = {}
        if request.cuisines:
            updates["cuisines"] = request.cuisines
        if request.allergies:
            updates["allergies"] = request.allergies
        if request.dislikes:
            updates["dislikes"] = request.dislikes
        if request.favorite_ingredients:
            updates["favorite_ingredients"] = request.favorite_ingredients
        if request.favorite_dishes:
            updates["favorite_dishes"] = request.favorite_dishes
        if request.dietary_restrictions:
            updates["dietary_restrictions"] = request.dietary_restrictions
        if request.spice_level:
            updates["spice_level"] = request.spice_level
        
        preference = long_term_memory.update_preference(request.user_id, **updates)
        
        return {
            "status": "success",
            "message": "偏好已更新",
            "preferences": preference.to_dict()
        }
    
    except Exception as e:
        app_logger.error(f"更新偏好失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/preferences/{user_id}")
async def get_preferences(user_id: str):
    """
    获取用户偏好
    """
    try:
        preference = long_term_memory.get_preference(user_id)
        if preference:
            return preference.to_dict()
        return {"message": "用户暂无偏好信息"}
    
    except Exception as e:
        app_logger.error(f"获取偏好失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/fridge")
async def manage_fridge(request: FridgeRequest):
    """
    管理虚拟冰箱
    """
    try:
        fridge = fridge_manager.get_or_create_fridge(request.user_id)
        
        if request.action == "add" and request.ingredients:
            fridge.add_ingredients(request.ingredients)
            return {
                "status": "success",
                "message": f"已添加 {len(request.ingredients)} 种食材",
                "fridge": fridge.to_dict()
            }
        
        elif request.action == "remove" and request.ingredients:
            count = fridge.remove_ingredients(request.ingredients)
            return {
                "status": "success",
                "message": f"已移除 {count} 种食材",
                "fridge": fridge.to_dict()
            }
        
        elif request.action == "list":
            return {
                "status": "success",
                "fridge": fridge.to_dict()
            }
        
        elif request.action == "clear":
            fridge.clear()
            return {
                "status": "success",
                "message": "冰箱已清空",
                "fridge": fridge.to_dict()
            }
        
        else:
            raise HTTPException(status_code=400, detail="无效的操作或缺少参数")
    
    except Exception as e:
        app_logger.error(f"冰箱操作失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/fridge/{user_id}")
async def get_fridge(user_id: str):
    """
    获取用户冰箱
    """
    try:
        fridge = fridge_manager.get_or_create_fridge(user_id)
        return fridge.to_dict()
    except Exception as e:
        app_logger.error(f"获取冰箱失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/recipes/search")
async def search_recipes(request: RecipeSearchRequest):
    """
    搜索食谱
    """
    try:
        if request.cuisine:
            recipes = recipe_retriever.search_by_cuisine(request.cuisine, k=request.k)
        else:
            recipes = recipe_retriever.search(request.query, k=request.k)
        
        return {
            "status": "success",
            "count": len(recipes),
            "recipes": [r.to_dict() for r in recipes]
        }
    
    except Exception as e:
        app_logger.error(f"搜索食谱失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    """
    获取用户完整档案
    """
    try:
        agent = agent_manager.get_agent(user_id)
        profile = agent.get_user_profile()
        return profile
    except Exception as e:
        app_logger.error(f"获取用户档案失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/session/{user_id}")
async def clear_session(user_id: str):
    """
    清空用户会话
    """
    try:
        agent = agent_manager.get_agent(user_id)
        agent.clear_session()
        return {"status": "success", "message": "会话已清空"}
    except Exception as e:
        app_logger.error(f"清空会话失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============= WebSocket接口（流式对话） =============

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    """
    WebSocket端点，支持流式对话
    """
    await websocket.accept()
    app_logger.info(f"WebSocket连接已建立: {user_id}")
    
    try:
        # 创建支持流式的Agent
        agent = RecipeRecommenderAgent(
            user_id=user_id,
            streaming=True
        )
        
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            user_message = message_data.get("message", "")
            
            if not user_message:
                continue
            
            app_logger.info(f"收到消息 [{user_id}]: {user_message}")
            
            # 发送开始标记
            await websocket.send_json({
                "type": "start",
                "timestamp": datetime.now().isoformat()
            })
            
            # 流式发送响应
            async for token in agent.stream_response(user_message):
                await websocket.send_json({
                    "type": "token",
                    "content": token
                })
            
            # 发送结束标记
            await websocket.send_json({
                "type": "end",
                "timestamp": datetime.now().isoformat()
            })
    
    except WebSocketDisconnect:
        app_logger.info(f"WebSocket连接断开: {user_id}")
    
    except Exception as e:
        app_logger.error(f"WebSocket错误: {e}")
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
