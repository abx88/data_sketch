#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
import numpy as np
#from io import StringIO
import plotly.graph_objects as go
import plotly.express as px
import scipy.stats as stats
import datetime as dt
from datetime import date



st.set_page_config(
    page_title="DataSketch",
    layout="wide")


np.random.seed(123)
dfprova = pd.DataFrame(np.random.randn(50, 5), columns=('col %d' % i for i in range(5)))
newdf_mod= dfprova

st.header("Data Sketch")


st.sidebar.header("Tool Modifica")
# Definisci la lista di delimitatori supportati da Pandas
delimiter_options = [',', '\t', '|', ';', ':']
# Aggiungi l'elemento checkbox per selezionare il delimitatore
delimitatore= st.sidebar.radio("Seleziona il delimitatore", delimiter_options)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file, delimiter = delimitatore)
    
else:
    df = dfprova
    

#verifica se è necessario inserire delle intestazioni
def tabella_senza_intestazioni(df):
    # Rinomina le colonne con numeri in ordine crescente
    new_column_names = list(range(len(df.columns)))
    df.loc[-1] = df.columns
    df.columns = new_column_names
    df.index = df.index + 1
    df.sort_index(inplace=True)
    return(df)
if st.sidebar.button("tabella senza intestazioni", key="tabella_senza_intestazioni", use_container_width=False):
    newdf = tabella_senza_intestazioni(df)
  
    

#verifica la necessità di una colonna indice    
expander_indice = st.sidebar.expander("scegli colonna indice")
# Aggiungi l'elemento selectbox per selezionare la colonna da usare come indice
colonna_indice = expander_indice.selectbox("Seleziona la colonna da usare come indice", newdf.columns.tolist())

def indice(df):
    # Imposta la colonna selezionata come indice del DataFrame
    df = df.set_index(colonna_indice)
    return(df)
if st.sidebar.button("indice", on_click=None, use_container_width=False):
    newdf = indice(newdf)
    

def indice_datetime(df):
    # imposta se indice è in formato date_time (time series) oppure no (scatter dati) 
    df.index = pd.to_datetime(df.index)#occorre per convertire in datetime la data
    df['giorno'] = df.index.day
    df['giorno_W'] = df.index.dayofweek
    df['mese'] = df.index.month
    df['anno'] = df.index.year
    return(df)
if st.sidebar.button("indice date-time", on_click=None, use_container_width=False):
    newdf = indice_datetime(newdf)
    

