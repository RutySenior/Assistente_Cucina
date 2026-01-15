from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    name: str
    quantity: str = "sconosciuta"
    is_expiring: bool = False

class KitchenState(BaseModel):
    inventory: List[Ingredient] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    disliked_ingredients: List[str] = Field(default_factory=list)
    health_constraints: List[str] = Field(default_factory=list)
    missing_info_reason: Optional[str] = None
    found_recipes: List[str] = Field(default_factory=list)

class AgentState(TypedDict):
    state: KitchenState
    messages: List[dict]