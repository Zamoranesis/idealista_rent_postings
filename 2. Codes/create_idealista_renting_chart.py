# -*- coding: utf-8 -*-
"""
Created on Mon Feb 21 20:27:12 2022

@author: danie
"""

#================================= Load libraries =================================
import pandas as pd
import geopandas as gpd
import sqlite3
import matplotlib.pyplot as plt
from datetime import date

#================================= Load Data ====================================
today=date.today().strftime("%Y%m%d")
geo_df=gpd.read_file("./1. Inputs/spain-provinces.geojson")
con = sqlite3.connect('./3. Database/idealista.db')
df = pd.read_sql_query("SELECT * FROM IDEALISTA_RENTING", con)
df=df[~df["Province"].isin(["Ceuta","Melilla"])]
con.close()

df_pivot_m2=pd.pivot_table(df, index="Province", columns="Scraped_date",values="Price_m2")
df_pivot_room=pd.pivot_table(df, index="Province", columns="Scraped_date",values="Price_room")
df_pivot_listings=pd.pivot_table(df, index="Province", columns="Scraped_date",values="N_listings")
#Most recent dates
most_recent=df.Scraped_date.max()
second_recent=df[df.Scraped_date!=df.Scraped_date.max()].Scraped_date.max()
df_pivot_m2["WoW_m2"]=(df_pivot_m2[most_recent] / df_pivot_m2[second_recent] - 1)*100
df_pivot_room["WoW_room"]=(df_pivot_room[most_recent] / df_pivot_room[second_recent] - 1)*100
df_pivot_listings["WoW_listings"]=(df_pivot_listings[most_recent] / df_pivot_listings[second_recent] - 1)*100

#Merge with geojson dataset
df_pivot_all=geo_df.merge(df_pivot_m2, left_on=["Province"], right_on=["Province"]) \
                   .merge(df_pivot_room, left_on=["Province"], right_on=["Province"]) \
                   .merge(df_pivot_listings, left_on=["Province"], right_on=["Province"]) 
                   


for c in ["m2","room","listings"]:
    #Labels for plotting
    df_pivot_all["Labels_"+c]=df_pivot_all["Province"] +":\n"+ round(df_pivot_all["WoW_"+c],1).astype(str)
    
    #================================= Plots ====================================    
    fig, ax = plt.subplots(1, figsize=(20,12))
    df_pivot_all.plot(column='WoW_'+c,
                     cmap='RdBu',
                     linewidth=0.4,
                     ax=ax,
                     missing_kwds={'color': 'lightgrey'},
                     edgecolor='0.1',
                     legend = True)
    df_pivot_all.apply(lambda x: ax.annotate(text=x['Labels_'+c],
                                            xy=x.geometry.centroid.coords[0],
                                            ha='right',
                                            fontsize=10,
                                            bbox={"facecolor":'white',
                                                  "edgecolor":'black',
                                                  "alpha":0.8}
                                            ),
                      axis=1);
    if c=="listings":
        ax.set_title(r"Variación Semanal del número de anuncios")
    else:
        ax.set_title(f"Variación Semanal del Precio del alquiler (€/{c})")
    ax.axis('off')
    plt.savefig(f"./4. Outputs/{c}/idealista_renting_prices_{c}_wow_{today}.png", dpi=1200)
