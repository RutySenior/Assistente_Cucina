# state.py
from typing import List, Optional, TypedDict  # <--- Fondamentale!
from pydantic import BaseModel, Field

class KitchenState(BaseModel):
    ingredients: List[str] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    found_recipes: List[str] = Field(default_factory=list)
    next_step: str = "parsing"
    final_output: Optional[str] = None

class AgentState(TypedDict):
    state: KitchenState
    messages: List[dict]