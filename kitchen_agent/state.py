from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    name: str
    quantity: str = "sconosciuta"
    is_expiring: bool = False

class Recipe(BaseModel):
    name: str
    prep_time: str
    ingredients: List[str] # Qui l'LLM scriverà "200g di Pasta"
    description: str
    image_url: Optional[str] = None
    search_keywords_en: str = Field(description="3 parole chiave in inglese separate da virgola, es: 'pasta,tomato,basil'")

class RecipeList(BaseModel):
    recipes: List[Recipe] = Field(description="Lista di 3 ricette")

class KitchenState(BaseModel):
    inventory: List[Ingredient] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    disliked_ingredients: List[str] = Field(default_factory=list)
    health_constraints: List[str] = Field(default_factory=list)
    missing_info_reason: Optional[str] = None
    found_recipes: List[Recipe] = Field(default_factory=list)
    # NUOVI CAMPI
    critic_feedback: Optional[str] = None
    reflection_steps: int = 0
    total_tokens_used: int = 0

class AgentState(TypedDict):
    state: KitchenState
    messages: List[dict]