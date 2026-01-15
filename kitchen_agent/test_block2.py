from parser import extract_kitchen_data
from state import KitchenState

initial = KitchenState()
result = extract_kitchen_data("In frigo ho dei pomodori, della pasta e sono vegetariano", initial)
print(f"Ingredienti estratti: {result.ingredients}")
print(f"Preferenze: {result.preferences}")