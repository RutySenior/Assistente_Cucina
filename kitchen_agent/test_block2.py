# test_block2_adv.py
from parser import extract_kitchen_data
from state import KitchenState

initial = KitchenState()
# Test con quantità e scadenza
result = extract_kitchen_data("Ho 3 uova che scadono domani e un pacco di farina nuovo", initial)
for ing in result.inventory:
    print(f"Ingrediente: {ing.name} | Qty: {ing.quantity} | In Scadenza: {ing.is_expiring}")