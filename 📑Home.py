import traceback as tb

import streamlit as st

from src.utilities import upload_file, submit_mapping, rename_cols_using_map, save_file

if 'data_uploaded' not in st.session_state:
    st.session_state['data_uploaded'] = False

if 'mapping_submitted' not in st.session_state:
    st.session_state['mapping_submitted'] = False

if 'stage' not in st.session_state:
    st.session_state.stage = 0


st.title('Automated Claims Analysis')

st.sidebar.success("Perform the given steps and then navigate through the pages in the sidebar.")

try:
    with st.expander('#### Upload Claims Data'):
        df, file_name = upload_file()
    if df is not None and file_name is not None:
        col_mapping = submit_mapping(df)
        df = rename_cols_using_map(df, col_mapping)
        res = save_file(df, file_name)
    else:
        raise Exception('Error processing the file.')
except Exception as e:
    tb.format_exc()
