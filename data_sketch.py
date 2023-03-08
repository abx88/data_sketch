#!/usr/bin/env python
# coding: utf-8

# In[1]:

import streamlit as st
import pandas as pd
import numpy as np
from io import StringIO
import plotly.graph_objects as go
import scipy.stats as stats


st.set_page_config(
    page_title="DataSketch",
    layout="wide")


st.header("Data Sketch")

pagina = st.radio("selezionare operazione",('modifica ed esporta','visualizzazione'))

    
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
    dfedit = col1.experimental_data_editor(df, num_rows="dynamic")
    #col1.write(df)
    
    col2.subheader("dataset modificato")
    newdf= dfedit
   
    
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
            scomponi_data = st.sidebar.checkbox("estrai giorno, mese, anno") 
            if scomponi_data ==True:
                newdf['giorno_W'] = newdf.index.dayofweek
                newdf['mese'] = newdf.index.month
                newdf['anno'] = newdf.index.year
                
    righe_da_eliminare = st.sidebar.checkbox("righe da eliminare")

    if righe_da_eliminare:
        #lista colonne presenti in df
        scegli_colonna_valori = st.sidebar.selectbox("Seleziona la colonna", newdf.columns.tolist())
        # crea una serie da una colonna del df, da questa crea una lista di valori univoci presenti nella serie
        if scegli_colonna_valori is not None:
            valori = newdf[scegli_colonna_valori].unique().tolist()

            # chiede all'utente di selezionare i valori da eliminare
            valori_da_elim = st.sidebar.multiselect('Seleziona i valori da eliminare:', valori)

            # elimina le righe che contengono i valori selezionati
            newdf = newdf.loc[~newdf[scegli_colonna_valori].isin(valori_da_elim)]
    
    col2.write(newdf)       
    newdfvisual=newdf

    
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
        tipologia_dati = st.radio("tipologia dati in esame",('Time Series','Cross Section (analisi correlazione)'))
        col3, col4 = st.columns([2, 2])
        
        if tipologia_dati == 'Time Series':
            with col3:
                #visualizzazione variabile    
                colonna_da_visualizzare = st.selectbox("Seleziona la colonna da visualizzare", newdfvisual.columns.tolist())
                variabile = go.Figure()

                variabile.add_trace(go.Scatter(
                    mode = "lines",
                    y = newdfvisual[colonna_da_visualizzare],
                    x = newdfvisual.index,
                    name="variabile",
                    connectgaps=False))

                variabile.update_layout(
                    xaxis_title_text="data",
                    title={
                        'text': colonna_da_visualizzare,
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'})
                st.plotly_chart(variabile,use_container_width=False )

            with col4:
                colonna_da_visualizzare2 = st.selectbox("Seleziona la colonna da visualizzare ", newdfvisual.columns.tolist())
                variabile2 = go.Figure()

                variabile2.add_trace(go.Scatter(
                    mode = "markers",
                    y = newdfvisual[colonna_da_visualizzare2],
                    x = newdfvisual.index,
                    name="variabile2",
                    connectgaps=False))

                variabile2.update_layout(
                    xaxis_title_text="data",
                    title={
                        'text': colonna_da_visualizzare2,
                        'y':0.9,
                        'x':0.5,
                        'xanchor': 'center',
                        'yanchor': 'top'})
                st.plotly_chart(variabile2,use_container_width=False )
            
        else:
            with col3:
                col5,col6,col9= st.columns([2,2,1])
                colonna_confrontoY = col5.selectbox("Seleziona asse Y (variabile dipendente)", newdfvisual.columns.tolist())
                colonna_confrontoX = col6.selectbox("Seleziona asse X", newdfvisual.columns.tolist())
                somma_valori = col9.checkbox("raggruppa valori Y per x")
                #newdfvisual[colonna_confrontoY] = pd.to_numeric(newdfvisual[colonna_confrontoY], errors='coerce')
                #newdfvisual[colonna_confrontoX] = pd.to_numeric(newdfvisual[colonna_confrontoX], errors='coerce')
                #st.write(newdfvisual)
               
                if somma_valori == False:
                    scatter = go.Figure()
                    
                    scatter.add_trace(go.Scatter(
                        mode = "markers",
                        y = newdfvisual[colonna_confrontoY],
                        x = newdfvisual[colonna_confrontoX],
                        name="scatter",
                        connectgaps=False))

                   
                    scatter.update_layout(
                        xaxis_title_text=colonna_confrontoX,
                        yaxis_title_text=colonna_confrontoY,
                        title={
                            'text': "confronto variabili",
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'})


                    st.plotly_chart(scatter,use_container_width=False )
                    
                else:
                    #creo tabella pivot + grafico che raggruppa valori di y per valori x (solo se x è categorica)
                    pivotVariabile = pd.pivot_table(newdfvisual, values=colonna_confrontoY, index=colonna_confrontoX, aggfunc=np.sum)
                   
                    graficoBarre = go.Figure()

                    graficoBarre.add_trace(go.Bar(
                        y = pivotVariabile[colonna_confrontoY],
                        x = pivotVariabile.index,
                        name="grafico a barre"))

                    graficoBarre.update_layout(
                        xaxis_title_text=colonna_confrontoX,
                        yaxis_title_text=colonna_confrontoY,
                        title={
                            'text': "raggruppamento Y per X",
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'})
                    st.plotly_chart(graficoBarre,use_container_width=False )
                    filtroAggiuntivo = st.checkbox("aggiungi filtro dati")
                    if filtroAggiuntivo ==True:
                        colonna_filtro = col5.selectbox("Seleziona colonna filtro", newdfvisual.columns.tolist())
                        valori = newdfvisual[colonna_filtro].unique().tolist()
                        valori_filt = col6.multiselect('Seleziona i valori da filtrare:', valori)
                        newdfvisual = newdf.loc[newdfvisual[colonna_filtro].(valori_filt)]

    
                    st.write(pivotVariabile)
            
            with col4:
                col7,col8 = st.columns([2, 2])
                #dal df scelgo una variabile per confrontare la sua distribuzione 
                colonna_distribuzione = col7.selectbox("Seleziona colonna per vedere la sua distribuzione", newdfvisual.columns.tolist())
                # calcola la media e la deviazione standard della variabile di interesse
                colonna_distribuzione_perc = col8.checkbox("distribuzione della variazione percentuale")
                if colonna_distribuzione_perc == False:
                    newdfvisual[colonna_distribuzione] = pd.to_numeric(newdfvisual[colonna_distribuzione], errors='coerce')
                    media = newdfvisual[colonna_distribuzione].mean()
                    dev_std = newdfvisual[colonna_distribuzione].std()    
                    # crea una figura con due tracce: la distribuzione dei dati e la distribuzione normale
                    distribuzione = go.Figure()

                    # traccia 1: distribuzione dei dati
                    distribuzione.add_trace(go.Histogram(
                        x=newdfvisual[colonna_distribuzione],
                        histnorm='probability',
                        name="distribuzione variabile"))

                    # traccia 2: distribuzione normale
                    x = np.linspace(newdfvisual[colonna_distribuzione].min(), newdfvisual[colonna_distribuzione].max(), 100)
                    pdf = stats.norm.pdf(x, media, dev_std)
                    distribuzione.add_trace(go.Scatter(
                        x=x, 
                        y=pdf, 
                        mode='lines', 
                        name='distribuzione normale',
                        yaxis='y2'))

                    # aggiungi i titoli degli assi e il titolo della figura
                    distribuzione.update_layout(
                        xaxis_title_text=colonna_distribuzione,
                        yaxis_title_text='densità di probabilità',
                        yaxis2=dict(overlaying='y',side='right'),
                        title={
                            'text': "Distribuzione dei dati e distribuzione normale",
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'})

                    # visualizza la figura
                    st.plotly_chart(distribuzione, use_container_width=False)
                    
                   
                else:
                    #creazione del df delle variazioni percentuali
                    newdfvisual[colonna_distribuzione] = pd.to_numeric(newdfvisual[colonna_distribuzione], errors='coerce')
                    serie_perc = newdfvisual[colonna_distribuzione].pct_change()
                    media_perc = serie_perc.mean()
                    dev_std_perc = serie_perc.std()    
                     
                    # crea una figura con due tracce: la distribuzione dei dati e la distribuzione normale
                    distribuzione_perc = go.Figure()

                    # traccia 1: distribuzione dei dati
                    distribuzione_perc.add_trace(go.Histogram(
                        x=serie_perc,
                        histnorm='probability',
                        name="distribuzione variabile"))

                    # traccia 2: distribuzione normale
                    x = np.linspace(serie_perc.min(), serie_perc.max(), 100)
                    pdf = stats.norm.pdf(x, media_perc, dev_std_perc)
                    distribuzione_perc.add_trace(go.Scatter(
                        x=x, 
                        y=pdf, 
                        mode='lines', 
                        name='distribuzione normale',
                        yaxis='y2'))

                    # aggiungi i titoli degli assi e il titolo della figura
                    distribuzione_perc.update_layout(
                        xaxis_title_text=colonna_distribuzione,
                        yaxis_title_text='densità di probabilità',
                        yaxis2=dict(overlaying='y',side='right'),
                        title={
                            'text': "Distribuzione dei dati e distribuzione normale",
                            'y':0.9,
                            'x':0.5,
                            'xanchor': 'center',
                            'yanchor': 'top'})
                    st.plotly_chart(distribuzione_perc, use_container_width=False)
                   
                    
          
    
else:
    st.text("inserire file csv")

