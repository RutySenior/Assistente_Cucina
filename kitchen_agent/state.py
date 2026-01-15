# state.py
from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    name: str
    quantity: str = "sconosciuta"
    is_expiring: bool = False

class Recipe(BaseModel):
    name: str = Field(description="Nome del piatto")
    prep_time: str = Field(description="Tempo di preparazione")
    ingredients: List[str] = Field(description="Lista ingredienti e quantità")
    description: str = Field(description="Passaggi dettagliati")
    image_url: Optional[str] = None

class RecipeList(BaseModel):
    recipes: List[Recipe] = Field(description="Lista di 3 ricette")

class KitchenState(BaseModel):
    inventory: List[Ingredient] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list) # Gusti SI
    disliked_ingredients: List[str] = Field(default_factory=list) # Gusti NO
    health_constraints: List[str] = Field(default_factory=list) # Allergie/Salute
    missing_info_reason: Optional[str] = None
    found_recipes: List[Recipe] = Field(default_factory=list)

class AgentState(TypedDict):
    state: KitchenState
    messages: List[dict]