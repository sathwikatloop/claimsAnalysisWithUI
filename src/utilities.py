from pathlib import Path

import appdirs

from src.settings import mapping
import streamlit as st
import traceback as tb
import pandas as pd

cols_to_be_mapped = mapping.get('required_columnss')


def upload_file():
    with st.form("Upload Data"):
        # st.subheader('Step 1: Upload the claims dump Excel file')
        uploaded_file = st.file_uploader('Upload the claims dump file')
        file_name = Path(f'{uploaded_file.name}').stem
        sheet_name = st.text_input('Sheet name in the Excel file: ')
        submitted = st.form_submit_button("Submit",
                                          on_click=upload_data_set_state)
    try:
        if uploaded_file is not None:
            if sheet_name:
                df = pd.read_excel(uploaded_file,
                                   header=0,
                                   sheet_name=sheet_name)
                st.write('File Contents', df)
                if submitted:
                    upload_data_set_state()
                return df, file_name
            else:
                raise Exception('Sheet name is invalid.')
        else:
            raise Exception('File name is empty.')
    except Exception as e:
        tb.format_exc()
        return None, None


def submit_mapping(df):
    col_mapping = {}
    with st.expander('#### Map columns from raw data'):
        with st.form("Submit Mapping"):
            for col_query, col_name in cols_to_be_mapped.items():
                col_name_from_file = st.selectbox(label=f'{col_query}: ',
                                                  options=(*df.columns,))
                col_mapping[col_name_from_file] = col_name
            col_mapping = {'Age': 'Age',
                           'Ailment_code': 'AilmentICDCode',
                           'Balance_Sum_Insured': 'BalanceSumInsured',
                           'BenefSex': 'Sex',
                           'City_Name': 'Location',
                           'ClaimStatus': 'ClaimStatus',
                           'Claim_Type': 'ClaimType',
                           'Claimed_Amount': 'ClaimedAmount',
                           'Date_of_Admission': 'DateOfAdmission',
                           'Date_of_Discharge': 'DateOfDischarge',
                           'Employee_Code': 'EmployeeCode',
                           'Incurred_Amount': 'IncurredAmount',
                           'Insurance_Company': 'PolicyStartDate',
                           'Policy_End_Date': 'PolicyEndDate',
                           'Procedure_Type_Surgical_Non_Surgical': 'ProcedureType',
                           'Relation': 'Relation',
                           'Sum_Insured': 'SumInsured'}
            try:
                submitted = st.form_submit_button("Submit",
                                                  on_click=submit_mapping_set_state)
                if submitted:
                    st.success('Mapping has been submitted.')
                    submit_mapping_set_state()
                    return col_mapping
            except Exception:
                print(tb.format_exc())


def rename_cols_using_map(df, col_mapping):
    if col_mapping is not None:
        df.rename(columns=col_mapping,
                  inplace=True)
        cols_to_drop = [col for col in df.columns if col not in col_mapping.values()]
        df.drop(cols_to_drop, axis=1, inplace=True)
        return df
    else:
        raise Exception("Error in column name mapping.")


def save_file(df, file_name):
    try:
        data_dir = Path(appdirs.user_data_dir())
        save_standardised_data = data_dir / f"{file_name}_Standardised.xlsx"
        df.to_excel(save_standardised_data, index=False)
        st.session_state['file_location'] = save_standardised_data
    except Exception as e:
        print(tb.format_exc())


def set_state(i):
    st.session_state.stage = i


def upload_data_set_state():
    st.session_state.stage = 1
    st.session_state['data_uploaded'] = True


def submit_mapping_set_state():
    st.session_state.stage = 2
    st.session_state['mapping_submitted'] = True
