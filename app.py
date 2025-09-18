import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

from st_aggrid import AgGrid

from helpers import db_functions as dbf
from helpers.constants import WORLDCUP_POINTS, WORLDCUP_FINALS, WORLDCUP_POINTS_FINALS, GENDER, DISCIPLINES
from helpers.ag_grid_options import grid_options_2

st.set_page_config(
    initial_sidebar_state="collapsed",
    page_title="Content Dashboard",
    layout="wide",
    )

st.header("Blick Content Dashboard")

#races
races = dbf.get_races_dp()
races_2025 = races[(races['Seasoncode'] == 2025) & (races['Disciplinecode'] == "SL") & (races['Gender'] == "W")]
st.write("GS W Season 2024/2025")
races_2025

#result of specific race
race_id = 123167
result = dbf.get_result(race_id)
st.write("Specific race: ", race_id)
result



def create_wc_points_df(season, genders, disciplines):
    results = pd.DataFrame()
    if 'All' in disciplines:
         disciplines = ['GS', 'SL', 'DH', 'SG']
    if 'All' in genders:
        genders = ['M', 'W']
    for discipline in disciplines:
        for gender in genders:
            result = dbf.get_results(season=season, discipline=discipline, gender=gender)
            results = pd.concat([result, results], ignore_index=True)

    results = results.rename(columns={"Competitor_Nationcode": "Nation", 'Disciplinecode': 'Discipline'})
    # drop cancelled races
    results = results[results['Webcomment'] != "Cancelled"]
    ## map world cup points
    results['isFinal'] = results['Raceid'].apply(lambda x: True if x in WORLDCUP_FINALS else False)
    results['WCPoints'] = 0
    mask = results['isFinal']
    results.loc[mask, 'WCPoints'] = results.loc[mask, 'Position'].map(WORLDCUP_POINTS_FINALS).fillna(0)
    results.loc[~mask, 'WCPoints'] = results.loc[~mask, 'Position'].map(WORLDCUP_POINTS).fillna(0)
    return results

def create_nation_cup_df(wc_points_df):
    #Nation Cup Standing 
    df = wc_points_df[['Nation', 'WCPoints', 'Discipline']]
    df_grp = df.groupby(['Nation', 'Discipline']).sum().reset_index()
    return df_grp






tab1, tab2 = st.tabs(["Overall", "By Gender and Discipline"])
with tab1:
        st.subheader("Overall Points Nations")
        df_results_wcpoints_overall = create_wc_points_df(season=2025, genders=['All'], disciplines=['All'])
        df_nations_cup_overall = df_results_wcpoints_overall[['Nation', 'WCPoints']]
        df_nations_cup_overall_grp = df_nations_cup_overall.groupby(['Nation']).sum().reset_index().sort_values(by=['WCPoints'], ascending=False)

        overall_nation_cup_fig = px.bar(
            df_nations_cup_overall_grp,
            x="Nation",
            y="WCPoints",
            text="WCPoints", 
        )
        overall_nation_cup_fig.update_traces(textposition="outside")
        overall_nation_cup_fig.update_layout(
            yaxis_title="WC Points",
            xaxis_title="Nation",
        )

        st.plotly_chart(overall_nation_cup_fig, use_container_width=True)

        #Wins, 2nd, 3rd, 4-15, 16-30 per nation and discipline AND points per nation and discipline AND % Points
        st.subheader("Summary Table")
        
        df_summary_table = df_results_wcpoints_overall[['Nation', 'Position', 'Discipline', 'WCPoints']]
        df_summary_table = df_summary_table[(df_summary_table['Position'] != 0) & (df_summary_table['WCPoints']!= 0)]
        df_summary_table['rank_group'] = df_summary_table['Position'].apply(lambda x: "Wins" if x == 1 else ("2nd" if x== 2 else ("3rd" if x==3 else ( "[4-15]" if x in [4,5,6,7,8,9,10,11,12,13,14,15] else ("[16-30]" if x in [16,17,18,19,20,21,22,23,24,25,26,27,28,29,30] else "")))))
        
        df_summary_wc_points = df_summary_table[['Nation', 'Discipline', 'WCPoints']].groupby(['Nation', 'Discipline']).sum().reset_index()
        total_points = df_summary_wc_points['WCPoints'].sum()
        
        dh_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="DH"]['WCPoints'].sum()
        sg_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="SG"]['WCPoints'].sum()
        gs_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="GS"]['WCPoints'].sum()
        sl_points = df_summary_wc_points[df_summary_wc_points['Discipline']=="SL"]['WCPoints'].sum()
        

        # Example dictionary of discipline totals
        discipline_totals = {
            "DH": dh_points,
            "SG": sg_points,
            "GS": gs_points,
            "SL": sl_points
        }

        # Map each discipline to its total
        df_summary_wc_points['TotalPoints'] = df_summary_wc_points['Discipline'].map(discipline_totals)

        # Compute percentage
        df_summary_wc_points['Percentage'] = (
            df_summary_wc_points['WCPoints'] / df_summary_wc_points['TotalPoints'] * 100
        ).fillna(0).round(2)
            

                
        df_summary_counts = (
            df_summary_table
            .groupby(['Nation', 'Discipline', 'rank_group'])
            .size()
            .reset_index(name='Count')
        )
        df_summary_pivot = df_summary_counts.pivot_table(
            index=['Nation', 'Discipline'], 
            columns='rank_group', 
            values='Count', 
            aggfunc=sum,
            fill_value=0
        )
        df_summary_pivot = df_summary_pivot.reset_index()
        df_summary_all = pd.merge(df_summary_pivot, df_summary_wc_points, how="left", on=['Nation', 'Discipline'])
        
        st.dataframe(
             df_summary_all,
             width="stretch",
             hide_index=True,
             column_order=['Nation', 'Discipline', 'Wins', '2nd', '3rd', '[4-15]', '[16-30]', 'WCPoints', 'Percentage']
        )
        AgGrid(df_summary_all, gridOptions=grid_options_2)
       



with tab2:
    filter1, filter2, filter3 = st.columns(3)

    gender_filter = filter1.selectbox(":blue[Gender]", options=GENDER) 
    discipline_filter = filter2.selectbox(":blue[Discipline]", options=DISCIPLINES)


    # Get results and wc points of selected discipline and gender
    df_results_wcpoints = create_wc_points_df(season=2025, genders=[gender_filter], disciplines=[discipline_filter])
    
    # create nations cup df
    df_nations_cup = create_nation_cup_df(df_results_wcpoints)
    
    # only nations that have points
    df_nations_cup_points = df_nations_cup[df_nations_cup['WCPoints'] != 0].reset_index(drop=True)

    # df with all nations

    # Get unique nations
    nations = df_nations_cup_points["Nation"].unique()

    # Define a color palette large enough (Plotly built-in or custom)
    # Plotly has many: px.colors.qualitative.Set1, Set2, Set3, Bold, Pastel, Dark24, etc.
    palette = px.colors.qualitative.Light24  

    # Assign each nation a unique color (cycling avoided if palette length >= nations)
    color_map = {nation: palette[i % len(palette)] for i, nation in enumerate(nations)}

    nation_cup_fig = px.bar(
        df_nations_cup_points,
        x="Discipline",
        y="WCPoints",
        color="Nation",
        barmode="group",
        text="WCPoints", 
        color_discrete_map=color_map
    )
    nation_cup_fig.update_traces(textposition="outside")
    nation_cup_fig.update_layout(
        legend=dict(
            orientation="h",   # horizontal
            yanchor="bottom",
            y=1.05,
            xanchor="center",
            x=0.5
        ),
        yaxis_title="WC Points",
        xaxis_title="Discipline",
    )
    st.subheader("Nations Ranking per Discipline")
    st.plotly_chart(nation_cup_fig, use_container_width=True)





footer="""<style>

.footer {
bottom: 0;
width: 100%;
color: rgb(177,179,181);
text-align: center;
}
</style>
<div class="footer">
<p style="font-size: 12px">Problems or Feedback? <a href="mailto:forschung+ld-tr-app@swiss-ski.ch?subject=Feedback Advanced Training Statistics App">Contact Us!</a></p>
<p style="font-size: 12px">Created by Swiss-Ski R&D - 2025</p>
</div>
"""

st.markdown(footer,unsafe_allow_html=True)
placeholder_col_1, placeholder_col_2, placeholder_col_3 = st.columns([0.46,0.08,0.46])
#!Change for production/development
# for production use: FIS_List_Dashboard-main/images/logo_rd_500.png
# placeholder_col_2.image("SwissSki_Tool/images/logo_rd_500.png")
# for development use: images/logo_rd_500.png
placeholder_col_2.image("images/logo_rd_500.png")