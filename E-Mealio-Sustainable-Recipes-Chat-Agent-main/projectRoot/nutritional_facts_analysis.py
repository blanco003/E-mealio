import json
import pandas as pd
import os
import numpy as np

from service.bot.LangChainService import ask_model

###############################################################
# Bisogna prima esportare il csv degli ingredienti da mongo db!
###############################################################

def build_input_by_index_range(df, start_idx, end_idx):
    """
    Recupera dal csv per ogni ingrediente tra l'indice di partenza e di fine specificato,
    il nome dell'ingrediente, il nome dell'ingrediente con cui è stato mappato nel db 
    ed il nome dell'ingrediente di cui sono stati recuperati i valori nutrizionali dall'API per 
    assegnarli all'ingrediente corrispondente, nel seguente formato : 

    {Indice} : 
    A : {ingredient}
    B : {mapped_api_ingredient}
    C : {mapped_item}
    """

    sub_df = df.iloc[start_idx:end_idx]
    input_text = ""
    for idx, row in sub_df.iterrows():
        if pd.isna(row['mapped_api_ingredient']) or row['mapped_api_ingredient'] == '':
            continue
        input_text += f"{idx+1}.\nA: {row['ingredient']} \nB: {row['mapped_api_ingredient']}"

        if not pd.isna(row['mapped_item']) and row['mapped_item'] not in ['NO_DATA', 'TOO_GENERIC', 'NO_MATCH']:
            input_text += f"\nC: {str(row['mapped_item'].lower().replace('-', ' '))}\n\n"
        else:
            input_text += "\n\n"
    return input_text



def ask_about_ingredients(df,prompt,start_idx,end_idx):

    
    input_text = build_input_by_index_range(df,start_idx,end_idx)

    if not input_text.strip():
        print(f"Nessun input generato per intervallo {start_idx}-{end_idx}!")
        return

    # effetua la chiamata al LLM
    risposta = ask_model(input=input_text, prompt=prompt)

    #print(risposta)

    try:
        parsed = json.loads(risposta)
        # conta il numero di ingredienti restituiti, ovvero ingredienti con valori non ragionevoli
        count = len(parsed)
    except Exception as e:
        print("\nErrore nel parsing della risposta JSON:")
        print(e)


    # salva in aggiunta su file
    output_path = os.path.join(os.path.dirname(__file__), "analisi_ingredienti_v2.txt")

    with open(output_path, "a", encoding="utf-8") as f:
        f.write("\n" + "#" * 80 + "\n")
        f.write(f"{start_idx} - {end_idx} :\n")
        f.write(risposta + "\n")
        f.write("#" * 80 + "\n")

    print(f"File aggiornato con {start_idx}-{end_idx}!")


PROMPT = (
        """
        Sei un esperto nutrizionista. Di seguito ti elenco una serie di coppie di ingredienti. 
        Per ciascuna coppia, indica se è ragionevole utilizzare i valori nutrizionali dell'ingrediente B come rappresentazione approssimativa dell'ingrediente A. Non essere troppo severo: considera accettabili le approssimazioni generiche 
        quando i due ingredienti si riferiscono allo stesso tipo di alimento nella pratica comune (es. latte-latte o formaggio-formaggio), anche se esistono varianti con valori diversi, ed anche se i termini sono troppo generici, purché A e B siano lo stesso termine o si riferiscano chiaramente allo stesso alimento nella pratica comune, 
        e anche ingredienti che rapresentano lo stesso alimento anche se in composizione diversa.
        Rifiuta solo se i due ingredienti sono chiaramente diversi e scollegati.
        Se il mapping NON è ragionevole, prima di stabilire la conclusione prendi anche in considerazione C e confrontalo con B.
        Fornisci la risposta solo come una stringa in formato JSON, dove ogni chiave è il nome dell'ingrediente, ovvero il campo 'A', avente come valori un campo 'descrizione', del perchè ritieni che il mapping non sia ragionevole, e un campo 'inappropriatezza', per indicare il grado da 1 a 10 di quanto ritieni inappropriato il mapping. 
        Se il mapping è accettabile, non includerlo nella risposta.
        
        Usa la seguente scala indicativa per il campo 'grado_non_ragionevolezza':
        1 = 'irrilevante'
        2 = 'trascurabile'
        3 = 'lieve'
        4 = 'limitato'
        5 = 'moderato'
        6 = 'notevole'
        7 = 'consistente'
        8 = 'marcato'
        9 = 'grave'
        10 = 'inaccettabile'"
"""
)


####################################################
# Chiamata LLM 
"""
df = pd.read_csv(os.path.join(os.path.dirname(__file__), "emealio_food_db.ingredients.csv"))

start_index = 0
end_index = 9100
step = 100

for start in range(start_index, end_index, step):
        end = min(start + step, end_index)
        ask_about_ingredients(df, PROMPT, start, end)
"""
#####################################################



##########################################################
## Prima ripulire il file txt per portalo in formato json!
##########################################################



df = pd.read_csv(os.path.join(os.path.dirname(__file__), "emealio_food_db.ingredients.csv"))

with open("projectRoot\\analisi_ingredienti_v2.txt", "r", encoding="utf-8") as f:
    json_string = f.read()

data = json.loads(json_string)  

distribuzione = {i: 0 for i in range(1, 11)}
ingredienti_di_cui_rimuovere_valori = []
count = 0

df = df.rename(columns={"potassium_mg": "potassium [mg]"})

for nome, info in data.items():
    if "inappropriatezza" in info:
        inappropr = info["inappropriatezza"]
        distribuzione[inappropr] +=1
        if inappropr >= 6:
            df.loc[df["ingredient"] == nome, ["calories [cal]","totalFat [g]","saturatedFat [g]","cholesterol [mg]","sodium [mg]","totalCarbohydrate [g]","dietaryFiber [g]","sugars [g]","protein [g]","potassium [mg]"]] = np.nan  
            count += 1

for livello in range(1, 11):
    print(f"Inappropriatezza {livello}: {distribuzione[livello]}")
    
print(f"Rimossi valori nutrizionali di {count} ingredienti")

df.to_csv("emealio_food_db.ingredients.csv", index=False)
