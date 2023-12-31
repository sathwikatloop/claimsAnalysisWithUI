import os
from pathlib import Path
from pprint import pprint

import appdirs
import numpy as np
from dateparser import parse

from src.questions import women_who_delivered_in_age_band
from src.settings import mapping, std_date_cols, compulsory_cols_to_be_mapped
import streamlit as st
import traceback as tb
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff

from scipy.stats import norm
import re
import plotly.graph_objects as go

from thefuzz import process

"""General Utility Functions"""

numeric_columns = ['SumInsured',
                   'BalanceSumInsured',
                   'ClaimedAmount',
                   'IncurredAmount',
                   'PercentOfSumInsuredClaimed']


def std_dates(df):
    """
    Args:
        df:

    Returns:

    """
    for col in std_date_cols:
        df[col] = df[col].apply(lambda val: parse(val,
                                                  date_formats=['%m/%d%Y', '%d-%b-%Y', '%d-%B-%Y']))
    return df


def allot_ailment_group(val):
    """

    Args:
        val:

    Returns:

    """
    if not val:
        return 'NA'
    res = re.search(r'[A-Z]', val)
    if not res:
        return 'NA'
    res = res.group()
    return res


def upload_file_form():
    try:
        file_uploaded, select_sheet = False, False
        with st.form("Upload Data"):
            uploaded_file = st.file_uploader('Upload the claims dump file')
            file_uploaded = st.form_submit_button("Upload")
            if uploaded_file is not None:
                sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        if uploaded_file is not None:
            sheet = st.selectbox('Sheet name in the Excel file',
                                 options=sheet_names)
            with st.form("Input Sheet name"):
                select_sheet = st.form_submit_button("Submit",
                                                     on_click=upload_data_set_state)
                if select_sheet:
                    st.success('File Uploaded Successfully!')
                    if sheet:
                        file_name = Path(f'{uploaded_file.name}').stem
                        df = pd.read_excel(uploaded_file,
                                           header=0,
                                           sheet_name=sheet)
                        return df, file_name
    except Exception as e:
        tb.format_exc()
    return None, None

def automated_mapping(df):
    mappings = {}
    compulsory_cols = compulsory_cols_to_be_mapped.keys()
    for col_name in compulsory_cols:
        matches = process.extract(col_name, df.columns, limit=5)
        closest_match = matches[0][0]
        if (closest_match in mappings.values()):
            closest_match = matches[1][0]
        mappings[col_name] = closest_match
    return mappings

def submit_mapping(df):
    col_mapping = automated_mapping(df)

    print("Automated mapping", col_mapping)
    sorted_cols = sorted(df.columns.to_list())
    st.session_state.column_mapping = {}
    print("Session state before form", st.session_state.column_mapping)

    # temp_columns = {col_name: col_name for col_name in compulsory_cols_to_be_mapped.keys()}

    temp_columns = {}

    # print("Temp columns before form", temp_columns)

    with st.form("Submit Mapping", clear_on_submit=False):
        st.subheader('Mandatory Columns')

        # Create a list of columns to be mapped
        # Use key of columns as variable names to store the selected column name

        for col_query, col_name in col_mapping.items():
            print("Col query : Col Name", col_query, ":", col_name)
            default_index = sorted_cols.index(col_mapping.get(col_query, sorted_cols[0]))
            col_name_from_file = st.selectbox(label=f'{col_query}: ',
                                              options=(*sorted_cols,),
                                              index=default_index,)
            temp_columns[col_name_from_file] = col_query
    
        submitted = st.form_submit_button("Submit", on_click=submit_mapping_set_state(temp_columns))

    return temp_columns

def update_col_mapping(col_query):
    print("on_change called")
    def callback():
        print("Callback called")
    return callback

def rename_cols_using_map(df, col_mapping):
    if st.session_state["column_mapping"] is not None:
        col_mapping = st.session_state["column_mapping"]
        df.rename(columns=col_mapping,
                  inplace=True)
        cols_to_drop = [col for col in df.columns if col not in col_mapping.values()]
        df.drop(cols_to_drop, axis=1, inplace=True)
        return df
    else:
        raise Exception("Error in column name mapping.")


def save_file(df, file_name):
    save_standardised_data = False
    try:
        data_dir = Path(appdirs.user_data_dir())
        save_standardised_data = data_dir / f"{file_name}_Standardised.xlsx"
        if save_standardised_data.is_file():
            os.remove(save_standardised_data)
        df.to_excel(save_standardised_data, index=False)
        st.session_state['file_location'] = save_standardised_data
        return save_standardised_data
    except Exception as e:
        print(tb.format_exc())
    return False


def set_stage(i):
    st.session_state.stage = i


def upload_data_set_state():
    set_stage(1)
    st.session_state['data_uploaded'] = True


def submit_mapping_set_state(temp_columns):
    set_stage(2)
    st.session_state['mapping_submitted'] = True
    st.session_state['column_mapping'] = temp_columns
    print("Column Mapping set in session state", st.session_state['column_mapping'])


def formatINR(number):
    number = float(number)
    number = round(number, 2)
    is_negative = number < 0
    number = abs(number)
    s, *d = str(number).partition(".")
    r = ",".join([s[x - 2:x] for x in range(-3, -len(s), -2)][::-1] + [s[-3:]])
    value = "".join([r] + d)
    if is_negative:
        value = '-' + value
    return '₹' + value


"""Data Standardisation Function"""


def standardise_data(df):
    """

    Args:
        df:

    Returns:

    """
    try:
        # df[str_cols] = df[str_cols].astype(str)
        # if df.columns != compulsory_cols_to_be_mapped.keys():
        #     pprint(df.columns)
        #     raise Exception("Some columns missing")
        # Drop rows with necessary columns missing
        df = df.dropna(subset=['AilmentICDCode', 'ClaimStatus', 'SumInsured'])

        # for col in numeric_columns:
        #     df[col] = df[col].str.replace(',', '').astype(float)

        # Standardise date columns specified earlier
        df = std_dates(df)

        # Standardise Sex
        df['Sex'] = df['Sex'].apply(lambda val: mapping['gender'].get(val.lower().strip(),
                                                                      'NA') if isinstance(val, str) else 'NA')

        # Standardise Ailment Codes
        df['AilmentICDCode'] = df['AilmentICDCode'].apply(allot_ailment_group)

        # Add Ailment Group Description
        df['AilmentGroupDescription'] = df['AilmentICDCode'].apply(lambda val: mapping['ailment_group'].get(val, 'NA'))

        # Standardise claim status as per mapping
        df['ClaimStatus'] = df['ClaimStatus'].apply(
            lambda val: mapping['claim_status'].get(val.lower().strip(), 'NA') if isinstance(val, str) else 'NA')
        df['ClaimStatus'] = df['ClaimStatus'].apply(
            lambda val: mapping['readable_str_mapping']['claim_status'].get(val, 'NA') if isinstance(val,
                                                                                                     str) else 'NA')

        # Standardise relation
        df['Relation'] = df['Relation'].apply(
            lambda val: mapping['relation'].get(val.lower().strip(), 'NA') if isinstance(val, str) else 'NA')

        # Add additional info
        df['PercentOfSumInsuredClaimed'] = ((df['ClaimedAmount'] / df['SumInsured']) * 100).round(2)
        df['NoOfHospitalisedDays'] = (df['DateOfDischarge'] - df['DateOfAdmission']).dt.days

        return df
    except Exception:
        print(tb.format_exc())


"""Visualisation / Analysis Functions"""


def show_basic_stats(specific_claims, data_df):
    """
    Given a set of claims, evaluate and show the count and value against the entirety of the claims data
    Args:
        specific_claims:
        data_df:

    Returns:

    """

    # Calculate the number and value of claims from Parents
    num_specific_claims = len(specific_claims)
    total_value_specific_claims = specific_claims['IncurredAmount'].sum()
    total_claims = len(data_df)
    # Calculate the percentage of claims from Parents by count and value
    percentage_by_count = (num_specific_claims / total_claims) * 100
    percentage_by_value = (total_value_specific_claims / data_df['IncurredAmount'].sum()) * 100

    st.markdown(f'- Number of such claims: **{(len(specific_claims))}**')
    st.markdown(f"- Percentage of such claims by count: :blue[**{percentage_by_count:.2f}%**]")
    total_value_of_specific_claims = specific_claims['IncurredAmount'].sum()
    st.markdown(f'- Total value of all such claims: '
                f':green[**{formatINR(total_value_of_specific_claims)}**]')
    st.markdown(f"- Percentage of such claims by value: :blue[**{percentage_by_value:.2f}%**]")


def show_parental_claims(parental_claims, data_df):
    """
    Calculate and plot parental claims data
    Args:
        parental_claims:
        data_df:

    Returns:

    """
    total_claims = len(data_df)
    total_parental_claims = len(parental_claims)
    total_parental_claims_value = parental_claims['IncurredAmount'].sum()
    show_basic_stats(parental_claims, data_df)
    st.write('#### Parental Claims Data')
    st.dataframe(parental_claims.sort_values(by='IncurredAmount',
                                             ascending=False))
    sub_col1, sub_col2 = st.columns(2)
    with sub_col1:
        st.write("##### Top 5 ailment categories, with avg. cost per ailment")
        # Group the parental claims by ailment category and calculate the average cost per ailment
        ailment_avg_cost = parental_claims.groupby('AilmentGroupDescription')[
            'IncurredAmount'].mean().reset_index()

        # Sort the ailment_avg_cost DataFrame in descending order based on average cost
        ailment_avg_cost = ailment_avg_cost.sort_values(by='IncurredAmount',
                                                        ascending=False)
        ailment_avg_cost = ailment_avg_cost.rename(
            columns={'IncurredAmount': 'Average Incurred Amount'})

        # Take the Top 5 ailment categories
        top_5_ailments = ailment_avg_cost.head(5)

        st.write(top_5_ailments)
    with sub_col2:
        eye_related_claims = parental_claims[parental_claims['AilmentICDCode'] == 'G']
        if not eye_related_claims.empty:
            st.write('##### Eye Related Claims')
            # Calculate the percentage of eye-related claims by count
            eye_related_claims_count = len(eye_related_claims)
            percentage_eye_related_by_count = (eye_related_claims_count / total_claims) * 100

            # Calculate the percentage of eye-related claims by value
            eye_related_claims_value = eye_related_claims['IncurredAmount'].sum()
            percentage_eye_related_by_value = (eye_related_claims_value /
                                               total_parental_claims_value) * 100
            avg_eye_related_claims_amt = eye_related_claims['IncurredAmount'].mean()

            st.markdown(f"- Percentage of eye-related claims by count: "
                        f":blue[**{percentage_eye_related_by_count}**]")
            st.markdown(f"- Percentage of eye-related claims by value: "
                        f":blue[**{percentage_eye_related_by_value}**]")
            st.markdown(f"- Average cost of an eye-related claim: "
                        f":green[**{formatINR(avg_eye_related_claims_amt)}**]")

            # Extract IncurredAmount data
            orthopedic_incurred_amount_data = eye_related_claims['IncurredAmount']

            # Calculate mean and standard deviation of IncurredAmount
            mean_incurred_amount = orthopedic_incurred_amount_data.mean()
            std_incurred_amount = orthopedic_incurred_amount_data.std()

            # Generate data points for the normal distribution curve
            x_range = np.linspace(mean_incurred_amount - 3 * std_incurred_amount,
                                  mean_incurred_amount + 3 * std_incurred_amount,
                                  100)
            y_values = norm.pdf(x_range,
                                mean_incurred_amount,
                                std_incurred_amount)

            # Create the figure
            fig = go.Figure()

            # Add the smooth line plot of IncurredAmount to the figure
            fig.add_trace(
                go.Scatter(x=orthopedic_incurred_amount_data,
                           y=norm.pdf(orthopedic_incurred_amount_data,
                                      mean_incurred_amount,
                                      std_incurred_amount),
                           mode='markers',
                           name='IncurredAmount',
                           marker=dict(color='blue')))

            # Add the normal distribution curve to the figure
            fig.add_trace(
                go.Scatter(x=x_range,
                           y=y_values,
                           mode='lines',
                           name='Normal Distribution',
                           line=dict(color='red', width=2)))

            # Update the layout to add axis labels and title
            fig.update_layout(
                title_text="Normal Distribution of IncurredAmount in Eye Related Parental Claims",
                xaxis_title="IncurredAmount",
                yaxis_title="Density",
            )

        # Filter orthopedic claims based on the AilmentICDCode mapping
        orthopedic_claims = parental_claims[parental_claims["AilmentICDCode"] == "M"]
        if not orthopedic_claims.empty:
            st.write("##### Orthopedic Claims")
            # Calculate the percentage of orthopedic claims by count
            orthopedic_claims_count = len(orthopedic_claims)
            orthopedic_claims_value = orthopedic_claims['IncurredAmount'].sum()
            avg_orthopedic_claims_amt = orthopedic_claims['IncurredAmount'].mean()

            percentage_orthopedic_claims_by_count = (orthopedic_claims_count / total_claims) * 100
            percentage_orthopedic_by_value = (orthopedic_claims_value /
                                              total_parental_claims_value) * 100

            st.markdown(f"- Percentage of parental claims that are orthopedic claims by count: "
                        f"{percentage_orthopedic_claims_by_count}%")
            st.markdown(f"- Percentage of parental claims that are orthopedic claims by value: "
                        f"{percentage_orthopedic_by_value}%")
            st.markdown(f"- Average cost of an orthopedic claim: "
                        f":green[**{formatINR(avg_orthopedic_claims_amt)}**]")

            # Extract IncurredAmount data
            orthopedic_incurred_amount_data = orthopedic_claims['IncurredAmount']

            # Calculate mean and standard deviation of IncurredAmount
            mean_incurred_amount = orthopedic_incurred_amount_data.mean()
            std_incurred_amount = orthopedic_incurred_amount_data.std()

            # Generate data points for the normal distribution curve
            x_range = np.linspace(mean_incurred_amount - 3 * std_incurred_amount,
                                  mean_incurred_amount + 3 * std_incurred_amount,
                                  100)
            y_values = norm.pdf(x_range,
                                mean_incurred_amount,
                                std_incurred_amount)

            # Create the figure
            fig = go.Figure()

            # Add the smooth line plot of IncurredAmount to the figure
            fig.add_trace(
                go.Scatter(x=orthopedic_incurred_amount_data,
                           y=norm.pdf(orthopedic_incurred_amount_data,
                                      mean_incurred_amount,
                                      std_incurred_amount),
                           mode='markers',
                           name='IncurredAmount',
                           marker=dict(color='blue')))

            # Add the normal distribution curve to the figure
            fig.add_trace(
                go.Scatter(x=x_range,
                           y=y_values,
                           mode='lines',
                           name='Normal Distribution',
                           line=dict(color='red', width=2)))

            # Update the layout to add axis labels and title
            fig.update_layout(
                title_text="Normal Distribution of IncurredAmount in Orthopaedic Parental Claims",
                xaxis_title="IncurredAmount",
                yaxis_title="Density",
            )


def show_maternity_claims(maternity_claims, data_df):
    """
    Given the maternity claims data, show the visualisations and stats
    Args:
        maternity_claims:
        data_df:

    Returns:

    """
    show_basic_stats(maternity_claims, data_df)
    perc_of_women_who_delivered = women_who_delivered_in_age_band(data_df)
    st.markdown(f'- Percentage of women (between 20-40) who delivered a child '
                f'(includes employee + spouse)%: :blue[**{perc_of_women_who_delivered}%**]')
    st.markdown(f"- Average cost of a maternity claims: :green[**"
                f"{formatINR(maternity_claims['IncurredAmount'].mean())}**]")

    # Extract IncurredAmount data
    incurred_amount_data = maternity_claims['IncurredAmount']

    # Calculate mean and standard deviation of IncurredAmount
    mean_incurred_amount = incurred_amount_data.mean()
    std_incurred_amount = incurred_amount_data.std()

    # Generate data points for the normal distribution curve
    x_range = np.linspace(mean_incurred_amount - 3 * std_incurred_amount,
                          mean_incurred_amount + 3 * std_incurred_amount, 100)
    y_values = norm.pdf(x_range, mean_incurred_amount, std_incurred_amount)

    # Create the figure
    fig = go.Figure()

    # Add the smooth line plot of IncurredAmount to the figure
    fig.add_trace(
        go.Scatter(x=incurred_amount_data, y=norm.pdf(incurred_amount_data, mean_incurred_amount, std_incurred_amount),
                   mode='markers', name='IncurredAmount', marker=dict(color='blue')))

    # Add the normal distribution curve to the figure
    fig.add_trace(
        go.Scatter(x=x_range, y=y_values, mode='lines', name='Normal Distribution', line=dict(color='red', width=2)))

    # Update the layout to add axis labels and title
    fig.update_layout(
        title_text="Normal Distribution of IncurredAmount in Maternity Claims",
        xaxis_title="IncurredAmount",
        yaxis_title="Density",
    )
    st.plotly_chart(fig)
