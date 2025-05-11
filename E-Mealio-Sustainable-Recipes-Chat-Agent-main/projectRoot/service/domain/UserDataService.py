# This file is used to get user data from the database
import dto.User as user
import persistence.UserPersistence as userDB
import jsonpickle


def getUserData(userId):
    """
    Recupera dalla collectione degli utenti del db l'utente con dato userId.

    Args : 
    - userId : id dell'utente da recuperare

    Returns : 
    - User or None : se esiste un utente con lo user id dato viene restituito l'utente corrispondente.
    """
    if(userId == None):
        print("User data is empty")
        return None
    else:
        userDbData = userDB.get_user_by_user_id(str(userId))
        if(userDbData == None):
            return None
        userJson = jsonpickle.encode(userDbData)
        userData = user.User(None,None,None,None,None,None,None,None,None,None,None,None,None,None,None)
        userData.from_json(userJson)
        return userData
    
    
def save_user(userData):
    """
    Salva l'utente nella collection degli utenti del db.

    Args : 
    - userData : utente da salvare nella collection degli utenti del db.
    """
    userDB.save_user(userData.to_plain_json())


def update_user(userData):
    """
    Aggiorna l'utente nella collection degli utenti del db.

    Args : 
    - userData : utente da aggiornare nella collection degli utenti del db.
    """
    userDB.update_user(userData.to_plain_json())


def update_user_last_interaction(userId, lastInteraction):
    """
    Aggiorna l'ultima interazione dell'utente con dato userId nella collection degli utenti nel db.

    Args : 
    - userId : id dell'utente di cui aggiornare l'ultima interazione.
    - lastInteraction : ultima interazione dell'utente avvenuta con il sistema.
    """
    userData = getUserData(userId)
    if(userData != None):
        userData.lastInteraction = lastInteraction
        update_user(userData)


def get_all_users_with_reminder():
    """
    Restituisce l'insieme degli utenti che hanno il promemoria attivo (reminder=True) dalla collection degli utenti nel db.

    Returns : 
    - users : utenti della collection degli utenti del db che hanno il promemoria attivo.
    """
    return userDB.get_all_users_with_reminder()


def get_taste(userId, mealType):
    """
    Restituisce il gusto dell'utente con dato userId di una specifica tipologia di pasto mealType.

    Args : 
    - userId : id dell'utente di cui recuperare il gusto.
    - mealType : tipologia di pasto di cui recuperare il gusto dell'utente.

    Returns :
    - taste or None : gusto dell'utente con dato userId della data specifica tipologia di pasto.
    """
    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['tastes'][mealType]
    

def get_allergies(userId):

    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['allergies']
    

def get_restrictions(userId):

    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['restrictions']
    

def get_disliked_ingredients(userId):

    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['disliked_ingredients']
    
def get_evolving_diet(userId):

    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    else:
        return userDbData['evolving_diet']



def get_reminder_info(DataJson):
    """
    Estrae da un json il numero di giorni e l'ora (da usare per il reminder).
    """

    info = jsonpickle.decode(DataJson)

    day = info['days_reminder']
    hour = info['hour_reminder']
    
    return day, hour


def get_num_days_reminder(userId):

    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    # per gestire il caso in cui c'erano utenti già con il reminder attivato prima della creazione della personalizzazione
    elif 'days_reminder' not in userDbData:
        return userDbData.get('days_reminder', 2)
    else:
        return userDbData['days_reminder']
    

def get_hour_reminder(userId):

    userDbData = userDB.get_user_by_user_id(str(userId))
    if(userDbData == None):
        return None
    # per gestire il caso in cui c'erano utenti già con il reminder attivato prima della creazione della personalizzazione
    elif 'hour_reminder' not in userDbData:
        return userDbData.get('hour_reminder', 12)
    # nel caso l'utente inserisce ad es. 19:00
    elif isinstance(userDbData['hour_reminder'], str):
        return userDbData['hour_reminder'].split(":")[0]  
    else:
        return userDbData['hour_reminder']
    
