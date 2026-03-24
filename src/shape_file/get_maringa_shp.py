import geopandas as gpd
import pandas as pd

parana_shp = gpd.read_file("C:\\Users\\joaov\\Downloads\\PR_subdistritos_CD2022\\PR_subdistritos_CD2022.shp")

maringa_shp = parana_shp[(parana_shp['NM_DIST'] == 'Maringá') & (~pd.isnull(parana_shp['NM_SUBDIST']))].reset_index(drop=True)

maringa_shp.to_file("maringa.shp", driver="ESRI Shapefile")