from typing import List, Optional, TypedDict
from pydantic import BaseModel, Field

class Ingredient(BaseModel):
    name: str
    quantity: str = "sconosciuta"
    is_expiring: bool = False

class Recipe(BaseModel):
    name: str = Field(description="Nome del piatto")
    prep_time: str = Field(description="Tempo totale di preparazione")
    ingredients: List[str] = Field(description="Lista ingredienti con quantità")
    description: str = Field(description="Descrizione dettagliata dei passaggi")

class RecipeList(BaseModel):
    """Contenitore strutturato per le 3 ricette finali"""
    recipes: List[Recipe] = Field(description="Lista di esattamente 3 ricette")

class KitchenState(BaseModel):
    inventory: List[Ingredient] = Field(default_factory=list)
    preferences: List[str] = Field(default_factory=list)
    disliked_ingredients: List[str] = Field(default_factory=list)
    health_constraints: List[str] = Field(default_factory=list)
    missing_info_reason: Optional[str] = None
    found_recipes: List[Recipe] = Field(default_factory=list)

class AgentState(TypedDict):
    state: KitchenState
    messages: List[dict]