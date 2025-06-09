import requests


HEADER = {"Content-Type": "application/json"}
URL_RECCOMENDATION = "http://localhost:8100/recommend"
URL_INFORMATION = "http://localhost:8100/food-info/"


# TODO : aggiornare classe Recipe, FoodHistory
# TODO : scrivere funzione per estarre la prima ricetta dal JSON (vedi formato sotto)

def get_recipe_suggestion(user_id, preferences, soft_restrictions, hard_restrictions, meal_time, previous_recommendations, recommendation_count,diversity_factor,conversation_id):
    
    payload = {
        "user_id": user_id,
        "preferences": preferences,
        "soft_restrictions": soft_restrictions,
        "hard_restrictions": hard_restrictions,
        "meal_time": meal_time,
        "previous_recommendations": previous_recommendations,
        "recommendation_count": recommendation_count,
        "diversity_factor": diversity_factor,
        "conversation_id": conversation_id
    }

    try :
      response = requests.post(URL_RECCOMENDATION, headers=HEADER, json=payload)
      print(f"Status Code: {response.status_code}")
      print("Response JSON:", response.json())
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta di raccomandazione {user_id}:", e)
        return None
    

    # TODO : estrarre Recipe a partire dal JSON 



def get_information(recipe_name):
   
   try :
      response = requests.get(URL_INFORMATION + recipe_name, headers=HEADER)
      print(f"Status Code: {response.status_code}")
      print("Response JSON:", response.json())
   except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta di recupero informazioni {recipe_name} :", e)
        return None




#get_information("onion")
get_recipe_suggestion(12345,["pasta", "Italian cuisine", "tomatoes"],["seafood", "spicy"],["peanuts", "shellfish"],"dinner",["spaghetti carbonara"],3,0.7,"conv_2025032012345")









########### ESEMPIO RACCOMANDAZIONE 
"""
curl -X POST http://localhost:8100/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 12345,
    "preferences": ["pasta", "Italian cuisine", "tomatoes"],
    "soft_restrictions": ["seafood", "spicy"],
    "hard_restrictions": ["peanuts", "shellfish"],
    "meal_time": "dinner",
    "previous_recommendations": ["spaghetti carbonara"],
    "recommendation_count": 3,
    "diversity_factor": 0.7,
    "conversation_id": "conv_2025032012345"
  }'

"""


"""
url = "http://localhost:8100/recommend"
headers = {"Content-Type": "application/json"}
payload = {
    "user_id": 12345,
    "preferences": ["pasta", "Italian cuisine", "tomatoes"],
    "soft_restrictions": ["seafood", "spicy"],
    "hard_restrictions": ["peanuts", "shellfish"],
    "meal_time": "dinner",
    "previous_recommendations": ["spaghetti carbonara"],
    "recommendation_count": 3,
    "diversity_factor": 0.7,
    "conversation_id": "conv_2025032012345"
}

response = requests.post(url, headers=headers, json=payload)

print(f"Status Code: {response.status_code}")
print("Response JSON:", response.json())
"""


"""

Response JSON: { 
                 'user_id': 12345, 

                 'recommendations': [ 

                          {'name': 'Spaghetti carbonara', 
                           'score': 0.8, 
                           'explanation': "U25 interacted_with 'Pasta amatriciana' has_ingredient 'guanciale' has_ingredient 'Spaghetti Carbonara'", 
                           'ingredients': [['spaghetti', '100g'], ['guanciale', '50g'], ['egg', '1']], 
                           'healthiness_score': 0.8, 
                           'sustainability_score': 0.5, 
                           'nutritional_values': {'calories': 500.0, 'fiber': 5.0, 'sugar': 2.0, 'carbs': 60.0, 'protein': 15.0, 'fat': 10.0}
                          },
                            
                          {'name': 'Fettuccine alfredo',
                           'score': 0.7, 
                           'explanation': "U25 interacted_with 'Pasta broccoli' has_indicator 'HIGH PROTEIN' has_indicator 'Fettuccine Alfredo'", 
                           'ingredients': [['fettuccine', '100g'], ['cream', '50ml'], ['parmesan', '20g']], 
                           'healthiness_score': 0.7, 
                           'sustainability_score': 0.6, 
                           'nutritional_values': {'calories': 600.0, 'fiber': 3.0, 'sugar': 4.0, 'carbs': 70.0, 'protein': 12.0, 'fat': 20.0}
                          }, 

                          {'name': 'Pennette with basil pesto', 
                           'score': 0.6, 
                           'explanation': "U25 interacted_with 'Pizza genovese' has_tag 'pesto' has_tag 'Pennette with basil pesto'", 
                           'ingredients': [['pennette', '100g'], ['basil pesto', '20g'], ['olive oil', '10ml']], 
                           'healthiness_score': 0.6, 
                           'sustainability_score': 0.7, 
                           'nutritional_values': {'calories': 550.0, 'fiber': 4.0, 'sugar': 3.0, 'carbs': 65.0, 'protein': 14.0, 'fat': 15.0}}
                    ],
                  
                  'conversation_id': 'conv_2025032012345'
                  }


"""

################# ESEMPIO RECUPERO INFORMAZIONI

"""
curl -X GET http://localhost:8100/food-info/onion \
  -H "Content-Type: application/json"
"""

"""
recipe = "onion"
url = "http://localhost:8100/food-info/onion"
headers = {"Content-Type": "application/json"}


response = requests.get(url, headers=headers)

print(f"Status Code: {response.status_code}")
print("Response JSON:", response.json())
"""

##############################################à