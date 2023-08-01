import traceback as tb
from pprint import pprint

import pandas as pd
import streamlit as st

from src.settings import mapping, compulsory_cols_to_be_mapped
from src.utilities import upload_file_form, submit_mapping, rename_cols_using_map, save_file, standardise_data, \
    submit_mapping_set_state, upload_data_set_state

st.set_page_config(page_title="Data Upload",
                   page_icon="📑")

st.title('Automated Claims Analysis')
st.sidebar.header("Data Upload")
col_mapping = {}
st.sidebar.info("Perform the given steps and then navigate through the pages in the sidebar.")

if 'stage' not in st.session_state:
    st.session_state.stage = 0

if 'data_uploaded' not in st.session_state:
    st.session_state['data_uploaded'] = False

if 'mapping_submitted' not in st.session_state:
    st.session_state['mapping_submitted'] = False

if 'file_location' not in st.session_state:
    st.session_state['file_location'] = ''


def initialize_stage():
    """

    Returns:

    """
    st.session_state.stage = 0
    st.session_state['data_uploaded'] = False
    st.session_state['mapping_submitted'] = False
    st.session_state['file_location'] = ''


def upload_claims_data():
    """

    Returns:

    """
    with st.expander('#### 1. Upload claims data'):
        df, file_name = upload_file_form()
        if df is not None and file_name is not None:
            print(df, file_name)
            return df, file_name
    return pd.DataFrame(), None


def input_mapping(df, file_name):
    """

    Args:
        df:
        file_name:

    Returns:

    """
    try:
        with st.expander('#### 2. Map corresponding relevant columns'):
            col_mapping = submit_mapping(df)
            if col_mapping:
                df = rename_cols_using_map(df, col_mapping)
                df = standardise_data(df)
                if df is not None and not df.empty:
                    res = save_file(df, file_name)
                    if res:
                        st.success(f'Mapping submitted and standardised file saved.')
                    return df, True
    except Exception as e:
        return pd.DataFrame(), False


if __name__ == '__main__':
    pprint(st.session_state.to_dict())
    df, file_name = pd.DataFrame(), None
    submit_mapping_status = False
    if st.session_state.stage == 0:
        df, file_name = upload_claims_data()
    if not df.empty:
        print(df)
        std_df, submit_mapping_status = input_mapping(df, file_name)
    if st.button('Reset'):
        initialize_stage()
    # pprint(st.session_state.to_dict())
    # print(f"mapping submitted: {st.session_state['mapping_submitted']}")

# else:
#     raise Exception('Error processing the file.')
