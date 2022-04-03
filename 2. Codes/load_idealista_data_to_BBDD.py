# -*- coding: utf-8 -*-
"""Idealista EDA.ipynb

Author: Daniel
"""

#================================= Load libraries =================================
import os
import pandas as pd
import numpy as np
import json
import glob
import sqlite3


#================================= Load Data ====================================
ls_files = glob.glob('./1. Inputs/*.csv') # * means all if need specific format then *.csv
latest_file = max(ls_files, key=os.path.getctime)

#Carga de datos
df=pd.read_csv("./"+ latest_file)

#Carga del diccionario para parsear provincias
with open("./1. Inputs/provinces_dict.json", "r") as j:
  prov_dict=json.load(j)


#================================= Preprocessing ====================================
#Eliminamos los anuncios duplicados 
df.drop_duplicates(subset=["Title","Rental_Price","Rooms"], inplace=True)

#En algunos filas de la columna Rooms figuran los m2
df["m2"]=np.where(df.Rooms.str.contains(r"^(?=.*m².*)", regex=True),
                  df.Rooms,
                  df.m2
                  )
#Imputamos NAs para aquellos registros donde el número de habitaciones no sea correcto
df["Rooms"]=np.where(df.Rooms.str.contains(r"^(?=.*m².*)", regex=True),
                      np.nan,
                      df.Rooms
                      )
df.dropna(inplace=True)
df["Municipality"]=df.Municipality.apply(lambda x: x.split("en")[-1])
df["Rental_Price"]=df["Rental_Price"].apply(lambda x: x.split("€")[0].replace(".","")).astype(int)
df["Rooms"]=df["Rooms"].apply(lambda x: x.split(" ")[0]).astype(int)
df["m2"]=df["m2"].apply(lambda x: x.split(" ")[0].replace(".","")).astype(int)
df["Province"]=df.Province.str.replace("-"," ").str.replace("provincia","")
df["Date"]=pd.to_datetime(df.Date)
#Creación de nuevas variables
df["Price_m2"]=df.Rental_Price/df.m2
df["Price_room"]=df.Rental_Price/df.Rooms

#================================= Grouping ====================================
#Apply multiple functions to multiple groupby columns
df_agg=df.groupby('Province').agg({'Price_m2':'median', 
                                   'Price_room':'median',
                                   'Province':'count'})
df_agg.rename(columns={"Province":"N_listings"}, inplace=True) 
df_agg.sort_values("Price_m2", ascending=False, inplace=True)     
df_agg.reset_index(inplace=True)

df_agg["Province"]=df_agg.Province.apply(lambda x: prov_dict[x.strip()])
df_agg["Scraped_date"]=df["Date"][0]

#================================= Uploading to DDBB ====================================
con = sqlite3.connect('./3. Database/idealista.db')

df.to_sql('IDEALISTA_RAW', con, if_exists='append', index=False)
df_agg.to_sql('IDEALISTA_RENTING', con, if_exists='append', index=False)
#Eliminamos posibles duplicados
cur = con.cursor()
cur.execute("""
            DELETE FROM IDEALISTA_RENTING
            WHERE rowid NOT IN 
                (
                SELECT MIN(rowid) 
                FROM IDEALISTA_RENTING 
                GROUP BY PROVINCE,SCRAPED_DATE
                )
            """)
cur.execute("""
            DELETE FROM IDEALISTA_RAW
            WHERE rowid NOT IN 
                (
                SELECT MIN(rowid) 
                FROM IDEALISTA_RAW 
                GROUP BY Title,Rental_price,rooms,date
                )
            """)
#Since by default Connector/Python does not autocommit,
#it is important to call this method after every transaction that modifies data for tables 
#that use transactional storage engines.
con.commit()
con.close()



