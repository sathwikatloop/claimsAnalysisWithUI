import re
import traceback as tb
from dateparser import parse
from tabulate import tabulate as tab
from src.settings import mapping

std_date_cols = ['PolicyStartDate',
                 'PolicyEndDate',
                 'DateOfAdmission',
                 'DateOfDischarge']
str_cols = ['AilmentCode',
            'Insurer',
            'PolicyStartDate',
            'PolicyEndDate',
            'EmployeeCode',
            'Sex',
            'Relation',
            'ClaimType',
            'ClaimStatus',
            'DateOfAdmission',
            'DateOfDischarge']


def std_dates(df):
    """
    Args:
        df:

    Returns:

    """
    for col in std_date_cols:
        df[col] = df[col].apply(lambda val: parse(val, date_formats=['%m/%d%Y']))
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


"""Data Standardisation Function"""


def standardise_data(df):
    """

    Args:
        df:

    Returns:

    """
    try:
        # df[str_cols] = df[str_cols].astype(str)
        # Drop rows with necessary columns missing
        df = df.dropna(subset=['AilmentCode', 'ClaimStatus', 'SumInsured'])

        # Standardise date columns specified earlier
        df = std_dates(df)

        # Standardise Ailment Codes
        df['AilmentCode'] = df['AilmentCode'].apply(allot_ailment_group)

        # Add Ailment Group Description
        df['AilmentGroupDescription'] = df['AilmentCode'].apply(lambda val: mapping['ailment_group'].get(val, 'NA'))

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
        df['PercentOfSumInsuredClaimed'] = ((df['IncurredAmount'] / df['SumInsured']) * 100).round(2)
        return df

    except Exception:
        print(tb.format_exc())


def q1(df):
    print('\n\nHigh value claims with percent of sum insured claimed is greater than 70%:\n')
    print(tab(df.loc[df['PercentOfSumInsuredClaimed'] > 70], df.columns, tablefmt="heavy_grid"))


def q2(df):
    print('\n\nInjury claims:\n')
    print(tab(df.loc[df['AilmentCode'].isin(["S", "T"])], df.columns, tablefmt="heavy_grid"))


def q3(df):
    print('\n\nClaims with sum insured exhausted:\n')
    print(tab(df.loc[df['PercentOfSumInsuredClaimed'] >= 100], df.columns, tablefmt="heavy_grid"))


def q4(df):
    print('\n\nClaims pertaining to infectious diseases')
    print(tab(df.loc[df['AilmentCode'] == "A"], df.columns, tablefmt="heavy_grid"))


def q5(df):
    print('\n\nEmployee-Dependant claim distribution based on relation:\n')
    print((df['Relation'].value_counts(normalize=True) * 100).round(2).to_string())


def q6(df):
    print('\n\nDistribution of claims by type:\n')
    print((df['ClaimType'].value_counts(normalize=True) * 100).round(2).to_string())


def q7(df):
    print('\n\nDistribution of claims by status:\n')
    print((df['ClaimStatus'].value_counts(normalize=True) * 100).round(2).to_string())


def execute_query(df, choice):
    """

    Args:
        df:
        choice:

    Returns:

    """
    query_functions = {
        '1': q1,
        '2': q2,
        '3': q3,
        '4': q4,
        '5': q5,
        '6': q6,
        '7': q7
    }
    return query_functions.get(choice, None)(df)
