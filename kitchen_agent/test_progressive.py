# test_progressive.py
from graph import app
from state import KitchenState

state = KitchenState()
msgs = [{"role": "user", "content": "Ho della pasta e del pomodoro"}]

# Step 1: Messaggio vago
out1 = app.invoke({"messages": msgs, "state": state})
print("Dopo messaggio 1:", out1["state"].missing_info_reason) 
# Output atteso: Richiesta di quantità per pasta e pomodoro

# Step 2: L'utente precisa
msgs.append({"role": "user", "content": "Ho 500g di pasta e una latta di pomodoro"})
out2 = app.invoke({"messages": msgs, "state": out1["state"]})
print("Dopo messaggio 2 - Ricette trovate:", len(out2["state"].found_recipes) > 0)
# Output atteso: True (ora ha le quantità e procede alla ricerca)