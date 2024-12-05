#Loads the rvest, stringr, dplyr and glue libraries
suppressWarnings({
  suppressPackageStartupMessages({
    library(rvest)
    library(stringr)
    library(dplyr)
    library(glue)
  })
})

setwd("C:\\Users\\joaov\\Documents\\Imoveis Maringá")

# Pedro Granado Imoveis

displayed_properties <- data.frame(NULL)

main_page <- 
  read_html('https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&finalidade=&dormitorio=&garagem=&vmi=&vma=&ordem=1')

num_properties <- main_page %>% html_elements("option") %>% .[5] %>% html_text() %>% str_extract(., "(?<=\\()[^)]*(?=\\))") %>% as.integer(.)
num_pages = ceiling(num_properties/16)

for (j in 1:num_pages){
  
  main_page <- 
    read_html(paste0('https://www.pedrogranado.com.br/pesquisa-de-imoveis/?locacao_venda=V&id_cidade%5B%5D=35&finalidade=&dormitorio=&garagem=&vmi=&vma=&ordem=1&&pag=',j))

  urls <- main_page %>% html_nodes("div.col-lg-4") %>% html_elements('a') %>% html_attr("href") %>% unique(.)

  for (i in 1:length(urls)){
    
    district <- main_page %>% html_nodes("h4.lead") %>% html_text() %>% .[i]
    
    price <- main_page %>% html_nodes("h3") %>% html_text() %>% .[i+1]
  
    property_url <- paste0("https://www.pedrogranado.com.br/", urls[i])
    
    property_page <- 
      read_html(property_url)
    
    # Category: Apartment, terrain, house
    category <- property_page %>% html_nodes('div.col-4.mb-4') %>% html_nodes('span') %>% html_text() %>% .[1]
    
    area <- property_page %>% html_nodes('div.col-4.mb-4') %>% html_nodes('span') %>% html_text(trim=TRUE) %>% .[3] %>% gsub(' M²','',.) %>% as.numeric(.)
    
    lat <- property_page %>% html_nodes("iframe") %>% html_attr("src") %>% .[2] %>% str_extract("(?<=latIni=)-?\\d+\\.\\d+") %>% as.numeric(.)
    
    long <- property_page %>% html_nodes("iframe") %>% html_attr("src") %>% .[2] %>% str_extract("(?<=longIni=)-?\\d+\\.\\d+") %>% as.numeric(.)
    
    bedrooms <- property_page %>% html_nodes('div.comodos') %>% html_text() %>% .[1] %>% as.integer(.)
    
    bathrooms <- property_page %>% html_nodes('div.comodos') %>% html_text() %>% .[2] %>% as.integer(.)
    
    suite <- property_page %>% html_nodes('div.comodos') %>% html_text() %>% .[3] %>% as.integer(.)
    
    garage <- property_page %>% html_nodes('div.comodos') %>% html_text() %>% .[4] %>% as.integer(.)
    
    broker <- 'Pedro Granado Imóveis'
    
    property_info <- data.frame(property_url = property_url,
                                broker = broker,
                                district = district,
                                price = price,
                                category = category,
                                area = area,
                                bedrooms = bedrooms+suite,
                                bathrooms = bathrooms+suite,
                                garage = garage,
                                lat = lat,
                                long = long)
    
    displayed_properties <- bind_rows(displayed_properties, property_info)
    
  }
  
}

# Lelo Imoveis

main_page <- 
  read_html('https://www.leloimoveis.com.br/imoveis/venda-maringa')

num_properties = main_page %>% html_nodes("strong.list__highlight") %>% html_text() %>% str_extract("\\d+") %>% as.integer(.)
num_pages = ceiling(num_properties/16)

for (j in 1:num_pages){
  
  main_page <- 
    read_html(paste0('https://www.leloimoveis.com.br/imoveis/venda-maringa-pagina-',j))
  
  urls <- main_page %>% html_nodes("div.list__hover") %>% html_elements('a') %>% html_attr("href")
  
  for (i in 1:length(urls)){
    
    category <- main_page %>% html_elements("span.list__type") %>% .[i] %>% html_text() %>% strsplit(" ") %>% .[[1]] %>% .[1]
    
    price <- main_page %>% html_elements("span.list__price") %>% .[seq(1, length(.), by = 2)] %>% html_text() %>% .[i]
    
    district <- main_page %>% html_elements("span.list__address") %>% .[i] %>% html_text(trim=TRUE) %>% strsplit(" - ") %>% .[[1]] %>% .[1]
    
    property_url <- paste0("https://www.leloimoveis.com.br", urls[i])
    
    property_page <- 
      read_html(property_url)
    
    bedrooms <- property_page %>% html_nodes("div.jetgrid.jetgrid--justify-left.jetgrid--align-center") %>% html_nodes("strong") %>% html_text(trim=TRUE) %>% .[6] %>% as.integer(.)
    
    bathrooms <- property_page %>% html_nodes("div.jetgrid.jetgrid--justify-left.jetgrid--align-center") %>% html_nodes("strong") %>% html_text(trim=TRUE) %>% .[7] %>% as.integer(.)
    
    garage <- property_page %>% html_nodes("div.jetgrid.jetgrid--justify-left.jetgrid--align-center") %>% html_nodes("strong") %>% html_text(trim=TRUE) %>% .[8] %>% as.integer(.)
    
    area <- property_page %>% html_nodes("div.jetgrid.jetgrid--justify-left.jetgrid--align-center") %>% html_nodes("strong") %>% html_text(trim=TRUE) %>% .[5] %>% str_extract(".*(?=m)") %>% gsub(',','.',.) %>% as.numeric(.)
    
    lat <- property_page %>% html_nodes("div.card__map-container") %>% html_attr("data-latitude") %>% as.numeric(.)

    long <- property_page %>% html_nodes("div.card__map-container") %>% html_attr("data-longitude") %>% as.numeric(.)
    
    broker <- 'Lelo Imóveis'
    
    property_info <- data.frame(property_url = property_url,
                                broker = broker,
                                district = district,
                                price = price,
                                category = category,
                                area = area,
                                bedrooms = bedrooms,
                                bathrooms = bathrooms,
                                garage = garage,
                                lat = lat,
                                long = long)
    
    displayed_properties <- bind_rows(displayed_properties, property_info)
    
  }
    
}

# Silvio Iwata Imoveis

main_page <- 
  read_html('https://www.silvioiwata.com.br/imoveis/venda')

num_properties = main_page %>% html_nodes("p.cor-primaria") %>% html_text() %>% str_extract("\\d+") %>% as.integer(.)
num_pages = ceiling(num_properties/9)

for (j in 1:num_pages){
  
  main_page <- 
    read_html(paste0('https://www.silvioiwata.com.br/imoveis/venda?pagina=',j))
  
  urls <- main_page %>% html_nodes("div.box-img-lista") %>% html_elements('a') %>% html_attr("href") %>% gsub(' ','',.)
  
  for (i in 1:length(urls)){
    
    category <- main_page %>% html_nodes("div.lista-imoveis-detalhes") %>% html_nodes("p") %>% .[2*i] %>% html_text(trim=TRUE) %>% strsplit("\\s*\n\\s*") %>% .[[1]] %>% .[1]
    
    area <- main_page %>% html_nodes("div.lista-imoveis-detalhes") %>% html_nodes("p") %>% .[2*i] %>% html_text(trim=TRUE) %>% strsplit("\\s*\n\\s*") %>% .[[1]] %>% .[2] %>% str_extract("(?<=: )[0-9,.]+") %>% gsub(",", ".", .) %>% as.numeric(.)

    district <- main_page %>% html_nodes("div.lista-imoveis-detalhes") %>% html_nodes("p") %>% .[i] %>% html_text(trim=TRUE) %>% strsplit("\\s*\n\\s*") %>% .[[1]] %>% .[2] %>% strsplit(" - ") %>% .[[1]] %>% .[1]
    
    price <- main_page %>% html_elements("div.lista-imoveis-detalhes") %>% html_nodes("span.valor") %>% .[i] %>% html_text()
    
    property_url <- paste0("https://www.silvioiwata.com.br", urls[i])
    
    property_page <- 
      read_html(property_url)
    
    lat <- property_page %>% html_nodes("#coordenadas_mapa") %>% html_text()%>% strsplit(",") %>% .[[1]] %>% .[1] %>% as.numeric(.)
    
    long <- property_page %>% html_nodes("#coordenadas_mapa") %>% html_text()%>% strsplit(",") %>% .[[1]] %>% .[2] %>% as.numeric(.)
    
    broker <- 'Silvio Iwata'
    
    property_info <- data.frame(property_url = property_url,
                                broker = broker,
                                district = district,
                                price = price,
                                category = category,
                                area = area,
                                bedrooms = NA,
                                bathrooms = NA,
                                garage = NA,
                                lat = lat,
                                long = long)
    
    displayed_properties <- bind_rows(displayed_properties, property_info)
    
  }
  
}

# Past properties

past_properties <- read.csv2("C:\\Users\\joaov\\Documents\\Imoveis Maringá\\Past Displayed Properties.csv")
past_properties <- past_properties %>% select(-X)

write.csv2(displayed_properties, "Past Displayed Properties.csv")

# Sold properties ##############################################################

sold_properties <- merge(past_properties, displayed_properties, by = c("property_url"), all.x = TRUE)
sold_properties <- sold_properties[is.na(sold_properties$district.y), ]
sold_properties <- sold_properties[, !names(sold_properties) %in% c("broker.y", "district.y", "price.y", "category.y", "area.y", "bedrooms.y", "bathrooms.y", "garage.y", "lat.y", "long.y")]
names(sold_properties) <- sub("\\.x", "", names(sold_properties))
sold_properties$sold_date <- as.character(Sys.Date() - 1)

past_sold_properties <- read.csv2("C:\\Users\\joaov\\Documents\\Imoveis Maringá\\Past Sold Properties.csv")
past_sold_properties <- past_sold_properties %>% select(-X)

past_sold_properties <- rbind(past_sold_properties, sold_properties)

write.csv2(past_sold_properties, "Past Sold Properties.csv")

# New properties ###############################################################

new_properties <- merge(displayed_properties, past_properties, by = c("property_url"), all.x = TRUE)
new_properties <- new_properties[is.na(new_properties$district.y), ]
new_properties <- new_properties[, !names(new_properties) %in% c("broker.y", "district.y", "price.y", "category.y", "area.y", "bedrooms.y", "bathrooms.y", "garage.y", "lat.y", "long.y")]
names(new_properties) <- sub("\\.x", "", names(new_properties))
new_properties$added_date <- as.character(Sys.Date() - 1)

past_new_properties = data.frame(NULL)

past_new_properties <- read.csv2("C:\\Users\\joaov\\Documents\\Imoveis Maringá\\Past New Properties.csv")
past_new_properties <- past_new_properties %>% select(-X)

past_new_properties <- rbind(past_new_properties, new_properties)

write.csv2(past_new_properties, "Past New Properties.csv")
