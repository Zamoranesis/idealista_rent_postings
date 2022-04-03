# -*- coding: utf-8 -*-
"""
Author: Daniel
"""
######## IMPORTANTE ######################
#Cuando se produzca un error en el webdriver(out of memory, etc):
#   1)Comentamos last_province=0 y descomentamos last_province=provinces.index(province)
#   2)Ejecutamos de nuevo la segunda celda
#   3)Finalizado el scrapeo, descomentamos last_province=0 y comentamos last_province=provinces.index(province)

#==================== LIBRERÍAS ========================
import pandas as pd
import numpy as np
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException,TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import date
import time
import re

#==================== PARÁMETROS ========================
# Obtenemos el excel de la web de la Agencia Tributaria
url=r"https://www.idealista.com/alquiler-viviendas/barcelona-provincia/con-publicado_ultima-semana/"
save_folder=r"C:\Users\danie\OneDrive\Escritorio\Sabadell\1. Python Projects\Idealista\1. Inputs"
today=date.today().strftime("%Y%m%d")
save_path=os.path.join(save_folder,f'idealista_{today}.csv' )
houses_df=pd.DataFrame(columns=["Title","Rental_Price","Rooms","m2","Province"])


#==================== CREACIÓN DEL NUEVO FICHERO ========================
chromeOptions = webdriver.ChromeOptions()
prefs = {"download.default_directory" : save_folder,
         "profile.default_content_setting_values.cookies": 1}
chromeOptions.add_experimental_option("prefs",prefs)

service=Service(ChromeDriverManager().install())
#Solución para no estar pendiente de la version del webdriver
#%%
last_province=0
#Cuando aparezca TimeOutError utilizar descomentar la linea siguiente (Importante volver a comentarla)
#last_province=provinces.index(province)


driver = webdriver.Chrome(service=service,
                          options=chromeOptions)
driver.get("https://www.idealista.com/")

#Obtención de las provincias
element_present = EC.presence_of_element_located((By.XPATH, r"//*[@class='locations-list clearfix']"))
WebDriverWait(driver, 60).until(element_present)
provinces_href= [p.get_attribute("href") for p in driver.find_elements(By.XPATH, ".//*[@class='locations-list clearfix']/ul/li/a")]
provinces= [h.split("/")[-2] for h in provinces_href]
#Las provincias especiales cuya capital no se llama igual que la provincia o no siguen el patron de las restantes
special_provinces=["alava",
                    "asturias",
                    "vizcaya",
                    "balears-illes",
                    "cantabria",
                    "guipuzcoa"
                    "navarra",
                    "la-rioja",
                    "las-palmas",
                    "castellon",
                    "alicante"                
                    ]

for province in provinces[last_province: ]:
    print(f"Scraping {province}")
    if province in special_provinces:
        url=f"https://www.idealista.com/alquiler-viviendas/{province}/con-publicado_ultima-semana/"
    else:
        url=f"https://www.idealista.com/alquiler-viviendas/{province}/con-publicado_ultima-semana/"
        
    driver.get(url)
    try:
        element_present = EC.presence_of_element_located((By.XPATH, r"//*[@class='item-info-container']"))
        WebDriverWait(driver, 60).until(element_present)
        #Obtenemos el número de páginas necesarias(Se publican 30 por página)
        n_pages=driver.find_element(By.XPATH, ".//*[@class='listing-title h1-simulated']").text
        n_pages=round(int(re.findall(r"^\d*\.*\d*", n_pages)[0].replace(".",""))/30)
        for p in range(n_pages):
            try:
                element_present = EC.presence_of_element_located((By.XPATH, r"//*[@class='item-info-container']"))
                WebDriverWait(driver, 20).until(element_present)
                houses=driver.find_elements(By.XPATH, r".//*[@class='item-info-container']")
                for h in houses:
                    time.sleep(np.random.uniform(0,0.3,1)[0])
                    title= h.find_element(By.XPATH, ".//*[@class='item-link']").text
                    rental_price=h.find_element(By.XPATH, ".//*[@class='item-price h2-simulated']").text
                    rooms=h.find_elements(By.XPATH, ".//*[@class='item-detail']")[0].text
                    m2=h.find_elements(By.XPATH, ".//*[@class='item-detail']")[1].text
                    
                    houses_df=houses_df.append({"Title":title,
                                                "Rental_Price":rental_price ,
                                                "Rooms":rooms,
                                                "m2": m2,
                                                "Province":province
                                                    },
                                               ignore_index=True)
                
                
                driver.find_element(By.XPATH, r".//*[@class='icon-arrow-right-after']").click()
                time.sleep(np.random.randint(1,5,1)[0])
            except NoSuchElementException:
                continue
            except TimeoutException:
                print(f"TimoutException catched in:\nProvince: {province}\nPage:{p+1}")
                continue
    except TimeoutException:
        continue
    
driver.quit()

#Preprocesado
houses_df.drop_duplicates(inplace=True)
houses_df["Municipality"]=houses_df["Title"].apply(lambda x: x.split(",")[-1].strip())
houses_df["Date"]=pd.to_datetime(date.today())
#Conversión a csv
houses_df.to_csv(save_path,index=False)
    

    
    
    
    
    