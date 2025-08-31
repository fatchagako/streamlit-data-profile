import streamlit as st 
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
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

def generate_advanced_analysis(df, config_minimal, config_explorative):
    """Génère une analyse avancée selon le mode choisi"""
    
    # Affichage basique des données
    st.subheader("Aperçu des données")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Premières lignes:**")
        st.dataframe(df.head(10))
    with col2:
        st.write("**Dernières lignes:**")
        st.dataframe(df.tail(5))
    
    # Informations sur les colonnes
    st.subheader("Informations sur les colonnes")
    col_info = pd.DataFrame({
        'Type': df.dtypes,
        'Non-null Count': df.count(),
        'Null Count': df.isnull().sum(),
        'Null %': (df.isnull().sum() / len(df) * 100).round(2),
        'Unique Values': df.nunique()
    })
    st.dataframe(col_info)
    
    # Statistiques descriptives
    st.subheader("Statistiques descriptives")
    st.dataframe(df.describe())
    
    if not config_minimal:
        # Analyse des valeurs manquantes
        st.subheader("📊 Analyse des valeurs manquantes")
        missing_data = df.isnull().sum()
        if missing_data.sum() > 0:
            missing_df = pd.DataFrame({
                'Colonne': missing_data.index,
                'Valeurs manquantes': missing_data.values,
                'Pourcentage': (missing_data / len(df) * 100).round(2)
            })
            missing_df = missing_df[missing_df['Valeurs manquantes'] > 0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(missing_df)
            with col2:
                fig = px.bar(missing_df, x='Colonne', y='Pourcentage',
                           title="Pourcentage de valeurs manquantes")
                fig.update_xaxis(tickangle=45)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.success("Aucune valeur manquante ! 🎉")
        
        # Analyses des colonnes numériques
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) > 0:
            st.subheader("📈 Analyse des variables numériques")
            
            # Sélection de colonnes
            selected_numeric = st.multiselect(
                "Sélectionnez les colonnes numériques à analyser:",
                numeric_cols,
                default=numeric_cols[:min(4, len(numeric_cols))]
            )
            
            if selected_numeric:
                # Histogrammes
                st.write("**Distributions:**")
                cols = st.columns(2)
                for i, col in enumerate(selected_numeric):
                    with cols[i % 2]:
                        fig = px.histogram(df, x=col, title=f"Distribution de {col}")
                        st.plotly_chart(fig, use_container_width=True)
                
                # Box plots
                if config_explorative:
                    st.write("**Box plots:**")
                    for i, col in enumerate(selected_numeric):
                        if i % 2 == 0:
                            cols = st.columns(2)
                        with cols[i % 2]:
                            fig = px.box(df, y=col, title=f"Box plot de {col}")
                            st.plotly_chart(fig, use_container_width=True)
        
        # Matrice de corrélation
        if len(numeric_cols) > 1:
            st.subheader("🔗 Matrice de corrélation")
            corr_matrix = df[numeric_cols].corr()
            
            # Graphique de corrélation
            fig = px.imshow(corr_matrix, 
                          text_auto=True, 
                          aspect="auto",
                          color_continuous_scale='RdBu',
                          title="Matrice de corrélation")
            st.plotly_chart(fig, use_container_width=True)
            
            # Tableau de corrélation
            if config_explorative:
                st.write("**Tableau de corrélation:**")
                st.dataframe(corr_matrix.style.background_gradient(cmap='coolwarm'))
        
        # Analyse des variables catégorielles
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
        if len(categorical_cols) > 0:
            st.subheader("🏷️ Variables catégorielles")
            
            selected_cat = st.selectbox(
                "Sélectionnez une variable catégorielle:",
                categorical_cols
            )
            
            if selected_cat:
                value_counts = df[selected_cat].value_counts().head(15)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Top 15 valeurs de {selected_cat}:**")
                    st.dataframe(value_counts)
                
                with col2:
                    fig = px.pie(values=value_counts.values, 
                               names=value_counts.index,
                               title=f"Distribution de {selected_cat}")
                    st.plotly_chart(fig, use_container_width=True)
        
        # Analyse explorative supplémentaire
        if config_explorative and len(numeric_cols) > 1:
            st.subheader("🔍 Analyse explorative")
            
            # Scatter plot interactif
            col1, col2 = st.columns(2)
            with col1:
                x_axis = st.selectbox("Variable X:", numeric_cols)
            with col2:
                y_axis = st.selectbox("Variable Y:", [col for col in numeric_cols if col != x_axis])
            
            if len(categorical_cols) > 0:
                color_by = st.selectbox("Colorer par (optionnel):", ["Aucun"] + categorical_cols)
                color_col = None if color_by == "Aucun" else color_by
            else:
                color_col = None
            
            fig = px.scatter(df, x=x_axis, y=y_axis, color=color_col,
                           title=f"Relation entre {x_axis} et {y_axis}")
            st.plotly_chart(fig, use_container_width=True)
    
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
                generate_advanced_analysis(df, config_minimal, config_explorative)
                    
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
