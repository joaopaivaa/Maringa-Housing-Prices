# Maringá Housing Prices

Author: João Paiva.

Contact: joaopaiva.datascience@gmail.com.

Github: https://github.com/joaopaivaa.

## ETL

### E - Extraction

Composed by the web scraping of 3 real estate agencies from the city of Maringá (Brazil).

### T - Transformation

Silver layer transformation:
* Standardization of variables writing and values;
* Definition of each variable type;
* Creation of new variables (days on market, is sold, price per m2);
* Selection of only properties located in the city of Maringá;
* Selection of properties added on sale after 01-08-2025;
* Exclusion of NaN values based on "district" and "price" columns.

Gold layer transformation:
* Join between properties database and districts geometry dimension base on properties coordinates.

### L - Load

Gold layer database is saved as a csv file.

## Dashboard

### Methodology

Available properties: Properties currently available at the real estate agencies' website.
Added date = Date in which the property first appeared on the real state agency's website.
Sold properties: Properties that were available at the real state agencies' website but aren't anymore, so property removed = property sold.
Sold date = Date in which the property was removed from the real state agency's website.
Time on market (days) = Sold date - Added date

### Visualization

#### Home page

<img width="1334" height="744" alt="image" src="https://github.com/user-attachments/assets/bf641160-b456-43ea-9725-6153d46d6731" />

#### Available properties page

<img width="1295" height="721" alt="image" src="https://github.com/user-attachments/assets/b3a0f58b-888e-4855-a728-5c9fdd4e5cb7" />

#### Sold properties page

<img width="1296" height="719" alt="image" src="https://github.com/user-attachments/assets/14f8ceb7-dc2b-4588-931a-ce9c18aee9f5" />
