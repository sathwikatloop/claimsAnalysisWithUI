import re
import traceback as tb
import streamlit as st
from dateparser import parse
from tabulate import tabulate as tab
from src.settings import mapping
import seaborn as sns

"""Claim Segregation"""


def get_high_value_claims(df):
    return df.loc[df['PercentOfSumInsuredClaimed'] > 70]


def get_injury_claims(df):
    return df.loc[df['AilmentICDCode'].isin(["S", "T"])]


def get_si_exhausted_claims(df):
    return df.loc[df['PercentOfSumInsuredClaimed'] >= 100]


def get_maternity_claims(df):
    """
     Segregate and gather insights for maternity claims
    Args:
        df:

    Returns:

    """
    return df.loc[df['AilmentICDCode'].isin(['O', 'P'])]


def get_parental_claims(df):
    """
    Args:
        df:

    Returns:

    """
    # Filter the DataFrame to include only claims from Parents
    return df.loc[df['Relation'] == 'Parent']


def get_prolonged_hospitalisations(df):
    """
    get claims that had longer than 10 days of hospitalisation
    Args:
        df:

    Returns:

    """
    return df.loc[df['NoOfHospitalisedDays'] > 10]



"""Distributions"""


def get_claim_status_dist(df):
    return (df['ClaimStatus'].value_counts(normalize=True) * 100).round(2)


def get_infectious_disease_claims(df):
    return df.loc[df['AilmentICDCode'] == "A"]


def get_relation_distribution(df):
    return (df['Relation'].value_counts(normalize=True) * 100).round(2)


def get_claim_type_dist(df):
    return (df['ClaimType'].value_counts(normalize=True) * 100).round(2)


def get_claim_type_dist_by_loc(df):
    return df.groupby(['ClaimType', 'Location']).size().unstack().transpose()


"""Get Specific Stats"""


def women_who_delivered_in_age_band(data_df):
    """
    % of women (between 20-40) who delivered a child (includes employee + spouse)
    Args:
        data_df:

    Returns:

    """
    num_women_in_age_group = len(data_df.loc[(data_df['Sex'] == 'Female') &
                                             (data_df['Age'] >= 20) &
                                             (data_df['Age'] <= 40) &
                                             (data_df['Relation'].isin(['Self', 'Spouse']))])
    num_women_delivered = len(data_df.loc[data_df['AilmentICDCode'].isin(['O', 'P'])])

    if num_women_in_age_group and num_women_delivered:
        return round((num_women_delivered / num_women_in_age_group) * 100, 2)
    return 0
