import traceback as tb
from pprint import pprint

import pandas as pd
import streamlit as st

from src.settings import mapping, compulsory_cols_to_be_mapped
from src.utilities import (
    upload_file_form,
    submit_mapping,
    rename_cols_using_map,
    save_file,
    standardise_data,
    submit_mapping_set_state,
    upload_data_set_state,
)

st.set_page_config(page_title="Data Upload", page_icon="📑")

st.title("Automated Claims Analysis")
st.sidebar.header("Data Upload")
col_mapping = {}
st.sidebar.info(
    "Perform the given steps and then navigate through the pages in the sidebar."
)

if "stage" not in st.session_state:
    st.session_state.stage = 0

if "data_uploaded" not in st.session_state:
    st.session_state["data_uploaded"] = False

if "mapping_submitted" not in st.session_state:
    st.session_state["mapping_submitted"] = False

if "file_location" not in st.session_state:
    st.session_state["file_location"] = ""

if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = pd.DataFrame()

if "file_name" not in st.session_state:
    st.session_state["file_name"] = None


def initialize_stage():
    """

    Returns:

    """
    st.session_state.stage = 0
    st.session_state["data_uploaded"] = False
    st.session_state["mapping_submitted"] = False
    st.session_state["file_location"] = ""
    st.session_state["uploaded_data"] = pd.DataFrame()
    st.session_state["file_name"] = None
    st.experimental_rerun()


def upload_claims_data():
    """

    Returns:

    """
    with st.expander("#### 1. Upload claims data"):
        df, file_name = upload_file_form()
        if df is not None:
            if not df.empty and file_name is not None:
                st.write(f"File Contents: {file_name}", df)
                st.session_state.uploaded_data = df
                st.session_state.file_name = file_name
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
        with st.expander("#### 2. Map corresponding relevant columns"):
            if not df.empty and file_name:
                col_mapping = submit_mapping(df)
                if col_mapping:
                    df = rename_cols_using_map(df, col_mapping)
                    df = standardise_data(df)
                    if df is not None and not df.empty:
                        save_file(df, file_name)
                        True
            else:
                st.warning(
                    "First upload the file above to get the inputs for columns to map"
                )
    except Exception as e:
        return False


if __name__ == "__main__":
    if st.session_state.stage < 2:
        df, file_name = upload_claims_data()
        input_mapping(df, file_name)
    if st.session_state.stage == 2:
        st.write(f"Name of File Uploaded: {st.session_state.file_name}")
        st.write(f"#### File Contents", st.session_state.uploaded_data)
        st.info(
            "The uploaded data has been processed and the insights are available "
            "to view in the Visualisations tab from the sidebar"
        )
        if st.button("Reset"):
            initialize_stage()
