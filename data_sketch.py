#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
from io import StringIO
import plotly.graph_objects as go

st.header("Data Sketch")

pagina = st.radio("Pagina",('modifica ed esporta','visualizzazione'))

    
uploaded_file = st.file_uploader("Selezionare un file .csv/.txt")
if uploaded_file is not None:
    st.sidebar.header("Tool Modifica")
    # Definisci la lista di delimitatori supportati da Pandas
    delimiter_options = [',', '\t', '|', ';', ':']


    # Aggiungi l'elemento checkbox per selezionare il delimitatore
    delimitatore= st.sidebar.radio("Seleziona il delimitatore", delimiter_options)
    
    col1, col2 = st.columns([2, 2])
    col1.subheader("dataset originale")
    df = pd.read_csv(uploaded_file, delimiter = delimitatore)
    col1.write(df)
    
    col2.subheader("dataset modificato")
    newdf= df
   
    
    #verifica se è necessario inserire delle intestazioni
    tabella_senza_intestazioni = st.sidebar.checkbox("tabella senza intestazioni")
    
    if tabella_senza_intestazioni == True:
        # Rinomina le colonne con numeri in ordine crescente
        new_column_names = list(range(len(df.columns)))
        newdf.loc[-1] = newdf.columns
        newdf.columns = new_column_names
        newdf.index = newdf.index + 1
        newdf.sort_index(inplace=True)
    
    #verifica se ci sono colonne da elimianre
    elimina_colonne = st.sidebar.checkbox("elimina colonne")
    
    if elimina_colonne == True:
        # Aggiungi l'elemento multiselect per selezionare le colonne da eliminare
        colonne_da_eliminare = st.sidebar.multiselect("Seleziona le colonne da eliminare", newdf.columns.tolist())

        # Elimina le colonne selezionate
        newdf = newdf.drop(columns=colonne_da_eliminare)
        
    #verifica se ci sono colonne da rinominare
    rinomina_colonne = st.sidebar.checkbox("colonne da rinominare")
    if rinomina_colonne == True:
        # Aggiungi l'elemento multiselect per selezionare le colonne da rinominare
        colonne_da_rinominare = st.sidebar.multiselect("Seleziona le colonne da rinominare", newdf.columns.tolist())

        # Crea un dizionario per mappare i vecchi nomi delle colonne ai nuovi nomi
        mapping_nomi_colonne = {}
        for colonna in colonne_da_rinominare:
            nuovo_nome_colonna = st.sidebar.text_input(f"Inserisci il nuovo nome per la colonna '{colonna}'", colonna)
            mapping_nomi_colonne[colonna] = nuovo_nome_colonna

        # Rinomina le colonne selezionate con i nuovi nomi
        newdf =  newdf.rename(columns=mapping_nomi_colonne)
        
    
    #verifica la necessità di una colonna indice    
    indice = st.sidebar.checkbox("colonna indice")

    if indice == True:
        # Aggiungi l'elemento selectbox per selezionare la colonna da usare come indice
        colonna_indice = st.sidebar.selectbox("Seleziona la colonna da usare come indice", newdf.columns.tolist())
        # Imposta la colonna selezionata come indice del DataFrame
        newdf = newdf.set_index(colonna_indice)
        
        # imposta se indice è in formato date_time (time series) oppure no (scatter dati) 
        indice_datetime = st.sidebar.checkbox("indice date_time")
        if indice_datetime ==True:
            newdf.index = pd.to_datetime(newdf.index)#occorre per convertire in datetime la data
    
    righe_da_eliminare = st.sidebar.checkbox("righe da eliminare")

    if righe_da_eliminare ==True:
        #lista colonne presenti in df
        scegli_colonna_valori=st.sidebar.multiselect("Seleziona le colonne da rinominare", newdf.columns.tolist())
        # crea una serie da una colonna del df, da questa crea una lista di valori univoci presenti nella serie
        if scegli_colonna_valori is not None:
            serie_valori= newdf[scegli_colonna_valori]
            valori = serie_valori.unique().tolist()

            # chiede all'utente di selezionare il valore da eliminare
            valore_da_elim = st.sidebar.selectbox('Seleziona il valore da eliminare:', valori)

            # elimina le righe che contengono il valore selezionato
            newdf = df[~df[scegli_colonna_valori].isin([valore_da_elim])]

    
    col2.write(newdf)
    
    if pagina == 'modifica ed esporta':
        st.subheader("esporta dataframe in csv")
        nome_file=st.text_input("inserisci il nome con cui vuoi salvare il file scaricato", "nuovo_dataset")

        @st.cache
        def convert_df(newdf):
            # IMPORTANT: Cache the conversion to prevent computation on every rerun
            return newdf.to_csv().encode('utf-8')

        csv = convert_df(newdf)

        st.download_button(
        label="Download dataset modificato",
        data=csv,
        file_name=f"{nome_file}.csv",  # utilizzo della f-string per inserire il valore di nome_file come stringa
        mime='text/csv')
   
    else:
        st.subheader("visualizza dati")
        col3, col4 = st.columns([2, 2])
        
      
        with col3:
            #visualizzazione variabile    
            colonna_da_visualizzare = st.selectbox("Seleziona la colonna da visualizzare", newdf.columns.tolist())
            variabile = go.Figure()

            variabile.add_trace(go.Scatter(
                mode = "lines",
                y = newdf[colonna_da_visualizzare],
                x = newdf.index,
                name="variabile",
                connectgaps=False))

            variabile.update_xaxes(
                title_text = "variabile",
                title_font = {"size": 15},
                title_standoff = 10)
            st.plotly_chart(variabile,use_container_width=False )
            
        with col4:
            colonna_da_visualizzare2 = st.selectbox("Seleziona la colonna da visualizzare ", newdf.columns.tolist())
            variabile2 = go.Figure()

            variabile2.add_trace(go.Scatter(
                mode = "markers",
                y = newdf[colonna_da_visualizzare2],
                x = newdf.index,
                name="variabile2",
                connectgaps=False))

            variabile2.update_xaxes(
                title_text = "variabile",
                title_font = {"size": 15},
                title_standoff = 10)
            st.plotly_chart(variabile2,use_container_width=False )
            
            
            
        scatter_correlazione= st.sidebar.checkbox("scatter correlazione variabili")
        if scatter_correlazione == True:
            colonna_confrontoY = st.selectbox("Seleziona asse Y", newdf.columns.tolist())
            colonna_confrontoX = st.selectbox("Seleziona asse X", newdf.columns.tolist())

            scatter = go.Figure()

            scatter.add_trace(go.Scatter(
                mode = "markers",
                y = newdf[colonna_confrontoY],
                x = newdf[colonna_confrontoX],
                #trendline="ols",
                name="variabile2",
                connectgaps=False))

            scatter.update_xaxes(
                title_text = "confronto variabili",
                title_font = {"size": 15},
                title_standoff = 10)
            st.plotly_chart(scatter,use_container_width=False )

            

    
else:
    st.text("inserire file csv")

