import os
import re
import dto.Response as resp
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv, find_dotenv
from langchain.memory import ChatMessageHistory
import Utils
import service.bot.LogService as log
import datetime

PRINT_LOG = False
"""Flag che indica se stampare i log (di default False)."""


#MODEL = 'openai'     # DA CONTROLLARE OPENAI
MODEL = 'anthropic'   # FUNZIONA
"""Modello LLM a cui vengono inviati i prompt e ricevute le risposte per gestire l'interazione con l'utente."""


TOKEN_REGEX = r"TOKEN -?\d+(\.\d+)?"
"""Regex per estrarre il token dalla risposta del LLM."""

INFO_REGEX_ANGULAR = r"<(.*?)>"
"""Regex per estrarre informazioni, racchiuse da parentesi angolari <...>, da un testo."""

# Regex to find JSON objects (limited to one level of nesting)
INFO_REGEX_CURLY = r'\{[^{}]*\}(?:,\s*\{[^{}]*\})*'
"""Regex per estrarre oggetti json, racchiuse da parentesi graffe {...}, da un testo. (limitata a 1 livello di nidificazione)"""

# Load environment variables from .env file

# Other available models:
# https://openai.com/api/pricing/
# gpt-3.5-turbo-0125
# gpt-4o-mini
# gpt-4o-2024-08-06 *
# gpt-4
# chatgpt-4o-latest
# gpt-4o
# o3-mini


#claude-3-sonnet-20241022 *
load_dotenv(find_dotenv())

if(MODEL == 'openai'):
    openai_api_key = os.getenv("OPENAI_API_KEY")
    llm = ChatOpenAI(api_key=openai_api_key, model="gpt-4o-2024-08-06")
    
if(MODEL == 'anthropic'):
    anthropic_api_key=os.getenv("ANTHROPIC_API_KEY")
    llm = ChatAnthropic(model='claude-3-5-sonnet-20241022')


def get_prompt(input_prompt, memory):
    """
    Costruisce un template di prompt  (ChatPromptTemplate) da inviare al LLM utilizzando LangChain,
    includendo l'input del prompt e ed eventuale memoria per mantenere il contesto della conversazione.
    
    Args : 
    - input_prompt : prompt iniziale da fornire come messaggio di sistema.
    - memory : contiene la memoria della conversazione, se presente.
    
    Returns : 
    - ChatPromptTemplate : Template del prompt da utilizzare nella catena LangChain.
    """

    if(memory != None):
        return ChatPromptTemplate.from_messages(
            [
                ("system", input_prompt),
                MessagesPlaceholder(variable_name="memory"),
                ("human", "{query}"),
            ]
        )
    else:
        return ChatPromptTemplate.from_messages(
            [
                ("system", input_prompt),
                ("human", "{query}"),
            ]
        )
    

def get_token(answer):
    """
    Estrare il token dalla risposta generata dal LLM.

    Args : 
    - answer : risposta generata dal LLM.

    Returns : 
    - action : token estratto dalla risposta generata dal LLM.
    """
    action = re.search(TOKEN_REGEX, answer)
    action = action.group()
    return action


def get_info(answer):
    """
    Estrae informazioni strutturate dalla risposta del LLM.
    
    Args : 
    - answer : testo della risposta generata dal LLM.

    Returns : 
    - str: stringa contenente le informazioni estratte, combinate da entrambi i pattern.
    """
    info_angular = re.search(INFO_REGEX_ANGULAR, answer)
    if info_angular != None:
        info_angular = info_angular.group()
    else:
        info_angular = ""

    info_curly = re.search(INFO_REGEX_CURLY, answer)
    if info_curly != None:
        info_curly = info_curly.group()
    else:
        info_curly = ""

    return info_angular + " " + info_curly


def clean_answer_from_token_and_info(answer, info):
    """
    Rimuove dalla risposta generata dal LLM il token e le informazioni aggiuntive, per ottenere il semplice
    testo della risposta (che sarà inviato dal chatbot all'utente). 
    Esegue anche una pulizia tramite funzione utility e rimuove spazi residui se erano presenti info.

    Args:
    - answer : risposta generata dal LLM.
    - info : informazioni aggiuntive precedentemente estratte dalla risposta.

    Returns:
    - str: risposta generata dal LLM ripulita da token, info e caratteri superflui.
    """
    answer = re.sub(TOKEN_REGEX, "", answer)
    answer = re.sub(INFO_REGEX_ANGULAR, "", answer)
    answer = re.sub(INFO_REGEX_CURLY, "", answer)
    answer = Utils.clean_json_string(answer)

    # Remove leading and trailing whitespace when info is not empty
    # this because in this situation the answer will be empty, so must ensure that there are no leading or trailing whitespaces
    if(info != ""):
        answer = answer.strip()
    return answer


def execute_chain(input_prompt, input_query, temperature, userData, memory = None, memory_enabled = False):

    """
    Esegue la chain di interazione con il modello LLM, in particolare : 
    1. Salva nei log input_query e input_prompt
    2. Imposta la temperatura del modello con la temperatura data in input.
    3. Costruisce il prompt con get_prompt(input_prompt, memory)
    4. Costruisce la pipeline chain come : prompt ->  LLM -> output parser
    5. Ottiene la risposta del modello invocando la chain tramite il metodo invoke.
    6. Estrae dalla risposta il token, le informazioni, e la risposta effettiva (inoltre, se presente, aggiorna la memoria)
    7. Crea l'oggetto risposta come istanza della classe Response, la salva nei log, e la restituisce in output.

    Args:
    - input_prompt : prompt di input.
    - input_query : query di input da inviare al modello.
    - temperature : valore della temperatura del modello (creatività).
    - userData : dati dell'utente sta interagendo con il sistema.
    - memory : memoria della conversazione, se già inizializzata.
    - memory_enabled : flag booleano che se True inizializza la memoria se non è già fornita (di default False).

    Returns:
    - Response: oggetto istanza della classe Response contenente la risposta generata, il token, le info estratte e lo stato della memoria.
    """
    log.save_log(input_query, datetime.datetime.now(), "User", userData.id, PRINT_LOG)
    log.save_log(input_prompt, datetime.datetime.now(), "System: input_prompt", userData.id, PRINT_LOG)
    llm.temperature = temperature

    # Initialize memory if it is not provided and required
    if memory == None and memory_enabled:
        memory = ChatMessageHistory()
        memory.add_user_message(input_prompt)

    prompt = get_prompt(input_prompt,memory)
    
    output_parser = StrOutputParser()

    chain = prompt | llm | output_parser

    if(memory != None):
        log.save_log(memory, datetime.datetime.now(), "System: memory", userData.id, PRINT_LOG)
        answer = chain.invoke({ "query": input_query, "memory": memory.messages })
    else:
        answer = chain.invoke({ "query": input_query })

    # answer rappresenta la risposta dal modello LLM, che oltre al semplice testo da inviare all'utente
    # tramite chatbot contiene altre informazioni da estrarre

    """
    Il LLM restituisce come risposta il TOKEN in cui fa la transizione di stato corrispodente 
    ed eventualmente un messaggio di risposta.
    """
        
    action = get_token(answer)
    info = get_info(answer)
    answer = clean_answer_from_token_and_info(answer, info)

    if(memory != None):
        memory.add_user_message(input_query)
        memory.add_ai_message(answer)
        
    response = resp.Response(answer,action,info,memory,'')
    log.save_log(response, datetime.datetime.now(), "Agent "+MODEL, userData.id, PRINT_LOG)
    
    return response

