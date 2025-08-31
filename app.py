import streamlit as st 
import pandas as pd 
from ydata_profiling import ProfileReport
from streamlit_ydata_profiling import st_profile_report
import sys
import os

st.set_page_config(page_title='Data Profiler', layout='wide')

def get_filesize(file):
    size_bytes = sys.getsizeof(file)
    size_mb = size_bytes / (1024**2)
    return size_mb

def validate_file(file):
    filename = file.name
    name, ext = os.path.splitext(filename)
    if ext in ('.csv','.xlsx'):
        return ext
    else:
        return False
    
# sidebar
with st.sidebar:
    uploaded_file = st.file_uploader("Upload .csv, .xlsx files not exceeding 10 MB")
    if uploaded_file is not None:
        st.write('Modes of Operation')
        minimal = st.checkbox('Do you want minimal report ?')
        
        # Configuration du thème (simplifié pour éviter les erreurs)
        display_mode = st.radio('Display mode:',
                                options=('Standard','Minimal','Explorative'))
        
        # Configuration basée sur le mode sélectionné
        if display_mode == 'Minimal':
            config_minimal = True
            config_explorative = False
        elif display_mode == 'Explorative':
            config_minimal = False
            config_explorative = True
        else:  # Standard
            config_minimal = minimal
            config_explorative = False
    
if uploaded_file is not None:
    ext = validate_file(uploaded_file)
    if ext:
        filesize = get_filesize(uploaded_file)
        if filesize <= 10:
            if ext == '.csv':
                # Chargement du fichier CSV
                try:
                    df = pd.read_csv(uploaded_file)
                except Exception as e:
                    st.error(f"Erreur lors du chargement du CSV: {str(e)}")
                    st.stop()
            else:
                # Chargement du fichier Excel
                try:
                    xl_file = pd.ExcelFile(uploaded_file)
                    sheet_tuple = tuple(xl_file.sheet_names)
                    sheet_name = st.sidebar.selectbox('Select the sheet', sheet_tuple)
                    df = xl_file.parse(sheet_name)
                except Exception as e:
                    st.error(f"Erreur lors du chargement du fichier Excel: {str(e)}")
                    st.stop()
            
            # Affichage d'informations sur le dataset
            st.write(f"**Dataset chargé:** {uploaded_file.name}")
            st.write(f"**Dimensions:** {df.shape[0]} lignes × {df.shape[1]} colonnes")
            
            # Génération du rapport
            with st.spinner('Generating Report...'):
                try:
                    # Configuration simplifiée pour éviter les erreurs de validation
                    pr = ProfileReport(
                        df,
                        title="Data Profiling Report",
                        minimal=config_minimal,
                        explorative=config_explorative
                    )
                    
                    st_profile_report(pr)
                    
                except Exception as e:
                    st.error(f"Erreur lors de la génération du rapport: {str(e)}")
                    st.info("Essayez avec le mode 'Minimal' si vous rencontrez des problèmes.")
                    
                    # Fallback: affichage basique des données
                    st.subheader("Aperçu des données")
                    st.dataframe(df.head(10))
                    
                    st.subheader("Informations sur les colonnes")
                    col_info = pd.DataFrame({
                        'Type': df.dtypes,
                        'Non-null Count': df.count(),
                        'Null Count': df.isnull().sum(),
                        'Null %': (df.isnull().sum() / len(df) * 100).round(2)
                    })
                    st.dataframe(col_info)
                    
                    st.subheader("Statistiques descriptives")
                    st.dataframe(df.describe())
                    
        else:
            st.error(f'Maximum allowed filesize is 10 MB. But received {filesize:.2f} MB')
            
    else:
        st.error('Kindly upload only .csv or .xlsx file')
        
else:
    st.title('Data Profiler')
    st.info('Upload your data in the left sidebar to generate profiling')
    
    # Informations sur l'utilisation
    st.markdown("""
    ### Comment utiliser cet outil :
    
    1. **Upload** : Glissez-déposez votre fichier CSV ou Excel dans la sidebar
    2. **Configuration** : Choisissez vos options d'analyse
    3. **Analyse** : Le rapport sera généré automatiquement
    
    ### Modes disponibles :
    - **Standard** : Rapport complet avec toutes les analyses
    - **Minimal** : Rapport rapide avec les informations essentielles
    - **Explorative** : Rapport détaillé avec analyses approfondies
    
    ### Formats supportés :
    - CSV (*.csv)
    - Excel (*.xlsx)
    - Taille maximum : 10 MB
    """)
