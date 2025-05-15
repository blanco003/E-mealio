import persistence.IngredientPersistence as ip
import dto.Ingredient as ingredientDto


def remove_additional_info(ingredient):
    """
    Rimuove dalla stringa in input, rappresentante un ingrediente, informazioni addizionali come quantità, unità e caratteri aggiuntivi, restituendo la stringa contenente il solo testo dell'ingrediente.

    Args : 
    - ingredient : stringa rappresentante un ingrediente da ripulire.

    Returns :
    - ingredient : stinga ripulita, contenente il solo testo dell'ingrediente.
    """
    #given a string like "water _ 2 __ cups"
    #find the  index of the character "_" and remove everything after it
    index = ingredient.find(' _')
    #if the character is not found then return the string as it is
    if index != -1:
        #get the substring from 0 to the index minus 1
        ingredient = ingredient[:index]
    #remove [,],{,} and '
    ingredient = ingredient.replace('[','')
    ingredient = ingredient.replace(']','')
    ingredient = ingredient.replace('{','')
    ingredient = ingredient.replace('}','')
    ingredient = ingredient.replace('"','')
    ingredient = ingredient.replace('\'','')
    #remove trailing and leading spaces
    return ingredient


def get_ingredient_list(ingredientsList):
    """
    Data una lista di ingredienti, sotto forma di stringa, recupera dal db un ingrediente alla volta a partire dal nome, 
    e restituisce la lista degli ingredienti, sotto forma di oggetti istanza della classe Ingredient.
    
    Args : 
    - ingredientsList : lista di ingredienti, sotto forma di stringa
    
    Returns : 
    - ingredientObjList : lista di ingredienti, sotto forma di oggetti istanze della classe Ingredient.
    """
    ingredientObjList = []
    for ingredient in ingredientsList:
        #query the database
        ingredientInDB = ip.get_ingredient_by_name(ingredient)

        #if the ingredienntDB has the cfp data then use it else use None
        if 'cfp' in ingredientInDB:
            cfp = ingredientInDB['cfp']
        else:
            cfp = None

        #if the ingredienntDB has the wfp data then use it else use None
        if 'wfp' in ingredientInDB:
            wfp = ingredientInDB['wfp']
        else:
            wfp = None

        ingredientObjList.append(ingredientDto.Ingredient(ingredient,cfp,wfp))
    
    return ingredientObjList


#use to extract the ingredients from a string like "['ingredient1 _ quantity __ unit','ingredient2 _ quantity __ unit']" used in recipe
def get_ingredient_list_from_full_ingredient_string(ingredients):
    """
    Estrae gli ingredienti da una stringa strutturata, come quella usata nelle ricette,
    rimuovendo quantità, unità e formattazioni, e restituisce la lista di oggetti Ingredient.

    La stringa input è attesa in un formato tipo : "['ingredient1 _ quantity __ unit','ingredient2 _ quantity __ unit']"

    Args:
    - ingredients : stringa contenente la lista di ingredienti formattati.

    Returns:
    - ingredientObjList : lista di oggetti Ingredient ottenuti dopo la pulizia e recupero da database.
    """
    ingredients = ingredients.split("',")
    ingredients = [ingredient.strip() for ingredient in ingredients]
    ingredients = [remove_additional_info(ingredient) for ingredient in ingredients]
    return get_ingredient_list(ingredients)


def get_ingredient_list_from_generic_list_of_string(ingredientsListOfString):
    """
    Converte una lista generica di stringhe in oggetti Ingredient, recuperando dal database gli ingredienti corrispondenti.
    
    Se un ingrediente non viene trovato esattamente, si cerca l'ingrediente con valore di similarità del coseno più alto all'ingrediente dato.

    Args:
    - ingredientsListOfString : Lista generica di nomi di ingredienti.

    Returns:
    - ingredientObjList : lista di oggetti Ingredient con dati recuperati dal database.
    """
    ingredients = []
    for ingredient in ingredientsListOfString:
        foodFromDB= ip.get_ingredient_by_name(ingredient)
        if foodFromDB == None or foodFromDB == 'null':
            foodFromDB = ip.get_most_similar_ingredient(ingredient)
        ingredients.append(foodFromDB['ingredient'])
    return get_ingredient_list(ingredients)


def get_data_origin(ingredient_name):

    ingredientData = ip.get_ingredient_by_name(str(ingredient_name))

    # su 9000 ingredienti circa 7000 non hanno il campo data_origin
    if(ingredientData != None) and ('data_origin' in ingredientData):
        return ingredientData['data_origin']
    else:
        return None 
