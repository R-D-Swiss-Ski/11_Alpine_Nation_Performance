import streamlit as st
import numpy as np

from helpers import db_functions as db
import re
import pandas as pd

def ranking_view():

    def go_back():
        st.session_state.details = True
        st.session_state.is_ranking =False

    st.button("Go Back", on_click=go_back)
    st.subheader("Ranking")

    #* Get Results of this race
    s = str(st.session_state.race)
    m = re.search(r'\d{4}-\d{2}-\d{2}', s)
    if m:
        race_date = m.group(0)
    else:
        # fallback: keep only digits and dashes
        race_date = re.sub(r'[^\d-]', '', s).strip()
 
    df_results = db.get_result_date(race_date=race_date, gender=st.session_state.gender, discipline=st.session_state.discipline)
    df_results.loc[df_results['Position'] == 0, 'Position'] = np.nan
    df_results = df_results.sort_values(by='Position', ascending=True, na_position='last', ignore_index=True)
    df_results['Racedate_format'] = pd.to_datetime(df_results['Racedate']).dt.strftime('%d.%m.%Y')
    race_title = f"{df_results['Racedate_format'].iloc[0]} {df_results['Place'].iloc[0]} {df_results['Disciplinecode'].iloc[0]} {df_results['Gender'].iloc[0]}"
    st.subheader(race_title)
    st.dataframe(
        df_results[['Competitorname', 'Competitor_Nationcode', 'Status', 'Position', 'Racepoints', 'Details']],
        hide_index=True,
        column_config={
            "Competitorname": "Athlete",
            "Competitor_Nationcode": 'Nation',
            "Position": "Rank",
            "Racepoints": "FISPoints",
            "Detals": "Time"
        }
        
        )