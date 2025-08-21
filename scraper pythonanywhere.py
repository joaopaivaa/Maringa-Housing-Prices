import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import os
from datetime import datetime
import time
import numpy as np

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
print(BASE_DIR)

past_properties = pd.read_csv(os.path.join(BASE_DIR, "bronze/Properties.csv"), encoding='utf-8', sep=';')
past_properties_images = pd.read_csv(os.path.join(BASE_DIR, "bronze/Properties Images.csv"), encoding='utf-8', sep=';')

actual_properties_url = []

# Função para obter o HTML de uma página
def get_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, 'lxml')

def pedro_granado_scraper():

    # Pedro Granado Imóveis

    displayed_properties = pd.DataFrame()
    properties_images = pd.DataFrame()

    main_page = get_html("https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&ordem=1")
    num_properties = int(re.search(r"(?<=\()\d+(?=\))", main_page.select("option")[4].text).group())
    num_pages = -(-num_properties // 16)  # Arredonda para cima

    properties = []
    for j in range(1, num_pages + 1):
        time.sleep(0.5)
        page_url = f"https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&ordem=1&&pag={j}"
        main_page = get_html(page_url)

        properties += main_page.select("div.card_imoveis_home")

    for property in properties:

        # Property URL
        if (len(property.select('div.col-lg-4 a')) > 0) and ('href' in property.select('div.col-lg-4 a')[0].attrs):
            url = property.select('div.col-lg-4 a')[0]['href']
            property_url = f"https://www.pedrogranado.com.br/{url}"
            actual_properties_url.append(property_url)
        else:
            property_url = 'URL not found'

        if (property_url == 'URL not found') or (property_url in past_properties['property_url'].values):
            continue

        # Property district
        if (len(property.select('div.col-lg-4 h4')) > 0):
            district = property.select('div.col-lg-4 h4')[0].text.strip()
        else:
            district = None

        # Property price
        if (len(property.select('div.col-lg-4 h3')) > 0):
            price = property.select('div.col-lg-4 h3')[0].text.strip()
        else:
            price = None

        # Property category, type, reference code, city, state and area
        if (len(property.select('div.col-lg-4 small')) > 0) and ('\n\n' in property.select('div.col-lg-4 small')[0].text):
            small_text = property.select('div.col-lg-4 small')[0].text.split('\n\n')

            if len(small_text) > 0:
                if (':' in small_text[0]):
                    ref = small_text[0].split(':')[1].strip() if len(small_text) > 0 else None
                else:
                    ref = None

            if len(small_text) > 1:
                if ('-' in small_text[1]):
                    category = small_text[1].split('-')[0].strip()
                    type = small_text[1].split('-')[1].strip()
                else:
                    category = None
                    type = None

            if len(small_text) > 2:
                if ('-' in small_text[2]):
                    city = small_text[2].split('-')[0].strip()
                    state = small_text[2].split('-')[1].strip()
                else:
                    city = None
                    state = None

            if len(small_text) > 3:
                if (':' in small_text[3]):
                    area = small_text[3].split(':')[1].strip()
                else:
                    area = None

        else:
            category = None
            type = None
            ref = None
            city = None
            state = None
            area = None

        # Property number of bedroom, bathroom and garage
        if (len(property.select('div.d-inline')) > 0):
            num_bed_bath_garage = property.select('div.d-inline')

            if ('|' in num_bed_bath_garage[0].text) and (len(num_bed_bath_garage) > 0):
                num_bedroom = num_bed_bath_garage[0].text.split('|')[1].strip()
            else:
                num_bedroom = None

            if ('|' in num_bed_bath_garage[1].text) and (len(num_bed_bath_garage) > 1):
                num_bathroom = num_bed_bath_garage[1].text.split('|')[1].strip()
            else:
                num_bathroom = None

            if ('|' in num_bed_bath_garage[2].text) and (len(num_bed_bath_garage) > 2):
                num_garage = num_bed_bath_garage[2].text.split('|')[1].strip()
            else:
                num_garage = None

        else:
            num_bedroom = None
            num_bathroom = None
            num_garage = None

        # Loads property page
        property_page = get_html(property_url)

        # Property latitude and longitude
        if (len(property_page.select("iframe")) > 1):
            lat_long_src = property_page.select("iframe")[1]['src']
            try:
                lat = float(re.search(r"(?<=latIni=)-?\d+\.\d+", lat_long_src).group())
                long = float(re.search(r"(?<=longIni=)-?\d+\.\d+", lat_long_src).group())
            except:
                lat = None
                long = None
        else:
            lat = None
            long = None

        # Property images
        if (len(property_page.select('#imageGallery')) > 0):

            images = property_page.select('#imageGallery')[0].select('img')
            images = [image['src'] for image in images]
            images = list(set(images))

            if (len(images) > 0):
                for image in images:
                    property_images = pd.DataFrame([{
                        'property_url': property_url,
                        'image_url': image,
                        'order': [i for i, img in enumerate(images) if img == image][0]
                    }])
                    properties_images = pd.concat([properties_images, property_images], ignore_index=True)

        # Property broker
        broker = 'Pedro Granado Imóveis'

        # Property informations
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

        time.sleep(0.5)

    return displayed_properties, properties_images

def lelo_scraper():

    # Lelo Imóveis

    displayed_properties = pd.DataFrame()
    properties_images = pd.DataFrame()

    main_page = get_html("https://www.leloimoveis.com.br/imoveis/venda-maringa")
    num_properties = int(re.search(r"\d+", main_page.select_one("strong.list__highlight").text).group())
    num_pages = -(-num_properties // 16)

    properties = []
    for j in range(1, num_pages + 1):
        time.sleep(0.5)
        page_url = f"https://www.leloimoveis.com.br/imoveis/venda-maringa-pagina-{j}"
        main_page = get_html(page_url)

        properties += main_page.select('div.list__hover')

    for property in properties:

        # Property URL
        if (len( property.select('a')) > 0) and ('href' in property.select('a')[0].attrs):
            url = property.select('a')[0]['href']
            property_url = f"https://www.leloimoveis.com.br{url}"
            actual_properties_url.append(property_url)
        else:
            property_url = 'URL not found'

        if (property_url == 'URL not found') or (property_url in past_properties['property_url'].values):
            continue

        # Property district
        if (len(property.select("span.list__address")) > 0):
            if ('-' in property.select("span.list__address")[0].text):
                district = property.select("span.list__address")[0].text.split("-")[0].strip()
            else:
                district = None
        else:
            district = None

        # Property price
        if (len(property.select("span.list__price")) > 0):
            price = property.select("span.list__price")[0].text.strip()
        else:
            price = None

        # Property category
        if (len(property.select("span.list__type")) > 0) and (len(property.select("span.list__type")[0].text.strip().split()) > 0):
            category = property.select("span.list__type")[0].text.strip().split()[0]
        else:
            category = None

        # Property reference code
        if (len(property.select("span.list__reference")) > 0):
            ref = property.select("span.list__reference")[0].text.strip()
        else:
            ref = None

        # Property city and state
        if (len(property.select("span.list__address")) > 0):
            if (' - ' in property.select("span.list__address")[0].text.strip()):
                if ('/' in property.select("span.list__address")[0].text.strip().split(" - ")[1]):
                    city = property.select("span.list__address")[0].text.strip().split(" - ")[1].split('/')[0]
                    state = property.select("span.list__address")[0].text.strip().split(" - ")[1].split('/')[1]
                else:
                    city = None
                    state = None
            else:
                city = None
                state = None
        else:
            city = None
            state = None

        # Property area
        if (len(property.select("div.list__feature")) > 0) and (len(property.select("div.list__feature")[0].select('div.list__item')) > 0) and (len(property.select("div.list__feature")[0].select('div.list__item')[0].select('span')) > 0) and (len(property.select("div.list__feature")[0].select('div.list__item')[0].select('span')[0].text.split()) > 0):
            area = property.select("div.list__feature")[0].select('div.list__item')[0].select('span')[0].text.split()[0]
        else:
            area = None

        # Property number of bedroom and garage
        if (len(property.select("div.list__feature")) > 0):

            if len(property.select("div.list__feature")[0].select('div.list__item')) > 1:
                num_bedroom = property.select("div.list__feature")[0].select('div.list__item')[1].select('span')[0].text.strip()
            else:
                num_bedroom = None

            if len(property.select("div.list__feature")[0].select('div.list__item')) > 2:
                num_garage = property.select("div.list__feature")[0].select('div.list__item')[2].select('span')[0].text.strip()
            else:
                num_garage = None

        else:
            num_bedroom = None
            num_garage = None

        # Loads property page
        property_page = get_html(property_url)

        # Property latitude and longitude
        try:
            lat = float(property_page.select_one("div.card__map-container")['data-latitude'])
            long = float(property_page.select_one("div.card__map-container")['data-longitude'])
        except:
            lat = None
            long = None

        # Property images
        if (len(property_page.select('div.card__photo-box')) > 0):
            
            images = property_page.select('div.card__photo-box')[0].select('img')
            images = [image['src'] for image in images]
            images = list(set(images))

            if (len(images) > 0):
                for image in images:
                    property_images = pd.DataFrame([{
                        'property_url': property_url,
                        'image_url': image,
                        'order': [i for i, img in enumerate(images) if img == image][0]
                    }])
                    properties_images = pd.concat([properties_images, property_images], ignore_index=True)

        # Property broker
        broker = 'Lelo Imóveis'

        # Property informations
        property_info = pd.DataFrame([{
            'property_url': property_url,
            'broker': broker,
            'district': district,
            'price': price,
            'type': None,
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

        time.sleep(0.5)

    return displayed_properties, properties_images

def silvio_iwata_scraper():

    # Silvio Iwata Imóveis

    displayed_properties = pd.DataFrame()
    properties_images = pd.DataFrame()

    main_page = get_html("https://www.silvioiwata.com.br/imoveis/venda")
    num_properties = int(re.search(r"\d+", main_page.select_one("p.cor-primaria").text).group())
    num_pages = -(-num_properties // 9)

    properties = []
    for j in range(1, num_pages + 1):

        page_url = f"https://www.silvioiwata.com.br/imoveis/venda?pagina={j}"
        main_page = get_html(page_url)

        properties += main_page.select('div.content')

    for property in properties:

        # Property URL
        if (len(property.select('div.box-img-lista')) > 0) and (len(property.select('div.box-img-lista')[0].select('a')) > 0) and ('href' in property.select('div.box-img-lista')[0].select('a')[0].attrs):
            url = property.select('div.box-img-lista')[0].select('a')[0]['href']
            property_url = f"https://www.silvioiwata.com.br{url}"
            actual_properties_url.append(property_url)
        else:
            property_url = 'URL not found'

        if (property_url == 'URL not found') or (property_url in past_properties['property_url'].values):
            continue

        # Property district, city and state
        if (len(property.select('div.lista-imoveis-detalhes')) > 0) and (len(property.select('div.lista-imoveis-detalhes')[0].select('strong')) > 1):
            if ('-' in property.select('div.lista-imoveis-detalhes')[0].select('strong')[1].text):
                bold_text = property.select('div.lista-imoveis-detalhes')[0].select('strong')[1].text.split('-')
                district = bold_text[0].strip() if len(bold_text) == 3 else None
                city = bold_text[1].strip() if len(bold_text) == 3 else bold_text[0].strip()
                state = bold_text[2].strip() if len(bold_text) == 3 else bold_text[1].strip()
            else:
                district = None
                city = None
                state = None
        else:
            district = None
            city = None
            state = None

        # Property price, category, area
        if (len(property.select('div.lista-imoveis-detalhes')) > 0):

            if (len(property.select('div.lista-imoveis-detalhes')[0].select('strong')) > 0):
                price = property.select('div.lista-imoveis-detalhes')[0].select('strong')[0].text.strip()
            else:
                price = None

            if (len(property.select('div.lista-imoveis-detalhes')[0].select('p')) > 1):
                if ('\n' in property.select('div.lista-imoveis-detalhes')[0].select('p')[1].text):
                    small_text = property.select('div.lista-imoveis-detalhes')[0].select('p')[1].text.split('\n')
                    small_text = [text.strip() for text in small_text]
                    small_text = [text for text in small_text if text != '']
                    category = small_text[0] if len(small_text) > 0 else None
                    if (len(small_text) > 1) and (':' in small_text[1]):
                        area = small_text[1].split(':')[1].strip() if len(small_text) > 1 else None
                    else:
                        area = None
                else:
                    category = None
                    area = None
            else:
                category = None
                area = None
        else:
            price = None
            category = None
            area = None

        # Property number of bedroom, bathroom and garage
        if (len(property.select('span.box-comodo')) > 0):
            bed_bath_garage = property.select('span.box-comodo')[0]

            if len(bed_bath_garage) > 1:

                gross_num_bedroom = bed_bath_garage.select('span.bath')
                gross_num_bedroom = gross_num_bedroom[0].text if gross_num_bedroom else None
                if gross_num_bedroom is not None:
                    if '+' in gross_num_bedroom:
                        num_bedroom = sum([float(num.strip()) for num in gross_num_bedroom.split('+')])
                    else:
                        num_bedroom = gross_num_bedroom.strip()
                else:
                    num_bedroom = None

                num_bathroom = bed_bath_garage.select('span.bathroom')
                num_bathroom = num_bathroom[0].text if num_bathroom else None

                num_garage = bed_bath_garage.select('span.garage')
                num_garage = num_garage[0].text.strip() if num_garage else None

            else:
                num_bedroom = None
                num_bathroom = None
                num_garage = None
        else:
                num_bedroom = None
                num_bathroom = None
                num_garage = None

        # Loads property page
        property_page = get_html(property_url)

        # Property latitude and longitude
        try:
            lat, long = map(float, property_page.select_one("#coordenadas_mapa").text.split(","))
        except:
            lat = None
            long = None

        # Property images
        if (len(property_page.select('div.slider')) > 0):
            
            images = property_page.select('div.slider')[0].select('img')
            images = [image['src'] for image in images]
            images = list(set(images))

            if (len(images) > 0):
                for image in images:
                    property_images = pd.DataFrame([{
                        'property_url': property_url,
                        'image_url': image,
                        'order': [i for i, img in enumerate(images) if img == image][0]
                    }])
                    properties_images = pd.concat([properties_images, property_images], ignore_index=True)

        # Property broker
        broker = 'Silvio Iwata'

        # Property informations
        property_info = pd.DataFrame([{
            'property_url': property_url,
            'broker': broker,
            'district': district,
            'price': price,
            'type': None,
            'city': city,
            'state': state,
            'ref': None,
            'category': category,
            'area': area,
            'lat': lat,
            'long': long,
            'num_bedroom': num_bedroom,
            'num_bathroom': num_bathroom,
            'num_garage': num_garage
        }])

        displayed_properties = pd.concat([displayed_properties, property_info], ignore_index=True)

        time.sleep(0.5)

    return displayed_properties, properties_images

# Execute scraper

inicio = time.time()
inicio_PG = time.time()

# Scrapes Pedro Granado Imóveis
try:
    displayed_properties_pedro_granado, properties_images_pedro_granado = pedro_granado_scraper()
except:
    max_tries = 2
    for i in range(max_tries):
        displayed_properties_pedro_granado, properties_images_pedro_granado = pedro_granado_scraper()
        break

fim = time.time()
print('\nPedro Granado Imóveis')
print(f'Número de imoveis: {len(displayed_properties_pedro_granado)}')
print(f"Tempo de execução: {round(fim - inicio_PG, 2)} segundos")

inicio_LE = time.time()

# Scrapes Lelo Imóveis
try:
    displayed_properties_lelo, properties_images_lelo = lelo_scraper()
except:
    max_tries = 2
    for i in range(max_tries):
        displayed_properties_lelo, properties_images_lelo = lelo_scraper()
        break

fim = time.time()
print('\nLelo Imóveis')
print(f'Número de imoveis: {len(displayed_properties_lelo)}')
print(f"Tempo de execução: {round(fim - inicio_LE, 2)} segundos")

inicio_SI = time.time()

# Scrapes Silvio Iwata Imóveis
try:
    displayed_properties_silvio_iwata, properties_images_silvio_iwata = silvio_iwata_scraper()
except:
    max_tries = 2
    for i in range(max_tries):
        displayed_properties_silvio_iwata, properties_images_silvio_iwata = silvio_iwata_scraper()
        break

fim = time.time()
print('\nSilvio Iwata Imóveis')
print(f'Número de imoveis: {len(displayed_properties_silvio_iwata)}')
print(f"Tempo de execução: {round(fim - inicio_SI, 2)} segundos")

# Properties data ###################################################################################

displayed_properties = pd.concat([displayed_properties_pedro_granado,
                                  displayed_properties_lelo,
                                  displayed_properties_silvio_iwata], ignore_index=True)
displayed_properties['added_date'] = (datetime.now()).strftime("%Y-%m-%d")
displayed_properties['sold_date'] = None

past_properties.loc[~past_properties['property_url'].isin(actual_properties_url), 'sold_date'] = datetime.now().strftime("%Y-%m-%d")

# Update list of properties
past_properties = pd.concat([past_properties, displayed_properties])
past_properties.to_csv(os.path.join(BASE_DIR, "bronze/Properties.csv"), sep=';', index=False)

# Images data ######################################################################################

properties_images = pd.concat([properties_images_pedro_granado,
                               properties_images_lelo,
                               properties_images_silvio_iwata], ignore_index=True)

# Update list of images
past_properties_images = pd.concat([past_properties_images, properties_images], ignore_index=True)
past_properties_images.to_csv(os.path.join(BASE_DIR, "bronze/Properties Images.csv"), sep=';', index=False)

fim = time.time()
print(f"Tempo de execução total: {fim - inicio:.6f} segundos")
