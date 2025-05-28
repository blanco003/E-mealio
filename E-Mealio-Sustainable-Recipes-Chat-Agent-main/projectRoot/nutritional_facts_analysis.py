import json
import pandas as pd
import os

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
    output_path = os.path.join(os.path.dirname(__file__), "analisi_ingredienti.txt")

    with open(output_path, "a", encoding="utf-8") as f:
        f.write("\n" + "#" * 80 + "\n")
        f.write(f"{start_idx} - {end_idx} :\n")
        f.write(risposta + "\n")
        f.write(f"\nNumero di mappature non ragionevoli : {count}\n")
        f.write("#" * 80 + "\n")

    print(f"File aggiornato con {start_idx}-{end_idx}!")



df = pd.read_csv(os.path.join(os.path.dirname(__file__), "emealio_food_db.ingredients.csv"))

prompt = (
        "Sei un esperto nutrizionista. Di seguito ti elenco una serie di coppie di ingredienti. "
        "Per ciascuna coppia, indica se è ragionevole utilizzare i valori nutrizionali dell'ingrediente B "
        "come rappresentazione approssimativa dell'ingrediente A. Non essere troppo severo: considera accettabili le approssimazioni generiche "
        "quando i due ingredienti si riferiscono allo stesso tipo di alimento nella pratica comune (es. latte-latte o formaggio-formaggio), anche se esistono varianti con valori diversi, ed anche se i termini sono troppo generici, purché A e B siano lo stesso termine o si riferiscano chiaramente allo stesso alimento nella pratica comune, "
        "e anche ingredienti che rapresentano lo stesso alimento anche se in composizione diversa."
        "Rifiuta solo se i due ingredienti sono chiaramente diversi e scollegati."
        "Se il mapping NON è ragionevole, prima di stabilire la conclusione prendi anche in considerazione C e confrontalo con B."
        "Fornisci la risposta solo come una stringa in formato JSON, dove ogni chiave è la coppia 'A-B', sostituendo i nomi, e ogni valore è la spiegazione del perché il mapping NON è ragionevole. Se il mapping è accettabile, non includerlo nella risposta."
    )


start_index = 0
end_index = 9100
step = 100

for start in range(start_index, end_index, step):
        end = min(start + step, end_index)
        ask_about_ingredients(df, prompt, start, end)
