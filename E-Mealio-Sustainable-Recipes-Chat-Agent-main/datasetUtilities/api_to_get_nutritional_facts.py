import pandas as pd
import requests

print("inizio...............")

# API key di CalorieNinjas
API_KEY = "Vtjc8FV7+TwFijnOIfWDGA==mdHBVdbHp2ddjbTP"

headers = { "X-Api-Key": API_KEY }

API_KEY_2 = "Vtjc8FV7+TwFijnOIfWDGA==mdHBVdbHp2ddjbTP"

headers_2 = { "X-Api-Key": API_KEY_2 }

url = "https://api.calorieninjas.com/v1/nutrition"

df = pd.read_csv("emealio_food_db.ingredients.csv")

# counter ingredienti trovati
found_total = 0

# colonne da aggiungere al csv
columns_to_add = [
    "mapped_api_ingredient", "calories", "fat_total_g", "fat_saturated_g", "cholesterol_mg", "sodium_mg",
    "carbohydrates_total_g", "fiber_g", "sugar_g", "protein_g",
    "potassium_mg"
]

# aggiungiamo le colonne
for col in columns_to_add:
    if col not in df.columns:
        df[col] = None

# aggiungiamo una colonna done per tenere traccia degli ingredienti già analizzati
if "done" not in df.columns:
    df["done"] = None


# scorriamo gli ingredienti, e per ciascuno effettuiamo la chiamata all'api per ottenere i valori nutrizionali
for index, ingredient in enumerate(df["ingredient"]):

    # saltiamo quelli già analizzati
    if df.at[index, "done"] == "yes" or df.at[index, "done"] == "yes_with_mapped" or df.at[index, "done"] == "yes_but_not_found":
        print(f"[{index}] : '{ingredient}' già analizzato.")
        continue
    
    try:

        print(f"[{index}] '{ingredient}' ...")

        ingredient_query = ingredient.lower().replace("_", " ")

        params = {
            "query": f"100g {ingredient_query}"
        }

        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        items = data.get("items", [])

        if not items:
            # se non troviamo risultati proviamo una seconda ricerca tramite mapped_item 
            mapped_item = df.at[index, "mapped_item"]

            # saltiamo se mapped_item è anch'esso troppo generico
            if mapped_item == "TOO_GENERIC" or mapped_item == "NO_DATA" or mapped_item == "NO_MATCH":
                df.at[index, "done"] = "yes_but_not_found"
                continue

            print(f"[{index}] Nessun risultato per '{ingredient}', provo con '{mapped_item}'")

            mapped_item_query = mapped_item.lower().replace("_", " ").replace("*", " ")

            try:
                params = {
                    "query": f"100g {mapped_item_query}"
                }

                response = requests.get(url, headers=headers_2, params=params)
                data = response.json()
                items = data.get("items", [])

            except Exception as e:
                print(f"[{index}] Errore nella seconda ricerca con 'mapped_item': {e}")
                items = []

            if not items:
                # se anche la seconda ricerca non ha trovato risultati
                print(f"[{index}] Non trovato: {ingredient}")
                df.at[index, "done"] = "yes_but_not_found"
                continue

            else:
                # se la seconda ricerca ha trovato risultati
                print(f"[{index}] Trovato con mapped: {ingredient}")
                df.at[index, "done"] = "yes_with_mapped"
        else:
            # se la prima ricerca ha trovato risultati
            df.at[index, "done"] = "yes"

        # counter ingredienti trovati con successo
        found_total += 1
        
        # prendiamo il primo risultato
        item = items[0]  

        # aggiorniamo i campi del csv con i risultati della richiesta      
        df.at[index, "mapped_api_ingredient"] = item.get("name")  
        df.at[index, "calories"] = item.get("calories")
        df.at[index, "fat_total_g"] = item.get("fat_total_g")
        df.at[index, "fat_saturated_g"] = item.get("fat_saturated_g")
        df.at[index, "cholesterol_mg"] = item.get("cholesterol_mg")
        df.at[index, "sodium_mg"] = item.get("sodium_mg")
        df.at[index, "carbohydrates_total_g"] = item.get("carbohydrates_total_g")
        df.at[index, "fiber_g"] = item.get("fiber_g")
        df.at[index, "sugar_g"] = item.get("sugar_g")
        df.at[index, "protein_g"] = item.get("protein_g")
        df.at[index, "potassium_mg"] = item.get("potassium_mg")


        if found_total % 10 == 0:
            print("Trovati finora:", found_total)

        # ogni 500 ingredienti trovati salviamo il csv per non perdere il risultati
        if found_total % 500 == 0:
            df.to_csv("emealio_food_db.ingredients.csv", index=False)
            print("CSV aggiornato.")


    except Exception as e:
        print(f"[{index}] Errore per '{ingredient}': {e}")



print("Totale ingredienti trovati:", found_total)

df.to_csv("emealio_food_db.ingredients.csv", index=False)
print("CSV aggiornato fine ricerca.")


# stampiamo i conteggi degli ingredienti sul campo done
print(df["done"].value_counts())


###################################################################################################
# PER PREPARE IL DATASET IN MODO DA IMPORTARLO IN MONGODB

"""


df = pd.read_csv("emealio_food_db.ingredients.csv")

# eliminiamo la colonna done
if 'done' in df.columns:
    df.drop(columns=['done'], inplace=True)

# rinomiamo le colonne, per usare gli stessi nomi dei campi delle ricette
rename_dict = {
    'calories': 'calories [cal]',
    'fat_total_g': 'totalFat [g]',
    'fat_saturated_g': 'saturatedFat [g]',
    'carbohydrates_total_g': 'totalCarbohydrate [g]',
    'protein_g': 'protein [g]',
    'sugar_g': 'sugars [g]',
    'fiber_g': 'dietaryFiber [g]',
    'cholesterol_mg': 'cholesterol [mg]',
    'sodium_mg': 'sodium [mg]'
}

df.rename(columns={k: v for k, v in rename_dict.items() if k in df.columns}, inplace=True)

df.to_csv("emealio_food_db.ingredients.csv", index=False)
print("CSV aggiornato e salvato.")
"""