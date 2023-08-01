import pandas as pd
import plotly.express as px
import streamlit as st

from src.questions import get_high_value_claims, \
    get_injury_claims, \
    get_claim_type_dist, \
    get_claim_status_dist, \
    get_infectious_disease_claims, \
    get_relation_distribution, \
    get_si_exhausted_claims, \
    get_maternity_claims, \
    get_claim_type_dist_by_loc, \
    get_parental_claims, \
    get_prolonged_hospitalisations
from src.utilities import show_basic_stats, \
    formatINR, \
    show_parental_claims, \
    show_maternity_claims

st.set_page_config(page_title="Visualisations",
                   page_icon="📊",
                   layout="wide")
st.sidebar.header("Visualisations")

if st.session_state['stage'] >= 2:
    if not st.session_state['data_uploaded'] or not st.session_state['mapping_submitted']:
        st.warning('Either data has not been uploaded or column mapping has not been submitted.')
    else:
        if st.session_state['file_location']:
            claims_df = pd.read_excel(st.session_state['file_location'])
            total_claims = len(claims_df)
            with st.expander('#### Browse Standardised Data'):
                st.markdown(f'- Number of claims '
                            f'(after discarding claims with data missing in necessary fields): **{len(claims_df)}**')
                st.markdown(f'- Total value of claims: '
                            f':green[**{formatINR(claims_df["IncurredAmount"].sum())}**]')
                st.write(claims_df)
            high_val_claims = get_high_value_claims(claims_df)
            injury_claims = get_injury_claims(claims_df)
            infectious_disease_claims = get_infectious_disease_claims(claims_df)
            si_exhausted_claims = get_si_exhausted_claims(claims_df)
            maternity_claims = get_maternity_claims(claims_df)
            parental_claims = get_parental_claims(claims_df)
            prolonged_hosp_claims = get_prolonged_hospitalisations(claims_df)

            claim_relation_dist = get_relation_distribution(claims_df)
            with st.expander('##### Claim Distribution by Type'):
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    #  Fig 1
                    claim_type_dist = get_claim_type_dist(claims_df)
                    claim_type_pie_fig = px.pie(claim_type_dist,
                                                values=claim_type_dist.values,
                                                names=claim_type_dist.index,
                                                title='Claim Distribution by Type')
                    claim_type_pie_fig.update_traces(textposition='inside',
                                                     textinfo='percent+label')
                    st.plotly_chart(claim_type_pie_fig, use_container_width=True)
                with sub_col2:
                    # Fig 2
                    claim_type_by_location = get_claim_type_dist_by_loc(claims_df)
                    total_claims_by_location = claims_df.groupby('Location')['ClaimType'].count()
                    claim_type_percentage_by_location = claim_type_by_location.div(total_claims_by_location,
                                                                                   axis=0) * 100

                    # Plot the bar chart using Plotly
                    claim_type_percentage_by_location_fig = px.bar(claim_type_percentage_by_location,
                                                                   x=claim_type_percentage_by_location.index,
                                                                   y=claim_type_percentage_by_location.columns,
                                                                   barmode='group',
                                                                   title="Percentage of "
                                                                         "Claim Type Distribution by Location",
                                                                   labels={'y': 'Percentage'})
                    st.plotly_chart(claim_type_percentage_by_location_fig, use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                with st.expander('##### Claim Distribution by Relation'):
                    claim_relation_dist_fig = px.pie(claim_relation_dist,
                                                     values=claim_relation_dist.values,
                                                     names=claim_relation_dist.index,
                                                     title='Claim Distribution by Relation')
                    claim_relation_dist_fig.update_traces(textposition='inside',
                                                          textinfo='percent+label')
                    st.plotly_chart(claim_relation_dist_fig, use_container_width=True)

            with col2:
                with st.expander('##### Claim Distribution by Status'):
                    claim_status_dist = get_claim_status_dist(claims_df)
                    claim_status_pie_fig = px.pie(claim_status_dist,
                                                  values=claim_status_dist.values,
                                                  names=claim_status_dist.index,
                                                  title='Claim Status Distribution')
                    claim_status_pie_fig.update_traces(textposition='inside', textinfo='percent+label')
                    st.plotly_chart(claim_status_pie_fig, use_container_width=True)

            with st.expander('##### Concentration'):
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    # Top 10 locations in decreasing order of count of claims
                    top_10_locations_by_count = claims_df['Location'].value_counts().nlargest(10)
                    st.write("Top 10 locations by count of claims:")
                    st.write(top_10_locations_by_count)

                    # Top 10 highest valued claims by location
                    top_10_highest_valued_claims_by_location = claims_df.groupby('Location')[
                        'IncurredAmount'].max().nlargest(10)
                    st.write("Top 10 highest valued claims by location:")
                    st.write(top_10_highest_valued_claims_by_location)

                with sub_col2:
                    # Top 5 hospitals by number of claims filed at that hospital
                    top_5_hospitals_by_claim_count = claims_df['Hospital'].value_counts().nlargest(5)
                    st.write("Top 5 hospitals by number of claims filed:")
                    st.write(top_5_hospitals_by_claim_count)

                    # Top 15 highest valued claims by hospital
                    top_15_highest_valued_claims_by_hospital = claims_df.groupby('Hospital')[
                        'IncurredAmount'].max().nlargest(15)
                    st.write("Top 15 highest valued claims by hospital:")
                    st.write(top_15_highest_valued_claims_by_hospital)

            if not high_val_claims.empty:
                with st.expander('##### High Value Claims'):
                    st.write('The claims where 70% or more of the sum insured has already been claimed.')
                    show_basic_stats(high_val_claims, claims_df)
                    st.dataframe(high_val_claims.sort_values(by='ClaimedAmount', ascending=False))

            if not prolonged_hosp_claims.empty:
                with st.expander('##### Prolonged Hospitalisation'):
                    st.write('The claims that had more than 10 days of hospitalisation.')
                    show_basic_stats(prolonged_hosp_claims, claims_df)
                    st.dataframe(prolonged_hosp_claims)

            if not injury_claims.empty:
                with st.expander('##### Injury Claims'):
                    st.write('Claims with the ailment corresponding to an injury.')
                    show_basic_stats(injury_claims, claims_df)
                    st.dataframe(injury_claims.sort_values(by='IncurredAmount', ascending=False))

            if not infectious_disease_claims.empty:
                with st.expander('##### Infectious Disease Claims'):
                    st.write('Claims with the ailment corresponding to an infectious disease.')
                    show_basic_stats(infectious_disease_claims, claims_df)
                    st.dataframe(infectious_disease_claims.sort_values(by='IncurredAmount', ascending=False))

            if not si_exhausted_claims.empty:
                with st.expander('##### Sum Insured Exhausted'):
                    st.write('Claims with sum insured exhausted.')
                    show_basic_stats(si_exhausted_claims, claims_df)
                    st.dataframe(si_exhausted_claims.sort_values(by='ClaimedAmount', ascending=False))

            if not maternity_claims.empty:
                with st.expander('##### Maternity Claims'):
                    st.write('Claims pertaining to maternity and childbirth related ailments.')
                    show_maternity_claims(maternity_claims, claims_df)

            if not parental_claims.empty:
                with st.expander('##### Parental Claims'):
                    st.write("Claims filed for the employee's parents")
                    show_parental_claims(parental_claims, claims_df)
else:
    st.warning('Upload file and submit mapping to see visualisations here.')
# set_stage(0)
