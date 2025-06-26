import os
import anthropic
import dto.Response as resp
import service.bot.LogService as log
import datetime
from dotenv import load_dotenv, find_dotenv


PRINT_LOG = False

load_dotenv(find_dotenv())


# disponibile solo con i modelli : claude-3-7-sonnet-20250219, claude-3-5-sonnet-latest, claude-3-5-haiku-latest

MODEL = "claude-3-7-sonnet-latest" 
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))


def get_response_text(response):
    """
    Estrae dalla riposta generata dal modello a seguito della ricerca web la risposta tesuale completa.

    Args : 
    - response : risposta generata dal modello di Web Search, contenente varie informazioni oltre alla risposta testuale.

    Returns : 
    - response_text : risposta testuale generata dal modello di Web Search.

    """
    # estraiamo tutti i blocchi di testo
    text_block = [
        block.text
        for block in response.content
        if getattr(block, 'type', None) == 'text' and getattr(block, 'text', None) is not None
    ]

    # concateniamo tutti i blocchi per ottenere la risposta finale
    response_text = ''.join(text_block)

    return response_text


def get_citations_and_urls(response):

    """
    Estrae dalla risposta generata dal modello di Web Search le citazioni delle risorse web usate considerate nella ricerca, con i loro rispettivi url.
    
    Args : 
    - response : risposta generata dal modello di Web Search, contenente varie informazioni oltre alla risposta testuale.

    Returns : 
    - citations_and_urls : citazioni da fonti esterne all'intero della risposta testuale generata, con i rispettivi url.
    """


    citations_and_urls = []
    
    for block in getattr(response, "content", []):
        if block.type == "text" and hasattr(block, "text") and block.text:
            citations = getattr(block, "citations", None)
            if citations:
                for citation in citations:
                    url = getattr(citation, "url", None)
                    cit = {
                        "url": url,
                        "title": getattr(citation, "title", None),
                        "cited_text": getattr(citation, "cited_text", None)
                    }
                    citations_and_urls.append(cit)
                    

    return citations_and_urls




def web_search(input_prompt, input_query, temperature, userData, memory=None, memory_enabled=False):

    #print("***************************************************************\nweb_search()")
    #print("input_prompt : ", input_prompt)
    #print("input_query : ", input_query)
    #print("temperature : ", temperature)
    #print("userData : ", userData)

    # input prompt  : prompt già costruito tramite WEB_SEARCH.format(concept=concep)
    # input_query : serve per aggiornare la memoria solo con la domanda dell'utente senza salvare tutto il prompt

    log.save_log(input_query, datetime.datetime.now(), "User", userData.id, PRINT_LOG)
    log.save_log(input_prompt, datetime.datetime.now(), "System: input_prompt", userData.id, PRINT_LOG)

    # Se messages non è fornito, inizializza una lista vuota
    if memory is None and memory_enabled:
        memory = []

    # aggiungiamo la richiesta dell'utente alla memoria
    if memory_enabled:
        memory.append({"role": "user", "content": input_query})

    """
    print("\nMemory aggiornata:")
    for msg in memory:
        print(msg)
        print()
    """

    response = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        system=input_prompt,
        messages=memory,
        temperature=temperature,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search",
            "max_uses": 5
        }]
    )

    # estraiamo la risposta testuale e le citazioni con le rispettive fonti dalla risposta generata dal modello di Web Search
    clean_answer = get_response_text(response)
    citations_and_urls = get_citations_and_urls(response)

    # aggiungiamo la risposta del modello alla memoria
    if memory_enabled :
        memory.append({"role": "assistant", "content": clean_answer})

    """
    print("\nMemory :")
    for msg in memory:
        print(msg)
        print()
    """

    # mettiamo tutto in answer in modo da salvare tutto nella risposta finale
    answer = {
        'clean_answer': clean_answer,
        'citations_and_urls': citations_and_urls
    }

    # creiamo la risposta finale, oggetto istanza della classe Response
    final_response = resp.Response(answer, "", "", memory, '')

    log.save_log(final_response, datetime.datetime.now(), "Web Search", userData.id, PRINT_LOG)

    print("***************************************************************")

    return final_response


"""
Esempio di response : 

Message(id='msg_01GNEJxMttaZ8QZGumfWo5B4', content=[

    TextBlock(
        citations=None, 
        text="I'll explore the relationship between food and climate change for you. Let me search for the most current information on this topic.", 
        type='text'), 

    TextBlock(
        citations=None, 
        text=None, 
        type='server_tool_use', 
        id='srvtoolu_019KmCrPk8AeVimyQJNN29en', 
        name='web_search', 
        input={'query': 'food production impact on climate change greenhouse gas emissions'}), 
    
    TextBlock(
        citations=None, 
        text=None, 
        type='web_search_tool_result', 
        tool_use_id='srvtoolu_019KmCrPk8AeVimyQJNN29en', 
        content=[
            
        {
            'type': 'web_search_result', 
            'title': 'Food and Climate Change: Healthy diets for a healthier planet | United Nations', 
            'url': 'https://www.un.org/en/climatechange/science/climate-issues/food', 
            'encrypted_content': '...', 
            'page_age': None}, 
    
        {   'type': 'web_search_result', 
            'title': 'Future warming from global food consumption | Nature Climate Change', 
            'url': 'https://www.nature.com/articles/s41558-023-01605-8', 
            'encrypted_content': '...', 
            'page_age': None}, 
            
        {   
            'type': 'web_search_result', 
            'title': 'Environmental Impacts of Food Production - Our World in Data', 
            'url': 'https://ourworldindata.org/environmental-impacts-of-food', 
            'encrypted_content': '...', 
            'page_age': 'December 2, 2022'},
        
        {
            'type': 'web_search_result', 
            'title': 'How Our Food System Affects Climate Change - FoodPrint', 
            'url': 'https://foodprint.org/issues/how-our-food-system-affects-climate-change/', 
            'encrypted_content': '...', 
            'page_age': 'February 28, 2024'},
        
        {
            'type': 'web_search_result', 
            'title': 'The Importance of the Food Industry for Climate Change | Econofact', 
            'url': 'https://econofact.org/the-importance-of-the-food-industry-for-climate-change', 
            'encrypted_content':'...', 
            'page_age': 'October 26, 2023'}, 
            
        {
            'type': 'web_search_result', 
            'title': 'Climate Change Impacts on Agriculture and Food Supply | US EPA', 
            'url': 'https://www.epa.gov/climateimpacts/climate-change-impacts-agriculture-and-food-supply', 'encrypted_content': '...', 
            'page_age': 'October 19, 2022'}, 
        
        {
            'type': 'web_search_result', 
            'title': 'Food and Climate Change | Food System Primer', 
            'url': 'https://foodsystemprimer.org/production/food-and-climate-change', 
            'encrypted_content':'...', 
            'page_age': None}, 
        
        {
            'type': 'web_search_result', 
            'title': 'How food and agriculture contribute to climate change | Reuters', 
            'url': 'https://www.reuters.com/business/environment/factbox-how-food-agriculture-contribute-climate-change-2023-12-02/', 
            'encrypted_content': '...', 
            'page_age': 'December 2, 2023'}, 
            
        {
            'type': 'web_search_result', 
            'title': "Here's How Much Food Contributes to Climate Change | Scientific American", 
            'url': 'https://www.scientificamerican.com/article/heres-how-much-food-contributes-to-climate-change/', '...', 
            'page_age': 'February 20, 2024'}, 
            
        {
            'type': 'web_search_result', 'title': 'What You Need to Know About Food Security and Climate Change', 'url': 'https://www.worldbank.org/en/news/feature/2022/10/17/what-you-need-to-know-about-food-security-and-climate-change', 'encrypted_content': '...', 
            'page_age': 'October 19, 2022'
        }
        ]),
        
    TextBlock(
        citations=None, 
        text='\n\nBased on the search results, I can provide you with a comprehensive explanation of how food is related to climate change.\n\n# How Food is Related to Climate Change\n\n## Food Systems: A Major Contributor to Greenhouse Gas Emissions\n\n', 
        type='text'), 
        
    TextBlock(
        citations=[
        
            CitationCharLocation(
                cited_text='One-quarter to one-third of global greenhouse gas emissions come from our food systems. ',
                document_index=None, document_title=None, end_char_index=None, start_char_index=None, 
                type='web_search_result_location', 
                url='https://ourworldindata.org/environmental-impacts-of-food', 
                title='Environmental Impacts of Food Production - Our World in Data', 
                encrypted_index='Eo8BCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDO3n41wwr+TddevwrxoMcuxbY1WQaW41lKGdIjBt7hRf2RXsnzDOYRlM88h6leBmDh+HhRYIPaPGlDQDZoRxVyWN6wK7YiKw7HrFnlsqE44G2Dl/2zgGKevyNyrmw263+BUYBA=='), 
            
            CitationCharLocation(
                cited_text='One-quarter to one-third of global greenhouse gas emissions come from our food systems. The rest comes from energy. While energy and industry make a b...', 
                document_index=None, document_title=None, end_char_index=None, start_char_index=None, 
                type='web_search_result_location', 
                url='https://ourworldindata.org/environmental-impacts-of-food', 
                title='Environmental Impacts of Food Production - Our World in Data', encrypted_index='EpMBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDLrka7KNPtRb863O3RoMZCaAcDEH35uw5iAdIjCYKHAh+MlH1hOlbNUl061VLjf9lFF94iLzNTdVEk02HS0xs5tUV3nyEiaZ/CT3lr0qFzfLNaOZq8NVI2lyQ4Yodd5l+jlNCeRPGAQ=')
        ], 
                
                
        text='One-quarter to one-third of global greenhouse gas emissions come from our food systems, with the rest coming from energy. 
             While energy and industry make a bigger contribution than food, we must tackle both food and energy systems to address climate change effectively.', 
        type='text'), 
        
    
    TextBlock(
        citations=None, 
        text=' In fact, ', 
        type='text'), 
    
    TextBlock(
        citations=[
            CitationCharLocation(
                cited_text='It’s recently been estimated that the global food system is responsible for about a third of greenhouse gas emissions—second only to the energy sector...', 
                document_index=None, document_title=None, end_char_index=None, start_char_index=None, 
                type='web_search_result_location', 
                url='https://www.worldbank.org/en/news/feature/2022/10/17/what-you-need-to-know-about-food-security-and-climate-change', 
                title='What You Need to Know About Food Security and Climate Change', 
                encrypted_index='EpABCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDKyG9EmFINV+uIutKxoMknnWt1dJWoXChAafIjAXoaEokhpnHu7k+Z0DHVHvArNB/T8v7kre/keg4AsDCiyXFhutTkN1rHsd3OS2k8AqFBRAMVrmSeg8IO0z/ZWmmv4iM+3yGAQ=')
        ],
        
        text="it's recently been estimated that the global food system is responsible for about a third of greenhouse gas emissions—second only to the energy sector; it is the number one source of methane and biodiversity loss.", 
        type='text'), 
        
        
    TextBlock(
        citations=None, 
        text='\n\n', type='text'), 
        
    TextBlock(
        citations=[
            CitationCharLocation(
                cited_text='Here are some details about the sources of emissions from the food and agriculture sector: Global food systems accounted for 17 billion metric tonnes ...', 
                document_index=None, document_title=None, end_char_index=None, start_char_index=None, 
                type='web_search_result_location', 
                url='https://www.reuters.com/business/environment/factbox-how-food-agriculture-contribute-climate-change-2023-12-02/', 
                title='How food and agriculture contribute to climate change | Reuters', 
                encrypted_index='EpEBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDB4gxnN9Sp9rIu4XXRoMjN7YxEz7G65hSTbTIjBSQSm6UeuwQuCJ2czgY8pzCVpfKjbPrgmn7z6T8cU32RJ8Mq+EBiyJevITDDsWSMkqFaMgiCHkYO+4CjdJX6muwgQGfGPayRgE')
        ],
        text="Global food systems accounted for 17 billion metric tonnes of carbon dioxide equivalent or 31% of human-made greenhouse gas emissions in 2019, according to the United Nations' Food and Agriculture Organization (FAO). This includes emissions related to farming and land use, producing crops and livestock, household food consumption and waste, and energy used in farm and food processing and transportation.", 
        type='text'), 
        
    TextBlock(
        citations=None, 
        text='\n\n', 
        type='text'),
    
    TextBlock(
        citations=[
            CitationCharLocation(
                cited_text='Soil tillage, crop and livestock transportation, manure management and all the other aspects of global food production generate greenhouse gas emissio...', 
                document_index=None, document_title=None, end_char_index=None, start_char_index=None, 
                type='web_search_result_location', 
                url='https://www.scientificamerican.com/article/heres-how-much-food-contributes-to-climate-change/', 
                title="Here's How Much Food Contributes to Climate Change | Scientific American", 
                encrypted_index='EpMBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDBgfQQ9AivjlYZVZwhoMtUwImsPByqtHvrLeIjC0p0IbjwuUMnhkKaeaolhKVRelXKwKaXTeM2q+xMrbDi3AyEjLHOI4OJwscdjI0s0qF7+3VEMB1icqowycklM5nhnxT4+Q4X9eGAQ=')
        ], 
        text='A study published in Nature Food confirms that global food production generates greenhouse gas emissions of more than 17 billion metric tons per year. Animal-based foods account for 57 percent of those emissions, while plant-based ones make up 29 percent. The detailed breakdown shows how much each agricultural practice, animal product, crop and country contributes to carbon emissions, which can help focus and fine-tune reduction efforts.', type='text'), 
        
    TextBlock(
        citations=None, 
        text='\n\n## Main Sources of Food-Related Emissions\n\n### 1. Animal Agriculture\n\n', 
        type='text'), TextBlock(citations=[CitationCharLocation(cited_text='Animal-based foods, especially red meat, dairy, and farmed shrimp, are generally associated with the highest greenhouse gas emissions. This is because...', document_index=None, document_title=None, end_char_index=None, start_char_index=None, type='web_search_result_location', url='https://www.un.org/en/climatechange/science/climate-issues/food', title='Food and Climate Change: Healthy diets for a healthier planet | United Nations', encrypted_index='EpEBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDEJDlxT9gJgudy2gjBoMW+XWqPjgVtoFgWTOIjBdEnrrKch6Yo8vZ3J2dgk5oNejKyaUG3ffxLsMhx6w9fS6WPM4rGRdRHclsPRVMCYqFUaPiw2NgaGH5JSuu6UP8JXEFEbDjxgE')], text='Animal-based foods, especially red meat, dairy, and farmed shrimp, are generally associated with the highest greenhouse gas emissions. This is because meat production often requires extensive grasslands, which is often created by cutting down trees, releasing carbon dioxide stored in forests.', type='text'), TextBlock(citations=None, text='\n\n', type='text'), TextBlock(citations=[CitationCharLocation(cited_text='We find that global food consumption alone could add nearly 1 °C to warming by 2100. Seventy five percent of this warming is driven by foods that are ...', document_index=None, document_title=None, end_char_index=None, start_char_index=None, type='web_search_result_location', url='https://www.nature.com/articles/s41558-023-01605-8', title='Future warming from global food consumption | Nature Climate Change', encrypted_index='EpEBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDAysLA4R37ovslSklBoM2jYWqq9ukWZKvz0sIjApVYhSRgy5iJubUTgqAbwU1x7/RCuYJdAYuIiyb4VOd4tOqgYXkFnNGt0FUptmm9cqFY/W8O9UQdCQaZNaVG5JXvA3xLp2BhgE')], text='Research indicates that global food consumption alone could add nearly 1°C to warming by 2100. Seventy-five percent of this warming is driven by foods that are high sources of methane (ruminant meat, dairy and rice).', type='text'), TextBlock(citations=None, text='\n\n', type='text'), TextBlock(citations=[CitationCharLocation(cited_text='Of the food products the study examined, beef production was the top emissions contributor by a wide margin, accounting for 25 percent of the total. A...', document_index=None, document_title=None, end_char_index=None, start_char_index=None, type='web_search_result_location', url='https://www.scientificamerican.com/article/heres-how-much-food-contributes-to-climate-change/', title="Here's How Much Food Contributes to Climate Change | Scientific American", encrypted_index='EpMBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDK05fdj10qc0Y+e+8RoMNOUo68vxkRI5vB5pIjBwer8A1hTl1X40lmYAYtSEGLGF15rb+4Qk9G1D769wPcwoxDvVeTO5qa/4dxY/B9UqF1EVExoMjvP/sIDOTp5mZxc9u1gec2CfGAQ=')], text='Of all food products, beef production is the top emissions contributor by a wide margin, accounting for 25 percent of the total. Among animal-based products, it is followed by cow milk, pork, and chicken meat, in that order.', type='text'), TextBlock(citations=None, text='\n\n### 2. Crop Production\n\n', type='text'), TextBlock(citations=[CitationCharLocation(cited_text='In the category of crops, rice farming was the top contributor—and it was the second-highest contributor among all products, accounting for 12 percent...', document_index=None, document_title=None, end_char_index=None, start_char_index=None, type='web_search_result_location', url='https://www.scientificamerican.com/article/heres-how-much-food-contributes-to-climate-change/', title="Here's How Much Food Contributes to Climate Change | Scientific American", encrypted_index='EpMBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDMOvdCPYuzARAOReLRoMwK6Rsf0IGbBC7jSvIjB+Iwer9RO0k4PVHB5yXBoZ3pa9vDjYvqHaqYFzntUKaNBfbvu3Bs45EZ6SWqHqZYMqF005WzBlmcACCN/u/C1FYkSG+qSP07m7GAQ=')], text="In the category of crops, rice farming is the top contributor—and the second-highest contributor among all food products, accounting for 12 percent of the total emissions. Rice's relatively high ranking comes from the methane-producing bacteria that thrive in the anaerobic conditions of flooded paddies. After rice, the highest emissions associated with plant production come from wheat, sugarcane, and maize.", type='text'), TextBlock(citations=None, text='\n\n### 3. Land Use Changes\n\n', type='text'), TextBlock(citations=[CitationCharLocation(cited_text="Deforestation is responsible for nearly 80% of emissions from food production in Brazil, for instance, the world's largest exporter of beef and soybea...", document_index=None, document_title=None, end_char_index=None, start_char_index=None, type='web_search_result_location', url='https://www.reuters.com/business/environment/factbox-how-food-agriculture-contribute-climate-change-2023-12-02/', title='How food and agriculture contribute to climate change | Reuters', encrypted_index='EpIBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDGin8x3LHiKZByTdMRoMvHjQ6Id+cnrZutu0IjAxR91n8zY8+KyMcxndGK+kUt6gI4HjUcBC3ZcK/nXPIX+a53mV5mSh+T61zQGo/swqFsE0y92Y+fsSJHfJE5eidolD0+5r3DQYBA==')], text="Deforestation is responsible for nearly 80% of emissions from food production in Brazil, for instance, the world's largest exporter of beef and soybeans. Peatlands, meanwhile, store massive amounts of carbon - twice as much as the world's forests. Draining or burning peatlands for purposes like growing crops or livestock grazing is responsible for about 5% of all anthropogenic emissions, according to a 2021 report by the United Nations.", type='text'), TextBlock(citations=None, text='\n\n', type='text'), TextBlock(citations=[CitationCharLocation(cited_text='Moreover, agriculture is the main source of deforestation, with forests being cleared to create cropland and pasture for subsistence farming as well a...', document_index=None, document_title=None, end_char_index=None, start_char_index=None, type='web_search_result_location', url='https://econofact.org/the-importance-of-the-food-industry-for-climate-change', title='The Importance of the Food Industry for Climate Change | Econofact', encrypted_index='EpMBCioIAxgCIiQxZDEzYmZjMi1jODE3LTQ0MTYtYmE2MS04N2ZkMTcyZGJjOWISDMCRxaanmeSNLCXT0RoM7K4VIWGE6Y7b3uyqIjAZdInuZ92BCqAM0C7EAKLBeKi11Iyr43G/UZjil8P9lMvdBqYRL0D7kEW7l4jt0gwqF55nMVIM3WZ0PoxOl35j3zL2HPbuhHNrGAQ=')], text="Agriculture is the main source of deforestation, with forests being cleared to create cropland and pasture for subsistence farming as well as for large-scale production. The food industry is one of the most globalized industries, and much of deforestation is due to production of food for exports. For instance, deforestation in the Amazon in recent years is largely due to Brazil's food exports to China and India. This matters because old-growth forests, especially the Amazon, are the best approach we have to carbon sequestration.", type='text')], model='claude-3-7-sonnet-20250219', role='assistant', stop_reason='max_tokens', stop_sequence=None, type='message', usage=Usage(cache_creation_input_tokens=0, cache_read_input_tokens=0, input_tokens=18831, output_tokens=1111, server_tool_use={'web_search_requests': 1}))


"""