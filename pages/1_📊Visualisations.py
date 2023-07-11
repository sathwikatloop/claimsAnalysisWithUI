from pprint import pprint

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Visualisations", page_icon="📊")
st.sidebar.header("Visualisations")
pprint(st.session_state.to_dict())

if not st.session_state['data_uploaded'] or \
        'file_location' not in st.session_state or \
        not st.session_state['mapping_submitted']:
    st.warning('Upload file and submit mapping to see visualisations here.')
else:
    df = pd.read_excel(st.session_state['file_location'])
    st.write(df)
