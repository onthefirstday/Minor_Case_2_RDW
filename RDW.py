import requests
import pandas as pd
import streamlit as st

def get_data():
    if "data_ken" not in st.session_state:
        url = "https://opendata.rdw.nl/resource/m9d7-ebf2.json"
        params = {
            "$select": "kenteken,merk,handelsbenaming,voertuigsoort,datum_tenaamstelling",
            "$order": "kenteken",#"datum_tenaamstelling DESC",
            "$limit": 100000
        }
        response = requests.get(url, params=params)
        st.session_state.data_ken = pd.json_normalize(response.json())
        st.session_state.data_ken['datum_tenaamstelling'] = pd.to_datetime(st.session_state.data_ken['datum_tenaamstelling'], format='%Y%m%d')
        st.session_state.data_ken = st.session_state.data_ken.loc[st.session_state.data_ken['datum_tenaamstelling'] > '2022-01-01']
        st.session_state.data_ken['voertuigsoort'] = st.session_state.data_ken['voertuigsoort'].str.lower().str.capitalize()
        st.session_state.data_ken = st.session_state.data_ken.loc[st.session_state.data_ken['voertuigsoort'] == 'Personenauto']
        
    if "data_ben" not in st.session_state:
        url = "https://opendata.rdw.nl/resource/8ys7-d773.json"
        params = {
            "$select": "kenteken,brandstof_omschrijving",
            "$order": "kenteken",
            "$limit": 100000
        }
        response = requests.get(url, params=params)
        st.session_state.data_ben = pd.json_normalize(response.json())
        st.session_state.data_ben['brandstof_omschrijving'].dropna(inplace=True)

get_data()
# if "data" not in st.session_state:
#     st.session_state.data = st.session_state.data_ken.merge(st.session_state.data_ben, on='kenteken', how='left')
if "data_merged" not in st.session_state:    
    st.session_state.data_merged = st.session_state.data_ken.merge(st.session_state.data_ben, on='kenteken', how='inner')
    st.session_state.data_merged = st.session_state.data_merged.drop_duplicates(subset=['kenteken'])
    st.session_state.data_merged['brandstof_omschrijving'].fillna('Onbekend', inplace=True)

top_makes = st.session_state.data_merged.groupby('merk').count().sort_values('kenteken', ascending=False).head(20).index.tolist()
st.session_state.data_merged = st.session_state.data_merged[st.session_state.data_merged['merk'].isin(top_makes)]

st.sidebar.title("RDW Data Explorer")
st.set_page_config(page_title="RDW Car Data Analysis", layout="wide")
st.sidebar.markdown("Explore RDW vehicle data including makes, models, and fuel types.")

pg = st.navigation(["page1.py", "page2.py"])
pg.run()

st.write('Hello')