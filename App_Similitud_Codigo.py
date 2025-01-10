############################################################################################
############################################################################################
# App de Comparador de codigos de respuesta de prueba segun similitud
############################################################################################
############################################################################################



#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# [A] Importacion de librerias
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&

# Obtener versiones de paquetes instalados
# !pip list > requirements.txt

import streamlit as st

# librerias para data
import pandas as pd
import numpy as np

import zipfile
import itertools
import io

# librerias para similitud de texto
import difflib




#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# [B] Creacion de funciones internas utiles
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&


#=======================================================================
# [B.1] Funcion de procesar archivo zip
#=======================================================================

@st.cache_resource() # https://docs.streamlit.io/library/advanced-features/caching
def zip2dic(
  ruta_zip
  ):
  
  contenido_zip = {}
  with zipfile.ZipFile(io.BytesIO(ruta_zip.read()), 'r') as zip_ref:
    
    # Obtener la lista de nombres de archivos en el ZIP
    nombres_archivos = zip_ref.namelist()
    
    # Filtrar y leer los archivos con las extensiones especificadas
    for nombre in nombres_archivos:
      # Verificar la extensión del archivo
      if nombre.endswith(('.txt', '.py', '.R')):
        # Leer el contenido del archivo
        with zip_ref.open(nombre) as archivo:
          contenido = archivo.read().decode('utf-8')
          contenido_zip[
            nombre.replace('.R','').replace('.py','').replace('.txt','')
            ] = contenido  # Guardar en el diccionario

  return contenido_zip


#=======================================================================
# [B.2] Funcion de procesar texto a lista de respuestas 
#=======================================================================


@st.cache_resource() # https://docs.streamlit.io/library/advanced-features/caching
def texto2lista(
  texto,
  patron
  ):
  
  # pasar a lista con espaciado
  texto2 = texto.split('\n')

  # crear lista donde se iran almacenando las respuestas
  entregable = []
  ind = 0
  for i in range(len(texto2)):

    t = texto2[ind]
    
    if t.find(patron)>0:
      print(ind)
      r = ''
      for j in range(ind+1,len(texto2)):
        t2 = texto2[j]
        if t2.find(patron)>0:
          break
        if t2.strip()=='' or t2[0]=='#':
          continue
        
        if t2.find('#')>0:
          r+= t2[0:t2.find('#')]+' \n '
        else:
          r+= t2+' \n '
      
      
      if len(r)>3:
        entregable.append(r[0:(len(r)-3)])
      else:
        entregable.append(r)
        
      ind = j
      
      
    else:
      ind+=1
      
    if ind>=len(texto2):
      break

  return entregable



#=======================================================================
# [B.3] Funcion de procesar zip a df
#=======================================================================


@st.cache_resource() # https://docs.streamlit.io/library/advanced-features/caching
def zip2df(
  ruta_zip,
  patron
  ):
  
  
  dic_respuestas = zip2dic(
    ruta_zip=ruta_zip
    )
  
  df = pd.DataFrame([])
  for k in list(dic_respuestas.keys()):
    
    l_respuestas = texto2lista(
      texto = dic_respuestas[k],
      patron = patron
      )
    
    df_aux = pd.DataFrame({
      'Archivo': k,
      'Pregunta': range(1,1+len(l_respuestas)),
      'Respuesta': l_respuestas
      })

    df = pd.concat([df,df_aux])
    
  return df





#=======================================================================
# [B.4] Funcion de calcular similitud entre 2 textos
#=======================================================================


@st.cache_resource() # https://docs.streamlit.io/library/advanced-features/caching
def similitud_txt(
  t1,
  t2,
  min_palabras = 3
  ):
  
  # agregar separadores "forzados" para que no quede un codigo de "una palabra"
  t1v = t1.replace(',',' , ').\
            replace('=',' = ').\
            replace(')',' ) ').\
            replace('(',' ( ').\
            replace('+',' + ').\
            replace('-',' - ').\
            replace('*',' * ').\
            replace('/',' / ').\
            replace('<',' < ').\
            replace('>',' > ')
            
  t2v = t2.replace(',',' , ').\
            replace('=',' = ').\
            replace(')',' ) ').\
            replace('(',' ( ').\
            replace('+',' + ').\
            replace('-',' - ').\
            replace('*',' * ').\
            replace('/',' / ').\
            replace('<',' < ').\
            replace('>',' > ')
                
  
  if len(t1v.split())<=min_palabras or len(t2v.split())<=min_palabras:
    entregable = 0
  else:
    entregable = difflib.SequenceMatcher(None, t1v, t2v).ratio()
    
  return round(100*entregable,2)




#=======================================================================
# [B.5] Funcion de procesar df a combinatorias
#=======================================================================


@st.cache_resource() # https://docs.streamlit.io/library/advanced-features/caching
def df2comb(
  df
  ):
  
  
  nro_pregs = list(set(df['Pregunta']))

  df_combinaciones = pd.DataFrame([])
  for p in nro_pregs:
    
    df_aux = df[df['Pregunta']==p]
    df_aux = df_aux.drop(columns='Pregunta')    

    # Generar todas las combinaciones sin repetición (pares de filas)
    # df_comb = list(itertools.combinations(df_aux.iterrows(), 2))
    df_comb = list(itertools.permutations(df_aux.iterrows(), 2))

    # Crear un nuevo DataFrame con las combinaciones
    data_comb = []
    for (idx1, row1), (idx2, row2) in df_comb:
      data_comb.append(
        list(row1) + list(row2)  # Concatenar valores de las filas combinadas
      )

    # Crear un DataFrame a partir de las combinaciones
    df_aux2 = pd.DataFrame(
      data_comb,
      columns=[
        f'{c}1' for c in df_aux.columns
        ] + [
        f'{c}2' for c in df_aux.columns
        ]
      )
    
    df_aux2['Pregunta']=p

    df_combinaciones = pd.concat([
      df_combinaciones,
      df_aux2
    ])

  df_combinaciones = df_combinaciones[
    ['Pregunta','Archivo1','Archivo2','Respuesta1','Respuesta2']
    ]
  
  df_combinaciones['Similitud']=df_combinaciones.apply(
    lambda x: similitud_txt(
      x['Respuesta1'], 
      x['Respuesta2']
      ),
    axis = 1
    )
  
  return df_combinaciones





#=======================================================================
# [B.6] Funcion de generar vista1: matriz comparativa
#=======================================================================


@st.cache_resource() # https://docs.streamlit.io/library/advanced-features/caching
def df2vis1_matriz(
  df_combs
  ):

  # crear valores promedio
  df_combinatorias_v1 = df_combs.groupby(['Archivo1','Archivo2']).agg(
    Conteo = pd.NamedAgg(column='Similitud',aggfunc=len),
    Similitud = pd.NamedAgg(column='Similitud',aggfunc= lambda x: round(np.mean(x),2))
  ).reset_index()
  df_combinatorias_v1['Pregunta']='Promedio'

  # unificar con df global
  df_combinatorias_v1 = pd.concat([
    df_combinatorias_v1[['Pregunta','Archivo1','Archivo2','Similitud']],
    df_combs[['Pregunta','Archivo1','Archivo2','Similitud']]
  ])

  # crear vista pivoteada
  df_combinatorias_v1 = df_combinatorias_v1.pivot(
    index = ['Pregunta','Archivo1'],
    columns = 'Archivo2',
    values = 'Similitud'
    ).reset_index()
  
  return df_combinatorias_v1





#=======================================================================
# [B.7] Funcion de generar vista2: cuadro comparativo
#=======================================================================


@st.cache_resource() # https://docs.streamlit.io/library/advanced-features/caching
def df2vis2_cuadro(
  df_combs
  ):

  df_combinatorias_v2 = df_combs.pivot(
    index = ['Archivo2','Archivo1'],
    columns = 'Pregunta',
    values = 'Similitud'
    ).reset_index()
  
  return df_combinatorias_v2



#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&
# [C] Generacion de la App
#&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&


# https://streamlit-emoji-shortcodes-streamlit-app-gwckff.streamlit.app/

st.set_page_config(layout='wide')

# titulo inicial 
st.markdown('## :clipboard: Comparador de respuestas codigos 	:clipboard:')

# autoria 
st.sidebar.markdown('**Autor :point_right: [Sebastian Barrera](https://www.linkedin.com/in/sebasti%C3%A1n-nicolas-barrera-varas-70699a28)**')

# subir archivo zip 
archivo_zip = st.sidebar.file_uploader(
  'Subir archivo ".zip" con archivos ".R", ".py" o ".txt"', 
  type='zip'
  )

# texto de patron separador
patron = st.sidebar.text_input(
  'Ingresa patron separador de cada pregunta'
  )

# colocar separador
st.sidebar.divider()

# colocar boton de procesar 
boton_procesar = st.sidebar.button('Procesar archivos',)

#_____________________________________________________________________________
# comenzar a desplegar app una vez ingresado el archivo

# cargar archivo y procesar
if archivo_zip is not None and boton_procesar:
  
  # Crear df de respuestas y almacenarlo en session_state
  if 'df_respuestas' not in st.session_state:    
    st.session_state.df_respuestas = zip2df(
      ruta_zip=archivo_zip,
      patron=patron
      )
    
  if 'df_combinatorias' not in st.session_state:        
    st.session_state.df_combinatorias = df2comb(
      df = st.session_state.df_respuestas
      )
    
  if 'df_vis1' not in st.session_state:    
    st.session_state.df_vis1 = df2vis1_matriz(
      df_combs = st.session_state.df_combinatorias
      )
    
  if 'df_vis2' not in st.session_state:    
    st.session_state.df_vis2 = df2vis2_cuadro(
      df_combs = st.session_state.df_combinatorias
      )


# Si el DataFrame ya está en session_state, continúa
if 'df_respuestas' in st.session_state:  
  df_respuestas = st.session_state.df_respuestas

if 'df_combinatorias' in st.session_state:    
  df_combinatorias = st.session_state.df_combinatorias
  
if 'df_vis1' in st.session_state:    
  df_vis1 = st.session_state.df_vis1

if 'df_vis2' in st.session_state:    
  df_vis2 = st.session_state.df_vis2
  
  

  # Crear 4 tabs
  tab1, tab2, tab3, tab4 = st.tabs([
    ':date: Cuadro de respuestas', 
    ':date: Cuadro de comparaciones', 
    ':chart_with_upwards_trend: Matriz Comparativa',
    ':chart_with_downwards_trend: Cuadro Comparativo'
    ])


  #...........................................................................
  # 1. Cuadro de respuestas

  with tab1:  
        
    # Crear un cuadro de texto para capturar la búsqueda
    filtro1 = st.text_input('Ingresa un término para filtrar:')

    # Filtrar el DataFrame por cualquier columna que contenga el texto ingresado
    if filtro1:
      
      # Filtrar el DataFrame para que coincida con cualquier columna que contenga el texto
      df_respuestas2 = df_respuestas[
        df_respuestas.apply(
          lambda r: r.astype(str).str.contains(filtro1, case=False).any(), 
          axis=1
          )
        ]
      
    else:
      df_respuestas2 = df_respuestas.copy()

    st.data_editor(
      df_respuestas2, 
      use_container_width=True, 
      disabled=True,
      hide_index=True
      )

#...........................................................................
  # 2. Cuadro de comparaciones
  
  with tab2:  
                
    # Crear un cuadro de texto para capturar la búsqueda
    col2a, col2b = st.columns([1,1])
    filtro2a = col2a.text_input('Ingresa un término para filtrar:',key='k_filtro2a')
    filtro2b = col2b.text_input('Ingresa otro término para filtrar:',key='k_filtro2b')

    # Filtrar el DataFrame por cualquier columna que contenga el texto ingresado
    if filtro2a or filtro2b:
      
      # Filtrar el DataFrame para que coincida con cualquier columna que contenga el texto
      df_combinatorias2 = df_combinatorias[
        df_combinatorias.apply(
          lambda r: r.astype(str).str.contains(filtro2a, case=False).any() and 
                    r.astype(str).str.contains(filtro2b, case=False).any(),
          axis=1
          )
        ]
      
    else:
      df_combinatorias2 = df_combinatorias.copy()

    st.data_editor(
      df_combinatorias2, 
      use_container_width=True, 
      disabled=True,
      hide_index=True
      )
  

  #...........................................................................
  # 3.  Matriz Comparativa
  
  with tab3:  
        
    nro_pregunta = st.radio(
      'Seleccione una pregunta a comparar',
      list(set(df_vis1['Pregunta'])),
      horizontal=True
      )   
        
    df_vis1_style = df_vis1[
      df_vis1['Pregunta']==nro_pregunta # aqui cambiar valor
      ].drop(
        columns = ['Pregunta']
        ).style.background_gradient(
          cmap='RdYlGn'
          ).format(
            '{:.2f}', 
            subset=df_vis1.select_dtypes(include=[np.number]).columns
            ).hide(axis='index')  

    st.markdown(
      df_vis1_style.to_html(), 
      unsafe_allow_html=True
      )
      
  
  #...........................................................................
  # 4.  Cuadro Comparativo
  
  
  with tab4:  
        
    comparar_con = st.selectbox(
      'Seleccione otro caso para comparar',
      list(set(df_vis2['Archivo2']))
      )   
        
    df_vis2_style = df_vis2[
      df_vis2['Archivo2']==comparar_con
      ].drop(columns = ['Archivo2']).style.bar(
        color='rgba(173, 216, 230, 0.2)'
        ).format(
          '{:.2f}', 
          subset=df_vis2.select_dtypes(include=[np.number]).columns
          ).hide(axis='index')  

    st.markdown(
      df_vis2_style.to_html(), 
      unsafe_allow_html=True
      )


# !streamlit run Similitud_Codigo2.py

# para obtener TODOS los requerimientos de librerias que se usan
# !pip freeze > requirements.txt


# para obtener el archivo "requirements.txt" de los requerimientos puntuales de los .py
# !pipreqs "/Seba/Actividades Seba/Programacion Python/44_ Revision similitud pruebas codigo (20-12-24)/App/"

# Video tutorial para deployar una app en streamlitcloud
# https://www.youtube.com/watch?v=HKoOBiAaHGg&ab_channel=Streamlit

