import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import datetime, timedelta
import time

# Configuração do diretório de trabalho
os.chdir(r"C:\Users\joaov\Documents\Maringa Housing")

# Função para obter o HTML de uma página
def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')

def pedro_granado_scraper():

    # Pedro Granado Imóveis

    displayed_properties = pd.DataFrame()

    main_page = get_html("https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&ordem=1")
    num_properties = int(re.search(r"(?<=\()\d+(?=\))", main_page.select("option")[4].text).group())
    num_pages = -(-num_properties // 16)  # Arredonda para cima

    for j in range(1, num_pages + 1):
        time.sleep(0.5)
        page_url = f"https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&ordem=1&&pag={j}"
        main_page = get_html(page_url)

        properties = main_page.select("div.card_imoveis_home")
                
        for property in properties:

            district = property.select('div.col-lg-4 h4')[0].text.strip()
            price = property.select('div.col-lg-4 h3')[0].text.strip()

            small_text = property.select('div.col-lg-4 small')[0].text.split('\n\n')

            category = small_text[1].split('-')[0].strip()
            type = small_text[1].split('-')[1].strip()
            ref = small_text[0].split(':')[1].strip()
            city = small_text[2].split('-')[0].strip()
            state = small_text[2].split('-')[1].strip()

            num_bedroom = property.select('div.d-inline')[0].text.split('|')[1].strip()
            num_bathroom = property.select('div.d-inline')[1].text.split('|')[1].strip()
            num_garage = property.select('div.d-inline')[2].text.split('|')[1].strip()

            try:
                area = small_text[3].split(':')[1].strip()
            except:
                area = None

            url = property.select('div.col-lg-4 a')[0]['href']
            property_url = f"https://www.pedrogranado.com.br/{url}"

            time.sleep(0.5)
            property_page = get_html(property_url)
                        
            lat_long_src = property_page.select("iframe")[1]['src']
            try:
                lat = float(re.search(r"(?<=latIni=)-?\d+\.\d+", lat_long_src).group())
                long = float(re.search(r"(?<=longIni=)-?\d+\.\d+", lat_long_src).group())
            except:
                lat = None
                long = None
            
            broker = 'Pedro Granado Imóveis'
            
            property_info = pd.DataFrame([{
                'property_url': property_url,
                'broker': broker,
                'district': district,
                'price': price,
                'type': type,
                'city': city,
                'state': state,
                'ref': ref,
                'category': category,
                'area': area,
                'lat': lat,
                'long': long,
                'num_bedroom': None,
                'num_bathroom': None,
                'num_garage': None
            }])
            
            displayed_properties = pd.concat([displayed_properties, property_info], ignore_index=True)
    
    return displayed_properties

def lelo_scraper():

    # Lelo Imóveis

    displayed_properties = pd.DataFrame()

    main_page = get_html("https://www.leloimoveis.com.br/imoveis/venda-maringa")
    num_properties = int(re.search(r"\d+", main_page.select_one("strong.list__highlight").text).group())
    num_pages = -(-num_properties // 16)

    for j in range(1, num_pages + 1):
        time.sleep(0.5)
        page_url = f"https://www.leloimoveis.com.br/imoveis/venda-maringa-pagina-{j}"
        main_page = get_html(page_url)

        properties = main_page.select('div.list__hover')
                
        for property in properties:

            district = property.select("span.list__address")[0].text.split("-")[0].strip()
            price = property.select("span.list__price")[0].text.strip()

            category = property.select("span.list__type")[0].text.strip().split()[0]
            type = None
            ref = property.select("span.list__reference")[0].text.strip()
            city = property.select("span.list__address")[0].text.strip().split(" - ")[1].split('/')[0]
            state = property.select("span.list__address")[0].text.strip().split(" - ")[1].split('/')[1]

            area = property.select("div.list__feature")[0].select('div.list__item')[0].select('span')[0].text.split()[0]

            if len(property.select("div.list__feature")[0].select('div.list__item')) > 1:
                num_bedroom = property.select("div.list__feature")[0].select('div.list__item')[1].select('span')[0].text.strip()
            else:
                num_bedroom = None
            
            if len(property.select("div.list__feature")[0].select('div.list__item')) > 2:
                num_garage = property.select("div.list__feature")[0].select('div.list__item')[2].select('span')[0].text.strip()
            else:
                num_garage = None

            url = property.select('a')[0]['href']
            property_url = f"https://www.leloimoveis.com.br{url}"

            time.sleep(0.5)
            property_page = get_html(property_url)

            try:
                lat = float(property_page.select_one("div.card__map-container")['data-latitude'])
                long = float(property_page.select_one("div.card__map-container")['data-longitude'])
            except:
                lat = None
                long = None
            
            broker = 'Lelo Imóveis'
            
            property_info = pd.DataFrame([{
                'property_url': property_url,
                'broker': broker,
                'district': district,
                'price': price,
                'type': type,
                'city': city,
                'state': state,
                'ref': ref,
                'category': category,
                'area': area,
                'lat': lat,
                'long': long,
                'num_bedroom': num_bedroom,
                'num_bathroom': None,
                'num_garage': num_garage
            }])
            
            displayed_properties = pd.concat([displayed_properties, property_info], ignore_index=True)

    return displayed_properties

def silvio_iwata_scraper():

    # Silvio Iwata Imóveis

    displayed_properties = pd.DataFrame()

    main_page = get_html("https://www.silvioiwata.com.br/imoveis/venda")
    num_properties = int(re.search(r"\d+", main_page.select_one("p.cor-primaria").text).group())
    num_pages = -(-num_properties // 9)

    for j in range(1, num_pages + 1):
        time.sleep(0.5)
        page_url = f"https://www.silvioiwata.com.br/imoveis/venda?pagina={j}"
        main_page = get_html(page_url)
        
        properties = main_page.select('div.content')
        
        for property in properties:

            bold_text = property.select('div.lista-imoveis-detalhes')[0].select('strong')[1].text.split('-')

            district = bold_text[0].strip() if len(bold_text) == 3 else None
            price = property.select('div.lista-imoveis-detalhes')[0].select('strong')[0].text.strip()

            small_text = property.select('div.lista-imoveis-detalhes')[0].select('p')[1].text.split('\n')
            small_text = [text.strip() for text in small_text]
            small_text = [text for text in small_text if text != '']

            category = small_text[0]
            type = None
            ref = None
            city = bold_text[1].strip() if len(bold_text) == 3 else bold_text[0].strip()
            state = bold_text[2].strip() if len(bold_text) == 3 else bold_text[1].strip()

            area = small_text[1].split(':')[1].strip()

            bed_bath_garage = property.select('span.box-comodo')[0]
            if len(bed_bath_garage) > 1:

                gross_num_bedroom = bed_bath_garage.select('span.bath')
                gross_num_bedroom = gross_num_bedroom[0].text if gross_num_bedroom else None
                if '+' in gross_num_bedroom:
                    num_bedroom = sum([float(num.strip()) for num in gross_num_bedroom.split('+')])
                else:
                    num_bedroom = gross_num_bedroom.strip()

                num_bathroom = bed_bath_garage.select('span.bathroom')
                num_bathroom = num_bathroom[0].text if num_bathroom else None

                num_garage = bed_bath_garage.select('span.garage')
                num_garage = num_garage[0].text.strip() if num_garage else None

            else:
                num_bedroom = None
                num_bathroom = None
                num_garage = None

            url = property.select('div.box-img-lista')[0].select('a')[0]['href']
            property_url = f"https://www.silvioiwata.com.br{url}"

            time.sleep(0.5)
            property_page = get_html(property_url)

            try:
                lat, long = map(float, property_page.select_one("#coordenadas_mapa").text.split(","))
            except:
                lat = None
                long = None
            
            broker = 'Silvio Iwata'
            
            property_info = pd.DataFrame([{
                'property_url': property_url,
                'broker': broker,
                'district': district,
                'price': price,
                'type': type,
                'city': city,
                'state': state,
                'ref': ref,
                'category': category,
                'area': area,
                'lat': lat,
                'long': long,
                'num_bedroom': num_bedroom,
                'num_bathroom': num_bathroom,
                'num_garage': num_garage
            }])
            
            displayed_properties = pd.concat([displayed_properties, property_info], ignore_index=True)
    
    return displayed_properties

displayed_properties_pedro_granado = pedro_granado_scraper()

displayed_properties_lelo = lelo_scraper()

displayed_properties_silvio_iwata = silvio_iwata_scraper()

displayed_properties = pd.concat([displayed_properties_pedro_granado,
                                  displayed_properties_lelo,
                                  displayed_properties_silvio_iwata], ignore_index=True)

print(displayed_properties)

# Execute scraper

# for i in range(5):
#     try:
#         displayed_properties = scraper()
#         print(f"Success in try {i+1}")
#         break
#     except Exception as e:
#         print(f"Failed in try {i+1}: {e}")
#         time.sleep(10)
# else:
#     print("All tries failed")

### Carregar imóveis passados

# past_properties = pd.read_csv("Past Displayed Properties.csv", sep=';')

# displayed_properties.to_csv("Past Displayed Properties.csv", sep=';', index=False)

# ### Identificar imóveis vendidos

# sold_properties = past_properties.merge(displayed_properties, on="property_url", how="left", indicator=True)
# sold_properties = sold_properties[sold_properties['_merge'] == 'left_only'].drop(columns=['_merge'])
# sold_properties['sold_date'] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# past_sold_properties = pd.read_csv("Past Sold Properties.csv", sep=';')
# past_sold_properties = pd.concat([past_sold_properties, sold_properties], ignore_index=True)

# past_sold_properties.to_csv("Past Sold Properties.csv", sep=';', index=False)

# ### Identificar novos imóveis

# new_properties = displayed_properties.merge(past_properties, on="property_url", how="left", indicator=True)
# new_properties = new_properties[new_properties['_merge'] == 'left_only'].drop(columns=['_merge'])
# new_properties['added_date'] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

# past_new_properties = pd.read_csv("Past New Properties.csv", sep=';')
# past_new_properties = pd.concat([past_new_properties, new_properties], ignore_index=True)

# past_new_properties.to_csv("Past New Properties.csv", sep=';', index=False)
