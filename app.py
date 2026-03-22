import streamlit as st
import pandas as pd
from google import genai
from google.genai import types
import os

# --- CONFIGURACIÓ DE L'API ---
# Introdueix la teva API Key de Gemini aquí o configura-la com a variable d'entorn
GEMINI_API_KEY = "AIzaSyDyCg4-gaxm0dS-EFsbHsJAo1KYLvyldXU" 
client = genai.Client(api_key=GEMINI_API_KEY)

# --- PAS 5: LECTURA DEL CSV DE PREUS ---
@st.cache_data
def carregar_dades_preus():
    try:
        # Intentem carregar l'arxiu recomanat al cas pràctic
        df = pd.read_csv("supermercado_sample.csv") 
        return df
    except FileNotFoundError:
        # Si no existeix, creem un petit dataframe simulat per a l'exemple
        dades_simulades = {
            'Producte': ['Pollastre sencer', 'Llenties', 'Arròs', 'Tomàquet', 'Salmó', 'Bròquil', 'Ous (Dotzena)'],
            'Categoria': ['Carn', 'Llegums', 'Cereals', 'Verdura', 'Peix', 'Verdura', 'Altres'],
            'Preu_Euros': [4.50, 1.20, 1.10, 1.80, 9.50, 1.50, 2.10]
        }
        return pd.DataFrame(dades_simulades)

df_preus = carregar_dades_preus()

# --- INTERFÍCIE D'USUARI (STREAMLIT) ---
st.title("🥦 Generador de Menús Automàtic (Batch Cooking)")
st.write("Crea menús setmanals personalitzats, optimitzats en preu i llestos per al nutricionista.")

# --- PAS 2: FORMULARI DE PERSONALITZACIÓ ---
st.header("1. Preferències del Client")
with st.form("formulari_client"):
    col1, col2 = st.columns(2)
    
    with col1:
        tipus_cuina = st.selectbox("Tipus de cuina", ["Mediterrània", "Vegetariana", "Asiàtica", "Halal", "Llatina"])
        comensals = st.number_input("Nombre de comensals", min_value=1, max_value=10, value=2)
        
    with col2:
        allergies = st.text_input("Aliments a excloure (al·lèrgies, intoleràncies o gustos)", placeholder="Ex: Gluten, lactosa, coriandre...")
        
    submit_button = st.form_submit_button(label="Generar Proposta de Menú")

# --- PAS 1, 3 i 4: GENERACIÓ AMB IA ---
if submit_button:
    st.info("Analitzant preus i dissenyant el menú...")
    
    # Convertim una mostra dels preus a text perquè la IA ho pugui llegir
    preus_text = df_preus.to_string(index=False)
    
    # Construïm el Prompt Mestre (Paso 1 i 5)
    prompt = f"""
    Ets un xef expert en batch cooking i nutrició. Has de crear una proposta de valor clara i útil[cite: 5].
    
    DADES DEL CLIENT:
    - Tipus de cuina: {tipus_cuina}
    - Comensals: {comensals}
    - Aliments a excloure: {allergies if allergies else "Cap"}
    
    DADES DE PREUS (Supermercat):
    {preus_text}
    
    INSTRUCCIONS:
    1. MENÚ SETMANAL: Dissenya un menú de dilluns a divendres amb 4 àpats al dia: esmorzar, dinar, berenar i sopar. Ha de ser nutricionalment equilibrat[cite: 8].
    2. RECEPTES PAS A PAS: Explica breument com fer el batch cooking el cap de setmana per preparar aquests plats.
    3. LLISTA DE LA COMPRA: Fes una llista detallada dels ingredients necessaris per a {comensals} persones.
    4. ANÀLISI DE PREUS: Basant-te en la taula de preus proporcionada, destaca 2 conclusions útils o recomanacions d'estalvi (ex: quins són els ingredients més rendibles).
    
    FORMAT:
    Retorna la resposta en format Markdown molt visual i atractiu, preparat per ser entregat en un document[cite: 21].
    """
    
    try:
        # Cridem a l'API de Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash', # Utilitzem el model Pro per a tasques complexes de raonament
            contents=prompt,
        )
        
        # Mostrem el resultat a la pantalla
        st.success("Menú generat correctament!")
        st.markdown(response.text)
        
        # --- PAS 3: AUTOMATITZACIÓ / ENVIAMENT ---
        st.divider()
        st.header("Validació del Nutricionista")
        st.write("Aquesta proposta s'ha posat a la cua per a la revisió del nutricionista de l'empresa.") # 
        if st.button("Simular enviament al nutricionista per Email/Slack"):
            st.toast("Enviat amb èxit al departament de nutrició! ✅")
            
    except Exception as e:
        st.error(f"Hi ha hagut un error en connectar amb la IA: {e}")

# Mostrar base de dades a la barra lateral
with st.sidebar:
    st.subheader("Base de dades de preus activa")
    st.dataframe(df_preus)
