import math
import service.domain.IngredientService as ingredientService
import dto.Recipe as recipe
import persistence.RecipePersistence as rp


def compute_normalized_cfp_sustainability(ingredients):
    """
    Calcolare il carbon footprint normalizzato di una lista di ingredienti.

    Args 
    - ingredients : lista di ingredienti di cui calcolare il cfp normalizzato.

    Returns : 
    - cfP_score : carbon footprint normalizzato della data lista di ingredienti.
    """
    normalized_cfps = []
    max_cfp = 78.8
    for ingredient in ingredients:
        if(ingredient.cfp != None):
            normalized_cfps.append(ingredient.cfp/max_cfp)
    #order cfps in descending order
    normalized_cfps.sort(reverse=True)

    cfp_score = 0
    for i in range(len(normalized_cfps)):
        cfp_score += normalized_cfps[i] * math.e ** (-i)
    
    return cfp_score

def compute_normalized_wfp_sustainability(ingredients):
    """
    Calcolare il water footprint normalizzato di una lista di ingredienti.

    Args 
    - ingredients : lista di ingredienti di cui calcolare il wfp normalizzato.

    Returns : 
    - wfP_score : carbon footprint normalizzato della data lista di ingredienti.
    """
    normalized_wfps = []
    max_wfp = 731000
    for ingredient in ingredients:
        if(ingredient.wfp != None):
            normalized_wfps.append(ingredient.wfp/max_wfp)
    #order wfps in descending order
    normalized_wfps.sort(reverse=True)

    wfp_score = 0
    for i in range(len(normalized_wfps)):
        wfp_score += normalized_wfps[i] * math.e ** (-i)
    
    return wfp_score


def compute_recipe_sustainability_score(recipe):
    """
    Calcola lo score di sostenibilità di una ricetta, come combinazione lineare del carbon footprint e water footprint.

    Args : 
    - recipe : ricetta di cui calcolare lo score di sostenibilità.
    """
    ingredients = recipe.ingredients
    alpha = 0.8
    beta = 0.2
    max_overall_sustainability = 0.8689
    cfp_score = compute_normalized_cfp_sustainability(ingredients)
    wfp_score = compute_normalized_wfp_sustainability(ingredients)

    overall_sustainability = alpha * cfp_score + beta * wfp_score
    normalized_overall_sustainability = overall_sustainability / max_overall_sustainability
    recipe.sustainabilityScore = normalized_overall_sustainability


def get_recipe_cluster(recipe):
    """
    Assegna alla ricetta il cluster di sostenibilità, in base al suo score di sostenibilità, in particolare . 
    - 0 : se lo score di sostenibilità appartiene all'intervallo [0, 0.04]
    - 1 : se lo score di sostenibilità appartiene all'intervallo ]0.04, 0.15]
    - 2 : se lo score di sostenibilità appartiene all'intervallo ]0.15, 1]
    
    Args : 
    - recipe : ricetta di cui calcolare l'indice del cluster di sostenibilità.

    Returns : 
    - int : indice del cluster di sostenibilità assegnato alla ricetta.
    """
    #if the sustainability score is in [0, 0.04] then the recipe belongs to cluster 0
    if recipe.sustainabilityScore >= 0 and recipe.sustainabilityScore <= 0.04:
        return 0
    
    #if the sustainability score is in ]0.04, 0.15] then the recipe belongs to cluster 1
    if recipe.sustainabilityScore > 0.04 and recipe.sustainabilityScore <= 0.15:
        return 1
    
    #if the sustainability score is in ]0.15, 1] then the recipe belongs to cluster 2
    if recipe.sustainabilityScore > 0.15 and recipe.sustainabilityScore <= 1:
        return 2


def convert_in_emealio_recipe(mongoRecipe,removedConstraints,mealType):
    """
    Converte una ricetta nel formato del mongodb (dizionario) in un oggetto istanza
    della classe Recipe, utilizzabile dal sistema E-malio.

    Args : 
    - mongoRecipe : ricetta nel formato mongodb.
    - removedConstraints : vincoli rimossi per poter estrarre la ricetta dal db.
    - mealType : tipologia di pasto della ricetta.

    Retursn :
    - Recipe : ricetta sotto forma di oggetto istanza della classe Recipe rappresentante la ricetta nel formato mongodb.
    """
    title = mongoRecipe['title']
    id = mongoRecipe['recipe_id']
    instructions = mongoRecipe['recipe_url']
    sustainabilityScore = mongoRecipe['sustainability_score']
    #check if the description is present
    if 'description' in mongoRecipe:
        description = mongoRecipe['description']
    else:
        description = None
    ingredients = ingredientService.get_ingredient_list_from_full_ingredient_string(mongoRecipe['ingredients'])
    return recipe.Recipe(title,id,ingredients,sustainabilityScore,instructions,description,removedConstraints,mealType)



def get_nutrional_facts(recipe_id):

    recipeData = rp.get_recipe_by_id(int(recipe_id))
   
    nutrional_facts = {}
    for info in ['calories [cal]', 'totalFat [g]', 'saturatedFat [g]', 'totalCarbohydrate [g]', 'protein [g]', 'sugars [g]', 'dietaryFiber [g]', 'cholesterol [mg]', 'sodium [mg]']:
        if recipeData[info] is not None:
            nutrional_facts[info] = recipeData[info]

    return nutrional_facts
