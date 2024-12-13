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

def scraper():

    # DataFrame para armazenar os imóveis exibidos
    displayed_properties = pd.DataFrame()

    ### Pedro Granado Imóveis

    main_page = get_html("https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&ordem=1")
    num_properties = int(re.search(r"(?<=\()\d+(?=\))", main_page.select("option")[4].text).group())
    num_pages = -(-num_properties // 16)  # Arredonda para cima

    for j in range(1, num_pages + 1):
        page_url = f"https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&ordem=1&&pag={j}"
        main_page = get_html(page_url)
        
        urls = list(set(a['href'] for a in main_page.select("div.col-lg-4 a")))
        
        for url in urls:
            property_url = f"https://www.pedrogranado.com.br/{url}"
            property_page = get_html(property_url)
            
            district = main_page.select_one("h4.lead").text.strip()
            price = main_page.select("h3")[urls.index(url) + 1].text.strip()
            category = property_page.select("div.col-4.mb-4 span")[0].text.strip()
            
            try:
                area = float(re.sub(" M²", "", property_page.select("div.col-4.mb-4 span")[2].text.strip()))
            except:
                area = None
            
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
                'category': category,
                'area': area,
                'lat': lat,
                'long': long
            }])
            
            displayed_properties = pd.concat([displayed_properties, property_info], ignore_index=True)

    ### Lelo Imóveis

    main_page = get_html("https://www.leloimoveis.com.br/imoveis/venda-maringa")
    num_properties = int(re.search(r"\d+", main_page.select_one("strong.list__highlight").text).group())
    num_pages = -(-num_properties // 16)

    for j in range(1, num_pages + 1):
        page_url = f"https://www.leloimoveis.com.br/imoveis/venda-maringa-pagina-{j}"
        main_page = get_html(page_url)
        
        urls = [a['href'] for a in main_page.select("div.list__hover a")]
        
        for url in urls:
            property_url = f"https://www.leloimoveis.com.br{url}"
            property_page = get_html(property_url)
            
            category = main_page.select("span.list__type")[urls.index(url)].text.strip().split()[0]
            price = main_page.select("span.list__price")[urls.index(url) * 2].text.strip()
            district = main_page.select("span.list__address")[urls.index(url)].text.strip().split(" - ")[0]
            
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
                'category': category,
                'lat': lat,
                'long': long
            }])
            
            displayed_properties = pd.concat([displayed_properties, property_info], ignore_index=True)

    ### Silvio Iwata Imóveis

    main_page = get_html("https://www.silvioiwata.com.br/imoveis/venda")
    num_properties = int(re.search(r"\d+", main_page.select_one("p.cor-primaria").text).group())
    num_pages = -(-num_properties // 9)

    for j in range(1, num_pages + 1):
        page_url = f"https://www.silvioiwata.com.br/imoveis/venda?pagina={j}"
        main_page = get_html(page_url)
        
        urls = [a['href'].strip() for a in main_page.select("div.box-img-lista a")]
        
        for url in urls:
            property_url = f"https://www.silvioiwata.com.br{url}"
            property_page = get_html(property_url)
            
            detail_page = main_page.select("div.lista-imoveis-detalhes p")[urls.index(url) * 2].text.strip().split("\n")
            
            category = detail_page[0] if len(detail_page) > 0 else None
            district = detail_page[1].split(" - ")[0] if len(detail_page) > 1 else None
            price = main_page.select("span.valor")[urls.index(url)].text.strip()
            
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
                'category': category,
                'lat': lat,
                'long': long
            }])
            
            displayed_properties = pd.concat([displayed_properties, property_info], ignore_index=True)
    
    return displayed_properties

# Execute scraper

for i in range(3):
    try:
        displayed_properties = scraper()
        print("Success in first try")
        break
    except Exception as e:
        print(f"Try {i + 1} times but failed in all of them: {e}")
        time.sleep(10)
else:
    print("All tries failed")

### Carregar imóveis passados

past_properties = pd.read_csv("Past Displayed Properties.csv", sep=';')

displayed_properties.to_csv("Past Displayed Properties.csv", sep=';', index=False)

### Identificar imóveis vendidos

sold_properties = past_properties.merge(displayed_properties, on="property_url", how="left", indicator=True)
sold_properties = sold_properties[sold_properties['_merge'] == 'left_only'].drop(columns=['_merge'])
sold_properties['sold_date'] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

past_sold_properties = pd.read_csv("Past Sold Properties.csv", sep=';')
past_sold_properties = pd.concat([past_sold_properties, sold_properties], ignore_index=True)

past_sold_properties.to_csv("Past Sold Properties.csv", sep=';', index=False)

### Identificar novos imóveis

new_properties = displayed_properties.merge(past_properties, on="property_url", how="left", indicator=True)
new_properties = new_properties[new_properties['_merge'] == 'left_only'].drop(columns=['_merge'])
new_properties['added_date'] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

past_new_properties = pd.read_csv("Past New Properties.csv", sep=';')
past_new_properties = pd.concat([past_new_properties, new_properties], ignore_index=True)

past_new_properties.to_csv("Past New Properties.csv", sep=';', index=False)
