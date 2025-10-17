"""
Prompt模板模块
"""
from src.prompts.templates import (
    create_agent_prompt,
    create_preference_prompt,
    create_recommendation_prompt,
    create_fridge_prompt,
    create_rag_query_prompt
)

__all__ = [
    'create_agent_prompt',
    'create_preference_prompt',
    'create_recommendation_prompt',
    'create_fridge_prompt',
    'create_rag_query_prompt'
]
