import service.ImproveRecipeService as irs
import jsonpickle

def extractRecipes(recipesData):
    """
    A partire da un dizionario contenente una lista di nomi di ricette e una lista di liste di ingredienti,
    recupera dal db le corrispondenti ricette e le restituisce come una lista di oggetti istanza della classe Recipe.

    Args : 
    - recipesData : dizionario contenente una lista di nomi di ricette e una lista di liste di ingredienti.

    Returns : 
    - recipes : lista di oggetti istanze della classe Recipe.
    """

    recipesNames = recipesData['recipeNames']
    recipesIngredients = recipesData['recipeIngredients']    
    recipes = []

    for name in recipesNames:
        mealData = {'name': name, 'ingredients': []}
        baseRecipe = irs.get_base_recipe(jsonpickle.encode(mealData))
        recipes.append(baseRecipe)

    for ingredients in recipesIngredients:
        mealData = {'name': None,'ingredients': ingredients}
        baseRecipe = irs.get_base_recipe(jsonpickle.encode(mealData))
        recipes.append(baseRecipe)

    return recipes